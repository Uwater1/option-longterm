import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde
import shutil
import argparse

# Set matplotlib style for premium look
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.size'] = 10
plt.rcParams['axes.edgecolor'] = '#CCCCCC'
plt.rcParams['axes.linewidth'] = 0.8
plt.rcParams['grid.color'] = '#F0F0F0'

# ETF configurations
etfs = {
    '50ETF': {
        'path': './data/50ETF_1d.parquet',
        'name': '50ETF (510050)'
    },
    '300ETF': {
        'path': './data/510300_1d.parquet',
        'name': '300ETF (510300)'
    },
    '500ETF': {
        'path': './data/500ETF_1d.parquet',
        'name': '500ETF (510500)'
    }
}

# 5 levels of overnight gaps configuration
gap_levels = {
    'sig_down': {
        'name': 'Sig Gap Down (< -0.5%)',
        'color': '#B71C1C',
        'filter_fn': lambda df: df['gap_pct'] < -0.5
    },
    'mod_down': {
        'name': 'Mod Gap Down ([-0.5%, -0.05%))',
        'color': '#EF5350',
        'filter_fn': lambda df: (df['gap_pct'] >= -0.5) & (df['gap_pct'] < -0.05)
    },
    'neutral': {
        'name': 'Neutral ([-0.05%, 0.05%])',
        'color': '#757575',
        'filter_fn': lambda df: (df['gap_pct'] >= -0.05) & (df['gap_pct'] <= 0.05)
    },
    'mod_up': {
        'name': 'Mod Gap Up ((0.05%, 0.5%])',
        'color': '#42A5F5',
        'filter_fn': lambda df: (df['gap_pct'] > 0.05) & (df['gap_pct'] <= 0.5)
    },
    'sig_up': {
        'name': 'Sig Gap Up (> 0.5%)',
        'color': '#0D47A1',
        'filter_fn': lambda df: df['gap_pct'] > 0.5
    }
}

def analyze_etf(name, info):
    if not os.path.exists(info['path']):
        print(f"Error: Path {info['path']} not found.")
        return None
    
    df = pd.read_parquet(info['path'])
    df = df.sort_values('date').tail(2000).copy()
    
    # Calculate difference
    df['diff_abs'] = df['high'] - df['open']
    df['diff_pct'] = (df['high'] - df['open']) / df['open'] * 100
    df['gap_pct'] = (df['open'] - df['prev_close']) / df['prev_close'] * 100
    
    stats = {
        'count': len(df),
        'data': df,
        'levels': {}
    }
    
    for lvl_id, lvl_info in gap_levels.items():
        lvl_df = df[lvl_info['filter_fn'](df)].copy()
        
        # Calculate stats for this level
        if len(lvl_df) > 0:
            p10 = lvl_df['diff_pct'].quantile(0.10)
            p50 = lvl_df['diff_pct'].quantile(0.50)
            p90 = lvl_df['diff_pct'].quantile(0.90)
            p10_abs = lvl_df['diff_abs'].quantile(0.10)
            p50_abs = lvl_df['diff_abs'].quantile(0.50)
            p90_abs = lvl_df['diff_abs'].quantile(0.90)
            
            stats['levels'][lvl_id] = {
                'count': len(lvl_df),
                'mean_pct': lvl_df['diff_pct'].mean(),
                'std_pct': lvl_df['diff_pct'].std(),
                'p10_pct': p10,
                'median_pct': p50,
                'p90_pct': p90,
                'mean_abs': lvl_df['diff_abs'].mean(),
                'median_abs': p50_abs,
                'p10_abs': p10_abs,
                'p90_abs': p90_abs,
                'data': lvl_df['diff_pct'].values
            }
        else:
            stats['levels'][lvl_id] = None
            
    return stats

def main():
    parser = argparse.ArgumentParser(description="Analyze daily Open-to-High price difference distributions and percentiles.")
    parser.add_argument("--artifact-dir", type=str, default=None, help="Optional artifact directory path to copy generated plots.")
    parser.add_argument("--bins", type=int, default=150, help="Number of bins for the histograms.")
    args = parser.parse_args()

    results = {}
    out_dir = './backtest'
    os.makedirs(out_dir, exist_ok=True)
    
    # 1. Generate Combined Overlay Figure (3-panel)
    fig_comb, axes_comb = plt.subplots(1, 3, figsize=(20, 7.5), sharey=False)
    
    for i, (name, info) in enumerate(etfs.items()):
        ax = axes_comb[i]
        print(f"Analyzing {name}...")
        stats = analyze_etf(name, info)
        if stats is None:
            continue
        results[name] = stats
        
        # Plot each level
        for lvl_id, lvl_info in gap_levels.items():
            lvl_stats = stats['levels'][lvl_id]
            if lvl_stats is None or lvl_stats['count'] < 5:
                continue
            
            data_pct = lvl_stats['data']
            # Compute KDE
            try:
                kde = gaussian_kde(data_pct)
                x_range = np.linspace(0, 3.5, 200)
                ax.plot(x_range, kde(x_range), color=lvl_info['color'], linewidth=2, 
                        label=f"{lvl_info['name']} (N={lvl_stats['count']})")
                ax.fill_between(x_range, kde(x_range), alpha=0.03, color=lvl_info['color'])
            except Exception as e:
                print(f"KDE failed for {name} - {lvl_id}: {e}")
            
            # Draw vertical line for 10th percentile (90% fill rate)
            p10 = lvl_stats['p10_pct']
            ax.axvline(p10, color=lvl_info['color'], linestyle='--', alpha=0.7, linewidth=1.2)
            
        ax.set_title(f"{info['name']} - Past {stats['count']} Days", fontsize=12, fontweight='bold', pad=10)
        ax.set_xlabel('Intraday (High - Open) / Open (%)', fontsize=10)
        ax.set_ylabel('Density', fontsize=10)
        ax.set_xlim(-0.05, 3.5)
        ax.legend(loc='upper right', frameon=True, facecolor='white', edgecolor='#E0E0E0', fontsize=8.5)
        ax.grid(True, linestyle=':', alpha=0.6)
        
    plt.suptitle('Distribution of Intraday ETF (High - Open) / Open (%) by 5 Overnight Gap Levels\n'
                 'Dashed Lines: Limit order offset for 90% fill success rate (10th percentile) per level', 
                 fontsize=14, fontweight='bold', y=0.98)
    plt.tight_layout(rect=[0, 0, 1, 0.92])
    
    comb_path = os.path.join(out_dir, 'open_high_distribution.png')
    plt.savefig(comb_path, dpi=300)
    plt.close(fig_comb)
    print(f"Saved combined plot to {comb_path}")
    
    if args.artifact_dir and os.path.exists(args.artifact_dir):
        shutil.copy(comb_path, os.path.join(args.artifact_dir, 'open_high_distribution.png'))
        
    # 2. Generate separate individual figures and facet plots for each ETF
    for name, info in etfs.items():
        stats = results.get(name)
        if stats is None:
            continue
            
        # A. Individual overlay figure (with statistics in text box)
        fig_ind, ax_ind = plt.subplots(figsize=(9, 6.5))
        
        # We will compile text for the box
        box_lines = []
        
        for lvl_id, lvl_info in gap_levels.items():
            lvl_stats = stats['levels'][lvl_id]
            if lvl_stats is None or lvl_stats['count'] < 5:
                continue
                
            data_pct = lvl_stats['data']
            try:
                kde = gaussian_kde(data_pct)
                x_range = np.linspace(0, 3.5, 200)
                ax_ind.plot(x_range, kde(x_range), color=lvl_info['color'], linewidth=2, 
                            label=f"{lvl_info['name']} (N={lvl_stats['count']})")
                ax_ind.fill_between(x_range, kde(x_range), alpha=0.03, color=lvl_info['color'])
            except:
                pass
                
            p10 = lvl_stats['p10_pct']
            p90 = lvl_stats['p90_pct']
            ax_ind.axvline(p10, color=lvl_info['color'], linestyle='--', alpha=0.8, linewidth=1.2)
            
            box_lines.append(f"{lvl_info['name']}:")
            box_lines.append(f"  Mean: {lvl_stats['mean_pct']:.3f}% | 90% Fill: {p10:.3f}%")
            
        ax_ind.set_title(f"Intraday (High - Open) / Open (%) Overlay - {info['name']}", fontsize=12, fontweight='bold', pad=10)
        ax_ind.set_xlabel('Intraday (High - Open) / Open (%)', fontsize=10)
        ax_ind.set_ylabel('Density', fontsize=10)
        ax_ind.set_xlim(-0.05, 3.5)
        
        # Textbox positioning
        textstr = '\n'.join(box_lines)
        props = dict(boxstyle='round', facecolor='white', alpha=0.95, edgecolor='#CCCCCC')
        ax_ind.text(0.40, 0.96, textstr, transform=ax_ind.transAxes, fontsize=8,
                    verticalalignment='top', bbox=props)
        
        ax_ind.legend(loc='upper right', frameon=True, facecolor='white', edgecolor='#E0E0E0', fontsize=8.5)
        ax_ind.grid(True, linestyle=':', alpha=0.6)
        
        ind_path = os.path.join(out_dir, f'open_high_distribution_{name}.png')
        fig_ind.savefig(ind_path, dpi=300, bbox_inches='tight')
        plt.close(fig_ind)
        print(f"Saved individual overlay plot to {ind_path}")
        
        if args.artifact_dir and os.path.exists(args.artifact_dir):
            shutil.copy(ind_path, os.path.join(args.artifact_dir, f'open_high_distribution_{name}.png'))
            
        # B. Facet figure (1x5 subplots side-by-side for maximum clarity)
        fig_facet, axes_facet = plt.subplots(1, 5, figsize=(22, 5), sharey=True)
        
        for j, (lvl_id, lvl_info) in enumerate(gap_levels.items()):
            ax_f = axes_facet[j]
            lvl_stats = stats['levels'][lvl_id]
            
            if lvl_stats is None or lvl_stats['count'] < 5:
                ax_f.text(0.5, 0.5, 'Insufficient Data', transform=ax_f.transAxes, ha='center')
                ax_f.set_title(lvl_info['name'], fontsize=10, fontweight='bold')
                continue
                
            data_pct = lvl_stats['data']
            bins = np.linspace(0, 3.5, args.bins // 2)
            
            # Histogram
            ax_f.hist(data_pct, bins=bins, density=True, alpha=0.25, color=lvl_info['color'], edgecolor=lvl_info['color'], linewidth=0.5)
            
            # KDE
            try:
                kde = gaussian_kde(data_pct)
                x_range = np.linspace(0, 3.5, 200)
                ax_f.plot(x_range, kde(x_range), color=lvl_info['color'], linewidth=2)
            except:
                pass
                
            p10 = lvl_stats['p10_pct']
            p90 = lvl_stats['p90_pct']
            ax_f.axvline(p10, color='#E53935', linestyle='--', linewidth=1.5, label=f'90% Fill: {p10:.3f}%')
            ax_f.axvline(p90, color='#43A047', linestyle='-.', linewidth=1.5, label=f'90% Cover: {p90:.3f}%')
            
            ax_f.set_title(f"{lvl_info['name']}\n(N={lvl_stats['count']})", fontsize=10, fontweight='bold', pad=8)
            ax_f.set_xlabel('Intraday Diff (%)', fontsize=9)
            if j == 0:
                ax_f.set_ylabel('Density', fontsize=9)
            ax_f.set_xlim(-0.05, 3.5)
            ax_f.legend(loc='upper right', fontsize=8, frameon=True, facecolor='white', edgecolor='#EEEEEE')
            ax_f.grid(True, linestyle=':', alpha=0.6)
            
        plt.suptitle(f"Intraday (High - Open) / Open (%) distribution details by regime - {info['name']}", 
                     fontsize=13, fontweight='bold', y=0.98)
        plt.tight_layout(rect=[0, 0, 1, 0.92])
        
        facet_path = os.path.join(out_dir, f'open_high_distribution_facets_{name}.png')
        fig_facet.savefig(facet_path, dpi=300, bbox_inches='tight')
        plt.close(fig_facet)
        print(f"Saved facet plot to {facet_path}")
        
        if args.artifact_dir and os.path.exists(args.artifact_dir):
            shutil.copy(facet_path, os.path.join(args.artifact_dir, f'open_high_distribution_facets_{name}.png'))

    # Output stats table
    print("\n| ETF | Regime | Count | Mean (%) | Median (%) | 10th Pct (%) | 90th Pct (%) | Mean (RMB) | Median (RMB) | 10th Pct (RMB) | 90th Pct (RMB) |")
    print("|---|---|---|---|---|---|---|---|---|---|---|")
    for name, stats in results.items():
        for lvl_id, lvl_info in gap_levels.items():
            s = stats['levels'][lvl_id]
            if s is None:
                continue
            print(f"| {name} | {lvl_info['name']} | {s['count']} | {s['mean_pct']:.3f}% | {s['median_pct']:.3f}% | {s['p10_pct']:.3f}% | {s['p90_pct']:.3f}% | {s['mean_abs']:.4f} | {s['median_abs']:.4f} | {s['p10_abs']:.4f} | {s['p90_abs']:.4f} |")

if __name__ == '__main__':
    main()
