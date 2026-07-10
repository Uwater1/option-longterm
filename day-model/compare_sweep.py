"""Quick comparison of sweep results: baseline vs sortino vs sw variants."""
import json, glob, os, sys
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
ETFS = ["300ETF", "500ETF", "50ETF", "588000ETF", "159915ETF"]
SIDES = ["single", "long", "short"]

def load_config(suffix=""):
    """Load results for a given config suffix (e.g. '', '_sortino', '_sw0.30')."""
    results = {}
    for etf in ETFS:
        for side in SIDES:
            if side == "single":
                fname = f"results_{etf}{suffix}.json"
            else:
                fname = f"results_{etf}_{side}{suffix}.json"
            path = DATA_DIR / fname
            if path.exists():
                with open(path) as f:
                    results[(etf, side)] = json.load(f)
    return results

def agg(results):
    """Compute aggregate stats across all ETF x side combinations."""
    import numpy as np
    if not results:
        return None
    out_ics = [v.get("lockbox_overall_ic", 0) for v in results.values()]
    out_tics = [v.get("lockbox_tail_ic", 0) for v in results.values()]
    pbos = [v.get("pbo", 0) for v in results.values()]
    perf_degs = [v.get("performance_degradation", 0) for v in results.values()]
    ic_gaps = [v.get("ic_generalization_gap", 0) for v in results.values()]
    feats = [len(v.get("selected_features", [])) for v in results.values()]
    return {
        "n": len(results),
        "out_ic": float(np.mean(out_ics)) if out_ics else 0.0,
        "out_ic_std": float(np.std(out_ics)) if out_ics else 0.0,
        "out_tic": float(np.mean(out_tics)) if out_tics else 0.0,
        "out_tic_std": float(np.std(out_tics)) if out_tics else 0.0,
        "pbo": float(np.mean(pbos)) if pbos else 0.0,
        "perf_deg": float(np.mean(perf_degs)) if perf_degs else 0.0,
        "ic_gap": float(np.mean(ic_gaps)) if ic_gaps else 0.0,
        "feats": float(np.mean(feats)) if feats else 0.0,
    }

def per_etf_table(configs):
    """Print per-ETF comparison table."""
    header = f"{'ETF':<14} {'Side':<7}"
    for name in configs:
        header += f" | {name:>10} IC {name:>10} TIC {name:>8} PBO {name:>8} Shp"
    print(header)
    print("-" * len(header))
    for etf in ETFS:
        for side in SIDES:
            row = f"{etf:<14} {side:<7}"
            for name, results in configs.items():
                d = results.get((etf, side))
                if d:
                    row += f" | {d.get('out_ic',0):14.4f} {d.get('out_tail_ic',0):14.4f} {d.get('pbo',0)*100:10.1f}% {d.get('out_sharpe',0):8.4f}"
                else:
                    row += f" | {'N/A':>14} {'N/A':>14} {'N/A':>10} {'N/A':>8}"
            print(row)

CONFIGS = {
    "baseline": "",
    "sortino": "_sortino",
    "s+cpcvblend": "_sortino_blended",
    "s+sw0.20": "_sortino_sw0.20",
    "s+sw0.30": "_sortino_sw0.30",
    "s+sw0.50": "_sortino_sw0.50",
    "sw0.20": "_sw0.20",
    "sw0.30": "_sw0.30",
    "sharpe-obj": "_sharpe",
}

def main():
    all_results = {}
    for name, suffix in CONFIGS.items():
        r = load_config(suffix)
        if r:
            all_results[name] = r
    
    # Aggregate summary
    print("=" * 105)
    print("AGGREGATE COMPARISON (mean across all ETF x side)")
    print("=" * 105)
    print(f"{'Config':<14} {'N':>3} {'OutIC':>8} {'OutICstd':>9} {'OutTIC':>8} {'OutTICstd':>9} {'PBO':>8} {'PerfDeg':>8} {'ICgap':>8} {'Feats':>6}")
    print("-" * 102)
    for name, results in all_results.items():
        a = agg(results)
        if a:
            print(f"{name:<14} {a['n']:3d} {a['out_ic']:8.4f} {a['out_ic_std']:9.4f} {a['out_tic']:8.4f} {a['out_tic_std']:9.4f} {a['pbo']*100:7.1f}% {a['perf_deg']:8.3f} {a['ic_gap']:8.4f} {a['feats']:6.1f}")
    
    # Per-ETF detail
    print(f"\n{'=' * 80}")
    print("PER-ETF x SIDE DETAIL")
    print("=" * 80)
    
    # Print simpler per-etf tables
    for etf in ETFS:
        print(f"\n--- {etf} ---")
        print(f"{'Side':<7} {'Config':<14} {'OutIC':>8} {'OutTIC':>8} {'PBO':>8} {'PerfDeg':>8} {'Feats':>6}")
        for side in SIDES:
            for name, results in all_results.items():
                d = results.get((etf, side))
                if d:
                    print(f"{side:<7} {name:<14} {d.get('lockbox_overall_ic',0):8.4f} {d.get('lockbox_tail_ic',0):8.4f} {d.get('pbo',0)*100:7.1f}% {d.get('performance_degradation',0):8.3f} {len(d.get('selected_features',[])):6d}")
                else:
                    print(f"{side:<7} {name:<14} {'---':>8} {'---':>8} {'---':>8} {'---':>8} {'---':>6}")

if __name__ == "__main__":
    main()
