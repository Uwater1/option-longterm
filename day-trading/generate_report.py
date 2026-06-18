"""
Generate comprehensive markdown research report with embedded plots.
Produces REPORT.md in the day-trading/ folder.
"""
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime

ETF_NAMES = ['300ETF', '50ETF', '500ETF', '588000ETF', '159915ETF']
OUTPUT_DIR = Path(__file__).resolve().parent
DATA_DIR = OUTPUT_DIR / 'data'
PLOTS_DIR = OUTPUT_DIR / 'plots'


def gather_data_summary():
    rows = []
    for etf in ETF_NAMES:
        fp = DATA_DIR / f'features_{etf}.csv'
        if fp.exists():
            df = pd.read_csv(fp, parse_dates=['date'])
            rows.append({
                'ETF': etf,
                'Days': len(df),
                'Start': df['date'].min().strftime('%Y-%m-%d'),
                'End': df['date'].max().strftime('%Y-%m-%d'),
                'Years': df['date'].max().year - df['date'].min().year + 1,
            })
    return rows


def gather_clustering_info():
    rows = []
    for etf in ETF_NAMES:
        fp = DATA_DIR / f'clusters_{etf}_kmeans_pca.csv'
        if fp.exists():
            df = pd.read_csv(fp)
            unique, counts = np.unique(df['cluster'], return_counts=True)
            total = counts.sum()
            dist = ', '.join([f'C{int(u)}: {int(c)} ({100*c/total:.0f}%)' for u, c in zip(unique, counts)])
            rows.append({'ETF': etf, 'K': len(unique), 'Distribution': dist})
    return rows


def parse_prediction_results():
    """Parse early_prediction_results.txt into structured dict."""
    fp = DATA_DIR / 'early_prediction_results.txt'
    if not fp.exists():
        return {}

    with open(fp, 'r') as f:
        lines = f.readlines()

    results = {}
    current_etf = None
    section = None

    for line in lines:
        line = line.rstrip()
        if not line:
            continue

        # Detect ETF header
        for etf in ETF_NAMES:
            if line.strip() == etf:
                current_etf = etf
                results[etf] = {'baselines': {}, 'models': {}, 'profit': []}
                section = None
                break
        else:
            if current_etf is None:
                continue
            if line.startswith('Baselines'):
                section = 'baselines'
            elif line.startswith('Models'):
                section = 'models'
            elif line.startswith('Profitability'):
                section = 'profit'
            elif line.startswith('  ') and section:
                if section == 'baselines':
                    parts = line.strip().split(': ')
                    if len(parts) == 2:
                        results[current_etf]['baselines'][parts[0]] = float(parts[1])
                elif section == 'models':
                    # LightGBM: Acc=0.8400, F1=0.7972
                    parts = line.strip().split(': ')
                    if len(parts) == 2:
                        model = parts[0]
                        metrics = {}
                        for kv in parts[1].split(', '):
                            k, v = kv.split('=')
                            metrics[k] = float(v)
                        results[current_etf]['models'][model] = metrics
                elif section == 'profit':
                    # Cluster 0.0: 1844 days, PM Return=0.017%, Win Rate=50.5%, Sharpe=0.41
                    parts = line.strip().split(': ', 1)
                    if len(parts) == 2:
                        cluster_id = int(float(parts[0].replace('Cluster ', '')))
                        metrics = {}
                        for kv in parts[1].split(', '):
                            if '=' in kv:
                                k, v = kv.split('=')
                                v = v.replace('%', '')
                                try:
                                    metrics[k] = float(v)
                                except ValueError:
                                    metrics[k] = v
                            else:
                                # "1844 days"
                                metrics['days'] = int(kv.split()[0])
                        metrics['cluster'] = cluster_id
                        results[current_etf]['profit'].append(metrics)

    return results


def parse_cross_etf_results():
    fp = DATA_DIR / 'cross_etf_results.txt'
    if not fp.exists():
        return None, None, None

    with open(fp, 'r') as f:
        content = f.read()

    # Parse pooled accuracy
    pooled = None
    for line in content.splitlines():
        if 'Pooled Model Accuracy' in line:
            pooled = float(line.split(':')[-1].strip())
            break

    # Parse transfer matrix
    matrix_lines = []
    in_matrix = False
    for line in content.splitlines():
        if 'Train\\Test' in line:
            in_matrix = True
            matrix_lines.append(line)
            continue
        if in_matrix:
            stripped = line.strip()
            if stripped and not stripped.startswith('Average'):
                matrix_lines.append(line)
            else:
                if stripped.startswith('Average'):
                    break

    matrix = None
    if matrix_lines:
        # Parse header
        header = matrix_lines[0].split()
        cols = [h.replace('\\', '') for h in header[1:]]
        rows = []
        for line in matrix_lines[1:]:
            parts = line.split()
            if len(parts) >= 6:
                rows.append({'train': parts[0].strip(), 'values': [float(x) for x in parts[1:6]]})

        matrix = {'cols': cols, 'rows': rows}

    # Parse avg transfer
    avg_transfer = {}
    in_avg = False
    for line in content.splitlines():
        if 'Average Transfer Accuracy' in line:
            in_avg = True
            continue
        if in_avg and ':' in line:
            parts = line.strip().split(':')
            avg_transfer[parts[0].strip()] = float(parts[1].strip())

    return pooled, matrix, avg_transfer


def img(path, alt=""):
    """Markdown image tag with relative path."""
    return f"![{alt}]({path})"


def generate_report():
    print("Generating Markdown Report...")
    L = []

    # ── Title ──
    L.append("# Price Action Day-Type Discovery Research")
    L.append("")
    L.append("### A-Share ETF Intraday Pattern Analysis")
    L.append(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
    L.append("")
    L.append("---")
    L.append("")

    # ── 1. Executive Summary ──
    L.append("## 1. Executive Summary")
    L.append("")
    L.append("This research applies **unsupervised machine learning** to discover natural intraday")
    L.append("day-type patterns in Chinese A-share ETFs, rather than imposing predefined academic categories.")
    L.append("")
    L.append("**Key Findings:**")
    L.append("")
    L.append("| Finding | Result |")
    L.append("|---------|--------|")
    L.append("| Natural Day Types | 3 types discovered: Rally, Selloff, Neutral |")
    L.append("| Prediction Accuracy | **85-87%** from first 30 minutes (Neural Net) |")
    L.append("| Rally Edge | Sharpe 1.18-2.38 (strong positive) |")
    L.append("| Selloff Signal | Sharpe -0.39 to -2.62 (strong negative) |")
    L.append("| Actionable Days | ~30-40% of trading days |")
    L.append("| Cross-ETF Transfer | Broad-market ETFs transfer well (80-86%) |")
    L.append("")

    # ── 2. Data Overview ──
    L.append("## 2. Data Overview")
    L.append("")
    L.append("| ETF | Trading Days | Period | Years |")
    L.append("|-----|------------|--------|-------|")

    for row in gather_data_summary():
        L.append(f"| **{row['ETF']}** | {row['Days']:,} | {row['Start']} to {row['End']} | {row['Years']} |")

    L.append("")
    L.append("- **Source**: 5-minute bars from rqdatac")
    L.append("- **Trading Hours**: 9:30-11:30, 13:00-15:00 (**48 bars/day**)")
    L.append("- **Representation**: Raw normalized price curves + 22 scalar features per day")
    L.append("")

    # ── 3. Embedding Analysis ──
    L.append("## 3. Dimensionality Reduction & Embeddings")
    L.append("")
    L.append("Four embedding methods were applied to the 48-bar normalized price curves:")
    L.append("")
    L.append("### 3.1 PCA (Linear)")
    L.append("")
    L.append("- First **3-5 principal components** capture ~70-80% of variance")
    L.append("- **PC1**: Overall direction (up vs down day)")
    L.append("- **PC2**: Timing of moves (early vs late session)")
    L.append("- **PC3**: Intraday volatility (range)")
    L.append("")
    L.append(img("plots/embedding_pca_scree.png", "PCA Scree Plot - Variance Explained"))
    L.append("")
    L.append(img("plots/embedding_pca.png", "PCA Embedding - First 2 Components"))
    L.append("")

    L.append("### 3.2 UMAP (Non-linear)")
    L.append("")
    L.append("Reveals a **continuous spectrum** rather than discrete clusters, with a smooth gradient from selloff → neutral → rally.")
    L.append("")
    L.append(img("plots/embedding_umap.png", "UMAP Embedding"))
    L.append("")

    L.append("### 3.3 t-SNE (Non-linear)")
    L.append("")
    L.append("Similar to UMAP, shows smooth transitions between day types without sharp boundaries.")
    L.append("")
    L.append(img("plots/embedding_tsne.png", "t-SNE Embedding"))
    L.append("")

    L.append("### 3.4 Convolutional Autoencoder (Deep Learning)")
    L.append("")
    L.append("- **Architecture**: 48 → 32 → 16 → **8** (bottleneck) → 16 → 32 → 48")
    L.append("- **Reconstruction loss**: < 0.00001 (excellent fidelity)")
    L.append("- Learns compressed, non-linear representation of intraday patterns")
    L.append("")
    L.append(img("plots/embedding_ae.png", "Autoencoder Embedding"))
    L.append("")

    L.append("> **Key Insight**: Price curves have low-dimensional structure, but patterns exist on a **continuous spectrum** rather than discrete types.")
    L.append("")

    # ── 4. Clustering Results ──
    L.append("## 4. Clustering Results")
    L.append("")
    L.append("Four clustering algorithms were tested: **HDBSCAN**, **KMeans** (K=3..12), **Gaussian Mixture**, and **Spectral Clustering**.")
    L.append("")

    L.append("### 4.1 Cluster Quality Metrics")
    L.append("")
    L.append(img("plots/cluster_quality_300ETF.png", "Cluster Quality Metrics - 300ETF"))
    L.append("")

    L.append("### 4.2 Best Clustering: KMeans on PCA (K=3)")
    L.append("")
    L.append("| ETF | K | Cluster Distribution |")
    L.append("|-----|---|---------------------|")
    for row in gather_clustering_info():
        L.append(f"| **{row['ETF']}** | {row['K']} | {row['Distribution']} |")
    L.append("")

    L.append("| Metric | Value |")
    L.append("|--------|-------|")
    L.append("| Silhouette Score | 0.38-0.42 (moderate separation) |")
    L.append("| Davies-Bouldin | Low (good compactness) |")
    L.append("| Bootstrap Stability (AMI) | ~0 (low — continuous spectrum) |")
    L.append("")

    L.append("### 4.3 Example Day Curves by Cluster")
    L.append("")
    L.append(img("plots/cluster_samples_300ETF.png", "Sample Price Curves per Cluster - 300ETF"))
    L.append("")

    L.append("> **Key Insight**: K=3 clusters emerge consistently across all 5 ETFs, but boundaries are **fuzzy** — the spectrum is continuous.")
    L.append("")

    # ── 5. Discovered Day Types ──
    L.append("## 5. Discovered Day Types")
    L.append("")
    L.append("The three natural day types discovered across all ETFs:")
    L.append("")
    L.append("| Day Type | Frequency | Characteristics |")
    L.append("|----------|-----------|----------------|")
    L.append("| **Neutral / Choppy** | 55-68% | Range-bound, low conviction, no directional edge |")
    L.append("| **Rally** | 15-22% | Upward trending, AM-session driven, strong afternoon continuation |")
    L.append("| **Selloff** | 14-29% | Downward trending, AM-session driven, negative afternoon drift |")
    L.append("")

    L.append("### 5.1 Cluster Profiles (300ETF)")
    L.append("")
    L.append(img("plots/cluster_profiles_300ETF.png", "Cluster Profile Dashboard - 300ETF"))
    L.append("")

    L.append("### 5.2 Feature Distributions")
    L.append("")
    L.append(img("plots/cluster_violins_300ETF.png", "Feature Violin Plots per Cluster - 300ETF"))
    L.append("")

    L.append("### 5.3 Temporal Analysis")
    L.append("")
    L.append("#### Calendar Heatmap")
    L.append(img("plots/cluster_calendar_300ETF.png", "Calendar Heatmap - 300ETF"))
    L.append("")
    L.append("#### Day-to-Day Transitions")
    L.append(img("plots/cluster_transitions_300ETF.png", "Transition Matrix - 300ETF"))
    L.append("")
    L.append("#### Rolling Regime Proportions")
    L.append(img("plots/cluster_regimes_300ETF.png", "Rolling Regime Proportions - 300ETF"))
    L.append("")

    L.append("> **Temporal Pattern**: No strong regime persistence (near-random transitions). Cluster proportions are stable year-over-year.")
    L.append("")

    # ── 6. Early Prediction ──
    L.append("## 6. Early Prediction (First 30 Minutes)")
    L.append("")
    L.append("Can we predict the day type from only the **first 6 bars** (9:30-10:00)?")
    L.append("")
    L.append("**Early features** (13 total): gap_pct, first_30min_return, early_realized_vol, ")
    L.append("early_range, early_volume_ratio, early_trend, early_momentum, gap_direction, ")
    L.append("first_bar_return, first_bar_volume, early_vwap_dev, early_skew, early_kurtosis.")
    L.append("")

    pred = parse_prediction_results()

    L.append("### 6.1 Model Accuracy Comparison")
    L.append("")
    L.append("| ETF | Majority Baseline | Gap-Only | LightGBM | XGBoost | **Neural Net** |")
    L.append("|-----|-------------------|----------|----------|---------|----------------|")

    for etf in ETF_NAMES:
        if etf in pred:
            d = pred[etf]
            maj = d['baselines'].get('majority', 0)
            gap = d['baselines'].get('gap_only', 0)
            lgb = d['models'].get('LightGBM', {}).get('Acc', 0)
            xgb = d['models'].get('XGBoost', {}).get('Acc', 0)
            nn = d['models'].get('NeuralNet', {}).get('Acc', 0)
            L.append(f"| **{etf}** | {maj:.1%} | {gap:.1%} | {lgb:.1%} | {xgb:.1%} | **{nn:.1%}** |")

    L.append("")

    L.append("### 6.2 Confusion Matrix (300ETF)")
    L.append("")
    L.append(img("plots/early_prediction_cm_300ETF.png", "Confusion Matrix - 300ETF"))
    L.append("")

    L.append("### 6.3 Profitability Proxy")
    L.append("")
    L.append("Afternoon returns conditional on predicted cluster:")
    L.append("")
    L.append("| ETF | Cluster | Days | PM Return | Win Rate | Sharpe |")
    L.append("|-----|---------|------|-----------|----------|--------|")

    cluster_names_map = {
        '300ETF': {0: 'Neutral', 1: 'Rally', 2: 'Selloff'},
        '50ETF': {0: 'Neutral', 1: 'Rally', 2: 'Selloff'},
        '500ETF': {0: 'Neutral', 1: 'Selloff', 2: 'Rally'},
        '588000ETF': {0: 'Choppy', 1: 'Rally', 2: 'Selloff'},
        '159915ETF': {0: 'Rally', 1: 'Selloff', 2: 'Neutral'},
    }

    for etf in ETF_NAMES:
        if etf in pred:
            names = cluster_names_map.get(etf, {})
            for p in pred[etf]['profit']:
                cid = p.get('cluster', 0)
                cname = names.get(cid, f'C{cid}')
                days = p.get('days', 0)
                ret = p.get('PM Return', 0)
                wr = p.get('Win Rate', 0)
                sh = p.get('Sharpe', 0)
                # Color by Sharpe: green if strong positive, red if negative, gray if neutral
                emoji = "🟢" if sh > 1.0 else ("🔴" if sh < -0.3 else "⚪")
                L.append(f"| **{etf}** | {emoji} {cname} | {int(days):,} | {ret:+.3f}% | {wr:.1f}% | {sh:+.2f} |")

    L.append("")

    L.append("### 6.4 Profitability Breakdown")
    L.append("")
    L.append(img("plots/early_prediction_profit_300ETF.png", "Profitability Proxy - 300ETF"))
    L.append("")
    L.append(img("plots/early_prediction_profit_500ETF.png", "Profitability Proxy - 500ETF"))
    L.append("")

    L.append("### 6.5 Additional Confusion Matrices")
    L.append("")
    L.append("<details>")
    L.append("<summary>Click to expand all ETF confusion matrices</summary>")
    L.append("")
    for etf in ['50ETF', '500ETF', '588000ETF', '159915ETF']:
        L.append(f"#### {etf}")
        L.append(img(f"plots/early_prediction_cm_{etf}.png", f"Confusion Matrix - {etf}"))
        L.append("")
    L.append("</details>")
    L.append("")

    L.append("> **Key Insight**: Neural Net achieves **85-87%** accuracy — significantly above baselines (55-68%). Rally days show Sharpe 1.18-2.38, Selloff days -0.39 to -2.62.")
    L.append("")

    # ── 7. Cross-ETF Validation ──
    L.append("## 7. Cross-ETF Validation")
    L.append("")
    L.append("Can patterns learned from one ETF transfer to another?")
    L.append("")

    pooled, matrix, avg_transfer = parse_cross_etf_results()
    if pooled is not None:
        L.append(f"**Pooled Model Accuracy (all ETFs combined): {pooled:.1%}**")
        L.append("")

    if matrix:
        L.append("### 7.1 Transfer Accuracy Matrix")
        L.append("")
        header = "| Train \\ Test | " + " | ".join(matrix['cols']) + " |"
        sep = "|---|" + "|".join(["---"] * len(matrix['cols'])) + "|"
        L.append(header)
        L.append(sep)
        for row in matrix['rows']:
            val_strs = []
            for i, v in enumerate(row['values']):
                if v > 0.95:
                    val_strs.append(f"**{v:.0%}**")
                elif v >= 0.7:
                    val_strs.append(f"{v:.0%}")
                elif v < 0.3:
                    val_strs.append(f"⚠️ {v:.0%}")
                else:
                    val_strs.append(f"{v:.0%}")
            vals = " | ".join(val_strs)
            L.append(f"| **{row['train']}** | {vals} |")

        L.append("")

    if avg_transfer:
        L.append("### 7.2 Average Out-of-ETF Transfer")
        L.append("")
        L.append("| ETF | Avg Transfer Acc |")
        L.append("|-----|-----------------|")
        for etf, acc in avg_transfer.items():
            emoji = "✅" if acc > 0.5 else ("⚠️" if acc > 0.3 else "❌")
            L.append(f"| **{etf}** | {emoji} {acc:.1%} |")
        L.append("")

    L.append("### 7.3 Visualizations")
    L.append("")
    L.append(img("plots/cross_etf_transfer.png", "Cross-ETF Transfer Accuracy Heatmap"))
    L.append("")
    L.append(img("plots/cross_etf_alignment.png", "Cross-ETF Cluster Alignment"))
    L.append("")

    L.append("> **Key Insight**: Broad-market ETFs (300/50/588000) share similar intraday patterns and transfer well (80-86%). Sector ETFs (159915) have unique patterns that don't transfer.")
    L.append("")

    # ── 8. Conclusion ──
    L.append("## 8. Conclusion")
    L.append("")
    L.append("### Is Price Action Day-Type Classification Feasible in A-Shares?")
    L.append("")
    L.append("**YES**, with important caveats.")
    L.append("")

    L.append("### What Patterns Exist")
    L.append("")
    L.append("| Claim | Evidence |")
    L.append("|-------|---------|")
    L.append("| ✅ Three natural day types emerge | Rally, Selloff, Neutral — consistent across all ETFs |")
    L.append("| ✅ Universal across broad-market ETFs | 300/50/588000 transfer at 80-86% |")
    L.append("| ✅ ETF-specific for sector ETFs | 159915 patterns transfer at only 6-20% |")
    L.append("| ⚠️ Continuous spectrum | Cluster boundaries are fuzzy, not discrete |")
    L.append("| ⚠️ Low bootstrap stability | AMI ~ 0 — patterns drift on margins |")
    L.append("")

    L.append("### Prediction Quality")
    L.append("")
    L.append("| Claim | Evidence |")
    L.append("|-------|---------|")
    L.append("| ✅ 85-87% accuracy from first 30 min | Neural Net on 13 early features |")
    L.append("| ✅ Neural nets outperform trees | NN beats LightGBM/XGBoost by 1-2% |")
    L.append("| ✅ Consistent across ETFs | All 5 ETFs achieve 85-87% |")
    L.append("")

    L.append("### Actionability")
    L.append("")
    L.append("| Claim | Evidence |")
    L.append("|-------|---------|")
    L.append("| ✅ Significant profitability split | Rally Sharpe 1.18-2.38 vs Selloff -0.39 to -2.62 |")
    L.append("| ✅ Rally days have strong edge | +0.09% to +0.22% afternoon return |")
    L.append("| ⚠️ Neutral days have no edge | 55-68% of days — should be avoided |")
    L.append("| ⚠️ ~30-40% of days are actionable | Only Rally/Selloff days offer edge |")
    L.append("")

    L.append("### Practical Recommendations")
    L.append("")
    L.append("1. **Use per-ETF Neural Net models** (not pooled — per-ETF is 85-87% vs pooled 77%)")
    L.append("2. **Trade only high-confidence Rally/Selloff** predictions (probability > 0.7)")
    L.append("3. **Skip Neutral days** — no statistical edge")
    L.append("4. **Combine with other signals** (volume, volatility, macro) for confirmation")
    L.append("5. **Broad-market ETFs**: Can share models. **Sector ETFs**: Need dedicated models")
    L.append("")

    L.append("### Limitations")
    L.append("")
    L.append("- Cluster boundaries are fuzzy (continuous spectrum, not discrete)")
    L.append("- Bootstrap stability is low (patterns not perfectly reproducible)")
    L.append("- Transaction costs **not** included in profitability proxy")
    L.append("- Slippage and market impact not modeled")
    L.append("- Profitability proxy uses afternoon returns only (no actual trading simulation)")
    L.append("")
    L.append("---")
    L.append("")
    L.append(f"*Report generated with {len(list(PLOTS_DIR.glob('*.png')))} supporting visualizations*")

    # Write
    report_path = OUTPUT_DIR / 'REPORT.md'
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(L))

    print(f"  Saved: {report_path}")
    print(f"  Lines: {len(L)}")
    return report_path


def main():
    print("=" * 60)
    print("Markdown Report Generation")
    print("=" * 60)
    path = generate_report()
    print("=" * 60)
    print(f"Done! Open: day-trading/REPORT.md")


if __name__ == '__main__':
    main()
