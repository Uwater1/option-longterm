"""
Lunch Break Change-Point Analysis
==================================
Tests whether a structural break exists at the A-share lunch boundary
(bar 24: 11:30 / 13:00) and whether AM and PM sessions behave differently.

Analyses:
1. Chow test (F-test) at bar 24 for mean + variance shift
2. CUSUM on the average intraday return curve
3. Rolling statistics (mean, vol) across bars with visual break detection
4. AM vs PM regime comparison: separate clustering per session
5. Per-ETF summary JSON

Outputs: plots/lunch_*.png, data/lunch_break_results.json
"""
import pandas as pd
import numpy as np
from pathlib import Path
import json
import warnings
warnings.filterwarnings('ignore')

from scipy import stats
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import adjusted_mutual_info_score

import matplotlib.pyplot as plt
import seaborn as sns

ETF_NAMES = ['300ETF', '50ETF', '500ETF', '588000ETF', '159915ETF']

OUTPUT_DIR = Path(__file__).resolve().parent
DATA_DIR = OUTPUT_DIR / 'data'
PLOTS_DIR = OUTPUT_DIR / 'plots'

BAR_LUNCH = 24  # index of first PM bar (13:00)


# ============================================================
# Statistical Tests
# ============================================================
def chow_test_at_lunch(return_curves):
    """Chow F-test: does mean return differ between AM (bars 0-23) and PM (bars 24-47)?

    Uses per-day mean AM return vs per-day mean PM return.
    Returns F-statistic, p-value, and mean difference.
    """
    am_means = return_curves[:, :BAR_LUNCH].mean(axis=1)
    pm_means = return_curves[:, BAR_LUNCH:].mean(axis=1)

    # Two-sample t-test (Welch) as a Chow proxy
    t_stat, p_val = stats.ttest_ind(am_means, pm_means, equal_var=False)
    # F = t^2 for two-sample case
    f_stat = t_stat ** 2
    mean_diff = am_means.mean() - pm_means.mean()
    return float(f_stat), float(p_val), float(mean_diff)


def variance_shift_test(return_curves):
    """Levene test: does return variance differ between AM and PM?"""
    am_vars = return_curves[:, :BAR_LUNCH].var(axis=1)
    pm_vars = return_curves[:, BAR_LUNCH:].var(axis=1)
    stat, p_val = stats.levene(am_vars, pm_vars)
    return float(stat), float(p_val)


def cusum_on_avg_curve(price_curves):
    """CUSUM change-point detection on the cross-day average price curve.

    Returns: detected change-point index (or None), CUSUM statistic at that point.
    """
    avg_curve = price_curves.mean(axis=0)  # shape (48,)
    n = len(avg_curve)
    overall_mean = avg_curve.mean()

    # CUSUM: cumulative sum of deviations from mean
    cusum = np.cumsum(avg_curve - overall_mean)
    # Max absolute deviation = change-point
    cp_idx = int(np.argmax(np.abs(cusum)))
    cp_stat = float(np.abs(cusum[cp_idx]))

    # Bootstrap significance: shuffle days and recompute
    n_boot = 200
    boot_stats = []
    for _ in range(n_boot):
        rng = np.random.RandomState(_)
        shuffled = rng.permutation(price_curves, axis=0)
        avg_shuf = shuffled.mean(axis=0)
        cusum_shuf = np.cumsum(avg_shuf - avg_shuf.mean())
        boot_stats.append(float(np.abs(cusum_shuf).max()))

    p_val = float((np.array(boot_stats) >= cp_stat).mean())
    return cp_idx, cp_stat, p_val, cusum


# ============================================================
# AM vs PM Regime Comparison
# ============================================================
def am_pm_clustering(price_curves, n_clusters=4):
    """Cluster AM bars and PM bars separately, compare labels.

    Returns AMI between AM-only and PM-only cluster assignments.
    """
    am_curves = price_curves[:, :BAR_LUNCH]   # (N, 24)
    pm_curves = price_curves[:, BAR_LUNCH:]   # (N, 24)

    def _cluster(curves):
        pca = PCA(n_components=min(6, curves.shape[1]))
        X = pca.fit_transform(curves)
        km = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        return km.fit_predict(X)

    am_labels = _cluster(am_curves)
    pm_labels = _cluster(pm_curves)
    ami = adjusted_mutual_info_score(am_labels, pm_labels)
    return am_labels, pm_labels, float(ami)


# ============================================================
# Per-ETF Analysis
# ============================================================
def analyze_etf(etf_name):
    print(f"\n{'='*60}")
    print(f"Lunch Break Analysis: {etf_name}")
    print('='*60)

    paths_npz = np.load(DATA_DIR / f'paths_{etf_name}.npz', allow_pickle=True)
    price_curves = paths_npz['price']
    return_curves = paths_npz['returns']
    n_days = len(price_curves)
    print(f"  {n_days} trading days, {price_curves.shape[1]} bars/day")

    results = {'etf': etf_name, 'n_days': n_days}

    # 1) Chow test (mean shift at bar 24)
    f_stat, p_val, mean_diff = chow_test_at_lunch(return_curves)
    results['chow_F'] = f_stat
    results['chow_p'] = p_val
    results['chow_mean_diff'] = mean_diff
    print(f"  Chow test: F={f_stat:.3f}, p={p_val:.4f}, mean_diff={mean_diff:.6f}")

    # 2) Variance shift (Levene)
    lev_stat, lev_p = variance_shift_test(return_curves)
    results['levene_stat'] = lev_stat
    results['levene_p'] = lev_p
    print(f"  Levene (variance shift): stat={lev_stat:.3f}, p={lev_p:.4f}")

    # 3) CUSUM change-point
    cp_idx, cp_stat, cp_p, cusum_arr = cusum_on_avg_curve(price_curves)
    results['cusum_cp_idx'] = cp_idx
    results['cusum_cp_stat'] = cp_stat
    results['cusum_p'] = cp_p
    near_lunch = abs(cp_idx - BAR_LUNCH) <= 3
    results['cusum_near_lunch'] = near_lunch
    print(f"  CUSUM change-point: bar {cp_idx} (stat={cp_stat:.3f}, p={cp_p:.4f}, near_lunch={near_lunch})")

    # 4) AM vs PM clustering AMI
    am_labels, pm_labels, ami = am_pm_clustering(price_curves, n_clusters=4)
    results['am_pm_AMI'] = ami
    print(f"  AM/PM clustering AMI: {ami:.4f} (0=independent, 1=identical)")

    # ---- Plots ----
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # (a) Average price curve with CUSUM
    ax = axes[0, 0]
    avg_curve = price_curves.mean(axis=0)
    bars = np.arange(len(avg_curve))
    ax.plot(bars, avg_curve, 'b-', linewidth=2, label='Avg price curve')
    ax.axvline(BAR_LUNCH, color='red', linestyle='--', alpha=0.7, label='Lunch (bar 24)')
    if near_lunch:
        ax.axvline(cp_idx, color='green', linestyle=':', linewidth=2, label=f'CUSUM CP (bar {cp_idx})')
    ax.fill_betweenx([avg_curve.min(), avg_curve.max()], BAR_LUNCH - 1, BAR_LUNCH + 1,
                     color='yellow', alpha=0.2)
    ax.set_xlabel('Bar Index')
    ax.set_ylabel('Normalized Price')
    ax.set_title(f'{etf_name}: Average Intraday Price Curve')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # (b) CUSUM statistic
    ax = axes[0, 1]
    ax.plot(bars, cusum_arr, 'purple', linewidth=1.5)
    ax.axvline(BAR_LUNCH, color='red', linestyle='--', alpha=0.7)
    ax.axvline(cp_idx, color='green', linestyle=':', linewidth=2, label=f'CP at bar {cp_idx}')
    ax.fill_betweenx([cusum_arr.min(), cusum_arr.max()], BAR_LUNCH - 1, BAR_LUNCH + 1,
                     color='yellow', alpha=0.2)
    ax.set_xlabel('Bar Index')
    ax.set_ylabel('CUSUM')
    ax.set_title(f'{etf_name}: CUSUM Change-Point (p={cp_p:.3f})')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # (c) Rolling mean return per bar (cross-day average)
    ax = axes[1, 0]
    bar_mean_return = return_curves.mean(axis=0)  # avg log return per bar
    bar_std_return = return_curves.std(axis=0)
    ax.bar(bars, bar_mean_return * 10000, color='steelblue', alpha=0.7, label='Mean return (bps)')
    ax.axvline(BAR_LUNCH, color='red', linestyle='--', alpha=0.7)
    ax.set_xlabel('Bar Index')
    ax.set_ylabel('Mean Return (bps)')
    ax.set_title(f'{etf_name}: Per-Bar Mean Return')
    ax.axhline(0, color='black', linewidth=0.5)
    ax.grid(True, alpha=0.3)

    # (d) AM vs PM return distribution
    ax = axes[1, 1]
    am_ret = return_curves[:, :BAR_LUNCH].sum(axis=1) * 100
    pm_ret = return_curves[:, BAR_LUNCH:].sum(axis=1) * 100
    ax.hist(am_ret, bins=60, alpha=0.5, color='orange', label=f'AM return (mean={am_ret.mean():.3f}%)')
    ax.hist(pm_ret, bins=60, alpha=0.5, color='blue', label=f'PM return (mean={pm_ret.mean():.3f}%)')
    ax.set_xlabel('Session Return (%)')
    ax.set_title(f'{etf_name}: AM vs PM Return Distribution')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    plt.suptitle(f'Lunch Break Analysis — {etf_name}', fontsize=13, fontweight='bold')
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / f'lunch_analysis_{etf_name}.png', dpi=120)
    plt.close()

    return results


# ============================================================
# Cross-ETF Summary
# ============================================================
def summary_plot(all_results):
    """Summary bar chart across all ETFs."""
    etfs = [r['etf'] for r in all_results]
    chow_p = [r['chow_p'] for r in all_results]
    cusum_p = [r['cusum_p'] for r in all_results]
    ami_vals = [r['am_pm_AMI'] for r in all_results]
    near_lunch = [r['cusum_near_lunch'] for r in all_results]

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    # Chow test p-values
    ax = axes[0]
    colors = ['green' if p < 0.05 else 'gray' for p in chow_p]
    ax.bar(etfs, chow_p, color=colors)
    ax.axhline(0.05, color='red', linestyle='--', label='p=0.05')
    ax.set_ylabel('p-value')
    ax.set_title('Chow Test (mean shift at lunch)')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # CUSUM p-values
    ax = axes[1]
    colors = ['green' if p < 0.05 else 'gray' for p in cusum_p]
    ax.bar(etfs, cusum_p, color=colors)
    ax.axhline(0.05, color='red', linestyle='--', label='p=0.05')
    ax.set_ylabel('p-value')
    ax.set_title('CUSUM (change-point near lunch?)')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # AM/PM AMI
    ax = axes[2]
    colors = ['orange' if a < 0.3 else 'blue' for a in ami_vals]
    ax.bar(etfs, ami_vals, color=colors)
    ax.set_ylabel('AMI score')
    ax.set_title('AM vs PM Cluster Agreement\n(0=independent, 1=identical)')
    ax.grid(True, alpha=0.3)

    plt.suptitle('Lunch Break Effects — Cross-ETF Summary', fontsize=13, fontweight='bold')
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / 'lunch_summary.png', dpi=120)
    plt.close()


# ============================================================
# Main
# ============================================================
def main():
    PLOTS_DIR.mkdir(exist_ok=True)

    print("Lunch Break Change-Point Analysis")
    print("=" * 60)

    all_results = []
    for etf_name in ETF_NAMES:
        try:
            results = analyze_etf(etf_name)
            all_results.append(results)
        except Exception as e:
            print(f"  [ERROR] {etf_name}: {e}")
            import traceback
            traceback.print_exc()

    # Summary plot
    if all_results:
        summary_plot(all_results)

    # Save JSON
    out_path = DATA_DIR / 'lunch_break_results.json'
    with open(out_path, 'w') as f:
        json.dump(all_results, f, indent=2)
    print(f"\nSaved: {out_path}")

    # Print summary table
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"{'ETF':<12} {'Chow p':<10} {'CUSUM p':<10} {'CP near lunch':<16} {'AM/PM AMI':<10}")
    for r in all_results:
        chow_sig = "***" if r['chow_p'] < 0.001 else ("**" if r['chow_p'] < 0.01 else ("*" if r['chow_p'] < 0.05 else "ns"))
        print(f"{r['etf']:<12} {r['chow_p']:.4f}{chow_sig:<5} {r['cusum_p']:.4f}   "
              f"{'YES' if r['cusum_near_lunch'] else 'NO':<16} {r['am_pm_AMI']:.4f}")

    print("\nLunch break analysis complete!")


if __name__ == '__main__':
    main()
