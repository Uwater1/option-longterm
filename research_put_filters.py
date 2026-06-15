"""
Synthetic Data Filter Evaluation for Long Put (Selective Hedge)
================================================================
Evaluates which filters make buying protective puts profitable.
"Pass filter" = buy put (hedge); "Fail filter" = skip (P&L = 0).
Baseline = always buy (expected net-negative = hedge drag).

Usage:
  python research_put_filters.py -e 300
  python research_put_filters.py -e 500
  python research_put_filters.py -e 50
  python research_put_filters.py -e 300 --level 3   # bootstrap at OTM3
"""
import pandas as pd
import numpy as np
import pandas_ta as ta
import argparse
import os
import sys

sys.path.insert(0, os.path.abspath("."))

N_BOOTSTRAP = 5000
MULTIPLIER = 10000
COMMISSION = 2.0
SLIPPAGE = 0.02

PATH_PARQUET = "synthetic_options_300ETF.parquet"
PATH_ETF = "./data/510300_1d.parquet"
ETF_TAG = "300"

OTM_LEVELS = [0, 1, 2, 3]  # 0=ATM-ish, 1=closest OTM, etc.


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

    # Technical indicators
    etf['sma20'] = ta.sma(etf['close'], length=20)
    etf['ema20'] = ta.ema(etf['close'], length=20)
    etf['rsi14'] = ta.rsi(etf['close'], length=14)
    etf['sma50'] = ta.sma(etf['close'], length=50)
    etf['atr20'] = ta.atr(etf['high'], etf['low'], etf['close'], length=20)
    macd = ta.macd(etf['close'])
    if macd is not None:
        etf['macd_hist'] = macd.iloc[:, 1]
    bbands = ta.bbands(etf['close'], length=20, std=2)
    if bbands is not None:
        etf['bb_upper'] = bbands.iloc[:, 2]
        etf['bb_lower'] = bbands.iloc[:, 0]
    etf['roc10'] = ta.roc(etf['close'], length=10)
    etf['roc20'] = ta.roc(etf['close'], length=20)
    etf['vol20'] = etf['close'].pct_change().rolling(20).std() * np.sqrt(252)
    etf['vol20_median'] = etf['vol20'].rolling(252).median()
    etf['roc5'] = ta.roc(etf['close'], length=5)

    df = df.merge(etf, left_on="Date", right_index=True, how="left")
    df = df.sort_values(['Option Type', 'Date', 'Strike']).reset_index(drop=True)
    return df


def compute_put_pnls(df, f_mask, otm_level):
    """
    Compute per-date P&L for long put with selective filter.
    Pass = buy put at given OTM level; Fail = skip (P&L = 0).
    """
    sub_p = df[df["Option Type"] == "P"].reset_index(drop=True)
    if sub_p.empty:
        return []

    dates = sub_p['Date'].values
    diff = np.where(dates[1:] != dates[:-1])[0] + 1
    boundaries = np.zeros(len(diff) + 2, dtype=np.int64)
    boundaries[0] = 0
    boundaries[1:-1] = diff
    boundaries[-1] = len(sub_p)

    filter_mask = f_mask.fillna(False).values
    # Align filter mask to put dates
    put_dates_all = sub_p['Date'].values
    all_dates_sorted = sorted(sub_p['Date'].unique())
    date_to_filter = {}
    for d in all_dates_sorted:
        mask_idx = np.where(put_dates_all == d)[0]
        if len(mask_idx) > 0:
            date_to_filter[d] = bool(filter_mask[mask_idx[0]])

    strikes = sub_p["Strike"].values.astype(np.float64)
    s0s = sub_p["Underlying Price at Date"].values.astype(np.float64)
    prices = sub_p["Price"].values.astype(np.float64)
    ret_vals = sub_p["Exp Ret Long"].values.astype(np.float64)

    pnl_map = {}
    n_groups = len(boundaries) - 1
    for g in range(n_groups):
        start = boundaries[g]
        end = boundaries[g + 1]
        d = dates[start]
        s0 = s0s[start]
        is_pass = date_to_filter.get(d, False)

        if not is_pass:
            pnl_map[d] = 0.0
            continue

        # Find OTM puts: strike < s0, sorted descending
        otm_indices = []
        for i in range(start, end):
            if strikes[i] < s0:
                otm_indices.append(i)
        # Sort by strike descending (closest to spot first = OTM1)
        otm_indices.sort(key=lambda i: strikes[i], reverse=True)

        date_pnl = 0.0
        if otm_level < len(otm_indices):
            idx = otm_indices[otm_level]
            ret = ret_vals[idx]
            prc = prices[idx]
            if not np.isnan(ret):
                exec_p = prc * (1.0 + SLIPPAGE)  # buy at ask
                date_pnl = ret * exec_p * MULTIPLIER - COMMISSION
        pnl_map[d] = date_pnl

    all_dates = sorted(sub_p['Date'].unique())
    return [pnl_map.get(d, 0.0) for d in all_dates]


def calc_risk_metrics(pnls):
    pnls = np.array(pnls, dtype=float)
    n = len(pnls)
    if n == 0:
        return {}
    cumulative = np.cumsum(pnls)
    running_max = np.maximum.accumulate(cumulative)
    drawdowns = cumulative - running_max
    max_dd = drawdowns.min()
    mean_pnl = pnls.mean()
    std_pnl = pnls.std()
    sharpe = mean_pnl / std_pnl if std_pnl > 0 else 0
    calmar = cumulative[-1] / abs(max_dd) if max_dd != 0 else 0
    wins = pnls[pnls > 0]
    losses = pnls[pnls < 0]
    win_rate = len(wins) / n
    profit_factor = abs(wins.sum() / losses.sum()) if len(losses) > 0 and losses.sum() != 0 else float('inf')
    sorted_pnls = np.sort(pnls)
    var5 = sorted_pnls[int(n * 0.05)]
    return {
        "total": cumulative[-1], "mean": mean_pnl, "std": std_pnl,
        "sharpe": sharpe, "max_dd": max_dd, "calmar": calmar,
        "win_rate": win_rate, "n_wins": len(wins), "n_total": n,
        "profit_factor": min(profit_factor, 99),
        "worst_loss": pnls.min(), "best_win": pnls.max(), "var5": var5,
    }


def bootstrap_risk_metrics(pnls, n_boot=N_BOOTSTRAP):
    pnls = np.array(pnls, dtype=float)
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
    }


def section_per_level_breakdown(df, filters):
    """Per-OTM-level P&L breakdown for key filters."""
    print("\n" + "=" * 110)
    print(f"  SECTION 1: PER-LEVEL PUT P&L BREAKDOWN — {ETF_TAG}ETF Synthetic")
    print(f"  'Pass' = Buy Put at level; 'Fail' = Skip (P&L=0)")
    print("=" * 110)

    key_filters = {k: v for k, v in filters.items()
                   if k in ["baseline", "f_rsi50", "f_rsi45", "f_bbl", "f_vol_high",
                            "f_roc10_neg", "f_sma50_below", "f_macd_neg",
                            "f_rsi50_AND_bbl", "f_rsi50_AND_vol", "f_rsi50_AND_sma50"]}

    for f_name, f_mask in key_filters.items():
        print(f"\n  --- {f_name} ---")
        print(f"  {'Level':>6} {'N_buy':>6} {'Total':>10} {'Mean':>8} {'WinRate':>8} "
              f"{'MaxLoss':>10} {'Sharpe':>7} {'Place%':>7}")
        print("  " + "-" * 70)

        for lv in OTM_LEVELS:
            pnls = compute_put_pnls(df, f_mask, lv)
            buy_pnls = [p for p in pnls if p != 0.0]
            n_buy = len(buy_pnls)
            n_total = len(pnls)
            placement = n_buy / n_total if n_total > 0 else 0

            if n_buy == 0:
                continue
            rm = calc_risk_metrics(pnls)
            buy_mean = np.mean(buy_pnls) if buy_pnls else 0
            buy_wins = sum(1 for p in buy_pnls if p > 0)
            buy_wr = buy_wins / n_buy if n_buy > 0 else 0
            buy_worst = min(buy_pnls) if buy_pnls else 0
            buy_sharpe = rm["sharpe"]

            print(f"  OTM{lv:<3} {n_buy:>6} {rm['total']:>10.0f} {buy_mean:>8.1f} "
                  f"{buy_wr:>7.1%} {buy_worst:>10.0f} {buy_sharpe:>7.3f} {placement:>6.1%}")


def section_filter_ranking(df, filters):
    """Rank all filters across all OTM levels."""
    print("\n" + "=" * 110)
    print(f"  SECTION 2: FILTER RANKING (ALL OTM LEVELS) — {ETF_TAG}ETF Synthetic")
    print("=" * 110)

    all_results = {}

    for lv in OTM_LEVELS:
        print(f"\n  ── OTM Level {lv} ──")
        print(f"  {'Filter':<30} {'Place%':>7} {'Total':>9} {'Mean':>7} {'Sharpe':>7} "
              f"{'MaxDD':>9} {'WinRate':>7} {'Worst':>9} {'PF':>5}")
        print("  " + "-" * 100)

        level_results = {}
        for f_name, f_mask in filters.items():
            pnls = compute_put_pnls(df, f_mask, lv)
            rm = calc_risk_metrics(pnls)
            n_buy = sum(1 for p in pnls if p != 0.0)
            placement = n_buy / len(pnls) if pnls else 0

            level_results[f_name] = {"pnls": pnls, "rm": rm, "placement": placement}

            print(f"  {f_name:<30} {placement:>6.1%} {rm['total']:>9.0f} {rm['mean']:>7.1f} "
                  f"{rm['sharpe']:>7.3f} {rm['max_dd']:>9.0f} {rm['win_rate']:>6.1%} "
                  f"{rm['worst_loss']:>9.0f} {rm['profit_factor']:>5.2f}")

        all_results[f"OTM{lv}"] = level_results

    return all_results


def section_bootstrap(df, filters, best_level=1):
    """Bootstrap CI for top filters at the best OTM level."""
    print("\n" + "=" * 110)
    print(f"  SECTION 3: BOOTSTRAP CI (OTM Level {best_level}) — {ETF_TAG}ETF ({N_BOOTSTRAP} iter)")
    print("=" * 110)

    print(f"\n  {'Filter':<30} {'Total':>9} {'CI Lo':>9} {'CI Hi':>9} {'MaxDD':>9} "
          f"{'DD CI Lo':>9} {'DD CI Hi':>9}")
    print("  " + "-" * 90)

    results = {}
    for f_name, f_mask in filters.items():
        pnls = compute_put_pnls(df, f_mask, best_level)
        rm = calc_risk_metrics(pnls)
        boot = bootstrap_risk_metrics(pnls)

        results[f_name] = {"pnls": pnls, "rm": rm, "boot": boot}

        print(f"  {f_name:<30} {rm['total']:>9.0f} {boot['ci_total_lo']:>9.0f} "
              f"{boot['ci_total_hi']:>9.0f} {rm['max_dd']:>9.0f} "
              f"{boot['ci_dd_lo']:>9.0f} {boot['ci_dd_hi']:>9.0f}")

    return results


def section_significance(boot_results):
    """Statistical significance vs baseline."""
    print("\n" + "=" * 110)
    print(f"  SECTION 4: SIGNIFICANCE vs BASELINE — {ETF_TAG}ETF Synthetic")
    print("=" * 110)

    if "baseline" not in boot_results:
        print("  No baseline, skipping.")
        return

    base_pnls = np.array(boot_results["baseline"]["pnls"])
    base_rm = boot_results["baseline"]["rm"]

    print(f"\n  Baseline: Total={base_rm['total']:.0f}, MaxDD={base_rm['max_dd']:.0f}, "
          f"Sharpe={base_rm['sharpe']:.3f}")
    print(f"\n  {'Filter':<30} {'Delta':>10} {'P(better)':>10} {'Combined':>15}")
    print("  " + "-" * 70)

    rankings = []
    for f_name, data in boot_results.items():
        if f_name == "baseline":
            continue
        f_pnls = np.array(data["pnls"])
        rm = data["rm"]
        min_len = min(len(base_pnls), len(f_pnls))
        diff = f_pnls[:min_len] - base_pnls[:min_len]
        delta = diff.sum()

        boot_diffs = np.zeros(N_BOOTSTRAP)
        for i in range(N_BOOTSTRAP):
            idx = np.random.choice(min_len, size=min_len, replace=True)
            boot_diffs[i] = diff[idx].sum()
        p_better = (boot_diffs > 0).mean()

        combined = "BETTER" if p_better > 0.90 else ("mixed" if p_better > 0.5 else "WORSE")
        rankings.append({"name": f_name, "delta": delta, "p_better": p_better, "combined": combined})
        print(f"  {f_name:<30} {delta:>+10.0f} {p_better:>9.1%} {combined:>15}")

    better = sorted([r for r in rankings if r["p_better"] > 0.9],
                    key=lambda x: x["p_better"], reverse=True)
    if better:
        print(f"\n  Filters significantly better than baseline (P>90%):")
        for r in better:
            print(f"    {r['name']}: P={r['p_better']:.1%}, Δ={r['delta']:+.0f}")
    else:
        print(f"\n  No filter significantly beats baseline (P>90%).")

    return rankings


def section_final_recommendations(all_results, best_level=1):
    """Final recommendations based on all analysis."""
    print("\n" + "=" * 110)
    print(f"  SECTION 5: FINAL RECOMMENDATIONS — {ETF_TAG}ETF")
    print("=" * 110)

    # Find best filter per OTM level by total P&L
    for lv in OTM_LEVELS:
        key = f"OTM{lv}"
        if key not in all_results:
            continue
        level_res = all_results[key]
        # Sort by total P&L (higher = less negative = better for puts)
        sorted_filters = sorted(level_res.items(),
                                key=lambda x: x[1]["rm"].get("total", -999999),
                                reverse=True)
        top3 = [(fn, d) for fn, d in sorted_filters[:3] if fn != "baseline"]
        base_rm = level_res.get("baseline", {}).get("rm", {})
        base_total = base_rm.get("total", 0)

        print(f"\n  OTM Level {lv} (Baseline Total: {base_total:.0f} RMB):")
        for i, (fn, d) in enumerate(top3):
            rm = d["rm"]
            delta = rm["total"] - base_total
            print(f"    {i+1}. {fn}: Total={rm['total']:.0f} (Δ{delta:+.0f}), "
                  f"Sharpe={rm['sharpe']:.3f}, Place={d['placement']:.1%}, "
                  f"MaxDD={rm['max_dd']:.0f}")

    print(f"\n  NOTE: Positive total P&L means the put filter is net profitable.")
    print(f"  Negative total means hedge drag. Best filter = least negative or positive.")
    print(f"  Use these results to configure PutStrategy filters in backtest_strategies.py")
    print()


def main():
    global N_BOOTSTRAP

    parser = argparse.ArgumentParser(description="Synthetic Put Filter Evaluation")
    parser.add_argument("-e", "--etf", type=str, choices=["50", "300", "500"], default="300")
    parser.add_argument("-n", "--bootstrap", type=int, default=N_BOOTSTRAP)
    parser.add_argument("-l", "--level", type=int, default=1,
                        help="OTM level for bootstrap section (default: 1)")
    args = parser.parse_args()
    select_etf(args.etf)
    N_BOOTSTRAP = args.bootstrap
    np.random.seed(42)

    print("=" * 110)
    print(f"  SYNTHETIC PUT FILTER EVALUATION — {ETF_TAG}ETF")
    print(f"  Strategy: Pass→Buy Put, Fail→Skip (Selective Hedge)")
    print(f"  Bootstrap iterations: {N_BOOTSTRAP} | Bootstrap OTM Level: {args.level}")
    print("=" * 110)

    df = load_data()
    n_dates = df[df["Option Type"] == "P"]["Date"].nunique()
    print(f"  Synthetic put samples: {n_dates} dates")

    # ── Define put-buying filters ─────────────────────────────────────
    # Puts profit when market drops. Buy when indicators suggest vulnerability.
    f_rsi40 = df['rsi14'] < 40
    f_rsi45 = df['rsi14'] < 45
    f_rsi50 = df['rsi14'] < 50
    f_rsi55 = df['rsi14'] < 55
    f_rsi60 = df['rsi14'] < 60
    f_bbl = df['close'] < df['bb_lower']
    f_bbl_atr = df['close'] < (df['bb_lower'] - 0.5 * df['atr20'])
    f_vol_high = df['vol20'] > df['vol20_median']
    f_roc10_neg3 = df['roc10'] < -3.0
    f_roc10_neg5 = df['roc10'] < -5.0
    f_roc10_neg7 = df['roc10'] < -7.0
    f_roc5_neg = df['roc5'] < -2.0
    f_sma50_below = df['close'] < df['sma50']
    f_sma20_below = df['close'] < df['sma20']
    f_macd_neg = df['macd_hist'] < 0
    f_ema_cross = df['ema20'] < df['sma50']  # bearish alignment

    # Fill NaN
    for f in [f_rsi40, f_rsi45, f_rsi50, f_rsi55, f_rsi60, f_bbl, f_bbl_atr,
              f_vol_high, f_roc10_neg3, f_roc10_neg5, f_roc10_neg7, f_roc5_neg,
              f_sma50_below, f_sma20_below, f_macd_neg, f_ema_cross]:
        f.fillna(False, inplace=True)

    filters = {
        "baseline": pd.Series(True, index=df.index),

        # Individual RSI thresholds
        "f_rsi40": f_rsi40,
        "f_rsi45": f_rsi45,
        "f_rsi50": f_rsi50,
        "f_rsi55": f_rsi55,
        "f_rsi60": f_rsi60,

        # Bollinger lower band
        "f_bbl": f_bbl,
        "f_bbl_atr": f_bbl_atr,

        # Vol regime
        "f_vol_high": f_vol_high,

        # Momentum (negative = market dropping)
        "f_roc10_neg3": f_roc10_neg3,
        "f_roc10_neg5": f_roc10_neg5,
        "f_roc10_neg7": f_roc10_neg7,
        "f_roc5_neg": f_roc5_neg,

        # Trend
        "f_sma50_below": f_sma50_below,
        "f_sma20_below": f_sma20_below,
        "f_macd_neg": f_macd_neg,
        "f_ema_cross": f_ema_cross,

        # 2-filter combos
        "f_rsi50_AND_bbl": f_rsi50 & f_bbl,
        "f_rsi50_AND_vol": f_rsi50 & f_vol_high,
        "f_rsi50_AND_sma50": f_rsi50 & f_sma50_below,
        "f_rsi50_AND_macd": f_rsi50 & f_macd_neg,
        "f_rsi45_AND_vol": f_rsi45 & f_vol_high,
        "f_bbl_AND_vol": f_bbl & f_vol_high,
        "f_sma50_AND_vol": f_sma50_below & f_vol_high,
        "f_sma50_AND_macd": f_sma50_below & f_macd_neg,
        "f_rsi55_AND_sma50": f_rsi55 & f_sma50_below,

        # 3-filter combos
        "f_rsi50_bbl_vol": f_rsi50 & f_bbl & f_vol_high,
        "f_rsi50_sma50_vol": f_rsi50 & f_sma50_below & f_vol_high,
        "f_rsi50_sma50_macd": f_rsi50 & f_sma50_below & f_macd_neg,
        "f_rsi45_sma50_vol": f_rsi45 & f_sma50_below & f_vol_high,
        "f_bbl_sma50_vol": f_bbl & f_sma50_below & f_vol_high,
    }

    section_per_level_breakdown(df, filters)
    all_results = section_filter_ranking(df, filters)
    boot_results = section_bootstrap(df, filters, best_level=args.level)
    section_significance(boot_results)
    section_final_recommendations(all_results, best_level=args.level)


if __name__ == "__main__":
    main()
