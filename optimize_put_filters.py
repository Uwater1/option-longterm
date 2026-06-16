"""
Real-Data Filter Optimizer for Long Put (Selective Hedge)
===========================================================
Mirrors optimize_filters.py but for put buying.
Pre-calculates put leg P&L for all real cycles at OTM levels 0-3,
then grid-searches filter conditions using the synthetic-informed filter space.

Profit-first composite score (v2):
  TotalPnL (35%), FilterLift (30%), Sharpe (15%), MaxDD (10%),
  WinRate (5%), PlacementRate (5%)

Usage:
  python optimize_put_filters.py [50|300|500]
  python optimize_put_filters.py 300 --level 1
  python optimize_put_filters.py 300 --sweep-levels   # rank all OTM levels 1-3
"""
import os
import sys
import argparse
import pandas as pd
import numpy as np
import pandas_ta as ta

sys.path.append(os.path.abspath("."))

from backtest_engine import (
    select_underlying, load_data, get_cycles,
    get_strike_by_level, calc_leg_pnl, PATH_IV_CACHE, IV_THRESHOLD
)


# ── Pre-calculate put leg P&L for all cycles at OTM levels 0-3 ──────────────

def precalculate_put_legs(opt, etf, cycles, levels=(0, 1, 2, 3)):
    """Return DataFrame with per-cycle put P&L at each OTM level."""
    print("Precalculating put leg P&Ls for all cycles (levels 0-3)...")
    rows = []
    for cyc in cycles:
        entry  = cyc["entry_date"]
        expiry = cyc["expiry_date"]
        row = {"entry_date": entry, "expiry_date": expiry}
        for lv in levels:
            put_leg = get_strike_by_level(opt, etf, entry, expiry, "P", lv)
            pnl = calc_leg_pnl(put_leg, opt, etf, expiry, "buy", True)
            row[f"Put{lv}"] = pnl["net_rmb"] if pnl is not None else 0.0
        rows.append(row)
    return pd.DataFrame(rows)


# ── Grid search ─────────────────────────────────────────────────────────────

def run_optimization(etf_choice, otm_level=1):
    select_underlying(etf_choice)
    inst, opt, etf = load_data()

    # Additional indicators on ETF daily data (mirrors optimize_filters.py)
    if "close_adj" in etf.columns:
        close_for_ind = etf["close_adj"]
        high_for_ind = etf["high_adj"]
        low_for_ind = etf["low_adj"]
    else:
        close_for_ind = etf["close"]
        high_for_ind = etf["high"]
        low_for_ind = etf["low"]

    etf["ema20"]  = ta.ema(close_for_ind, length=20)
    etf["roc20"]  = ta.roc(close_for_ind, length=20)
    etf["roc5"]   = ta.roc(close_for_ind, length=5)
    bb = ta.bbands(close_for_ind, length=20, std=2)
    if bb is not None:
        etf["bbu20"]  = bb["BBU_20_2.0_2.0"]
        etf["bbl20"]  = bb["BBL_20_2.0_2.0"]
    else:
        etf["bbu20"]  = np.nan
        etf["bbl20"]  = np.nan
    etf["vol20"]  = close_for_ind.pct_change().rolling(20).std() * np.sqrt(252)
    etf["vol20_median"] = etf["vol20"].rolling(252).median()
    macd = ta.macd(close_for_ind)
    etf["macd_hist"] = macd.iloc[:, 1] if macd is not None else np.nan

    cycles = get_cycles(opt, etf)
    print(f"Found {len(cycles)} cycles for {etf_choice}ETF.\n")

    # Pre-calculate put P&Ls
    df_legs = precalculate_put_legs(opt, etf, cycles, levels=(0, 1, 2, 3))
    put_col = f"Put{otm_level}"
    put_pnl = df_legs[put_col].values

    # Align indicators with cycle entry dates
    cycle_indicators = []
    for cyc in cycles:
        idx = cyc["entry_date"].normalize()
        row = etf.loc[idx]
        cycle_indicators.append({
            "entry_date":   cyc["entry_date"],
            "rsi14":        row["rsi14"],
            "close":        row["close_adj"] if "close_adj" in etf.columns else row["close"],
            "sma20":        row["sma20"],
            "ema20":        row["ema20"],
            "sma50":        row["sma50"],
            "atr20":        row["atr20"],
            "bbu20":        row["bbu20"],
            "bbl20":        row["bbl20"],
            "roc10":        row["roc10"],
            "roc20":        row["roc20"],
            "roc5":         row["roc5"],
            "vol20":        row["vol20"],
            "vol20_median": row["vol20_median"],
            "macd_hist":    row["macd_hist"],
        })
    df_ind = pd.DataFrame(cycle_indicators)

    # ── Synthetic-informed filter grid ──────────────────────────────────
    # Puts profit when market drops → buy when indicators suggest vulnerability.
    # Grid informed by research_put_filters.py results:
    #   Best: f_rsi40, f_rsi45, f_bbl, f_bbl_atr, f_vol_high, combos
    rsi_thresholds    = [40, 45, 50, 55, 60, 999.0]   # RSI < threshold
    bbl_modes         = [0, 1, 2, 3]  # 0=skip, 1=close<bbl, 2=close<bbl-0.5*atr, 3=close<bbl+0.5*atr
    sma50_modes       = [False, True]   # close < SMA50
    vol_high_modes    = [False, True]   # vol20 > vol20_median
    roc10_thresholds  = [-999.0, -3.0, -5.0, -7.0]    # roc10 < threshold
    macd_neg_modes    = [False, True]   # MACD hist < 0

    results = []
    n_cycles = len(put_pnl)

    # Baseline: always buy → avg P&L per cycle
    baseline_avg = put_pnl.mean()

    for rsi_t in rsi_thresholds:
        for bbl_mode in bbl_modes:
            for sma50_on in sma50_modes:
                for vol_on in vol_high_modes:
                    for roc_t in roc10_thresholds:
                        for macd_on in macd_neg_modes:

                            # Build boolean mask
                            cond_rsi = (
                                pd.Series(True, index=df_ind.index) if rsi_t == 999.0
                                else df_ind["rsi14"] < rsi_t
                            )

                            if bbl_mode == 0:
                                cond_bbl = pd.Series(True, index=df_ind.index)
                            elif bbl_mode == 1:
                                cond_bbl = df_ind["close"] < df_ind["bbl20"]
                            elif bbl_mode == 2:
                                cond_bbl = df_ind["close"] < (df_ind["bbl20"] - 0.5 * df_ind["atr20"])
                            else:  # mode 3
                                cond_bbl = df_ind["close"] < (df_ind["bbl20"] + 0.5 * df_ind["atr20"])

                            cond_sma50 = (
                                df_ind["close"] < df_ind["sma50"] if sma50_on
                                else pd.Series(True, index=df_ind.index)
                            )

                            cond_vol = (
                                df_ind["vol20"] > df_ind["vol20_median"] if vol_on
                                else pd.Series(True, index=df_ind.index)
                            )

                            if roc_t == -999.0:
                                cond_roc = pd.Series(True, index=df_ind.index)
                            else:
                                cond_roc = df_ind["roc10"] < roc_t

                            cond_macd = (
                                df_ind["macd_hist"] < 0 if macd_on
                                else pd.Series(True, index=df_ind.index)
                            )

                            filter_passed = (
                                cond_rsi & cond_bbl & cond_sma50
                                & cond_vol & cond_roc & cond_macd
                            ).fillna(False)
                            fmask = filter_passed.values

                            # Selective hedge: pass → buy put; fail → skip (P&L = 0)
                            cycle_pnls = np.where(fmask, put_pnl, 0.0)

                            total_pnl   = cycle_pnls.sum()
                            n_placed    = int(fmask.sum())
                            placed_pnls = cycle_pnls[fmask]
                            win_rate    = np.mean(placed_pnls > 0) if n_placed > 0 else 0.0
                            std_pnl     = cycle_pnls.std()
                            mean_pnl    = cycle_pnls.mean()
                            sharpe      = (mean_pnl / std_pnl * np.sqrt(12)) if std_pnl > 0 else 0.0

                            cum_pnl = np.cumsum(cycle_pnls)
                            max_dd  = (cum_pnl - np.maximum.accumulate(cum_pnl)).min()

                            placement_rate = n_placed / n_cycles if n_cycles > 0 else 0.0

                            # Filter lift: avg P&L on placed cycles minus baseline avg
                            avg_pnl_placed = placed_pnls.mean() if n_placed > 0 else 0.0
                            filter_lift    = avg_pnl_placed - baseline_avg

                            # Skip overly restrictive filters (< 5% placement)
                            if placement_rate < 0.05:
                                continue

                            # Also skip "always on" (all filters disabled)
                            all_on = (rsi_t == 999.0 and bbl_mode == 0
                                      and not sma50_on and not vol_on
                                      and roc_t == -999.0 and not macd_on)

                            results.append({
                                "rsi_thresh":     rsi_t,
                                "bbl_mode":       bbl_mode,
                                "sma50":          sma50_on,
                                "vol_high":       vol_on,
                                "roc10_thresh":   roc_t,
                                "macd_neg":       macd_on,
                                "baseline":       all_on,
                                "placement_rate": placement_rate,
                                "n_placed":       n_placed,
                                "total_pnl":      total_pnl,
                                "win_rate":       win_rate,
                                "sharpe":         sharpe,
                                "max_dd":         max_dd,
                                "filter_lift":    filter_lift,
                            })

    df_res = pd.DataFrame(results)
    if df_res.empty:
        print("No valid filter combinations found.")
        return df_res

    # ── Multi-criteria composite scoring (normalized) ───────────────────
    def norm(col, higher_better=True):
        val = df_res[col].values.astype(float)
        vmin, vmax = val.min(), val.max()
        if vmax == vmin:
            return np.zeros_like(val)
        if higher_better:
            return (val - vmin) / (vmax - vmin)
        else:
            return (vmax - val) / (vmax - vmin)

    # Profit-first composite (v2): TotalPnL 35%, FilterLift 30%, Sharpe 15%,
    #                              MaxDD 10%, WinRate 5%, PlacementRate 5%
    df_res["score"] = (
        0.35 * norm("total_pnl", True)
      + 0.30 * norm("filter_lift", True)
      + 0.15 * norm("sharpe", True)
      + 0.10 * norm("max_dd", False)
      + 0.05 * norm("win_rate", True)
      + 0.05 * norm("placement_rate", True)
    )

    df_res = df_res.sort_values(by="score", ascending=False).reset_index(drop=True)
    return df_res


# ── Level sweep helper ───────────────────────────────────────────────────────

def sweep_levels(etf_choice, levels=(1, 2, 3)):
    """Run optimizer for each OTM level and print a summary ranking."""
    summary = []
    for lv in levels:
        print(f"\n{'='*60}")
        print(f"  Sweeping OTM Level {lv} — {etf_choice}ETF")
        print(f"{'='*60}")
        df = run_optimization(etf_choice, otm_level=lv)
        if df.empty:
            continue
        best = df.iloc[0]
        BBL_LABELS = {0: "skip", 1: "<BBL", 2: "<BBL-0.5ATR", 3: "<BBL+0.5ATR"}
        summary.append({
            "OTM Level":     lv,
            "Total P&L":     best["total_pnl"],
            "FilterLift":    best["filter_lift"],
            "Sharpe":        best["sharpe"],
            "MaxDD":         best["max_dd"],
            "WinRate":       best["win_rate"],
            "Placement":     best["placement_rate"],
            "Score":         best["score"],
            "RSI<":          best["rsi_thresh"],
            "BBL":           BBL_LABELS.get(int(best["bbl_mode"]), "?"),
            "SMA50":         best["sma50"],
            "VolHigh":       best["vol_high"],
            "ROC10<":        best["roc10_thresh"],
            "MACD<0":        best["macd_neg"],
        })
        # Save per-level CSV
        os.makedirs("backtest", exist_ok=True)
        out_name = f"backtest/optimization_put_{etf_choice}ETF_level{lv}.csv"
        df.head(200).to_csv(out_name, index=False)
        print(f"  Saved → {out_name}")

    if not summary:
        print("No results.")
        return

    df_sum = pd.DataFrame(summary)
    df_sum = df_sum.sort_values("Total P&L", ascending=False).reset_index(drop=True)
    print("\n" + "="*100)
    print(f"  LEVEL SWEEP SUMMARY — {etf_choice}ETF  (sorted by Total P&L)")
    print(f"  Score: 35%TotalPnL + 30%FilterLift + 15%Sharpe + 10%MaxDD + 5%WinRate + 5%Place")
    print("="*100)
    pd.set_option("display.float_format", lambda x: f"{x:.3f}")
    pd.set_option("display.max_columns", 20)
    pd.set_option("display.width", 200)
    print(df_sum.to_string(index=False))
    print()


# ── CLI ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Real-Data Put Filter Optimizer")
    parser.add_argument("etf", nargs="?", default="300",
                        help="ETF choice: 50, 300, or 500")
    parser.add_argument("--level", type=int, default=1,
                        help="OTM level for put (0=ATM-ish, 1=closest OTM, etc.)")
    parser.add_argument("--sweep-levels", action="store_true",
                        help="Sweep OTM levels 1-3 and compare best filters")
    args = parser.parse_args()

    if args.sweep_levels:
        sweep_levels(args.etf)
        import sys; sys.exit(0)

    print(f"Running put filter optimization for {args.etf}ETF at OTM level {args.level}")
    df_res = run_optimization(args.etf, otm_level=args.level)

    if df_res.empty:
        sys.exit(1)

    # ── Display results ────────────────────────────────────────────────
    BBL_LABELS = {0: "skip", 1: "<BBL", 2: "<BBL-0.5ATR", 3: "<BBL+0.5ATR"}

    print("\n" + "=" * 120)
    print(f"  TOP 20 PUT FILTERS — {args.etf}ETF  OTM Level {args.level}")
    print(f"  Score: 35%TotalPnL + 30%FilterLift + 15%Sharpe + 10%MaxDD + 5%WinRate + 5%Place")
    print("=" * 120)

    display_cols = [
        "rsi_thresh", "bbl_mode", "sma50", "vol_high", "roc10_thresh",
        "macd_neg", "placement_rate", "n_placed", "total_pnl",
        "win_rate", "sharpe", "max_dd", "filter_lift", "score",
    ]

    top = df_res[display_cols].head(20).copy()
    top["bbl_mode"] = top["bbl_mode"].map(BBL_LABELS)
    pd.set_option("display.float_format", lambda x: f"{x:.4f}")
    pd.set_option("display.max_columns", 20)
    pd.set_option("display.width", 200)
    print(top.to_string())

    # ── Baseline comparison ────────────────────────────────────────────
    base_row = df_res[df_res["baseline"] == True]
    if not base_row.empty:
        b = base_row.iloc[0]
        print(f"\n  BASELINE (always buy): Total={b['total_pnl']:.0f}, "
              f"MaxDD={b['max_dd']:.0f}, Sharpe={b['sharpe']:.3f}, "
              f"WinRate={b['win_rate']:.1%}, Place={b['placement_rate']:.1%}")

    # ── Save to CSV ────────────────────────────────────────────────────
    os.makedirs("backtest", exist_ok=True)
    out_name = f"backtest/optimization_put_{args.etf}ETF_level{args.level}.csv"
    df_res.head(200).to_csv(out_name, index=False)
    print(f"\n  Saved top 200 results to {out_name}")

    # ── Best filter summary for PutStrategy ────────────────────────────
    best = df_res.iloc[0]
    print(f"\n  ── BEST FILTER for PutStrategy ───────────────────────────")
    print(f"  RSI   < {best['rsi_thresh']:.0f}")
    print(f"  BBL   : {BBL_LABELS.get(int(best['bbl_mode']), '?')}")
    print(f"  SMA50 : {'close < SMA50' if best['sma50'] else 'disabled'}")
    print(f"  Vol20 : {'vol20 > median' if best['vol_high'] else 'disabled'}")
    roc_label = f"roc10 < {best['roc10_thresh']:.1f}%" if best['roc10_thresh'] > -900 else "disabled"
    print(f"  ROC10 : {roc_label}")
    print(f"  MACD  : {'hist < 0' if best['macd_neg'] else 'disabled'}")
    print(f"  ──────────────────────────────────────────────────────────")
    print(f"  Score       : {best['score']:.4f}")
    print(f"  Total P&L   : {best['total_pnl']:>+.0f} RMB")
    print(f"  Sharpe      : {best['sharpe']:>+.3f}")
    print(f"  MaxDD       : {best['max_dd']:>+.0f} RMB")
    print(f"  WinRate     : {best['win_rate']:.1%}")
    print(f"  Placement   : {best['placement_rate']:.1%} ({best['n_placed']:.0f} cycles)")
    print(f"  Filter Lift : {best['filter_lift']:>+.2f} RMB/cycle")
    print()
