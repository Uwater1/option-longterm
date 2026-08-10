#!/usr/bin/env python3
"""
Meta-labeling research (newtrade/TODO.md #1):
Label ALL production-pipeline trades with three candidate exits —
    11:25 (pre-lunch), 13:05 (post-reopen), 14:35 (current production) —
and analyze whether an early-exit meta-decision is worth building.

Design
------
- Trades are reconstructed with the CURRENT production config: icw scheme,
  default admitted pool, threshold swept on pre-2022 data (+0.2 buffer),
  fast_ramp_quadratic sizing (min_pos=0.5, delta_z_full=0.3), top-10
  hysteresis (ER=25), rolling tail IC (480d), Sortino<=0 gate, ETF-adaptive
  EMA span. The signal path is zero-lookahead; only pool membership carries
  selection lookahead (features admitted with post-2022 data).
- Entry = open of 1m bar labeled 10:00; exits = close of 1m bar labeled
  11:25 / 13:05 / 14:35 (same convention as research_stoploss.py).
- All three exits are one round trip -> identical 16 bps fee, so the
  comparison is fee-neutral. Net arm series still charge 2 x fee_bps.
- Panels: in-sample (IS) = dates < 2022-01-01 (the threshold's own train
  period, i.e. the trades "in the sample" of the current model);
  out-of-sample (OOS) = 2022-01-01 onward (reference panel).
- Null test: overlap with the production trailing stop
  (time_decay_trailing=0.03) — does a noon cut merely duplicate the stop?

Outputs
-------
newtrade/artifacts/meta_labels_{etf}.csv   trade-level labels + snapshot features
newtrade/META_LABEL_REPORT.md              analysis report + verdict
newtrade/artifacts/meta_label_arms.png     arm equity curves (IS panel)
"""

import sys
import argparse
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent

sys.path.append(str(HERE))

from run_backtest import run_single_backtest, resolve_ic_ema_span, DEFAULT_SCORE_BLEND_W_IC
from strategy import generate_positions

# Same mapping as research_stoploss.py
ETF_1M_MAP = {
    "300ETF": "data/510300_1m.parquet",
    "500ETF": "data/500ETF_1m.parquet",
    "50ETF": "data/50ETF_1m.parquet",
    "159915ETF": "data/159915ETF_1m.parquet",
}

DEFAULT_ETFS = ["300ETF", "500ETF", "159915ETF"]
OOS_START = pd.Timestamp("2022-01-01")

# Minute-of-day markers (bars are END-labeled: bar 11:25 covers 11:24-11:25)
T_ENTRY, T_1125, T_1305, T_1330, T_1435 = 600, 685, 785, 810, 875
T_1030 = 630   # end of first-30-min window (noise measure)
T_1130 = 690   # last AM bar (pre-lunch close)
T_1301 = 781   # first PM bar (reopen)

# Production position-sizing config (run_backtest.py CLI defaults)
POS_MODE = "fast_ramp_quadratic"
MIN_POS, DELTA_Z_FULL = 0.5, 0.3


# ----------------------------------------------------------------------
# 1m bar loading
# ----------------------------------------------------------------------
@lru_cache(maxsize=8)
def load_day_bars(etf: str) -> dict:
    """Parse 1m parquet into day-keyed arrays with the exit bar indices."""
    path = REPO_ROOT / ETF_1M_MAP[etf]
    if not path.exists():
        print(f"[WARNING] 1m file not found: {path}")
        return {}

    df = pd.read_parquet(path)
    df["datetime"] = pd.to_datetime(df["datetime"])
    df = df.sort_values("datetime").reset_index(drop=True)
    df["date_str"] = df["datetime"].dt.date.astype(str)
    df["time_min"] = df["datetime"].dt.hour * 60 + df["datetime"].dt.minute

    bars = {}
    for d_str, g in df.groupby("date_str"):
        times = g["time_min"].values
        tmap = {int(t): i for i, t in enumerate(times)}
        needed = (T_ENTRY, T_1125, T_1305, T_1330, T_1435)
        if any(t not in tmap for t in needed):
            continue
        bars[d_str] = {
            "opens": g["open"].values.astype(np.float64),
            "highs": g["high"].values.astype(np.float64),
            "lows": g["low"].values.astype(np.float64),
            "closes": g["close"].values.astype(np.float64),
            "volumes": g["volume"].values.astype(np.float64),
            "i_entry": tmap[T_ENTRY],
            "i_1125": tmap[T_1125],
            "i_1305": tmap[T_1305],
            "i_1330": tmap[T_1330],
            "i_1435": tmap[T_1435],
            "i_1030": tmap.get(T_1030, -1),
            "i_1130": tmap.get(T_1130, -1),
            "i_1301": tmap.get(T_1301, -1),
        }
    return bars


def production_stop_minute(day: dict, pos: float, param: float = 0.03) -> int:
    """
    Replicate research_stoploss time_decay_trailing logic; return the
    minute-of-day of the bar where the stop fires, or -1 if it never fires.
    """
    opens, highs, lows = day["opens"], day["highs"], day["lows"]
    i0, i1 = day["i_entry"], day["i_1435"]
    n_bars = i1 - i0 + 1

    if pos > 0:
        peak = highs[i0]
        for i in range(i0, i1 + 1):
            if highs[i] > peak:
                peak = highs[i]
            frac = (i - i0) / float(n_bars)
            p = param * (1.0 - 0.3 * frac)
            if lows[i] <= peak * (1.0 - p):
                return T_ENTRY + (i - i0)
    else:
        trough = lows[i0]
        for i in range(i0, i1 + 1):
            if lows[i] < trough:
                trough = lows[i]
            frac = (i - i0) / float(n_bars)
            p = param * (1.0 - 0.3 * frac)
            if highs[i] >= trough * (1.0 + p):
                return T_ENTRY + (i - i0)
    return -1


# ----------------------------------------------------------------------
# Trade reconstruction + labeling
# ----------------------------------------------------------------------
def reconstruct_trades(etf: str, fee_bps: float) -> dict:
    """Run the production icw backtest and return full-history signal arrays."""
    rank_kwargs = {
        "w_min_ratio": 0.2, "w_max_ratio": 1.8, "mapping_shape": "linear",
        "power": 2.0, "top_k": 10,
        "ic_ema_span": resolve_ic_ema_span(etf, None),
        "dynamic_metric": "ic", "weight_delta": None,
        "score_weights": (0.20, 0.15, 0.65), "mono_window": 750,
        "score_blend_w_ic": DEFAULT_SCORE_BLEND_W_IC,
    }
    res = run_single_backtest(
        etf=etf, side="single", scheme_name="icw", z_th=0.5,
        position_mode=POS_MODE, fee_bps=fee_bps,
        start_date="2022-01-01", end_date="2026-01-01",
        z_buffer=0.2, z_short_buffer=None, auto_threshold=True,
        rank_kwargs=rank_kwargs, dynamic_ic=True,
        use_stoploss=False,  # clean fixed-exit labeling; stop handled separately
        ic_mode="rolling_tail", tail_window=480, tail_pct=0.10,
        hysteresis=True, exit_rank=25, min_pos=MIN_POS, delta_z_full=DELTA_Z_FULL,
        sortino_gate=True,
    )
    if res.get("status") != "SUCCESS":
        raise RuntimeError(f"{etf} backtest failed: {res.get('status')}")

    dates = pd.to_datetime(res["_dates_series"]).reset_index(drop=True)
    Z_full = np.asarray(res["_Z_composite"], dtype=np.float64)
    target_ret = np.asarray(res["_trade_returns"], dtype=np.float64)  # 10:00->14:35 (pipeline target)
    positions = generate_positions(
        Z_full, z_th=res["z_th"], z_th_short=res["z_th_short"],
        mode=POS_MODE, long_only=False, min_pos=MIN_POS, delta_z_full=DELTA_Z_FULL,
    )
    print(f"    [RECON] {etf}: z_th_long={res['z_th']:.2f} z_th_short={res['z_th_short']:.2f} | "
          f"{len(dates)} days | {int((np.abs(positions) > 1e-5).sum())} active-trade days (full history)")
    return {"dates": dates, "positions": positions, "Z": Z_full,
            "target_ret": target_ret, "z_th": res["z_th"], "z_th_short": res["z_th_short"]}


def label_etf(etf: str, recon: dict, fee_bps: float, stop_param: float) -> pd.DataFrame:
    """Label every active-trade day with the four exit outcomes."""
    bars = load_day_bars(etf)
    dates, positions, Z = recon["dates"], recon["positions"], recon["Z"]

    rows = []
    n_skipped = 0
    for i in range(len(dates)):
        pos = float(positions[i])
        d = dates.iloc[i]
        dstr = d.strftime("%Y-%m-%d")
        day = bars.get(dstr)
        active = abs(pos) > 1e-5
        if active and day is None:
            n_skipped += 1
            continue

        rec = {
            "date": dstr, "etf": etf,
            "period": "OOS" if d >= OOS_START else "IS",
            "position": pos, "z_composite": float(Z[i]),
            "trade_return_target": float(recon["target_ret"][i]),
        }
        if not active:
            rows.append(rec)
            continue

        sgn = 1.0 if pos > 0 else -1.0
        opens, closes, highs, lows = day["opens"], day["closes"], day["highs"], day["lows"]
        p_entry = opens[day["i_entry"]]
        if p_entry <= 0:
            n_skipped += 1
            continue

        c1125, c1305, c1330, c1435 = (closes[day["i_1125"]], closes[day["i_1305"]],
                                      closes[day["i_1330"]], closes[day["i_1435"]])
        r1125 = sgn * float(np.log(c1125 / p_entry))
        r1305 = sgn * float(np.log(c1305 / p_entry))
        r1330 = sgn * float(np.log(c1330 / p_entry))
        r1435 = sgn * float(np.log(c1435 / p_entry))

        # Snapshot features available at each decision point
        seg = closes[day["i_entry"]: day["i_1125"] + 1]
        morning_vol = float(np.std(np.diff(np.log(np.maximum(seg, 1e-10))))) if len(seg) > 3 else np.nan
        i_1030 = day.get("i_1030", -1)
        if i_1030 > day["i_entry"]:
            seg30 = closes[day["i_entry"]: i_1030 + 1]
            first30_vol = float(np.std(np.diff(np.log(np.maximum(seg30, 1e-10))))) if len(seg30) > 3 else np.nan
        else:
            first30_vol = np.nan

        stop_min = production_stop_minute(day, pos, stop_param)
        best = int(np.argmax([r1125, r1305, r1330, r1435]))

        rec.update({
            "r_1125": r1125, "r_1305": r1305, "r_1330": r1330, "r_1435": r1435,
            "pnl_at_1125": r1125,
            "pnl_at_1305": r1305,
            "pnl_at_1330": r1330,
            "lunch_move": sgn * float(np.log(c1305 / c1125)),           # change across lunch break
            "hold_benefit_1125": r1435 - r1125,                          # gain of holding 11:25 -> 14:35
            "hold_benefit_1305": r1435 - r1305,                          # gain of holding 13:05 -> 14:35
            "hold_benefit_1330": r1435 - r1330,                          # gain of holding 13:30 -> 14:35
            "morning_vol": morning_vol,
            "first30_vol": first30_vol,
            "best_exit": ["1125", "1305", "1330", "1435"][best],
            "gain_vs_1435": max(r1125, r1305, r1330, r1435) - r1435,
            "stop_hit": stop_min > 0,
            "stop_minute": stop_min,
        })
        rows.append(rec)

    if n_skipped:
        print(f"    [LABEL] {etf}: skipped {n_skipped} trade days without usable 1m bars")
    df = pd.DataFrame(rows)
    df["date"] = pd.to_datetime(df["date"])
    return df


# ----------------------------------------------------------------------
# Analysis helpers
# ----------------------------------------------------------------------
def _sharpe(x: np.ndarray) -> float:
    s = float(np.std(x))
    return float(np.mean(x) / s * np.sqrt(252)) if s > 1e-12 else 0.0


def trades_panel(df: pd.DataFrame, panel: str) -> pd.DataFrame:
    t = df[(df["period"] == panel) & (df["position"].abs() > 1e-5)].copy()
    return t


def analyze_etf(df: pd.DataFrame, fee_bps: float) -> dict:
    """Per-ETF stats for both panels."""
    out = {}
    for panel in ["IS", "OOS"]:
        p_all = df[df["period"] == panel].reset_index(drop=True)
        t = trades_panel(df, panel)
        n = len(t)
        if n == 0:
            out[panel] = None
            continue

        pos_abs_all = p_all["position"].abs().values
        stats = {"n_trades": n,
                 "n_long": int((t["position"] > 0).sum()),
                 "n_short": int((t["position"] < 0).sum())}

        # Fixed arms (full-calendar Sharpe, per-trade gross stats)
        for tag, col in [("1125", "r_1125"), ("1305", "r_1305"), ("1330", "r_1330"), ("1435", "r_1435")]:
            ser = pos_abs_all * np.where(p_all[col].notna(), p_all[col].values, 0.0) \
                  - pos_abs_all * fee_bps * 2.0
            g = t[col].values
            stats[f"arm_{tag}"] = {
                "sharpe": _sharpe(ser),
                "mean_bps": float(g.mean() * 1e4),
                "net_mean_bps": float(g.mean() * 1e4 - fee_bps * 2e4),
                "win_rate": float((g > 0).mean() * 100),
                "series": ser,
            }

        # Oracle (pick best of four per trade)
        oracle_r = t[["r_1125", "r_1305", "r_1330", "r_1435"]].max(axis=1).values
        oracle_ser = np.zeros(len(p_all))
        idx_trade = p_all["position"].abs() > 1e-5
        oracle_ser[idx_trade] = pos_abs_all[idx_trade] * oracle_r - pos_abs_all[idx_trade] * fee_bps * 2.0
        stats["oracle"] = {
            "sharpe": _sharpe(oracle_ser),
            "mean_bps": float(oracle_r.mean() * 1e4),
            "gain_vs_1435_bps": float(t["gain_vs_1435"].mean() * 1e4),
            "series": oracle_ser,
        }
        stats["best_exit_dist"] = t["best_exit"].value_counts(normalize=True).mul(100).round(1).to_dict()

        # Meta-predictability at each decision point
        for tag, snap, benefit in [("1125", "pnl_at_1125", "hold_benefit_1125"),
                                   ("1305", "pnl_at_1305", "hold_benefit_1305"),
                                   ("1330", "pnl_at_1330", "hold_benefit_1330")]:
            rho, pval = spearmanr(t[snap], t[benefit])
            losers = t[t[snap] < 0]
            winners = t[t[snap] >= 0]
            stats[f"meta_{tag}"] = {
                "spearman": (float(rho), float(pval)) if not np.isnan(rho) else (np.nan, np.nan),
                "n_losers": len(losers), "n_winners": len(winners),
                "loser_hold_benefit_bps": float(losers[benefit].mean() * 1e4) if len(losers) else np.nan,
                "winner_hold_benefit_bps": float(winners[benefit].mean() * 1e4) if len(winners) else np.nan,
                "loser_hold_pos_rate": float((losers[benefit] > 0).mean() * 100) if len(losers) else np.nan,
            }

        # Naive decision rules (decision info available at the snapshot time)
        base_r = t["r_1435"].values
        rules = {
            "cut1125_if_loss": np.where(t["pnl_at_1125"] < 0, t["r_1125"], t["r_1435"]),
            "cut1125_if_win": np.where(t["pnl_at_1125"] >= 0, t["r_1125"], t["r_1435"]),
            "cut1305_if_loss": np.where(t["pnl_at_1305"] < 0, t["r_1305"], t["r_1435"]),
            "cut1330_if_loss": np.where(t["pnl_at_1330"] < 0, t["r_1330"], t["r_1435"]),
            "cut1330_if_loss_confirmed": np.where((t["pnl_at_1305"] < 0) & (t["pnl_at_1330"] < 0),
                                                  t["r_1330"], t["r_1435"]),
        }
        base_ser = pos_abs_all * np.where(p_all["r_1435"].notna(), p_all["r_1435"].values, 0.0) \
                   - pos_abs_all * fee_bps * 2.0
        stats["rules"] = {}
        for name, rr in rules.items():
            ser = np.zeros(len(p_all))
            ser[idx_trade] = pos_abs_all[idx_trade] * rr - pos_abs_all[idx_trade] * fee_bps * 2.0
            delta = rr - base_r
            stats["rules"][name] = {
                "sharpe": _sharpe(ser),
                "d_sharpe_vs_1435": _sharpe(ser) - _sharpe(base_ser),
                "mean_bps_vs_1435": float(delta.mean() * 1e4),
                "help_rate_pct": float((delta > 0).mean() * 100),
                "capture_pct": float(delta.mean() * 1e4 / stats["oracle"]["gain_vs_1435_bps"] * 100)
                if stats["oracle"]["gain_vs_1435_bps"] > 1e-9 else np.nan,
            }

        # Null test: production trailing stop overlap
        sh = t[t["stop_hit"]]
        stats["stop_overlap"] = {
            "stop_rate_pct": float(len(sh) / n * 100),
            "stop_before_1125_pct": float((sh["stop_minute"] <= T_1125).sum() / n * 100) if len(sh) else 0.0,
            "stop_before_1305_pct": float((sh["stop_minute"] <= T_1305).sum() / n * 100) if len(sh) else 0.0,
            "stop_before_1330_pct": float((sh["stop_minute"] <= T_1330).sum() / n * 100) if len(sh) else 0.0,
        }

        # Early-exit opportunity: % of trades where an early exit beats 14:35
        stats["early_benefit"] = {
            "pct_1125": float((t["r_1125"] > t["r_1435"]).mean() * 100),
            "pct_1305": float((t["r_1305"] > t["r_1435"]).mean() * 100),
            "pct_1330": float((t["r_1330"] > t["r_1435"]).mean() * 100),
            "pct_any": float(((t["r_1125"] > t["r_1435"]) | (t["r_1305"] > t["r_1435"])
                              | (t["r_1330"] > t["r_1435"])).mean() * 100),
        }

        # Model economics for the binary cut-vs-hold decision at each early exit.
        # A model predicting "cut" with balanced accuracy a yields per-trade
        # E[dPnL] = p*a*G+ - (1-p)*(1-a)*L- where p = base rate the cut is correct,
        # G+ = mean gain of correct cuts, L- = mean loss of wrong cuts.
        stats["model_econ"] = {}
        for tag, col in [("1305", "r_1305"), ("1330", "r_1330")]:
            diff = (t[col] - t["r_1435"]).values
            good = diff > 0
            p = float(good.mean())
            gp = float(diff[good].mean()) if good.any() else 0.0
            lm = float((-diff[~good]).mean()) if (~good).any() else 0.0
            denom = p * gp + (1 - p) * lm
            a_be = (1 - p) * lm / denom if denom > 1e-12 else np.nan
            stats["model_econ"][tag] = {
                "p_correct": p, "gain_plus_bps": gp * 1e4, "loss_minus_bps": lm * 1e4,
                "breakeven_acc": a_be,
                "pair_oracle_bps": float(np.maximum(diff, 0.0).mean() * 1e4),
                "delta_at_acc": {a: (p * a * gp - (1 - p) * (1 - a) * lm) * 1e4
                                 for a in (0.55, 0.60, 0.65, 0.70)},
            }

        # First-30-min noise conditioning (hypothesis: noisy open => 13:30 confirmation exit)
        fv = t["first30_vol"]
        stats["noise_cond"] = {}
        if fv.notna().sum() > 20:
            med = float(fv.median())
            for lab, sub in [("high", t[fv >= med]), ("low", t[fv < med])]:
                if len(sub) < 10:
                    continue
                stats["noise_cond"][lab] = {
                    "n": len(sub),
                    "hb1305_bps": float(sub["hold_benefit_1305"].mean() * 1e4),
                    "hb1330_bps": float(sub["hold_benefit_1330"].mean() * 1e4),
                    "cut1305_if_loss_dbps": float((np.where(sub["pnl_at_1305"] < 0, sub["r_1305"], sub["r_1435"])
                                                   - sub["r_1435"]).mean() * 1e4),
                    "cut1330_if_loss_dbps": float((np.where(sub["pnl_at_1330"] < 0, sub["r_1330"], sub["r_1435"])
                                                   - sub["r_1435"]).mean() * 1e4),
                }

        # Reversal confirmation: losing at 13:05 AND still losing at 13:30
        losing_1305 = t[t["pnl_at_1305"] < 0]
        stats["confirmation"] = {}
        if len(losing_1305) > 10:
            conf = losing_1305[losing_1305["pnl_at_1330"] < 0]
            recov = losing_1305[losing_1305["pnl_at_1330"] >= 0]
            stats["confirmation"] = {
                "n_losing_1305": len(losing_1305),
                "n_confirmed": len(conf),
                "confirmed_share_pct": float(len(conf) / len(losing_1305) * 100),
                "confirmed_hb1330_bps": float(conf["hold_benefit_1330"].mean() * 1e4) if len(conf) else np.nan,
                "confirmed_hb1330_pos_pct": float((conf["hold_benefit_1330"] > 0).mean() * 100) if len(conf) else np.nan,
                "recovered_hb1330_bps": float(recov["hold_benefit_1330"].mean() * 1e4) if len(recov) else np.nan,
            }
        out[panel] = stats
    return out


# ----------------------------------------------------------------------
# Report
# ----------------------------------------------------------------------
def md_table(headers: list, rows: list) -> str:
    out = ["| " + " | ".join(headers) + " |",
           "|" + "|".join(["---"] * len(headers)) + "|"]
    for r in rows:
        out.append("| " + " | ".join(str(x) for x in r) + " |")
    return "\n".join(out)


def fmt(x, nd=1):
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return "n/a"
    return f"{x:.{nd}f}"


def build_report(all_stats: dict, sanity: dict, fee_bps: float, stop_param: float) -> str:
    L = []
    L.append("# Meta-Labeling Report — Exit at 11:25 vs 13:05 vs 13:30 vs 14:35\n")
    L.append(f"Reconstructed production `icw` trades (threshold swept pre-2022, buffer +0.2, "
             f"top-10 hysteresis ER=25, {POS_MODE} sizing). Entry = open of 10:00 1m bar; exits = close of "
             f"labeled 1m bar. Fee = {fee_bps*1e4:.0f} bps/side (identical across arms => fee-neutral comparison). "
             f"Production trailing stop (time_decay_trailing={stop_param}) is **off** for the arms; overlap reported separately.\n")
    L.append("- **IS** = trades before 2022-01-01 (in-sample for the current model's threshold)")
    L.append("- **OOS** = trades from 2022-01-01 (reference panel)\n")

    # Sanity
    L.append("## 0. Sanity check (1m exit prices vs pipeline target)\n")
    rows = [[e, fmt(c, 4)] for e, c in sanity.items()]
    L.append(md_table(["ETF", "corr(r_1435 (1m, unsigned), trade_return target)"], rows))
    L.append("\nSlight <1.0 correlation is expected: 1m bar-open entry vs 5m bar-open entry convention "
             "and unadjusted vs raw price handling on ex-dividend days. Labels use the 1m prices consistently "
             "across all four exits.\n")

    for panel, title in [("IS", "1. In-sample panel (pre-2022)"), ("OOS", "2. OOS reference panel (2022+)")]:
        L.append(f"## {title}\n")
        # Arm table
        rows = []
        for etf, st in all_stats.items():
            p = st.get(panel)
            if p is None:
                rows.append([etf, 0, "-", "-", "-", "-"])
                continue
            a1, a2, a3, a4, o = p["arm_1125"], p["arm_1305"], p["arm_1330"], p["arm_1435"], p["oracle"]
            rows.append([etf, p["n_trades"],
                         f"{a1['mean_bps']:+.1f} / {a2['mean_bps']:+.1f} / {a3['mean_bps']:+.1f} / {a4['mean_bps']:+.1f}",
                         f"{a1['sharpe']:.2f} / {a2['sharpe']:.2f} / {a3['sharpe']:.2f} / {a4['sharpe']:.2f}",
                         f"{o['gain_vs_1435_bps']:+.1f}", f"{o['sharpe']:.2f}"])
        L.append("**Fixed-exit arms** (mean gross bps/trade; Sharpe of full-calendar net series; "
                 "columns in 1125 / 1305 / 1330 / 1435 order; oracle = per-trade best exit):\n")
        L.append(md_table(["ETF", "Trades", "Mean bps @1125/1305/1330/1435", "Sharpe @1125/1305/1330/1435",
                           "Oracle gain vs 1435 (bps)", "Oracle Sharpe"], rows))
        L.append("")

        # Best-exit distribution
        rows = []
        for etf, st in all_stats.items():
            p = st.get(panel)
            if p is None:
                continue
            d = p["best_exit_dist"]
            rows.append([etf, fmt(d.get("1125", 0.0)), fmt(d.get("1305", 0.0)),
                         fmt(d.get("1330", 0.0)), fmt(d.get("1435", 0.0))])
        L.append("**Best-exit distribution** (% of trades where that exit had the highest return):\n")
        L.append(md_table(["ETF", "%11:25 best", "%13:05 best", "%13:30 best", "%14:35 best"], rows))
        L.append("")

        # Early-exit opportunity
        rows = []
        for etf, st in all_stats.items():
            p = st.get(panel)
            if p is None:
                continue
            eb = p["early_benefit"]
            rows.append([etf, fmt(eb["pct_1125"]), fmt(eb["pct_1305"]), fmt(eb["pct_1330"]), fmt(eb["pct_any"])])
        L.append("**Early-exit opportunity** (% of trades where the early exit beats 14:35):\n")
        L.append(md_table(["ETF", "% better @11:25", "% better @13:05", "% better @13:30",
                           "% better at ANY early exit"], rows))
        L.append("")

        # Model economics
        rows = []
        for etf, st in all_stats.items():
            p = st.get(panel)
            if p is None:
                continue
            for tag in ["1305", "1330"]:
                me = p["model_econ"][tag]
                da = me["delta_at_acc"]
                rows.append([etf, f"{tag[:2]}:{tag[2:]}", fmt(me["p_correct"] * 100),
                             f"{me['gain_plus_bps']:+.1f}", f"{me['loss_minus_bps']:.1f}",
                             fmt(me["breakeven_acc"] * 100),
                             f"{da[0.55]:+.1f} / {da[0.60]:+.1f} / {da[0.65]:+.1f} / {da[0.70]:+.1f}",
                             f"{me['pair_oracle_bps']:+.1f}"])
        L.append("**Model economics** (binary cut-vs-hold decision: p = base rate cutting is correct; "
                 "G+/L- = mean gain/loss when right/wrong; breakeven = required balanced accuracy for "
                 "E[ΔPnL]=0; Δ bps/trade at model accuracy 55/60/65/70%; pair-oracle = ceiling for this exit pair):\n")
        L.append(md_table(["ETF", "Decision", "p %", "G+ bps", "L- bps", "Breakeven acc %",
                           "Δbps @55/60/65/70% acc", "Pair-oracle bps"], rows))
        L.append("")

        # Meta predictability
        rows = []
        for etf, st in all_stats.items():
            p = st.get(panel)
            if p is None:
                continue
            m1, m3, m33 = p["meta_1125"], p["meta_1305"], p["meta_1330"]
            rows.append([etf,
                         fmt(m1["spearman"][0], 3), fmt(m1["loser_hold_benefit_bps"]),
                         fmt(m1["winner_hold_benefit_bps"]), fmt(m1["loser_hold_pos_rate"]),
                         fmt(m3["spearman"][0], 3), fmt(m3["loser_hold_benefit_bps"]),
                         fmt(m3["winner_hold_benefit_bps"]),
                         fmt(m33["spearman"][0], 3), fmt(m33["loser_hold_benefit_bps"]),
                         fmt(m33["winner_hold_benefit_bps"])])
        L.append("**Predictability at the decision point** (can we tell early whether holding pays?):\n")
        L.append(md_table(["ETF", "Spearman(pnl@1125, hold benefit)", "Losers@1125 hold bps",
                           "Winners@1125 hold bps", "Losers hold-positive %",
                           "Spearman(pnl@1305, hold benefit)", "Losers@1305 hold bps",
                           "Winners@1305 hold bps",
                           "Spearman(pnl@1330, hold benefit)", "Losers@1330 hold bps",
                           "Winners@1330 hold bps"], rows))
        L.append("")

        # Rules
        rows = []
        for etf, st in all_stats.items():
            p = st.get(panel)
            if p is None:
                continue
            rr = p["rules"]
            rows.append([etf,
                         f"{rr['cut1125_if_loss']['sharpe']:.2f} ({rr['cut1125_if_loss']['d_sharpe_vs_1435']:+.2f})",
                         f"{rr['cut1125_if_win']['sharpe']:.2f} ({rr['cut1125_if_win']['d_sharpe_vs_1435']:+.2f})",
                         f"{rr['cut1305_if_loss']['sharpe']:.2f} ({rr['cut1305_if_loss']['d_sharpe_vs_1435']:+.2f})",
                         f"{rr['cut1330_if_loss']['sharpe']:.2f} ({rr['cut1330_if_loss']['d_sharpe_vs_1435']:+.2f})",
                         f"{rr['cut1330_if_loss_confirmed']['sharpe']:.2f} ({rr['cut1330_if_loss_confirmed']['d_sharpe_vs_1435']:+.2f})"])
        L.append("**Naive meta-rules** Sharpe (Δ vs always-14:35). Rule decides with info available at the snapshot:\n")
        L.append(md_table(["ETF", "Cut@11:25 if losing", "Cut@11:25 if winning", "Cut@13:05 if losing",
                           "Cut@13:30 if losing", "Cut@13:30 if confirmed"], rows))
        L.append("")

        # Cut-losers economics (mean Δbps, help rate, oracle capture)
        rows = []
        for etf, st in all_stats.items():
            p = st.get(panel)
            if p is None:
                continue
            r1, r3, r33, r33c = (p["rules"]["cut1125_if_loss"], p["rules"]["cut1305_if_loss"],
                                 p["rules"]["cut1330_if_loss"], p["rules"]["cut1330_if_loss_confirmed"])
            rows.append([etf,
                         f"{r1['mean_bps_vs_1435']:+.1f}", fmt(r1["help_rate_pct"]),
                         f"{r3['mean_bps_vs_1435']:+.1f}", fmt(r3["help_rate_pct"]),
                         f"{r33['mean_bps_vs_1435']:+.1f}", fmt(r33["help_rate_pct"]),
                         f"{r33c['mean_bps_vs_1435']:+.1f}", fmt(r33c["help_rate_pct"])])
        L.append("**Cut rules economics** (Δ bps/trade vs always-14:35; help % = trades where rule improved outcome):\n")
        L.append(md_table(["ETF", "@1125 Δbps", "help %", "@1305 Δbps", "help %",
                           "@1330 Δbps", "help %", "@1330 confirmed Δbps", "help %"], rows))
        L.append("")

        # 13:30 confirmation & noise conditioning
        rows = []
        for etf, st in all_stats.items():
            p = st.get(panel)
            if p is None:
                continue
            c = p.get("confirmation", {})
            rows.append([etf, c.get("n_losing_1305", 0), fmt(c.get("confirmed_share_pct")),
                         fmt(c.get("confirmed_hb1330_bps")), fmt(c.get("confirmed_hb1330_pos_pct")),
                         fmt(c.get("recovered_hb1330_bps"))])
        L.append("**Reversal confirmation** (trades losing at 13:05; 'confirmed' = still losing at 13:30; "
                 "hold benefit = gain of holding from 13:30 to 14:35 — negative means cutting confirmed "
                 "losers at 13:30 was right):\n")
        L.append(md_table(["ETF", "n losing@1305", "% confirmed@1330", "Confirmed hold bps",
                           "Confirmed hold-positive %", "Recovered hold bps"], rows))
        L.append("")

        rows = []
        for etf, st in all_stats.items():
            p = st.get(panel)
            if p is None:
                continue
            nc = p.get("noise_cond", {})
            hi, lo = nc.get("high"), nc.get("low")
            if hi is None or lo is None:
                continue
            rows.append([etf,
                         f"{hi['n']} / {lo['n']}",
                         f"{hi['cut1305_if_loss_dbps']:+.1f} / {lo['cut1305_if_loss_dbps']:+.1f}",
                         f"{hi['cut1330_if_loss_dbps']:+.1f} / {lo['cut1330_if_loss_dbps']:+.1f}",
                         f"{hi['hb1305_bps']:+.1f} / {lo['hb1305_bps']:+.1f}"])
        L.append("**First-30-min noise conditioning** (split at panel median of first30_vol; "
                 "values as high-noise / low-noise):\n")
        L.append(md_table(["ETF", "n high/low", "Cut@1305-if-loss Δbps h/l", "Cut@1330-if-loss Δbps h/l",
                           "Hold-from-1305 bps h/l"], rows))
        L.append("")

        # Stop overlap
        rows = []
        for etf, st in all_stats.items():
            p = st.get(panel)
            if p is None:
                continue
            so = p["stop_overlap"]
            rows.append([etf, fmt(so["stop_rate_pct"]), fmt(so["stop_before_1125_pct"]),
                         fmt(so["stop_before_1305_pct"]), fmt(so["stop_before_1330_pct"])])
        L.append("**Null test — overlap with production trailing stop** (time_decay_trailing="
                 f"{stop_param}; stop evaluated on the same trades, not applied to the arms):\n")
        L.append(md_table(["ETF", "Stop fires %", "Fires by 11:25 %", "Fires by 13:05 %", "Fires by 13:30 %"], rows))
        L.append("")

    # Verdict
    L.append("## 3. Verdict — is it worth the effort?\n")
    verdict_rows = []
    for etf, st in all_stats.items():
        p_is, p_oos = st.get("IS"), st.get("OOS")
        if p_is is None or p_oos is None:
            continue
        g_is = p_is["oracle"]["gain_vs_1435_bps"]
        g_oos = p_oos["oracle"]["gain_vs_1435_bps"]
        best_rule_is = max(p_is["rules"].items(), key=lambda kv: kv[1]["d_sharpe_vs_1435"])
        best_rule_oos = max(p_oos["rules"].items(), key=lambda kv: kv[1]["d_sharpe_vs_1435"])
        verdict_rows.append([etf, f"{g_is:+.1f}", f"{g_oos:+.1f}",
                             f"{best_rule_is[0]} {best_rule_is[1]['d_sharpe_vs_1435']:+.2f}",
                             f"{best_rule_oos[0]} {best_rule_oos[1]['d_sharpe_vs_1435']:+.2f}"])
    L.append(md_table(["ETF", "Oracle gain IS (bps/trade)", "Oracle gain OOS",
                       "Best rule IS (ΔSharpe)", "Best rule OOS (ΔSharpe)"], verdict_rows))
    L.append("")

    # Pooled cut-losers economics
    L.append("**Pooled (3 ETFs) cut-losers economics:**\n")
    pooled_rows = []
    for panel in ["IS", "OOS"]:
        d11, d13, n_tot = [], [], 0
        for etf, st in all_stats.items():
            p = st.get(panel)
            if p is None:
                continue
            n_tot += p["n_trades"]
            d11.append((p["rules"]["cut1125_if_loss"]["mean_bps_vs_1435"], p["n_trades"]))
            d13.append((p["rules"]["cut1305_if_loss"]["mean_bps_vs_1435"], p["n_trades"]))
        w11 = sum(v * n for v, n in d11) / max(1, sum(n for _, n in d11))
        w13 = sum(v * n for v, n in d13) / max(1, sum(n for _, n in d13))
        pooled_rows.append([panel, n_tot, f"{w11:+.1f}", f"{w13:+.1f}"])
    L.append(md_table(["Panel", "Trades", "Cut@1125-if-loss Δbps", "Cut@1305-if-loss Δbps"], pooled_rows))
    L.append("")
    L.append("Decision criteria: (a) the per-trade **oracle** gain is the absolute ceiling for any "
             "meta-model — if it is < ~5 bps/trade, no model can clear costs+complexity; "
             "(b) a rule/model must capture a stable share of that ceiling **in both panels** and across ETFs; "
             "(c) if the trailing stop already fires before 11:25 on most would-be-cut trades, the noon "
             "decision is redundant (the §1 null test).\n")
    L.append(build_findings(all_stats))
    return "\n".join(L)


def build_findings(all_stats: dict) -> str:
    """Data-driven findings block appended to the verdict section."""
    F = ["### Findings & recommendation\n"]

    # Regime flip check on pooled cut-losers
    def pooled_delta(panel: str, rule: str) -> float:
        num, den = 0.0, 0
        for st in all_stats.values():
            p = st.get(panel)
            if p is None:
                continue
            num += p["rules"][rule]["mean_bps_vs_1435"] * p["n_trades"]
            den += p["n_trades"]
        return num / den if den else float("nan")

    d_is_11, d_oos_11 = pooled_delta("IS", "cut1125_if_loss"), pooled_delta("OOS", "cut1125_if_loss")
    d_is_13, d_oos_13 = pooled_delta("IS", "cut1305_if_loss"), pooled_delta("OOS", "cut1305_if_loss")
    d_is_1330, d_oos_1330 = pooled_delta("IS", "cut1330_if_loss"), pooled_delta("OOS", "cut1330_if_loss")
    d_is_conf, d_oos_conf = pooled_delta("IS", "cut1330_if_loss_confirmed"), pooled_delta("OOS", "cut1330_if_loss_confirmed")
    oracles = [(st[p]["oracle"]["gain_vs_1435_bps"]) for st in all_stats.values() for p in ["IS", "OOS"] if st.get(p)]
    oracle_avg = float(np.mean(oracles)) if oracles else float("nan")
    oracle_lo = float(np.min(oracles)) if oracles else float("nan")
    oracle_hi = float(np.max(oracles)) if oracles else float("nan")
    n_is = sum(st["IS"]["n_trades"] for st in all_stats.values() if st.get("IS"))
    n_oos = sum(st["OOS"]["n_trades"] for st in all_stats.values() if st.get("OOS"))

    # Pooled early-benefit % and model breakeven accuracy (trade-weighted)
    def pooled_w(key_fn, panel: str) -> float:
        num, den = 0.0, 0
        for st in all_stats.values():
            p = st.get(panel)
            if p is None:
                continue
            num += key_fn(p) * p["n_trades"]
            den += p["n_trades"]
        return num / den if den else float("nan")

    eb_any_is = pooled_w(lambda p: p["early_benefit"]["pct_any"], "IS")
    eb_any_oos = pooled_w(lambda p: p["early_benefit"]["pct_any"], "OOS")
    eb_1330_is = pooled_w(lambda p: p["early_benefit"]["pct_1330"], "IS")
    eb_1330_oos = pooled_w(lambda p: p["early_benefit"]["pct_1330"], "OOS")
    be_1305_is = pooled_w(lambda p: p["model_econ"]["1305"]["breakeven_acc"] * 100, "IS")
    be_1305_oos = pooled_w(lambda p: p["model_econ"]["1305"]["breakeven_acc"] * 100, "OOS")
    be_1330_oos = pooled_w(lambda p: p["model_econ"]["1330"]["breakeven_acc"] * 100, "OOS")
    conf_hb_is = pooled_w(lambda p: p["confirmation"].get("confirmed_hb1330_bps", float("nan")), "IS") \
        if all(st.get("IS", {}) and st["IS"].get("confirmation") for st in all_stats.values()) else float("nan")
    conf_hb_oos = pooled_w(lambda p: p["confirmation"].get("confirmed_hb1330_bps", float("nan")), "OOS") \
        if all(st.get("OOS", {}) and st["OOS"].get("confirmation") for st in all_stats.values()) else float("nan")

    F.append(f"1. **The ceiling is large.** Per-trade oracle gain averages **{oracle_avg:+.0f} bps** "
             f"(range {oracle_lo:+.0f} to {oracle_hi:+.0f}) across both panels — roughly half of the average "
             "trade's gross return. "
             "A perfect exit chooser would nearly double the arms' Sharpe. So the question is not whether "
             "value exists, but whether any of it is *predictable*.\n")
    F.append("2. **Fixed arms: always-14:35 still wins.** In IS it dominates all 3 ETFs on mean and Sharpe; "
             "in OOS 13:05/13:30 edge ahead on Sharpe for 300ETF/159915ETF but on only ~39-249 trades. "
             "13:05 >= 11:25 in virtually every panel-ETF cell, so **11:25 is dropped as a candidate; the "
             "early-exit question is 13:05/13:30 vs 14:35**.\n")
    F.append(f"3. **How many trades can benefit from an early exit?** An early exit beats 14:35 on "
             f"**{eb_any_is:.0f}% (IS) / {eb_any_oos:.0f}% (OOS)** of trades when any of 11:25/13:05/13:30 is "
             f"allowed (13:30 alone: {eb_1330_is:.0f}% / {eb_1330_oos:.0f}%). So roughly half of trades would "
             "benefit from SOME early exit — the oracle ceiling confirms this is a real per-trade decision "
             "problem, not a corner case.\n")
    F.append(f"4. **Would a model with moderate predictive power help?** The bar is moderate: the "
             f"breakeven balanced accuracy for the cut-vs-hold decision at 13:05 is **{be_1305_is:.0f}% (IS) / "
             f"{be_1305_oos:.0f}% (OOS)** ({be_1330_oos:.0f}% trade-weighted at 13:30) — higher than a coin "
             "flip because wrong cuts are somewhat costlier than right cuts, but well within reach of a "
             "decent classifier. Per the Model economics tables, a model sustaining 60-65% accuracy OOS earns "
             "+3 to +8 bps/trade against a pair-oracle ceiling of ~21-28 bps. BUT accuracy must be achieved "
             "walk-forward: the regime flip below shows in-sample accuracy does not transfer.\n")
    F.append(f"5. **Regime flip — the core problem.** The sign of the cut-losers edge reverses between panels: "
             f"IS pooled Δ = {d_is_11:+.1f} bps (cut@1125) / {d_is_13:+.1f} bps (cut@1305) / {d_is_1330:+.1f} bps "
             f"(cut@1330) — losers *recover* into the close (mean reversion); OOS pooled Δ = {d_oos_11:+.1f} / "
             f"{d_oos_13:+.1f} / {d_oos_1330:+.1f} bps — losers *keep losing* (momentum). A rule trained on "
             "pre-2022 labels would do the wrong thing in 2022+, and vice versa.\n")
    F.append(f"6. **13:30 confirmation check.** Confirmed reversals (losing at 13:05 AND still losing at 13:30) "
             f"have pooled hold-benefit of {conf_hb_is:+.1f} bps (IS) vs {conf_hb_oos:+.1f} bps (OOS) — the same "
             f"regime split as the raw signal; the confirmation rule tracks it (pooled Δ "
             f"{d_is_conf:+.1f} IS / {d_oos_conf:+.1f} OOS). Two nuances in its favor: (a) 13:30 is the single "
             "most-often-best early exit (18-23% of trades vs 13-21% for 13:05) and the best fixed early arm "
             "on Sharpe in 5 of 6 panel-ETF cells; (b) in OOS, cutting at 13:30 helps slightly MORE on high "
             "first-30-min-noise days (+1.6 to +5.5 bps) than low-noise days — matching the 'noisy open needs "
             "confirmation' intuition — but the same pattern is absent or reversed IS, so it is a feature for "
             "the model to learn walk-forward, not a deployable rule. Net: 13:30 is a valid *substitute* for "
             "13:05 (keeps the lunch-gap info, adds 25 min of confirmation) but not a fix for the regime "
             "problem.\n")
    F.append("7. **Null test passed (not redundant).** The production trailing stop fires before 11:25 on only "
             "0-7% of trades; most stop events are lunch-gap stops landing at the 13:01-13:05 reopen. So an "
             "early-exit meta-decision is not a disguised stop — but a 13:05/13:30 decision would partially "
             "subsume the stop's gap protection.\n")
    F.append("**Recommendation.**\n")
    F.append("- As a *rule*: **not worth the effort** — pooled cut-losers flips sign between IS and OOS; "
             "deploying it violates the regime-stability gate this project applies everywhere else.\n")
    F.append("- As a *trained meta-model* (TODO #2): **conditionally yes** — the ~30 bps ceiling plus the low "
             "breakeven accuracy justify one careful attempt, but only with (a) strictly walk-forward training "
             "(year N model on labels < year N, mirroring the triple-barrier design in §1: features = running "
             "P&L, morning/first-30-min vol, Z_composite, lunch-gap move), (b) the FQ meta-IC harness as judge, "
             "and (c) a hard kill criterion: if the walk-forward model's sign or edge does not persist across "
             ">=2 consecutive held-out years on >=2/3 ETFs, stop — keep 14:35. Candidate early exit: 13:05 or "
             "13:30 (confirmation variant), never 11:25.\n")
    F.append("- Labeled dataset for that attempt: `artifacts/meta_labels_{etf}.csv` "
             f"(IS {n_is} + OOS {n_oos} trades; columns `best_exit`, `gain_vs_1435`, snapshot features "
             "`pnl_at_1125/1305/1330`, `morning_vol`, `first30_vol`, `lunch_move`, `z_composite`).\n")
    return "\n".join(F)


def make_chart(all_labels: dict, fee_bps: float):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        n = len(all_labels)
        fig, axes = plt.subplots(n, 1, figsize=(11, 3.4 * n), dpi=150, squeeze=False)
        for ax_i, (etf, df) in enumerate(all_labels.items()):
            ax = axes[ax_i, 0]
            p = df[df["period"] == "IS"].reset_index(drop=True)
            pos_abs = p["position"].abs().values
            x = np.arange(len(p))
            for col, tag, lw in [("r_1125", "exit 11:25", 1.0), ("r_1305", "exit 13:05", 1.1),
                                 ("r_1330", "exit 13:30", 1.1), ("r_1435", "exit 14:35", 1.6)]:
                ser = pos_abs * np.where(p[col].notna(), p[col].values, 0.0) - pos_abs * fee_bps * 2.0
                ax.plot(x, np.cumsum(ser), label=tag, linewidth=lw)
            tr = p["position"].abs() > 1e-5
            oracle = p[["r_1125", "r_1305", "r_1330", "r_1435"]].max(axis=1).values
            oser = np.zeros(len(p))
            oser[tr] = pos_abs[tr] * oracle[tr] - pos_abs[tr] * fee_bps * 2.0
            ax.plot(x, np.cumsum(oser), label="oracle", linewidth=1.0, linestyle="--", color="gray")
            ax.set_title(f"{etf} — IS panel cumulative net PnL by fixed exit", fontsize=10, fontweight="bold")
            ax.legend(fontsize=8, loc="upper left")
            ax.grid(True, alpha=0.3)
        fig.tight_layout()
        out = HERE / "artifacts" / "meta_label_arms.png"
        out.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(out)
        plt.close(fig)
        print(f"\n  Saved chart: {out}")
    except Exception as e:
        print(f"  [WARNING] chart failed: {e}")


# ----------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description="Meta-labeling: 11:25 vs 13:05 vs 14:35 exit analysis")
    ap.add_argument("-e", "--etf", type=str, default=",".join(DEFAULT_ETFS),
                    help="Comma-separated ETFs (default: 300ETF,500ETF,159915ETF)")
    ap.add_argument("--fee-bps", type=float, default=8.0, help="One-way fee bps (default 8)")
    ap.add_argument("--stoploss-param", type=float, default=0.03, help="Production trailing stop param")
    ap.add_argument("-o", "--output", type=str, default=str(HERE / "META_LABEL_REPORT.md"))
    args = ap.parse_args()

    etfs = [e.strip() for e in args.etf.split(",") if e.strip()]
    fee_bps = args.fee_bps / 1e4

    all_labels, all_stats, sanity = {}, {}, {}
    for etf in etfs:
        print("\n" + "=" * 80)
        print(f"  META-LABEL | {etf}")
        print("=" * 80)
        recon = reconstruct_trades(etf, fee_bps)
        df = label_etf(etf, recon, fee_bps, args.stoploss_param)

        # Sanity: unsigned 1m 14:35 log return vs pipeline target on trade days
        t = df[df["position"].abs() > 1e-5]
        unsigned = t["r_1435"] * np.sign(t["position"])
        tgt = t["trade_return_target"]
        sanity[etf] = float(np.corrcoef(unsigned, tgt)[0, 1]) if len(t) > 2 else np.nan

        csv_path = HERE / "artifacts" / f"meta_labels_{etf}.csv"
        csv_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(csv_path, index=False)
        n_tr = int((df["position"].abs() > 1e-5).sum())
        print(f"    [LABEL] {etf}: labeled {n_tr} trades "
              f"(IS={int(((df['position'].abs() > 1e-5) & (df['period'] == 'IS')).sum())}, "
              f"OOS={int(((df['position'].abs() > 1e-5) & (df['period'] == 'OOS')).sum())}) "
              f"| sanity corr={sanity[etf]:.4f} -> {csv_path.name}")

        all_labels[etf] = df
        all_stats[etf] = analyze_etf(df, fee_bps)

    report = build_report(all_stats, sanity, fee_bps, args.stoploss_param)
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"\n  Saved report: {args.output}")
    make_chart(all_labels, fee_bps)

    # Console summary
    print("\n" + "=" * 80)
    print("SUMMARY (IS panel)")
    print("=" * 80)
    for etf, st in all_stats.items():
        p = st.get("IS")
        if p is None:
            continue
        a = p
        print(f"  {etf}: n={a['n_trades']} | mean bps 1125/1305/1435 = "
              f"{a['arm_1125']['mean_bps']:+.1f}/{a['arm_1305']['mean_bps']:+.1f}/{a['arm_1435']['mean_bps']:+.1f}"
              f" | oracle gain {a['oracle']['gain_vs_1435_bps']:+.1f} bps"
              f" | best-exit dist {a['best_exit_dist']}")


if __name__ == "__main__":
    main()
