#!/usr/bin/env python3
"""
Feature Selection Research: What makes a good pool?

Questions:
1. Sweet spot for feature count? (granular sweep)
2. Do low-correlation features produce better signals?
3. Does regime-adaptive top-K help? (use top-10 features per regime vs fixed top-10)
4. IC-weighted vs EW on full pool — does smart weighting fix dilution?

Methodology: Fixed Z_th=0.8, binary L+S, 8bps. Report train/OOS/per-year.
"""
import sys, numpy as np, pandas as pd
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from utils import load_admitted_pool, load_etf_dataset, build_pool_feature_matrix, expanding_zscore_numba
from strategy import generate_positions, simulate_etf_spot

Z_TH = 0.8
BURN_IN = 252
FEE = 0.0008


def eval_composite(Z_comp, full_trade_ret, dates, label=""):
    """Evaluate a composite signal. Returns dict of metrics."""
    pos = generate_positions(Z_comp, z_th=Z_TH, z_th_short=Z_TH, mode="binary", long_only=False)
    net_ret, _, _ = simulate_etf_spot(full_trade_ret, pos, fee_bps=FEE)
    
    tr_mask = (dates < pd.Timestamp("2022-01-01")).values
    oos_mask = ~tr_mask
    
    s_full = np.mean(net_ret[BURN_IN:]) / np.std(net_ret[BURN_IN:]) * np.sqrt(252) if np.std(net_ret[BURN_IN:]) > 1e-12 else 0
    tr_ret = net_ret[tr_mask]
    s_tr = np.mean(tr_ret[BURN_IN:]) / np.std(tr_ret[BURN_IN:]) * np.sqrt(252) if np.std(tr_ret[BURN_IN:]) > 1e-12 else 0
    oos_ret = net_ret[oos_mask]
    s_oos = np.mean(oos_ret) / np.std(oos_ret) * np.sqrt(252) if np.std(oos_ret) > 1e-12 else 0
    nt = int((np.abs(pos) > 1e-5).sum())
    wr = (net_ret[np.abs(pos) > 1e-5] > 0).mean() * 100 if nt > 0 else 0
    
    # Per-year
    yr_df = pd.DataFrame({"ret": net_ret, "date": dates})
    yr_df["year"] = yr_df["date"].dt.year
    yearly = {}
    for y in range(2019, 2027):
        grp = yr_df[yr_df["year"] == y]["ret"]
        if len(grp) >= 20:
            yearly[y] = grp.mean() / grp.std() * np.sqrt(252) if grp.std() > 1e-12 else 0
    
    return {"label": label, "full": s_full, "train": s_tr, "oos": s_oos, 
            "trades": nt, "wr": wr, "yearly": yearly, "net_ret": net_ret}


def print_result(r):
    yr_str = " ".join(f"{y}:{v:+.1f}" for y, v in sorted(r["yearly"].items()))
    print(f"  {r['label']:<40} Full={r['full']:.3f} Train={r['train']:.3f} OOS={r['oos']:.3f} N={r['trades']:>5} WR={r['wr']:.1f}% | {yr_str}")


# ═══════════════════════════════════════════════════════════
# Q1: Granular feature count sweet spot
# ═══════════════════════════════════════════════════════════
def research_q1(etf, pool_sorted, df, full_trade_ret, dates):
    print(f"\n{'═'*90}")
    print(f"Q1: Feature Count Sweet Spot — {etf}")
    print(f"{'═'*90}")
    
    counts = sorted(set([3, 4, 5, 6, 7, 8, 9, 10, 12, 15, 20, 25, len(pool_sorted)]))
    counts = [c for c in counts if c <= len(pool_sorted)]
    
    for n in counts:
        sub = pool_sorted[:n]
        X_raw, signs, _ = build_pool_feature_matrix(df, sub)
        Z_std = expanding_zscore_numba(X_raw, burn_in=BURN_IN, clip=3.0)
        Z_comp = np.mean(Z_std * signs, axis=1)
        r = eval_composite(Z_comp, full_trade_ret, dates, f"EW top-{n} by IC")
        print_result(r)


# ═══════════════════════════════════════════════════════════
# Q2: Low-correlation features vs high-correlation
# ═══════════════════════════════════════════════════════════
def research_q2(etf, pool, df, full_trade_ret, dates):
    print(f"\n{'═'*90}")
    print(f"Q2: Low-Corr vs High-Corr Features — {etf}")
    print(f"{'═'*90}")
    
    X_raw, signs, feat_names = build_pool_feature_matrix(df, pool)
    Z_std = expanding_zscore_numba(X_raw, burn_in=BURN_IN, clip=3.0)
    Z_signed = Z_std * signs
    
    # Compute mean absolute correlation for each feature
    corr_mat = np.corrcoef(Z_signed.T)
    np.fill_diagonal(corr_mat, 0)
    mean_abs_corr = np.mean(np.abs(corr_mat), axis=1)
    
    # Sort by correlation: low-corr first (diverse) vs high-corr first (redundant)
    low_corr_idx = np.argsort(mean_abs_corr)  # most independent first
    high_corr_idx = np.argsort(-mean_abs_corr)  # most correlated first
    
    print(f"  Mean |r| range: {mean_abs_corr.min():.3f} (most independent) to {mean_abs_corr.max():.3f} (most redundant)")
    
    for n in [5, 10, min(15, len(pool))]:
        # Low-corr subset
        sub_low = [pool[i] for i in low_corr_idx[:n]]
        X_low, s_low, _ = build_pool_feature_matrix(df, sub_low)
        Z_low = expanding_zscore_numba(X_low, burn_in=BURN_IN, clip=3.0)
        Z_comp_low = np.mean(Z_low * s_low, axis=1)
        r_low = eval_composite(Z_comp_low, full_trade_ret, dates, f"Low-corr top-{n} (diverse)")
        print_result(r_low)
        
        # High-corr subset
        sub_high = [pool[i] for i in high_corr_idx[:n]]
        X_high, s_high, _ = build_pool_feature_matrix(df, sub_high)
        Z_high = expanding_zscore_numba(X_high, burn_in=BURN_IN, clip=3.0)
        Z_comp_high = np.mean(Z_high * s_high, axis=1)
        r_high = eval_composite(Z_comp_high, full_trade_ret, dates, f"High-corr top-{n} (redundant)")
        print_result(r_high)
        
        # IC-sorted top-n for comparison
        pool_by_ic = sorted(pool, key=lambda p: -abs(p["deflated_ic"]))[:n]
        X_ic, s_ic, _ = build_pool_feature_matrix(df, pool_by_ic)
        Z_ic = expanding_zscore_numba(X_ic, burn_in=BURN_IN, clip=3.0)
        Z_comp_ic = np.mean(Z_ic * s_ic, axis=1)
        r_ic = eval_composite(Z_comp_ic, full_trade_ret, dates, f"IC-sorted top-{n} (baseline)")
        print_result(r_ic)
        print()


# ═══════════════════════════════════════════════════════════
# Q3: Regime-adaptive top-K
# ═══════════════════════════════════════════════════════════
def research_q3(etf, pool, df, full_trade_ret, dates):
    print(f"\n{'═'*90}")
    print(f"Q3: Regime-Adaptive Feature Selection — {etf}")
    print(f"{'═'*90}")
    print(f"  Idea: Use expanding IC to pick top-K features per period (adaptive)")
    print(f"  vs fixed top-K. Tests whether feature ranking is stable or regime-dependent.")
    
    X_raw, signs, feat_names = build_pool_feature_matrix(df, pool)
    Z_std = expanding_zscore_numba(X_raw, burn_in=BURN_IN, clip=3.0)
    N = len(pool)
    T = len(df)
    
    # Compute expanding IC for each feature (zero-lookahead)
    # IC_t = corr(Z_signed_t-1, return_t) over trailing 252 days
    Z_signed = Z_std * signs
    returns = full_trade_ret
    
    # Rolling 252-day IC per feature
    window = 252
    rolling_ic = np.full((T, N), np.nan)
    for t in range(window + 1, T):
        for j in range(N):
            z_slice = Z_signed[t-window:t, j]
            r_slice = returns[t-window:t]
            valid = ~(np.isnan(z_slice) | np.isnan(r_slice))
            if valid.sum() > 50:
                rolling_ic[t, j] = np.corrcoef(z_slice[valid], r_slice[valid])[0, 1]
    
    # Adaptive: each day, pick top-K features by trailing IC
    for K in [5, 10]:
        Z_adaptive = np.zeros(T, dtype=np.float64)
        for t in range(BURN_IN, T):
            ic_row = rolling_ic[t]
            valid_feats = np.where(~np.isnan(ic_row))[0]
            if len(valid_feats) < K:
                # Fallback: use all available
                Z_adaptive[t] = np.mean(Z_signed[t, valid_feats]) if len(valid_feats) > 0 else 0
            else:
                top_k = valid_feats[np.argsort(-np.abs(ic_row[valid_feats]))[:K]]
                Z_adaptive[t] = np.mean(Z_signed[t, top_k])
        
        r_adapt = eval_composite(Z_adaptive, full_trade_ret, dates, f"Adaptive top-{K} by rolling IC")
        print_result(r_adapt)
    
    # Fixed top-K for comparison
    pool_by_ic = sorted(pool, key=lambda p: -abs(p["deflated_ic"]))
    for K in [5, 10]:
        sub = pool_by_ic[:K]
        X_sub, s_sub, _ = build_pool_feature_matrix(df, sub)
        Z_sub = expanding_zscore_numba(X_sub, burn_in=BURN_IN, clip=3.0)
        Z_fixed = np.mean(Z_sub * s_sub, axis=1)
        r_fixed = eval_composite(Z_fixed, full_trade_ret, dates, f"Fixed top-{K} by IC (baseline)")
        print_result(r_fixed)
    
    # All features
    Z_all = np.mean(Z_signed, axis=1)
    r_all = eval_composite(Z_all, full_trade_ret, dates, f"All {N} features EW")
    print_result(r_all)
    
    # Feature ranking stability: how often does top-5 change?
    print(f"\n  Feature ranking stability (top-5 overlap between consecutive years):")
    for y in range(2016, 2026):
        yr_mask = dates.dt.year == y
        yr_indices = np.where(yr_mask.values)[0]
        if len(yr_indices) < 50:
            continue
        # Average IC within this year
        yr_ic = np.nanmean(rolling_ic[yr_indices], axis=0)
        valid = ~np.isnan(yr_ic)
        if valid.sum() < 5:
            continue
        top5 = set(np.where(valid)[0][np.argsort(-np.abs(yr_ic[valid]))[:5]])
        
        # Compare with previous year
        prev_mask = dates.dt.year == (y - 1)
        prev_indices = np.where(prev_mask.values)[0]
        if len(prev_indices) < 50:
            continue
        prev_ic = np.nanmean(rolling_ic[prev_indices], axis=0)
        prev_valid = ~np.isnan(prev_ic)
        if prev_valid.sum() < 5:
            continue
        prev_top5 = set(np.where(prev_valid)[0][np.argsort(-np.abs(prev_ic[prev_valid]))[:5]])
        
        overlap = len(top5 & prev_top5)
        print(f"    {y-1}→{y}: {overlap}/5 overlap")


# ═══════════════════════════════════════════════════════════
# Q4: IC-weighted vs EW on full pool
# ═══════════════════════════════════════════════════════════
def research_q4(etf, pool, df, full_trade_ret, dates):
    print(f"\n{'═'*90}")
    print(f"Q4: IC-Weighted vs EW (does smart weighting fix dilution?) — {etf}")
    print(f"{'═'*90}")
    
    X_raw, signs, feat_names = build_pool_feature_matrix(df, pool)
    Z_std = expanding_zscore_numba(X_raw, burn_in=BURN_IN, clip=3.0)
    N = len(pool)
    
    # EW baseline
    Z_ew = np.mean(Z_std * signs, axis=1)
    r_ew = eval_composite(Z_ew, full_trade_ret, dates, f"EW all-{N}")
    print_result(r_ew)
    
    # Static IC-weighted (pool metadata)
    ics = np.array([abs(p.get("deflated_ic", 0.01)) for p in pool])
    w_ic = ics / ics.sum()
    Z_icw = (Z_std * signs) @ w_ic
    r_icw = eval_composite(Z_icw, full_trade_ret, dates, f"IC-weighted all-{N}")
    print_result(r_icw)
    
    # Sqrt-IC weighted (less concentrated)
    w_sqrt = np.sqrt(ics)
    w_sqrt /= w_sqrt.sum()
    Z_sqrt = (Z_std * signs) @ w_sqrt
    r_sqrt = eval_composite(Z_sqrt, full_trade_ret, dates, f"Sqrt-IC weighted all-{N}")
    print_result(r_sqrt)
    
    # Inverse-corr weighted (down-weight redundant features)
    corr_mat = np.corrcoef((Z_std * signs).T)
    np.fill_diagonal(corr_mat, 0)
    mean_corr = np.mean(np.abs(corr_mat), axis=1)
    w_inv = 1.0 / (1.0 + mean_corr * 5)  # penalize high-corr features
    w_inv /= w_inv.sum()
    Z_inv = (Z_std * signs) @ w_inv
    r_inv = eval_composite(Z_inv, full_trade_ret, dates, f"Inv-corr weighted all-{N}")
    print_result(r_inv)
    
    # IC × Inv-corr combined
    w_combo = ics * w_inv
    w_combo /= w_combo.sum()
    Z_combo = (Z_std * signs) @ w_combo
    r_combo = eval_composite(Z_combo, full_trade_ret, dates, f"IC×InvCorr weighted all-{N}")
    print_result(r_combo)


def main():
    ETFS = ["500ETF", "159915ETF", "300ETF"]
    
    for etf in ETFS:
        pool = load_admitted_pool(etf, side="single", min_features=10)
        if not pool or len(pool) < 10:
            continue
        pool_sorted = sorted(pool, key=lambda p: -abs(p["deflated_ic"]))
        df = load_etf_dataset(etf)
        full_trade_ret = df["trade_return"].values.astype(np.float64) if "trade_return" in df.columns else df["close"].pct_change().fillna(0).values
        dates = df["date"]
        
        research_q1(etf, pool_sorted, df, full_trade_ret, dates)
        research_q2(etf, pool, df, full_trade_ret, dates)
        research_q3(etf, pool, df, full_trade_ret, dates)
        research_q4(etf, pool, df, full_trade_ret, dates)


if __name__ == "__main__":
    main()
