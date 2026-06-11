import pandas as pd
import numpy as np
import pandas_ta as ta
import argparse
import os
import sys

# Parameters
MULTIPLIER = 10000
COMMISSION = 2.0
SLIPPAGE = 0.02

# Paths
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

    # Technical indicators for the filters
    etf['sma20'] = ta.sma(etf['close'], length=20)
    etf['ema20'] = ta.ema(etf['close'], length=20)
    etf['sma50'] = ta.sma(etf['close'], length=50)
    etf['rsi14'] = ta.rsi(etf['close'], length=14)
    macd = ta.macd(etf['close'])
    if macd is not None:
        etf['macd_hist'] = macd.iloc[:, 1]
    bbands = ta.bbands(etf['close'], length=20, std=2)
    if bbands is not None:
        etf['bb_upper'] = bbands.iloc[:, 2]
    etf['roc10'] = ta.roc(etf['close'], length=10)
    etf['vol20'] = etf['close'].pct_change().rolling(20).std() * np.sqrt(252)
    etf['vol20_median'] = etf['vol20'].rolling(252).median()

    # Pre-merge to align dates
    df = df.merge(etf, left_on="Date", right_index=True, how="left")
    df = df.sort_values(['Option Type', 'Date', 'Strike']).reset_index(drop=True)
    return df, etf

def get_filter_mask(df, choice):
    if choice == "50":
        # RSI < 60 AND RSI > 30 AND ROC10 < 3% AND Vol20 < Vol20_median
        mask = (df['rsi14'] < 60.0) & (df['rsi14'] > 30.0) & (df['roc10'] < 3.0) & (df['vol20'] < df['vol20_median'])
    elif choice == "500":
        # RSI > 30 AND Close < BBU AND Close > SMA50
        mask = (df['rsi14'] > 30.0) & (df['Underlying Price at Date'] < df['bb_upper']) & (df['Underlying Price at Date'] > df['sma50'])
    else: # 300ETF
        # RSI < 72 AND RSI > 25 AND MACD Histogram < 0
        mask = (df['rsi14'] < 72.0) & (df['rsi14'] > 25.0) & (df['macd_hist'] < 0.0)
    return mask.fillna(False)

def precompute_prob_ups(etf, unit):
    dates = etf.index.values
    closes = etf["close"].values
    fwd_pt = np.full(len(etf), np.nan)
    for i, dt in enumerate(dates):
        target_dt = dt + np.timedelta64(30, 'D')
        idx = np.searchsorted(dates, target_dt)
        if idx < len(dates):
            fwd_pt[i] = closes[idx] - closes[i]

    is_up = (fwd_pt > unit).astype(float)
    is_valid = (~np.isnan(fwd_pt)).astype(float)

    # Completed moves are those starting at t <= D - 30 days
    limit_indices = np.searchsorted(dates + np.timedelta64(30, 'D'), dates, side='right') - 1

    cumsum_up = np.cumsum(np.nan_to_num(is_up))
    cumsum_valid = np.cumsum(is_valid)

    prob_ups = np.full(len(etf), 0.5)
    for i in range(len(etf)):
        idx_limit = limit_indices[i]
        if idx_limit >= 0 and cumsum_valid[idx_limit] > 0:
            prob_ups[i] = cumsum_up[idx_limit] / cumsum_valid[idx_limit]
    
    return pd.Series(prob_ups, index=etf.index)

def calc_risk_metrics(pnls):
    pnls = np.array(pnls)
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

    return {
        "total": cumulative[-1],
        "mean": mean_pnl,
        "std": std_pnl,
        "sharpe": sharpe,
        "max_dd": max_dd,
        "calmar": calmar,
        "win_rate": win_rate,
        "worst_loss": pnls.min(),
        "profit_factor": profit_factor,
    }

def main():
    parser = argparse.ArgumentParser(description="Optimize dynamic alpha strike selection on synthetic options data")
    parser.add_argument("-e", "--etf", type=str, choices=["50", "300", "500"], default="300")
    args = parser.parse_args()

    select_etf(args.etf)
    print(f"Optimizing for {ETF_TAG}ETF using synthetic options data...")

    df, etf = load_data()
    df["Pass Filter"] = get_filter_mask(df, args.etf)

    sub_c = df[df["Option Type"] == "C"].copy()
    sub_c = sub_c.sort_values(['Date', 'Strike']).reset_index(drop=True)
    
    dates = sub_c['Date'].values
    diff = np.where(dates[1:] != dates[:-1])[0] + 1
    boundaries = np.zeros(len(diff) + 2, dtype=np.int64)
    boundaries[0] = 0
    boundaries[1:-1] = diff
    boundaries[-1] = len(sub_c)

    n_groups = len(boundaries) - 1
    group_dates = dates[boundaries[:-1]]
    filter_passed_group = sub_c["Pass Filter"].values[boundaries[:-1]]

    # Pre-extract OTM option prices and returns
    # shape: (n_groups, 6)
    # otm_prices[g, k] is the price of the (k+1)-th OTM call option for group g
    otm_prices = np.full((n_groups, 6), np.nan)
    otm_rets = np.full((n_groups, 6), np.nan)
    
    strikes = sub_c["Strike"].values
    s0s = sub_c["Underlying Price at Date"].values
    prices = sub_c["Price"].values
    rets = sub_c["Exp Ret Short"].values
    
    for g in range(n_groups):
        start = boundaries[g]
        end = boundaries[g + 1]
        s0 = s0s[start]
        
        idx = 0
        for i in range(start, end):
            if strikes[i] > s0:
                if idx < 6:
                    otm_prices[g, idx] = prices[i]
                    otm_rets[g, idx] = rets[i]
                    idx += 1
                else:
                    break

    # Setup Grid
    if args.etf == "50":
        units = [0.02, 0.03, 0.04, 0.05]
        t1s = [0.20, 0.25, 0.28, 0.30]
        t2s = [0.30, 0.35, 0.38, 0.40]
    elif args.etf == "500":
        units = [0.06, 0.07, 0.08, 0.09, 0.10]
        t1s = [0.20, 0.25, 0.28, 0.30]
        t2s = [0.30, 0.35, 0.38, 0.40]
    else: # 300
        units = [0.03, 0.04, 0.05, 0.06, 0.07]
        t1s = [0.25, 0.28, 0.30, 0.32, 0.35]
        t2s = [0.35, 0.38, 0.40, 0.42, 0.45]

    offset_combos = [
        # format: (O1, O2, O3)
        ([2, 3], [3, 3], [4, 4]), # Baseline
        ([2, 2], [2, 3], [3, 3]), # Aggressive
        ([2, 3], [3, 4], [4, 4]), # Standard
        ([2, 3], [3, 4], [4, 5]), # Safer high
        ([3, 3], [4, 4], [5, 5]), # Ultra safe
        ([2, 2], [3, 3], [4, 4]), # Jump
        ([3, 3], [3, 4], [4, 4]), # Defensive low
        ([1, 2], [2, 3], [3, 3]), # Very aggressive
    ]

    # ── Precompute no-filter baseline (OTM2+3, trade every group) ──────────
    # Used for filter_lift: how much value the filter adds vs always trading.
    # This depends only on offset combo, not on unit/t1/t2, so precompute once.
    pnls_nofilter_by_combo = np.zeros((len(offset_combos), n_groups))
    for combo_idx, (O1, O2, O3) in enumerate(offset_combos):
        o_base = [o - 1 for o in O1]  # Use low-regime offsets as no-filter baseline
        for g in range(n_groups):
            date_pnl = 0.0
            for off in o_base:
                if 0 <= off < 6:
                    prc = otm_prices[g, off]
                    ret = otm_rets[g, off]
                    if not np.isnan(prc) and not np.isnan(ret):
                        exec_p = prc * (1.0 - SLIPPAGE)
                        pnl = ret * exec_p * MULTIPLIER - COMMISSION
                        date_pnl += pnl
            pnls_nofilter_by_combo[combo_idx, g] = date_pnl

    best_sharpe = -float('inf')
    best_params = None
    all_runs = []

    # Map group_dates to series index for fast lookups
    etf_date_to_idx = {d: idx for idx, d in enumerate(etf.index)}
    group_idx_in_etf = np.array([etf_date_to_idx.get(pd.Timestamp(d)) for d in group_dates])

    print(f"Starting parameter search...")
    for unit in units:
        # Precompute prob_ups for this unit
        prob_ups = precompute_prob_ups(etf, unit).values
        # Map back to group indices
        prob_ups_group = prob_ups[group_idx_in_etf]

        for t1 in t1s:
            for t2 in t2s:
                if t2 <= t1:
                    continue
                for combo_idx, (O1, O2, O3) in enumerate(offset_combos):
                    # Simulate
                    o1_idx = [o - 1 for o in O1]
                    o2_idx = [o - 1 for o in O2]
                    o3_idx = [o - 1 for o in O3]
                    
                    pnls = np.zeros(n_groups)
                    n_placed = 0
                    sum_pnl_placed_filtered = 0.0
                    sum_pnl_placed_nofilter = 0.0

                    pnls_nf = pnls_nofilter_by_combo[combo_idx]

                    for g in range(n_groups):
                        prob = prob_ups_group[g]
                        if prob < t1:
                            offsets = o1_idx
                        elif prob <= t2:
                            offsets = o2_idx
                        else:
                            offsets = o3_idx
                        
                        if filter_passed_group[g]:
                            n_placed += 1
                            date_pnl = 0.0
                            for off in offsets:
                                if 0 <= off < 6:
                                    prc = otm_prices[g, off]
                                    ret = otm_rets[g, off]
                                    if not np.isnan(prc) and not np.isnan(ret):
                                        exec_p = prc * (1.0 - SLIPPAGE)
                                        pnl = ret * exec_p * MULTIPLIER - COMMISSION
                                        date_pnl += pnl
                            pnls[g] = date_pnl
                            sum_pnl_placed_filtered += date_pnl
                            sum_pnl_placed_nofilter += pnls_nf[g]
                        # else: pnls[g] stays 0 (filter blocked, no trade)

                    # Filter lift: avg P&L per placed cycle (filtered) minus
                    # avg P&L per cycle if always trading (no-filter baseline)
                    placement_rate = n_placed / n_groups if n_groups > 0 else 0.0
                    if n_placed > 0:
                        avg_pnl_placed_filtered = sum_pnl_placed_filtered / n_placed
                        avg_pnf = pnls_nf.mean()
                        filter_lift = avg_pnl_placed_filtered - avg_pnf
                    else:
                        avg_pnl_placed_filtered = 0.0
                        filter_lift = 0.0

                    rm = calc_risk_metrics(pnls)
                    if not rm:
                        continue

                    rm.update({
                        "unit": unit,
                        "t1": t1,
                        "t2": t2,
                        "O1": O1,
                        "O2": O2,
                        "O3": O3,
                        "combo_idx": combo_idx,
                        "placement_rate": placement_rate,
                        "filter_lift": filter_lift,
                        "n_placed": n_placed,
                    })
                    all_runs.append(rm)

    # Multi-criteria scoring (similar to eval_synth_filters.py)
    runs_df = pd.DataFrame(all_runs)
    if runs_df.empty:
        print("Error: No valid runs generated.")
        return

    # Normalize metrics for scoring
    def norm(col, higher_better=True):
        val = runs_df[col].values
        if val.max() == val.min():
            return np.zeros_like(val)
        if higher_better:
            return (val - val.min()) / (val.max() - val.min())
        else:
            return (val.max() - val) / (val.max() - val.min())

    runs_df["norm_total"] = norm("total", True)
    runs_df["norm_sharpe"] = norm("sharpe", True)
    runs_df["norm_max_dd"] = norm("max_dd", False)
    runs_df["norm_win_rate"] = norm("win_rate", True)
    runs_df["norm_placement_rate"] = norm("placement_rate", True)
    runs_df["norm_filter_lift"] = norm("filter_lift", True)

    # 6-component composite score:
    # 20% Sharpe, 15% Total, 15% MaxDD, 15% WinRate, 15% PlacementRate, 20% FilterLift
    runs_df["Score"] = (
        0.20 * runs_df["norm_sharpe"] +
        0.15 * runs_df["norm_total"] +
        0.15 * runs_df["norm_max_dd"] +
        0.15 * runs_df["norm_win_rate"] +
        0.15 * runs_df["norm_placement_rate"] +
        0.20 * runs_df["norm_filter_lift"]
    )

    runs_df = runs_df.sort_values("Score", ascending=False).reset_index(drop=True)

    print("\n" + "="*80)
    print(f" TOP 5 DYNAMIC ALPHA PARAMETERS FOR {ETF_TAG}ETF (SYNTHETIC DATA)")
    print("="*80)
    for i in range(min(5, len(runs_df))):
        row = runs_df.iloc[i]
        print(f"Rank {i+1} (Score: {row['Score']:.3f}):")
        print(f"  - Unit={row['unit']:.3f}, T1={row['t1']:.2f}, T2={row['t2']:.2f}")
        print(f"  - Offsets: <T1: {row['O1']}, <=T2: {row['O2']}, >T2: {row['O3']}")
        print(f"  - Performance: P&L={row['total']:.2f} RMB, Sharpe={row['sharpe']:.3f}, MaxDD={row['max_dd']:.2f} RMB, WinRate={row['win_rate']:.1%}")
        print(f"  - Placement: {row['placement_rate']:.1%} ({int(row['n_placed'])}/{n_groups}), FilterLift={row['filter_lift']:.2f} RMB/cycle")
    print("="*80)

    # Print baseline (combo_idx=0, unit=0.05 for 300, 0.03 for 50, 0.08 for 500)
    def_unit = 0.03 if args.etf == "50" else (0.08 if args.etf == "500" else 0.05)
    def_t1 = 0.28 if args.etf in ["50", "500"] else 0.30
    def_t2 = 0.38 if args.etf in ["50", "500"] else 0.40
    
    baseline = runs_df[
        (runs_df["combo_idx"] == 0) & 
        (np.abs(runs_df["unit"] - def_unit) < 1e-5) & 
        (np.abs(runs_df["t1"] - def_t1) < 1e-5) & 
        (np.abs(runs_df["t2"] - def_t2) < 1e-5)
    ]
    if not baseline.empty:
        base_row = baseline.iloc[0]
        print(f"\nBaseline Performance:")
        print(f"  - Unit={base_row['unit']:.3f}, T1={base_row['t1']:.2f}, T2={base_row['t2']:.2f}")
        print(f"  - Offsets: <T1: {base_row['O1']}, <=T2: {base_row['O2']}, >T2: {base_row['O3']}")
        print(f"  - Performance: P&L={base_row['total']:.2f} RMB, Sharpe={base_row['sharpe']:.3f}, MaxDD={base_row['max_dd']:.2f} RMB, WinRate={base_row['win_rate']:.1%}")
        print(f"  - Placement: {base_row['placement_rate']:.1%} ({int(base_row['n_placed'])}/{n_groups}), FilterLift={base_row['filter_lift']:.2f} RMB/cycle")
    
    # Save top run to file for report
    runs_df.to_csv(f"optimization_alpha_{args.etf}ETF_synthetic.csv", index=False)
    print(f"Full optimization results saved to optimization_alpha_{args.etf}ETF_synthetic.csv")

if __name__ == "__main__":
    main()
