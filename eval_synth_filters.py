"""
Enhanced Synthetic Data Filter Evaluation for 500ETF
=====================================================
Simulates the FULL strategy per filter (pass→OTM2+3 call, fail→OTM4 call, + Put L1 always)
and evaluates with risk metrics:
  1. Per-level OTM breakdown (calls)
  2. Full strategy simulation → per-date P&L, cumulative curve
  3. Risk metrics: Sharpe, max drawdown, Calmar, tail risk, VaR
  4. Bootstrap CIs on total P&L and max drawdown
  5. Multi-criteria scoring & ranking
  6. Per-filter deep dive for top candidates

Usage:
  python eval_synth_filters.py -e 500
  python eval_synth_filters.py -e 300
"""
import pandas as pd
import numpy as np
import pandas_ta as ta
import argparse
import logging
from numba_utils import calculate_research_metrics_numba

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)

N_BOOTSTRAP = 5000
MULTIPLIER = 10000
COMMISSION = 2.0
SLIPPAGE = 0.02

PATH_PARQUET = "synthetic_options_300ETF.parquet"
PATH_ETF = "./data/510300_1d.parquet"
ETF_TAG = "300"


def select_etf(choice):
    global PATH_PARQUET, PATH_ETF, ETF_TAG
    if choice == "50":
        PATH_PARQUET = "synthetic_options_50ETF.parquet"
        PATH_ETF = "./data/50ETF_1d.parquet"
        ETF_TAG = "50"
    elif choice == "500":
        PATH_PARQUET = "synthetic_options_500ETF.parquet"
        PATH_ETF = "./data/500ETF_1d.parquet"
        ETF_TAG = "500"
    else:
        PATH_PARQUET = "synthetic_options_300ETF.parquet"
        PATH_ETF = "./data/510300_1d.parquet"
        ETF_TAG = "300"


def load_data():
    df = pd.read_parquet(PATH_PARQUET)
    df["Date"] = pd.to_datetime(df["Date"])
    if 'Underlying Price at Date' not in df.columns and 'Underlying_Price' in df.columns:
        df['Underlying Price at Date'] = df['Underlying_Price']

    etf = pd.read_parquet(PATH_ETF)
    etf["date"] = pd.to_datetime(etf["date"])
    etf = etf.set_index("date").sort_index()

    etf['sma20'] = ta.sma(etf['close'], length=20)
    etf['ema20'] = ta.ema(etf['close'], length=20)
    etf['rsi14'] = ta.rsi(etf['close'], length=14)
    macd = ta.macd(etf['close'])
    if macd is not None:
        etf['macd_hist'] = macd.iloc[:, 1]
    bbands = ta.bbands(etf['close'], length=20, std=2)
    if bbands is not None:
        etf['bb_upper'] = bbands.iloc[:, 2]
    etf['roc20'] = ta.roc(etf['close'], length=20)
    etf['atr20'] = ta.atr(etf['high'], etf['low'], etf['close'], length=20)
    adx = ta.adx(etf['high'], etf['low'], etf['close'], length=14)
    if adx is not None:
        etf['adx14'] = adx.iloc[:, 0]
    etf['ema10'] = ta.ema(etf['close'], length=10)
    etf['ema30'] = ta.ema(etf['close'], length=30)
    stoch = ta.stoch(etf['high'], etf['low'], etf['close'], k=14, d=3, smooth_k=3)
    if stoch is not None:
        etf['stoch_k'] = stoch.iloc[:, 0]
    etf['rolling_high_20'] = etf['close'].rolling(20).max()
    etf['rolling_high_252'] = etf['close'].rolling(252).max()

    df = df.merge(etf, left_on="Date", right_index=True, how="left")
    df = df.sort_values(['Option Type', 'Date', 'Strike']).reset_index(drop=True)
    return df


def compute_strategy_pnls(df, f_mask, call_pass_offsets, call_fail_offsets, put_offsets):
    df["Pass Filter"] = f_mask.fillna(True)

    sub_c = df[df["Option Type"] == "C"].copy()
    sub_p = df[df["Option Type"] == "P"].copy()

    call_pnl_map = _compute_leg_pnls(sub_c, call_pass_offsets, call_fail_offsets, "Exp Ret Short", True)
    put_pnl_map = _compute_leg_pnls(sub_p, put_offsets, put_offsets, "Exp Ret Long", False)

    all_dates = sorted(set(call_pnl_map.keys()) | set(put_pnl_map.keys()))
    results = []
    for d in all_dates:
        results.append({
            "date": d,
            "call_pnl": call_pnl_map.get(d, 0.0),
            "put_pnl": put_pnl_map.get(d, 0.0),
            "total_pnl": call_pnl_map.get(d, 0.0) + put_pnl_map.get(d, 0.0),
        })
    return results


def _compute_leg_pnls(sub_df, pass_offsets, fail_offsets, ret_col, is_short):
    sub_df = sub_df.reset_index(drop=True)
    dates = sub_df['Date'].values
    diff = np.where(dates[1:] != dates[:-1])[0] + 1
    boundaries = np.zeros(len(diff) + 2, dtype=np.int64)
    boundaries[0] = 0
    boundaries[1:-1] = diff
    boundaries[-1] = len(sub_df)

    filter_mask = sub_df["Pass Filter"].values
    strikes = sub_df["Strike"].values.astype(np.float64)
    s0s = sub_df["Underlying Price at Date"].values.astype(np.float64)
    prices = sub_df["Price"].values.astype(np.float64)
    ret_vals = sub_df[ret_col].values.astype(np.float64)

    is_call = (ret_col == "Exp Ret Short")

    pnl_map = {}
    n_groups = len(boundaries) - 1
    for g in range(n_groups):
        start = boundaries[g]
        end = boundaries[g + 1]
        s0 = s0s[start]
        is_pass = bool(filter_mask[start])
        offsets = pass_offsets if is_pass else fail_offsets

        if is_call:
            otm_indices = []
            for i in range(start, end):
                if strikes[i] > s0:
                    otm_indices.append(i)
            selected = []
            for off in offsets:
                if off - 1 < len(otm_indices):
                    selected.append(otm_indices[off - 1])
        else:
            itm_indices = []
            for i in range(start, end):
                if strikes[i] >= s0:
                    atm_idx = i
                    break
            else:
                atm_idx = -1
            otm_indices = []
            if atm_idx != -1:
                for i in range(atm_idx - 1, start - 1, -1):
                    otm_indices.append(i)
            selected = []
            for off in offsets:
                if off - 1 < len(otm_indices):
                    selected.append(otm_indices[off - 1])

        date_pnl = 0.0
        for idx in selected:
            ret = ret_vals[idx]
            prc = prices[idx]
            if np.isnan(ret):
                continue
            if is_short:
                exec_p = prc * (1.0 - SLIPPAGE)
                pnl = ret * exec_p * MULTIPLIER - COMMISSION
            else:
                exec_p = prc * (1.0 + SLIPPAGE)
                pnl = ret * exec_p * MULTIPLIER - COMMISSION
            date_pnl += pnl

        pnl_map[dates[start]] = date_pnl

    return pnl_map


def calc_risk_metrics(pnls):
    pnls = np.array(pnls)
    n = len(pnls)
    if n == 0:
        return {}

    cumulative = np.cumsum(pnls)
    running_max = np.maximum.accumulate(cumulative)
    drawdowns = cumulative - running_max
    max_dd = drawdowns.min()

    dd_end_idx = np.argmin(drawdowns)
    dd_start_idx = np.argmax(cumulative[:dd_end_idx + 1]) if dd_end_idx > 0 else 0

    mean_pnl = pnls.mean()
    std_pnl = pnls.std()
    sharpe = mean_pnl / std_pnl if std_pnl > 0 else 0
    calmar = cumulative[-1] / abs(max_dd) if max_dd != 0 else 0

    wins = pnls[pnls > 0]
    losses = pnls[pnls < 0]
    avg_win = wins.mean() if len(wins) > 0 else 0
    avg_loss = losses.mean() if len(losses) > 0 else 0
    win_rate = len(wins) / n
    profit_factor = abs(wins.sum() / losses.sum()) if len(losses) > 0 and losses.sum() != 0 else float('inf')

    sorted_pnls = np.sort(pnls)
    var5 = sorted_pnls[int(n * 0.05)]
    cvar5 = sorted_pnls[:int(n * 0.05)].mean()

    max_loss_streak = 0
    cur_streak = 0
    for p in pnls:
        if p < 0:
            cur_streak += 1
            max_loss_streak = max(max_loss_streak, cur_streak)
        else:
            cur_streak = 0

    return {
        "total": cumulative[-1],
        "mean": mean_pnl,
        "std": std_pnl,
        "sharpe": sharpe,
        "max_dd": max_dd,
        "max_dd_start": dd_start_idx,
        "max_dd_end": dd_end_idx,
        "calmar": calmar,
        "win_rate": win_rate,
        "n_wins": len(wins),
        "n_losses": len(losses),
        "n_total": n,
        "avg_win": avg_win,
        "avg_loss": avg_loss,
        "profit_factor": profit_factor,
        "worst_loss": pnls.min(),
        "best_win": pnls.max(),
        "var5": var5,
        "cvar5": cvar5,
        "max_loss_streak": max_loss_streak,
        "pnl_5pct": np.percentile(pnls, 5),
        "pnl_25pct": np.percentile(pnls, 25),
        "pnl_50pct": np.percentile(pnls, 50),
        "pnl_75pct": np.percentile(pnls, 75),
        "pnl_95pct": np.percentile(pnls, 95),
    }


def bootstrap_risk_metrics(pnls, n_boot=N_BOOTSTRAP):
    pnls = np.array(pnls)
    n = len(pnls)
    boot_totals = np.zeros(n_boot)
    boot_max_dd = np.zeros(n_boot)

    for i in range(n_boot):
        sample = np.random.choice(pnls, size=n, replace=True)
        boot_totals[i] = sample.sum()
        cum = np.cumsum(sample)
        rmax = np.maximum.accumulate(cum)
        boot_max_dd[i] = (cum - rmax).min()

    return {
        "ci_total_lo": np.percentile(boot_totals, 2.5),
        "ci_total_hi": np.percentile(boot_totals, 97.5),
        "ci_dd_lo": np.percentile(boot_max_dd, 2.5),
        "ci_dd_hi": np.percentile(boot_max_dd, 97.5),
        "boot_total_std": boot_totals.std(),
        "boot_dd_std": boot_max_dd.std(),
        "boot_totals": boot_totals,
        "boot_max_dds": boot_max_dd,
    }


def section_per_level_breakdown(df, filters):
    print("\n" + "=" * 110)
    print(f"  SECTION 1: PER-LEVEL OTM BREAKDOWN (Short Calls) — {ETF_TAG}ETF Synthetic")
    print("=" * 110)

    level_names = {0: "ATM", 1: "OTM1", 2: "OTM2", 3: "OTM3", 4: "OTM4", 5: "OTM5"}

    key_filters = {k: filters[k] for k in ["baseline", "f3", "f3_rsi66", "f6", "f3_AND_f6", "f3_rsi66_AND_f6", "f4_AND_f6", "f5"] if k in filters}

    for f_name, f_mask in key_filters.items():
        df["Pass Filter"] = f_mask.fillna(True)
        sub_df = df[df["Option Type"] == "C"].reset_index(drop=True)

        dates = sub_df['Date'].values
        diff = np.where(dates[1:] != dates[:-1])[0] + 1
        boundaries = np.zeros(len(diff) + 2, dtype=np.int64)
        boundaries[0] = 0
        boundaries[1:-1] = diff
        boundaries[-1] = len(sub_df)

        group_filter_mask = sub_df["Pass Filter"].values[boundaries[:-1]]
        strikes = sub_df["Strike"].values.astype(np.float64)
        s0s = sub_df["Underlying Price at Date"].values.astype(np.float64)
        prices = sub_df["Price"].values.astype(np.float64)
        worthless = sub_df["Expire_worthless"].values.astype(np.int8)
        ret_val = sub_df["Exp Ret Short"].values.astype(np.float64)

        metrics_p, metrics_f = calculate_research_metrics_numba(
            strikes, s0s, ret_val, prices, worthless, boundaries, True, group_filter_mask
        )

        n_pass = int(group_filter_mask.sum())
        n_total = len(group_filter_mask)
        pr = n_pass / n_total if n_total > 0 else 0

        print(f"\n  --- {f_name} (Placement: {pr:.1%}, {n_pass}/{n_total} dates) ---")
        print(f"  {'Level':>6} {'N':>6} {'WinRate':>8} {'ExpWorth':>9} {'Avg ER':>10} {'Max Loss':>10}")
        print("  " + "-" * 55)

        for lv in range(6):
            count = int(metrics_p[lv, 0])
            if count == 0:
                continue
            pnl_sum = metrics_p[lv, 1]
            wins = metrics_p[lv, 2]
            exp_w = metrics_p[lv, 3]
            min_pnl = metrics_p[lv, 4]
            wr = wins / count
            ewr = exp_w / count
            avg_er = pnl_sum / count
            ml = min_pnl if min_pnl < 9999998 else float('nan')
            print(f"  {level_names[lv]:>6} {count:>6} {wr:>7.1%} {ewr:>8.1%} {avg_er:>10.1f} {ml:>10.0f}")


def section_strategy_risk_analysis(df, filters):
    print("\n" + "=" * 120)
    print(f"  SECTION 2: FULL STRATEGY RISK ANALYSIS — {ETF_TAG}ETF Synthetic")
    print(f"  Strategy: Pass→OTM2+3 Call, Fail→OTM4 Call, + Put L1 always")
    print("=" * 120)

    all_results = {}

    for f_name, f_mask in filters.items():
        results = compute_strategy_pnls(
            df, f_mask,
            call_pass_offsets=[2, 3], call_fail_offsets=[4],
            put_offsets=[1],
        )
        pnls = np.array([r["total_pnl"] for r in results])
        call_pnls = np.array([r["call_pnl"] for r in results])
        put_pnls = np.array([r["put_pnl"] for r in results])

        rm = calc_risk_metrics(pnls)
        call_rm = calc_risk_metrics(call_pnls)
        put_rm = calc_risk_metrics(put_pnls)

        placement = f_mask.fillna(True)
        sub_c = df[df["Option Type"] == "C"].reset_index(drop=True)
        dates_c = sub_c['Date'].values
        diff_c = np.where(dates_c[1:] != dates_c[:-1])[0] + 1
        bnd = np.zeros(len(diff_c) + 2, dtype=np.int64)
        bnd[0] = 0
        bnd[1:-1] = diff_c
        bnd[-1] = len(sub_c)
        aligned = placement[df["Option Type"] == "C"].reset_index(drop=True)
        gm = aligned.values[bnd[:-1]]
        pr = gm.sum() / len(gm)

        rm["placement_rate"] = pr
        rm["call_total"] = call_rm["total"]
        rm["put_total"] = put_rm["total"]
        rm["call_mean"] = call_rm["mean"]
        rm["put_mean"] = put_rm["mean"]

        all_results[f_name] = {"pnls": pnls, "rm": rm, "results": results}

    print(f"\n  {'Filter':<25} {'Place%':>7} {'Total':>9} {'Mean':>7} {'Std':>7} "
          f"{'Sharpe':>7} {'MaxDD':>9} {'Calmar':>7} {'WinRate':>7} "
          f"{'Worst':>9} {'VaR5%':>8} {'PF':>5}")
    print("  " + "-" * 120)

    for f_name, data in all_results.items():
        rm = data["rm"]
        print(f"  {f_name:<25} {rm['placement_rate']:>6.1%} {rm['total']:>9.0f} {rm['mean']:>7.1f} "
              f"{rm['std']:>7.1f} {rm['sharpe']:>7.3f} {rm['max_dd']:>9.0f} {rm['calmar']:>7.2f} "
              f"{rm['win_rate']:>6.1%} {rm['worst_loss']:>9.0f} {rm['var5']:>8.0f} "
              f"{rm['profit_factor']:>5.2f}")

    print(f"\n  --- CALL vs PUT BREAKDOWN ---")
    print(f"  {'Filter':<25} {'Call Total':>11} {'Call Mean':>10} {'Put Total':>10} {'Put Mean':>10} {'Put Drag%':>10}")
    print("  " + "-" * 80)
    for f_name, data in all_results.items():
        rm = data["rm"]
        put_drag_pct = abs(rm["put_total"] / rm["call_total"] * 100) if rm["call_total"] != 0 else 0
        print(f"  {f_name:<25} {rm['call_total']:>11.0f} {rm['call_mean']:>10.1f} "
              f"{rm['put_total']:>10.0f} {rm['put_mean']:>10.1f} {put_drag_pct:>9.1f}%")

    return all_results


def section_bootstrap_risk(all_results):
    print("\n" + "=" * 120)
    print(f"  SECTION 3: BOOTSTRAP CONFIDENCE INTERVALS — {ETF_TAG}ETF Synthetic ({N_BOOTSTRAP} iterations)")
    print("=" * 120)

    print(f"\n  {'Filter':<25} {'Total':>9} {'95% CI Lo':>10} {'95% CI Hi':>10} {'Boot Std':>10} "
          f"{'MaxDD':>9} {'DD CI Lo':>10} {'DD CI Hi':>10}")
    print("  " + "-" * 110)

    for f_name, data in all_results.items():
        pnls = data["pnls"]
        rm = data["rm"]
        boot = bootstrap_risk_metrics(pnls)
        data["boot"] = boot

        print(f"  {f_name:<25} {rm['total']:>9.0f} {boot['ci_total_lo']:>10.0f} "
              f"{boot['ci_total_hi']:>10.0f} {boot['boot_total_std']:>10.0f} "
              f"{rm['max_dd']:>9.0f} {boot['ci_dd_lo']:>10.0f} {boot['ci_dd_hi']:>10.0f}")


def section_statistical_significance(all_results):
    print("\n" + "=" * 120)
    print(f"  SECTION 4: STATISTICAL SIGNIFICANCE vs BASELINE — {ETF_TAG}ETF Synthetic")
    print("=" * 120)

    if "baseline" not in all_results:
        print("  No baseline found, skipping.")
        return

    base_pnls = all_results["baseline"]["pnls"]
    base_rm = all_results["baseline"]["rm"]

    print(f"\n  Baseline: Total={base_rm['total']:.0f}, MaxDD={base_rm['max_dd']:.0f}, "
          f"Sharpe={base_rm['sharpe']:.3f}, Calmar={base_rm['calmar']:.2f}")

    print(f"\n  {'Filter':<25} {'Δ Total':>10} {'P(total>)':>10} {'Δ MaxDD':>10} {'P(DD>)':>10} "
          f"{'Δ Sharpe':>10} {'Combined':>10}")
    print("  " + "-" * 100)

    rankings = []

    for f_name, data in all_results.items():
        if f_name == "baseline":
            continue
        f_pnls = data["pnls"]
        rm = data["rm"]

        min_len = min(len(base_pnls), len(f_pnls))
        if min_len == 0:
            continue

        base_s = base_pnls[:min_len]
        f_s = f_pnls[:min_len]
        diff = f_s - base_s
        delta_total = diff.sum()

        boot_diffs = np.zeros(N_BOOTSTRAP)
        boot_dd_diff = np.zeros(N_BOOTSTRAP)
        for i in range(N_BOOTSTRAP):
            idx = np.random.choice(min_len, size=min_len, replace=True)
            sample_diff = diff[idx]
            boot_diffs[i] = sample_diff.sum()
            f_cum = np.cumsum(f_s[idx])
            b_cum = np.cumsum(base_s[idx])
            f_dd = (f_cum - np.maximum.accumulate(f_cum)).min()
            b_dd = (b_cum - np.maximum.accumulate(b_cum)).min()
            boot_dd_diff[i] = f_dd - b_dd

        p_total_better = (boot_diffs > 0).mean()
        p_dd_better = (boot_dd_diff > 0).mean()
        delta_sharpe = rm["sharpe"] - base_rm["sharpe"]
        delta_dd = rm["max_dd"] - base_rm["max_dd"]

        n_better = sum(1 for p in [p_total_better, p_dd_better] if p > 0.5)
        combined = "BETTER" if n_better == 2 else ("mixed" if n_better == 1 else "WORSE")

        if p_total_better > 0.5 and p_dd_better > 0.5:
            combined = f"BETTER ({p_total_better:.0%}/{p_dd_better:.0%})"
        elif p_total_better > 0.5 or p_dd_better > 0.5:
            combined = f"mixed ({p_total_better:.0%}/{p_dd_better:.0%})"
        else:
            combined = f"WORSE ({p_total_better:.0%}/{p_dd_better:.0%})"

        rankings.append({
            "name": f_name,
            "delta_total": delta_total,
            "p_total": p_total_better,
            "delta_dd": delta_dd,
            "p_dd": p_dd_better,
            "delta_sharpe": delta_sharpe,
            "combined": combined,
        })

        print(f"  {f_name:<25} {delta_total:>+10.0f} {p_total_better:>9.1%} "
              f"{delta_dd:>+10.0f} {p_dd_better:>9.1%} {delta_sharpe:>+10.3f} {combined}")

    better = [r for r in rankings if r["p_total"] > 0.5 and r["p_dd"] > 0.5]
    better.sort(key=lambda x: (x["p_total"] + x["p_dd"]) / 2, reverse=True)

    if better:
        print(f"\n  Filters that beat baseline on BOTH total P&L AND max drawdown:")
        for r in better:
            print(f"    {r['name']}: P(total>)={r['p_total']:.1%}, P(DD>)={r['p_dd']:.1%}, "
                  f"ΔSharpe={r['delta_sharpe']:+.3f}")
    else:
        print(f"\n  No filters beat baseline on both metrics simultaneously.")

    return rankings


def section_multi_criteria_ranking(all_results):
    print("\n" + "=" * 120)
    print(f"  SECTION 5: MULTI-CRITERIA SCORING & RANKING — {ETF_TAG}ETF Synthetic")
    print("=" * 120)

    all_rms = {fn: data["rm"] for fn, data in all_results.items()}

    totals = [rm["total"] for rm in all_rms.values()]
    sharpes = [rm["sharpe"] for rm in all_rms.values()]
    max_dds = [rm["max_dd"] for rm in all_rms.values()]
    calmars = [rm["calmar"] for rm in all_rms.values()]
    win_rates = [rm["win_rate"] for rm in all_rms.values()]
    worst_losses = [rm["worst_loss"] for rm in all_rms.values()]
    pfs = [min(rm["profit_factor"], 10) for rm in all_rms.values()]

    def rank_normalize(values, higher_better=True):
        arr = np.array(values)
        if higher_better:
            return (arr - arr.min()) / (arr.max() - arr.min() + 1e-10)
        else:
            return (arr.max() - arr) / (arr.max() - arr.min() + 1e-10)

    n_total_rank = rank_normalize(totals, True)
    sharpe_rank = rank_normalize(sharpes, True)
    dd_rank = rank_normalize(max_dds, False)
    calmar_rank = rank_normalize(calmars, True)
    wr_rank = rank_normalize(win_rates, True)
    worst_rank = rank_normalize(worst_losses, False)
    pf_rank = rank_normalize(pfs, True)

    weights = {
        "total": 0.20,
        "sharpe": 0.20,
        "max_dd": 0.20,
        "calmar": 0.15,
        "win_rate": 0.10,
        "worst_loss": 0.10,
        "profit_factor": 0.05,
    }

    scored = []
    for i, (f_name, rm) in enumerate(all_rms.items()):
        composite = (
            weights["total"] * n_total_rank[i] +
            weights["sharpe"] * sharpe_rank[i] +
            weights["max_dd"] * dd_rank[i] +
            weights["calmar"] * calmar_rank[i] +
            weights["win_rate"] * wr_rank[i] +
            weights["worst_loss"] * worst_rank[i] +
            weights["profit_factor"] * pf_rank[i]
        )
        scored.append({
            "filter": f_name,
            "composite": composite,
            "total": rm["total"],
            "sharpe": rm["sharpe"],
            "max_dd": rm["max_dd"],
            "calmar": rm["calmar"],
            "win_rate": rm["win_rate"],
            "worst_loss": rm["worst_loss"],
            "profit_factor": rm["profit_factor"],
        })

    scored.sort(key=lambda x: x["composite"], reverse=True)

    print(f"\n  Weights: Total={weights['total']:.0%}, Sharpe={weights['sharpe']:.0%}, "
          f"MaxDD={weights['max_dd']:.0%}, Calmar={weights['calmar']:.0%}, "
          f"WinRate={weights['win_rate']:.0%}, WorstLoss={weights['worst_loss']:.0%}, "
          f"PF={weights['profit_factor']:.0%}")
    print(f"\n  {'Rank':>4} {'Filter':<25} {'Score':>6} {'Total':>9} {'Sharpe':>7} "
          f"{'MaxDD':>9} {'Calmar':>7} {'WinRate':>7} {'Worst':>9} {'PF':>5}")
    print("  " + "-" * 100)

    for i, s in enumerate(scored):
        marker = " ★" if s["filter"] != "baseline" and s["composite"] > scored[-1]["composite"] + 0.01 else ""
        print(f"  {i + 1:>4} {s['filter']:<25} {s['composite']:>6.3f} {s['total']:>9.0f} "
              f"{s['sharpe']:>7.3f} {s['max_dd']:>9.0f} {s['calmar']:>7.2f} "
              f"{s['win_rate']:>6.1%} {s['worst_loss']:>9.0f} {s['profit_factor']:>5.2f}{marker}")

    baseline_score = next(s for s in scored if s["filter"] == "baseline")
    print(f"\n  Baseline composite score: {baseline_score['composite']:.3f} (rank {next(i+1 for i,s in enumerate(scored) if s['filter']=='baseline')})")

    top5 = [s for s in scored if s["filter"] != "baseline"][:5]
    print(f"\n  Top 5 non-baseline filters:")
    for i, s in enumerate(top5):
        vs = s["composite"] - baseline_score["composite"]
        print(f"    {i + 1}. {s['filter']}: Score={s['composite']:.3f} "
              f"(vs baseline {'+'if vs>0 else ''}{vs:.3f}), "
              f"Total={s['total']:.0f}, MaxDD={s['max_dd']:.0f}, Sharpe={s['sharpe']:.3f}")

    return scored


def section_deep_dive(df, all_results, scored, top_n=3):
    print("\n" + "=" * 120)
    print(f"  SECTION 6: DEEP DIVE — TOP {top_n} FILTERS vs BASELINE")
    print("=" * 120)

    candidates = [s for s in scored if s["filter"] != "baseline"][:top_n]
    candidates.insert(0, {"filter": "baseline"})

    for cand in candidates:
        f_name = cand["filter"]
        data = all_results[f_name]
        rm = data["rm"]
        pnls = data["pnls"]

        print(f"\n  --- {f_name} ---")
        print(f"  N={rm['n_total']}, Total={rm['total']:.0f}, Mean={rm['mean']:.1f}, Std={rm['std']:.1f}")
        print(f"  Sharpe={rm['sharpe']:.3f}, MaxDD={rm['max_dd']:.0f}, Calmar={rm['calmar']:.2f}")
        print(f"  WinRate={rm['win_rate']:.1%} ({rm['n_wins']}/{rm['n_total']}), "
              f"AvgWin={rm['avg_win']:.0f}, AvgLoss={rm['avg_loss']:.0f}, PF={rm['profit_factor']:.2f}")
        print(f"  Worst={rm['worst_loss']:.0f}, Best={rm['best_win']:.0f}, "
              f"VaR5%={rm['var5']:.0f}, CVaR5%={rm['cvar5']:.0f}")
        print(f"  MaxLossStreak={rm['max_loss_streak']}, "
              f"PnL Percentiles: 5%={rm['pnl_5pct']:.0f}, 25%={rm['pnl_25pct']:.0f}, "
              f"50%={rm['pnl_50pct']:.0f}, 75%={rm['pnl_75pct']:.0f}, 95%={rm['pnl_95pct']:.0f}")

        if "boot" in data:
            boot = data["boot"]
            print(f"  Bootstrap: Total 95% CI=[{boot['ci_total_lo']:.0f}, {boot['ci_total_hi']:.0f}], "
                  f"MaxDD 95% CI=[{boot['ci_dd_lo']:.0f}, {boot['ci_dd_hi']:.0f}]")

        losses = pnls[pnls < 0]
        big_losses = pnls[pnls < -2000]
        print(f"  Loss distribution: {len(losses)} losses, {len(big_losses)} big (>-2000)")
        if len(big_losses) > 0:
            print(f"    Big loss avg: {big_losses.mean():.0f}, max: {big_losses.min():.0f}")

        cum = np.cumsum(pnls)
        rmax = np.maximum.accumulate(cum)
        dd = cum - rmax
        in_dd = dd < 0
        if in_dd.any():
            dd_segments = []
            start = None
            for i in range(len(in_dd)):
                if in_dd[i] and start is None:
                    start = i
                elif not in_dd[i] and start is not None:
                    dd_segments.append((start, i - 1, dd[start:i].min()))
                    start = None
            if start is not None:
                dd_segments.append((start, len(in_dd) - 1, dd[start:].min()))
            dd_segments.sort(key=lambda x: x[2])
            print(f"  Top 3 drawdown periods:")
            for s, e, d in dd_segments[:3]:
                print(f"    [{s}→{e}] depth={d:.0f}, duration={e - s + 1} periods")


def section_put_strategy_comparison(df, all_results):
    print("\n" + "=" * 120)
    print(f"  SECTION 7: PUT STRATEGY COMPARISON — {ETF_TAG}ETF Synthetic")
    print("=" * 120)

    f_mask = filters["baseline"]

    put_configs = [
        ("No Put", []),
        ("Put L1", [1]),
        ("Put L2", [2]),
    ]

    base_rm = all_results["baseline"]["rm"]

    for put_name, put_offsets in put_configs:
        results = compute_strategy_pnls(
            df, f_mask,
            call_pass_offsets=[2, 3], call_fail_offsets=[4],
            put_offsets=put_offsets,
        )
        pnls = np.array([r["total_pnl"] for r in results])
        rm = calc_risk_metrics(pnls)
        delta_total = rm["total"] - base_rm["total"] if put_offsets else rm["total"]
        delta_dd = rm["max_dd"] - base_rm["max_dd"] if put_offsets else rm["max_dd"]

        print(f"\n  {put_name}: Total={rm['total']:.0f}, Mean={rm['mean']:.1f}, "
              f"Sharpe={rm['sharpe']:.3f}, MaxDD={rm['max_dd']:.0f}, "
              f"Calmar={rm['calmar']:.2f}, WinRate={rm['win_rate']:.1%}, Worst={rm['worst_loss']:.0f}")
        if put_offsets:
            print(f"    vs No Put: ΔTotal={delta_total:+.0f}, ΔMaxDD={delta_dd:+.0f}")


def section_final_conclusions(all_results, scored):
    print("\n" + "=" * 120)
    print(f"  SECTION 8: CONCLUSIONS — {ETF_TAG}ETF Synthetic ({all_results['baseline']['rm']['n_total']} dates)")
    print("=" * 120)

    baseline_rm = all_results["baseline"]["rm"]
    top_non_baseline = [s for s in scored if s["filter"] != "baseline"][0]

    print(f"\n  Baseline: Total={baseline_rm['total']:.0f}, MaxDD={baseline_rm['max_dd']:.0f}, "
          f"Sharpe={baseline_rm['sharpe']:.3f}")

    print(f"\n  Best filter: {top_non_baseline['filter']}")
    print(f"    Total={top_non_baseline['total']:.0f} (Δ{top_non_baseline['total'] - baseline_rm['total']:+.0f}), "
          f"MaxDD={top_non_baseline['max_dd']:.0f} (Δ{top_non_baseline['max_dd'] - baseline_rm['max_dd']:+.0f}), "
          f"Sharpe={top_non_baseline['sharpe']:.3f} (Δ{top_non_baseline['sharpe'] - baseline_rm['sharpe']:+.3f})")

    better_filters = [s for s in scored
                      if s["filter"] != "baseline"
                      and all_results[s["filter"]]["rm"]["total"] > baseline_rm["total"]
                      and all_results[s["filter"]]["rm"]["max_dd"] > baseline_rm["max_dd"]]

    if better_filters:
        print(f"\n  Filters beating baseline on BOTH total and drawdown ({len(better_filters)}):")
        for s in better_filters[:5]:
            rm = all_results[s["filter"]]["rm"]
            print(f"    {s['filter']}: Total={rm['total']:.0f}, MaxDD={rm['max_dd']:.0f}, Sharpe={rm['sharpe']:.3f}")
    else:
        worse_dd = [s for s in scored if s["filter"] != "baseline" and s["max_dd"] <= baseline_rm["max_dd"]]
        print(f"\n  No filter beats baseline on both total and drawdown.")
        if worse_dd:
            print(f"  Filters with shallower drawdown (but possibly lower total):")
            for s in worse_dd[:3]:
                rm = all_results[s["filter"]]["rm"]
                print(f"    {s['filter']}: Total={rm['total']:.0f} (Δ{rm['total']-baseline_rm['total']:+.0f}), "
                      f"MaxDD={rm['max_dd']:.0f} (Δ{rm['max_dd']-baseline_rm['max_dd']:+.0f})")

    print()


def main():
    global N_BOOTSTRAP, filters

    parser = argparse.ArgumentParser(description="Enhanced Synthetic Filter Evaluation")
    parser.add_argument("-e", "--etf", type=str, choices=["50", "300", "500"], default="500")
    parser.add_argument("-n", "--bootstrap", type=int, default=N_BOOTSTRAP)
    args = parser.parse_args()
    select_etf(args.etf)
    N_BOOTSTRAP = args.bootstrap

    np.random.seed(42)

    print("=" * 120)
    print(f"  ENHANCED SYNTHETIC FILTER EVALUATION — {ETF_TAG}ETF")
    print(f"  Strategy: Pass→OTM2+3 Call, Fail→OTM4 Call, + Put L1 always")
    print(f"  Bootstrap iterations: {N_BOOTSTRAP}")
    print("=" * 120)

    df = load_data()
    n_dates = df[df["Option Type"] == "C"]["Date"].nunique()
    print(f"  Synthetic samples: {n_dates} dates, {len(df)} rows")

    f1 = df['close'] < df['sma20']
    f2 = df['close'] < df['ema20']
    f3 = df['rsi14'] < 70
    f3_rsi66 = df['rsi14'] < 66
    f3_rsi60 = df['rsi14'] < 60
    f4 = df['rsi14'] > 30
    f5 = df['macd_hist'] < 0
    f6 = df['close'] < df['bb_upper']
    f9 = df['roc20'] < 5.0
    f10 = df['close'] < (df['sma20'] + df['atr20'])
    f11 = df['adx14'] < 25
    f12 = df['ema10'] < df['ema30']
    f15 = df['stoch_k'] < 80
    f16 = df['close'] < (0.98 * df['rolling_high_20'])
    f17 = df['close'] < (0.95 * df['rolling_high_252'])
    f20 = df['close'] < (df['ema20'] + 1.0 * df['atr20'])

    df['vol20'] = df['close'].pct_change().rolling(20).std() * np.sqrt(252)
    df['roc10'] = ta.roc(df['close'], length=10)
    df['roc5'] = ta.roc(df['close'], length=5)
    df['sma50'] = ta.sma(df['close'], length=50)
    bbands_lower = ta.bbands(df['close'], length=20, std=2)
    if bbands_lower is not None:
        df['bb_lower'] = bbands_lower.iloc[:, 0]
    df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / df['sma20']
    df['atr10'] = ta.atr(df['high'], df['low'], df['close'], length=10)
    cci = ta.cci(df['high'], df['low'], df['close'], length=20)
    if cci is not None:
        df['cci20'] = cci
    df['vol_ratio'] = df['atr20'] / df['atr10']
    df['tr'] = ta.true_range(df['high'], df['low'], df['close'])
    df['atr5'] = df['tr'].rolling(5).mean()
    df['atr_ratio_5_20'] = df['atr5'] / df['atr20']

    f_vol_low = df['vol20'] < df['vol20'].rolling(252).quantile(0.5)
    f_roc10 = df['roc10'] < 5.0
    f_roc5 = df['roc5'] < 3.0
    f_sma50 = df['close'] > df['sma50']
    f_bw_expand = df['bb_width'] < df['bb_width'].rolling(20).mean()
    f_cci = df['cci20'] < 100
    f_vol_ratio = df['atr_ratio_5_20'] < 1.2
    f_atr_low = df['atr20'] < df['atr20'].rolling(60).quantile(0.7)

    filters = {
        "baseline": pd.Series(True, index=df.index),

        # --- Individual filters ---
        "f1_SMA20": f1,
        "f2_EMA20": f2,
        "f3_RSI70": f3,
        "f3_rsi66": f3_rsi66,
        "f3_rsi60": f3_rsi60,
        "f4_RSI30": f4,
        "f5_MACD": f5,
        "f6_BBU": f6,
        "f9_ROC20": f9,
        "f10_ATRBreakout": f10,
        "f11_ADX": f11,
        "f12_EMAcross": f12,
        "f15_Stoch": f15,
        "f16_RollHi20": f16,
        "f17_RollHi252": f17,
        "f20_Keltner": f20,
        "f_vol_low": f_vol_low.fillna(True),
        "f_roc10": f_roc10.fillna(True),
        "f_roc5": f_roc5.fillna(True),
        "f_sma50": f_sma50.fillna(True),
        "f_bw_expand": f_bw_expand.fillna(True),
        "f_cci": f_cci.fillna(True),
        "f_vol_ratio": f_vol_ratio.fillna(True),
        "f_atr_low": f_atr_low.fillna(True),

        # --- 2-filter combos from evaluate_combinations.py ---
        "c1_f1_AND_f3": f1 & f3,
        "c2_f1_OR_f3": f1 | f3,
        "c3_f11_AND_f12": f11 & f12,
        "c4_f11_OR_f12": f11 | f12,
        "c5_f16_AND_f15": f16 & f15,
        "c6_f17_AND_f12": f17 & f12,
        "c7_f20_AND_f4": f20 & f4,
        "c8_f9_AND_f10": f9 & f10,
        "c9_f12_AND_f16": f12 & f16,
        "c10_f11_AND_f10": f11 & f10,
        "c11_f6_AND_f9": f6 & f9,
        "c12_f5_AND_f16": f5 & f16,
        "c13_f12_AND_f20": f12 & f20,
        "c14_f11_AND_f20": f11 & f20,
        "c15_f16_AND_f20": f16 & f20,
        "c16_f3_AND_f10": f3 & f10,

        # --- 3-filter combos from evaluate_combinations.py ---
        "c17_f11_f12_f16": f11 & f12 & f16,
        "c18_f11_OR_f12_f16": f11 | (f12 & f16),
        "c19_f20_f4_f3": f20 & f4 & f3,
        "c20_f12_f16_f20": f12 & f16 & f20,
        "c21_f1f11_AND_f3": (f1 | f11) & f3,
        "c22_f12_OR_f16_f20": f12 | (f16 & f20),
        "c23_f1f2_AND_f16": (f1 | f2) & f16,

        # --- BBU + RSI combos (winners from previous research) ---
        "f3_AND_f6": f3 & f6,
        "f3_rsi66_AND_f6": f3_rsi66 & f6,
        "f4_AND_f6": f4 & f6,
        "f3_AND_f4_AND_f6": f3 & f4 & f6,
        "f9_AND_f6": f9 & f6,
        "f3_AND_f20_AND_f6": f3 & f20 & f6,
        "f12_OR_f3_AND_f6": f12 | (f3 & f6),

        # --- New combos with novel filters ---
        "f6_AND_f_cci": f6 & f_cci.fillna(True),
        "f3_AND_f6_AND_f_cci": f3 & f6 & f_cci.fillna(True),
        "f6_AND_f_vol_ratio": f6 & f_vol_ratio.fillna(True),
        "f6_AND_f_atr_low": f6 & f_atr_low.fillna(True),
        "f3_AND_f6_AND_f_roc5": f3 & f6 & f_roc5.fillna(True),
        "f4_AND_f6_AND_f_cci": f4 & f6 & f_cci.fillna(True),
        "f6_AND_f_bw_expand": f6 & f_bw_expand.fillna(True),
        "f3_AND_f6_AND_f_bw": f3 & f6 & f_bw_expand.fillna(True),
    }

    section_per_level_breakdown(df, filters)
    all_results = section_strategy_risk_analysis(df, filters)
    section_bootstrap_risk(all_results)
    rankings = section_statistical_significance(all_results)
    scored = section_multi_criteria_ranking(all_results)
    section_deep_dive(df, all_results, scored, top_n=3)
    section_put_strategy_comparison(df, all_results)
    section_final_conclusions(all_results, scored)


if __name__ == "__main__":
    main()
