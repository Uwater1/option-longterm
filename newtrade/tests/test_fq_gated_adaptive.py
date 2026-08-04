#!/usr/bin/env python3
"""
FQ Follow-up — tailIC + hard gates with ADAPTIVE K (no fill-in).

Main sweep verdict: no fixed top-10 rescoring reaches 8+ TP' (best 7.15/10).
The count metric is contaminated when gates fail and we fill remaining slots
with unvalidated factors. Here we select ONLY factors passing the gate
(ranked by tailIC480), and measure the TP' RATE among selected.

Question: is there a gate config with TP' rate >= 80% while still selecting
enough factors (coverage) to feed the top-K portfolio?

Usage:
    python newtrade/tests/test_fq_gated_adaptive.py
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

from utils import (load_admitted_pool, load_etf_dataset, build_pool_feature_matrix,
                   expanding_zscore_numba)
from test_fq_diagnostic import forward_ic_matrix, AVAILABLE_ETFS, SNAPSHOT_STEP
from test_fq_validation import forward_sortino_matrix
from test_fq_sweep import build_component_library, START_YEAR, PRIMARY_H

GATE_CONFIGS = {
    "tailIC>0": ["gt0"],
    "gt0+sort>0": ["gt0", "sort0"],
    "+mono>=.52": ["gt0", "sort0", "mono52"],
    "+nneg=0": ["gt0", "sort0", "nneg0"],
    "+loo>0": ["gt0", "sort0", "loo0"],
    "+reg=2": ["gt0", "sort0", "reg2"],
    "+IC>floor": ["gt0", "sort0", "floor"],
    "kitchen(nneg+floor)": ["gt0", "sort0", "nneg0", "floor"],
    "kitchen+loo": ["gt0", "sort0", "nneg0", "floor", "loo0"],
}


def apply_gates(lib, gates, flags):
    T, N = lib["tailIC480"].shape
    mask = np.ones((T, N), dtype=bool)
    floor = np.median(np.abs(lib["tailIC480"]), axis=1, keepdims=True)
    for f in flags:
        if f == "gt0":
            mask &= lib["tailIC480"] > 0
        elif f == "sort0":
            mask &= lib["sortino480"] > 0
        elif f == "mono52":
            mask &= lib["mono"] >= 0.52
        elif f == "nneg0":
            mask &= gates["n_neg_blocks"] == 0
        elif f == "loo0":
            mask &= gates["loo_min"] > 0
        elif f == "reg2":
            mask &= gates["regime_sign"] == 2
        elif f == "floor":
            mask &= lib["tailIC480"] > floor
    return mask


def main():
    print("=" * 100)
    print("FQ FOLLOW-UP — tailIC + hard gates, ADAPTIVE K (TP' rate among selected, no fill-in)")
    print("=" * 100)

    rows = []
    for etf in AVAILABLE_ETFS:
        pool = load_admitted_pool(etf, side="single", min_features=10)
        if not pool:
            continue
        df = load_etf_dataset(etf)
        trade_ret = (df["trade_return"].values.astype(np.float64)
                     if "trade_return" in df.columns
                     else df["close"].pct_change().fillna(0.0).values)
        X_raw, signs, _ = build_pool_feature_matrix(df, pool)
        burn_in = 252 if len(df) > 500 else 100
        Z_std = expanding_zscore_numba(X_raw, burn_in=burn_in, clip=3.0)

        print(f"\n[{etf}] N={len(pool)} — building library & forward targets...")
        lib, gates, _ = build_component_library(Z_std, signs, trade_ret, burn_in)
        fwd63 = forward_ic_matrix(Z_std, signs, trade_ret, horizon=PRIMARY_H)
        fwd_sort = forward_sortino_matrix(Z_std, signs, trade_ret, horizon=PRIMARY_H)

        dates = df["date"]
        t_start = int(np.searchsorted(dates.values, np.datetime64(f"{START_YEAR}-01-01")))
        t_start = max(t_start, 970)
        snapshots = list(range(t_start, len(df) - PRIMARY_H - 1, SNAPSHOT_STEP))

        for cfg_name, flags in GATE_CONFIGS.items():
            mask = apply_gates(lib, gates, flags)
            tp_rates, n_sels = [], []
            for t in snapshots:
                f63, fs = fwd63[t], fwd_sort[t]
                ok = np.isfinite(f63) & np.isfinite(fs)
                sel = mask[t] & ok
                n = int(sel.sum())
                n_sels.append(n)
                if n > 0:
                    tp = int(((f63[sel] > 0) & (fs[sel] > 0)).sum())
                    tp_rates.append(tp / n)
            rows.append({
                "ETF": etf, "Gate": cfg_name,
                "TP_rate_pct": float(np.mean(tp_rates) * 100) if tp_rates else np.nan,
                "AvgSelected": float(np.mean(n_sels)),
                "Cov_ge10_pct": float(np.mean(np.array(n_sels) >= 10) * 100),
                "Cov_ge5_pct": float(np.mean(np.array(n_sels) >= 5) * 100),
            })

    df_res = pd.DataFrame(rows)
    agg = df_res.groupby("Gate").agg(TP_rate=("TP_rate_pct", "mean"),
                                     AvgSel=("AvgSelected", "mean"),
                                     Cov_ge10=("Cov_ge10_pct", "mean"),
                                     Cov_ge5=("Cov_ge5_pct", "mean")).round(1)
    agg = agg.sort_values("TP_rate", ascending=False)

    print("\n" + "=" * 100)
    print("RESULTS — TP' RATE among gate-passing factors (adaptive K, ranked by tailIC480)")
    print("         Cov_ge10 = % of snapshots where >=10 factors pass (portfolio feedable)")
    print("=" * 100)
    print(agg.to_string())

    print("\n" + "-" * 100)
    print("PER-ETF TP' rate (%)")
    print("-" * 100)
    print(df_res.pivot_table(index="Gate", columns="ETF", values="TP_rate_pct").round(1).to_string())

    best = agg.index[0]
    if agg.loc[best, "TP_rate"] >= 80:
        print(f"\nVERDICT: gate '{best}' reaches {agg.loc[best,'TP_rate']:.1f}% TP' rate "
              f"(avg {agg.loc[best,'AvgSel']:.1f} selected, cov>=10: {agg.loc[best,'Cov_ge10']:.0f}%).")
    else:
        print(f"\nVERDICT: no gate config reaches 80% TP' rate. Best = '{best}' "
              f"@ {agg.loc[best,'TP_rate']:.1f}%. The 3-month TP' ceiling for these pools is below 80%.")

    df_res.to_csv(HERE / "fq_gated_adaptive_results.csv", index=False)
    print(f"Saved to {HERE / 'fq_gated_adaptive_results.csv'}")
    print("\n[OK] Gated adaptive-K follow-up complete.")


if __name__ == "__main__":
    main()
