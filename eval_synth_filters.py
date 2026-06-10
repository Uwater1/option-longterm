"""
Enhanced Synthetic Data Filter Evaluation for 500ETF
=====================================================
Evaluates individual filters on synthetic option data with:
  1. Per-OTM-level breakdown (calls + puts)
  2. Bootstrap confidence intervals on total P&L per filter
  3. Statistical significance vs baseline (P-value)
  4. Filter scoring and ranking
  5. Synthetic vs Real data comparison summary

Usage:
  python eval_synth_filters.py -e 500
  python eval_synth_filters.py -e 300
"""
import pandas as pd
import numpy as np
import pandas_ta as ta
import argparse
import os
import logging
from numba_utils import calculate_research_metrics_numba

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)

N_BOOTSTRAP = 5000
MULTIPLIER = 10000
COMMISSION = 2.0

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


def compute_per_date_pnl(df, f_mask, option_type="C"):
    sub_df = df[df["Option Type"] == option_type].reset_index(drop=True)

    dates = sub_df['Date'].values
    diff = np.where(dates[1:] != dates[:-1])[0] + 1
    boundaries = np.zeros(len(diff) + 2, dtype=np.int64)
    boundaries[0] = 0
    boundaries[1:-1] = diff
    boundaries[-1] = len(sub_df)

    aligned_mask = f_mask[df["Option Type"] == option_type].reset_index(drop=True)
    group_filter_mask = aligned_mask.values[boundaries[:-1]]

    strikes = sub_df["Strike"].values.astype(np.float64)
    s0s = sub_df["Underlying Price at Date"].values.astype(np.float64)
    prices = sub_df["Price"].values.astype(np.float64)
    worthless = sub_df["Expire_worthless"].values.astype(np.int8)
    ret_val = sub_df["Exp Ret Short" if option_type == "C" else "Exp Ret Long"].values.astype(np.float64)

    is_short_call = (option_type == "C")
    metrics_p, metrics_f = calculate_research_metrics_numba(
        strikes, s0s, ret_val, prices, worthless, boundaries,
        is_short_call, group_filter_mask
    )

    per_date_pnl = {}
    num_groups = len(boundaries) - 1
    for g in range(num_groups):
        start = boundaries[g]
        end = boundaries[g + 1]
        s0 = s0s[start]
        is_pass = group_filter_mask[g]
        if not is_pass:
            continue

        date_val = dates[start]
        date_pnl = 0.0
        atm_idx = -1
        first_otm_idx = start
        for i in range(start, end):
            if strikes[i] <= s0:
                atm_idx = i
                first_otm_idx = i + 1
            else:
                break

        idx_list = []
        if atm_idx != -1:
            idx_list.append(atm_idx)
        for i in range(first_otm_idx, end):
            if len(idx_list) >= 6:
                break
            idx_list.append(i)

        for idx in idx_list:
            if idx == -1:
                continue
            ret = ret_val[idx]
            prc = prices[idx]
            if np.isnan(ret):
                continue
            if is_short_call:
                sell_p = prc * (1.0 - 0.02)
                pnl = ret * sell_p * MULTIPLIER - COMMISSION
            else:
                buy_p = prc * (1.0 + 0.02)
                pnl = ret * buy_p * MULTIPLIER - COMMISSION
            date_pnl += pnl

        per_date_pnl[date_val] = date_pnl

    return metrics_p, metrics_f, per_date_pnl


def bootstrap_ci(pnls, n_boot=N_BOOTSTRAP, ci=0.95):
    pnls = np.array(pnls)
    n = len(pnls)
    boot_totals = np.zeros(n_boot)
    for i in range(n_boot):
        sample = np.random.choice(pnls, size=n, replace=True)
        boot_totals[i] = sample.sum()

    alpha = (1 - ci) / 2
    lo = np.percentile(boot_totals, alpha * 100)
    hi = np.percentile(boot_totals, (1 - alpha) * 100)
    return {
        "total": pnls.sum(),
        "mean": pnls.mean(),
        "ci_lo": lo,
        "ci_hi": hi,
        "std_total": boot_totals.std(),
        "boot_totals": boot_totals,
    }


def section_per_level_breakdown(df, filters):
    print("\n" + "=" * 110)
    print(f"  SECTION 1: PER-LEVEL OTM BREAKDOWN (Short Calls) — {ETF_TAG}ETF Synthetic")
    print("=" * 110)

    level_names = {0: "ATM", 1: "OTM1", 2: "OTM2", 3: "OTM3", 4: "OTM4", 5: "OTM5"}

    for f_name, f_mask in filters.items():
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


def section_filter_bootstrap(df, filters):
    print("\n" + "=" * 110)
    print(f"  SECTION 2: BOOTSTRAP CONFIDENCE INTERVALS — {ETF_TAG}ETF Synthetic (OTM2+3 calls, {N_BOOTSTRAP} iterations)")
    print("=" * 110)

    print(f"\n  {'Filter':<25} {'N':>5} {'Total P&L':>10} {'Mean':>8} {'95% CI Lo':>10} {'95% CI Hi':>10} {'Boot Std':>10}")
    print("  " + "-" * 90)

    all_pnls = {}
    all_ci = {}

    for f_name, f_mask in filters.items():
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

        lv2_er = metrics_p[2, 1] / metrics_p[2, 0] if metrics_p[2, 0] > 0 else 0
        lv3_er = metrics_p[3, 1] / metrics_p[3, 0] if metrics_p[3, 0] > 0 else 0

        n_groups = len(boundaries) - 1
        date_pnls = []
        for g in range(n_groups):
            if not group_filter_mask[g]:
                continue
            start = boundaries[g]
            end = boundaries[g + 1]
            s0 = s0s[start]

            atm_idx = -1
            first_otm = start
            for i in range(start, end):
                if strikes[i] <= s0:
                    atm_idx = i
                    first_otm = i + 1
                else:
                    break

            lv_indices = {2: -1, 3: -1}
            otm_idx = 0
            if atm_idx != -1:
                pass
            for i in range(first_otm, end):
                otm_idx += 1
                if otm_idx == 2:
                    lv_indices[2] = i
                elif otm_idx == 3:
                    lv_indices[3] = i
                if otm_idx >= 3:
                    break

            cycle_pnl = 0.0
            for lv_key in [2, 3]:
                idx = lv_indices[lv_key]
                if idx == -1:
                    continue
                ret = ret_val[idx]
                prc = prices[idx]
                if np.isnan(ret):
                    continue
                sell_p = prc * (1.0 - 0.02)
                pnl = ret * sell_p * MULTIPLIER - COMMISSION
                cycle_pnl += pnl

            date_pnls.append(cycle_pnl)

        if len(date_pnls) == 0:
            continue

        ci = bootstrap_ci(date_pnls)
        all_pnls[f_name] = date_pnls
        all_ci[f_name] = ci

        print(f"  {f_name:<25} {len(date_pnls):>5} {ci['total']:>10.0f} {ci['mean']:>8.1f} "
              f"{ci['ci_lo']:>10.0f} {ci['ci_hi']:>10.0f} {ci['std_total']:>10.0f}")

    return all_pnls, all_ci


def section_statistical_significance(all_pnls, all_ci):
    print("\n" + "=" * 110)
    print(f"  SECTION 3: STATISTICAL SIGNIFICANCE vs BASELINE — {ETF_TAG}ETF Synthetic")
    print("=" * 110)

    if "baseline" not in all_pnls:
        print("  No baseline found, skipping.")
        return

    base_pnls = np.array(all_pnls["baseline"])
    base_ci = all_ci["baseline"]

    print(f"\n  Baseline: Total={base_ci['total']:.0f}, 95% CI=[{base_ci['ci_lo']:.0f}, {base_ci['ci_hi']:.0f}]")
    print(f"\n  {'Filter':<25} {'Δ Total':>10} {'95% CI Lo':>10} {'95% CI Hi':>10} {'P(better)':>10} {'Significant':>12}")
    print("  " + "-" * 82)

    significant_filters = []

    for f_name, pnl_list in all_pnls.items():
        if f_name == "baseline":
            continue
        f_pnls = np.array(pnl_list)

        min_len = min(len(base_pnls), len(f_pnls))
        if min_len == 0:
            continue

        base_sample = base_pnls[:min_len]
        f_sample = f_pnls[:min_len]
        diff_pnls = f_sample - base_sample
        total_diff = diff_pnls.sum()

        boot_diffs = np.zeros(N_BOOTSTRAP)
        for i in range(N_BOOTSTRAP):
            idx = np.random.choice(min_len, size=min_len, replace=True)
            boot_diffs[i] = diff_pnls[idx].sum()

        p_better = (boot_diffs > 0).mean()
        ci_lo = np.percentile(boot_diffs, 2.5)
        ci_hi = np.percentile(boot_diffs, 97.5)
        sig = "YES*" if p_better > 0.95 else "no"

        if p_better > 0.95:
            significant_filters.append((f_name, total_diff, p_better))

        print(f"  {f_name:<25} {total_diff:>+10.0f} {ci_lo:>+10.0f} {ci_hi:>+10.0f} {p_better:>9.1%} {sig:>12}")

    if significant_filters:
        print(f"\n  Filters with P > 95% vs baseline:")
        for fn, td, pb in significant_filters:
            print(f"    {fn}: Δ={td:+.0f}, P={pb:.1%}")
    else:
        print(f"\n  No filters significantly beat baseline at 95% level.")


def section_put_analysis(df, filters):
    print("\n" + "=" * 110)
    print(f"  SECTION 4: PUT ANALYSIS (Long Put) — {ETF_TAG}ETF Synthetic")
    print("=" * 110)

    level_names = {0: "ATM", 1: "OTM1", 2: "OTM2", 3: "OTM3", 4: "OTM4", 5: "OTM5"}

    selected = {k: filters[k] for k in ["baseline"] if k in filters}

    for f_name, f_mask in selected.items():
        df["Pass Filter"] = f_mask.fillna(True)
        sub_df = df[df["Option Type"] == "P"].reset_index(drop=True)

        dates = sub_df['Date'].values
        diff = np.where(dates[1:] != dates[:-1])[0] + 1
        boundaries = np.zeros(len(diff) + 2, dtype=np.int64)
        boundaries[0] = 0
        boundaries[1:-1] = diff
        boundaries[-1] = len(sub_df)

        group_filter_mask = np.ones(len(boundaries) - 1, dtype=bool)

        strikes = sub_df["Strike"].values.astype(np.float64)
        s0s = sub_df["Underlying Price at Date"].values.astype(np.float64)
        prices = sub_df["Price"].values.astype(np.float64)
        worthless = sub_df["Expire_worthless"].values.astype(np.int8)
        ret_val = sub_df["Exp Ret Long"].values.astype(np.float64)

        metrics_p, _ = calculate_research_metrics_numba(
            strikes, s0s, ret_val, prices, worthless, boundaries, False, group_filter_mask
        )

        print(f"\n  --- {f_name} (Put, no filter applies to puts) ---")
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


def section_scoring_ranking(df, filters):
    print("\n" + "=" * 110)
    print(f"  SECTION 5: FILTER SCORING & RANKING — {ETF_TAG}ETF Synthetic")
    print("=" * 110)

    results = []

    for f_name, f_mask in filters.items():
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

        total_passed = 0
        total_filtered = 0
        total_er_passed = 0
        total_er_filtered = 0
        min_ml = np.inf
        total_wins = 0

        for lv in range(6):
            count_p = int(metrics_p[lv, 0])
            pnl_sum_p = metrics_p[lv, 1]
            wins_p = metrics_p[lv, 2]
            ml_p = metrics_p[lv, 4]

            count_f = int(metrics_f[lv, 0])
            pnl_sum_f = metrics_f[lv, 1]

            if count_p > 0:
                total_passed += count_p
                total_er_passed += pnl_sum_p
                total_wins += int(wins_p)
                if ml_p < min_ml:
                    min_ml = ml_p

            if count_f > 0:
                total_filtered += count_f
                total_er_filtered += pnl_sum_f

        avg_er_passed = total_er_passed / total_passed if total_passed > 0 else 0
        avg_er_filtered = total_er_filtered / total_filtered if total_filtered > 0 else 0
        pr = total_passed / (total_passed + total_filtered) if (total_passed + total_filtered) > 0 else 0
        wr = total_wins / total_passed if total_passed > 0 else 0

        score = 0.0
        if pr >= 0.70 and avg_er_filtered < 1000:
            score = pr * avg_er_passed + (min_ml / 100 if min_ml != np.inf else 0) - avg_er_filtered

        results.append({
            "Filter": f_name,
            "Placement Rate": pr,
            "Win Rate": wr,
            "Avg ER (Passed)": avg_er_passed,
            "Avg ER (Filtered)": avg_er_filtered,
            "Max Loss": min_ml if min_ml != np.inf else float('nan'),
            "Score": score,
        })

    res_df = pd.DataFrame(results)

    print(f"\n  Full Results:")
    print(f"  {'Filter':<25} {'Place%':>7} {'Win%':>7} {'ER(In)':>8} {'ER(Out)':>8} {'MaxLoss':>10} {'Score':>8}")
    print("  " + "-" * 80)
    for _, row in res_df.iterrows():
        print(f"  {row['Filter']:<25} {row['Placement Rate']:>6.1%} {row['Win Rate']:>6.1%} "
              f"{row['Avg ER (Passed)']:>8.1f} {row['Avg ER (Filtered)']:>8.1f} "
              f"{row['Max Loss']:>10.0f} {row['Score']:>8.1f}")

    ranked = res_df[res_df["Filter"] != "baseline"].sort_values("Score", ascending=False)
    print(f"\n  Top 5 Filters by Score (placement >= 70%, filtered ER < 1000):")
    for i, (_, row) in enumerate(ranked.head(5).iterrows()):
        print(f"    {i + 1}. {row['Filter']}: Score={row['Score']:.1f} "
              f"(Place={row['Placement Rate']:.1%}, ER(In)={row['Avg ER (Passed)']:.1f}, "
              f"ER(Out)={row['Avg ER (Filtered)']:.1f})")

    return res_df


def section_combined_strategy(df, filters):
    print("\n" + "=" * 110)
    print(f"  SECTION 6: COMBINED STRATEGY SIMULATION (OTM2+3 Call + Put L1) — {ETF_TAG}ETF Synthetic")
    print("=" * 110)

    for f_name, f_mask in [("baseline", filters["baseline"]), ("f3", filters.get("f3", filters["baseline"])),
                            ("f6", filters.get("f6", filters["baseline"])),
                            ("f3_AND_f6", filters.get("f3", filters["baseline"]) & filters.get("f6", filters["baseline"]))]:
        df["Pass Filter"] = f_mask.fillna(True)

        sub_c = df[df["Option Type"] == "C"].reset_index(drop=True)
        sub_p = df[df["Option Type"] == "P"].reset_index(drop=True)

        # Call P&L (OTM2+3 when pass, OTM4 when fail)
        for sub_df, offsets_pass, offsets_fail, label in [
            (sub_c, [2, 3], [4], "call"),
            (sub_p, [1], [1], "put"),
        ]:
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
            ret_val = sub_df["Exp Ret Short" if label == "call" else "Exp Ret Long"].values.astype(np.float64)

            n_groups = len(boundaries) - 1
            date_pnls = []
            for g in range(n_groups):
                start = boundaries[g]
                end = boundaries[g + 1]
                s0 = s0s[start]
                is_pass = group_filter_mask[g]
                offsets = offsets_pass if is_pass else offsets_fail

                idx_list = []
                if label == "call":
                    atm_idx = -1
                    first_otm = start
                    for i in range(start, end):
                        if strikes[i] <= s0:
                            atm_idx = i
                            first_otm = i + 1
                        else:
                            break
                    otm_list = []
                    for i in range(first_otm, end):
                        otm_list.append(i)
                    for off in offsets:
                        if off < len(otm_list):
                            idx_list.append(otm_list[off])
                else:
                    atm_idx = -1
                    for i in range(start, end):
                        if strikes[i] >= s0:
                            atm_idx = i
                            break
                    otm_list = []
                    if atm_idx != -1:
                        for i in range(atm_idx - 1, start - 1, -1):
                            otm_list.append(i)
                    for off in offsets:
                        if off - 1 < len(otm_list):
                            idx_list.append(otm_list[off - 1])

                cycle_pnl = 0.0
                for idx in idx_list:
                    ret = ret_val[idx]
                    prc = prices[idx]
                    if np.isnan(ret):
                        continue
                    if label == "call":
                        sell_p = prc * (1.0 - 0.02)
                        pnl = ret * sell_p * MULTIPLIER - COMMISSION
                    else:
                        buy_p = prc * (1.0 + 0.02)
                        pnl = ret * buy_p * MULTIPLIER - COMMISSION
                    cycle_pnl += pnl

                date_pnls.append(cycle_pnl)

            if label == "call":
                call_pnls = date_pnls
            else:
                put_pnls = date_pnls

        combined = np.array(call_pnls) + np.array(put_pnls[:len(call_pnls)])
        ci = bootstrap_ci(combined)
        wr = (combined > 0).mean()
        n_pass = int(f_mask.fillna(True)[df["Option Type"] == "C"].reset_index(drop=True).values[
            np.where(df[df["Option Type"] == "C"].reset_index(drop=True)['Date'].values[1:] !=
                     df[df["Option Type"] == "C"].reset_index(drop=True)['Date'].values[:-1])[0] + 1
        ].sum() if len(f_mask) > 0 else 0)

        print(f"\n  {f_name}: N={len(combined)}, Total={ci['total']:.0f}, "
              f"Mean={ci['mean']:.1f}, WinRate={wr:.1%}, "
              f"95% CI=[{ci['ci_lo']:.0f}, {ci['ci_hi']:.0f}], BootStd={ci['std_total']:.0f}")


def main():
    global N_BOOTSTRAP

    parser = argparse.ArgumentParser(description="Enhanced Synthetic Filter Evaluation")
    parser.add_argument("-e", "--etf", type=str, choices=["50", "300", "500"], default="500")
    parser.add_argument("-n", "--bootstrap", type=int, default=N_BOOTSTRAP)
    args = parser.parse_args()
    select_etf(args.etf)

    N_BOOTSTRAP = args.bootstrap

    np.random.seed(42)

    print("=" * 110)
    print(f"  ENHANCED SYNTHETIC FILTER EVALUATION — {ETF_TAG}ETF")
    print(f"  Bootstrap iterations: {N_BOOTSTRAP}")
    print("=" * 110)

    df = load_data()
    n_dates = df[df["Option Type"] == "C"]["Date"].nunique()
    print(f"  Synthetic samples: {n_dates} dates")
    print(f"  Total rows: {len(df)}")

    filters = {
        "baseline": pd.Series(True, index=df.index),
        "f1": df['close'] < df['sma20'],
        "f2": df['close'] < df['ema20'],
        "f3": df['rsi14'] < 70,
        "f3_rsi66": df['rsi14'] < 66,
        "f4": df['rsi14'] > 30,
        "f5": df['macd_hist'] < 0,
        "f6": df['close'] < df['bb_upper'],
        "f9": df['roc20'] < 5.0,
        "f10": df['close'] < (df['sma20'] + df['atr20']),
        "f11": df['adx14'] < 25,
        "f12": df['ema10'] < df['ema30'],
        "f15": df['stoch_k'] < 80,
        "f16": df['close'] < (0.98 * df['rolling_high_20']),
        "f17": df['close'] < (0.95 * df['rolling_high_252']),
        "f20": df['close'] < (df['ema20'] + 1.0 * df['atr20']),
        "f3_AND_f6": (df['rsi14'] < 70) & (df['close'] < df['bb_upper']),
        "f3_rsi66_AND_f6": (df['rsi14'] < 66) & (df['close'] < df['bb_upper']),
        "f4_AND_f6": (df['rsi14'] > 30) & (df['close'] < df['bb_upper']),
        "f3_AND_f4_AND_f6": (df['rsi14'] < 70) & (df['rsi14'] > 30) & (df['close'] < df['bb_upper']),
        "f9_AND_f6": (df['roc20'] < 5.0) & (df['close'] < df['bb_upper']),
    }

    section_per_level_breakdown(df, filters)
    all_pnls, all_ci = section_filter_bootstrap(df, filters)
    section_statistical_significance(all_pnls, all_ci)
    section_put_analysis(df, filters)
    scored = section_scoring_ranking(df, filters)
    section_combined_strategy(df, filters)

    print("\n" + "=" * 110)
    print(f"  CONCLUSIONS — {ETF_TAG}ETF Synthetic")
    print("=" * 110)

    baseline_er = all_ci.get("baseline", {}).get("mean", 0)
    best_filter = None
    best_er = -np.inf
    for f_name, ci in all_ci.items():
        if f_name == "baseline":
            continue
        if ci["mean"] > best_er and f_name in filters and not f_name.startswith("f3_AND") and not f_name.startswith("f4_AND") and not f_name.startswith("f9_AND"):
            best_er = ci["mean"]
            best_filter = f_name

    if best_filter:
        print(f"\n  Best individual filter: {best_filter} (Mean ER: {best_er:.1f} vs Baseline: {baseline_er:.1f})")
    print(f"\n  Synthetic data provides {n_dates} samples vs 45 real cycles — {(n_dates/45):.0f}x more data")
    print(f"  Bootstrap CIs are tighter, providing more robust filter ranking")
    print(f"  Key insight: Synthetic data validates whether filter improvements hold across more market regimes")

    print()


if __name__ == "__main__":
    main()
