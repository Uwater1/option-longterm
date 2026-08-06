#!/usr/bin/env python3
"""
Bake Part A selections into newtrade/qmt_strategy.py.

Reads:
  - newtrade/data/qmt_selection_{ETF}.json          (Part A deliverable)
  - day-model/data/features_{ETF}.parquet           (raw feature history)
  - data/{index}_1d.parquet                         (prev_close / exp_bar_vol seeds)

Writes (in-place, between the QMT-CONFIG markers of qmt_strategy.py):
  - per-ETF feature list (name, sign, recipe) + z thresholds
  - train_stats: pre-2022 mean/std (ddof=1) + median per raw component
    (mirrors build_pool_feature_matrix recipe standardization)
  - ecdf_grids: 128-knot ECDF (xp/fp) per rank component
    (mirrors compute_recipe full-sample grid)
  - combo_stats: expanding mu/sigma through the latest day per selected
    feature (matches expanding_zscore_numba at t = final+1)
  - prev_close_seed / exp_bar_vol_seed from the index daily parquet

Usage:  python newtrade/build_qmt_config.py
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO_ROOT / "day-model-new" / "mining"))

from recipe_utils import build_ecdf_grid_float32  # noqa: E402
from utils import load_etf_dataset  # noqa: E402

ETFS = {
    "500ETF": {
        "qmt_underlying": "510500.SH",
        "index_code": "000905.SH",
        "index_1d": "000905_1d.parquet",
        "is_20pct": False,
        "strike_mode": "nearest",
    },
    "159915ETF": {
        "qmt_underlying": "159915.SZ",
        "index_code": "399006.SZ",
        "index_1d": "399006_1d.parquet",
        "is_20pct": True,
        "strike_mode": "vol_t1",
    },
}
TRAIN_END = pd.Timestamp("2022-01-01")
BEGIN_MARK = "# ===QMT-CONFIG-BEGIN==="
END_MARK = "# ===QMT-CONFIG-END==="


def required_raws(features: list) -> tuple[set, set, set]:
    """Return (std_cols, rank_cols, cond_cols) referenced by recipes."""
    std_cols, rank_cols, cond_cols = set(), set(), set()
    STD_OPS = {"min", "max", "diff", "z_diff", "z_sum", "mean", "product",
               "abs_diff", "clamp_diff", "sig_product", "rel_diff",
               "tri_mean", "tri_z_mean", "tri_sig_max", "tri_min", "tri_max",
               "tri_median"}
    for f in features:
        r = f.get("recipe")
        if not r:
            continue
        op = r["op"]
        if op == "ifelse":
            cond_cols.add(r["feature_cond"])
            std_cols.add(r["feature_a"])
            std_cols.add(r["feature_b"])
        elif op in ("rank_min", "rank_max"):
            rank_cols.add(r["feature_a"])
            rank_cols.add(r["feature_b"])
        elif op == "ratio":
            pass  # raw values, no stats
        elif op == "tri_ifelse":
            cond_cols.add(r["feature_cond"])
            cond_cols.add(r["feature_cond2"])
            std_cols.update([r["feature_a"], r["feature_b"], r["feature_c"]])
        elif op in STD_OPS:
            for k in ("feature_a", "feature_b", "feature_c"):
                if k in r:
                    std_cols.add(r[k])
        else:
            raise ValueError(f"Unsupported op {op} for {f['feature_name']}")
    return std_cols, rank_cols, cond_cols


def bake_etf(etf: str, meta: dict) -> dict:
    sel_path = HERE / "data" / f"qmt_selection_{etf}.json"
    with open(sel_path, "r", encoding="utf-8") as f:
        sel = json.load(f)
    features = sel["features"]

    df = load_etf_dataset(etf)  # same defensive fills as the backtest path
    train_df = df[df["date"] < TRAIN_END]

    std_cols, rank_cols, cond_cols = required_raws(features)

    train_stats = {}
    for col in sorted(std_cols | cond_cols):
        train_stats[col] = {
            "mean": round(float(train_df[col].mean()), 10),
            "std": round(float(train_df[col].std()), 10),  # ddof=1 like pandas
            "median": round(float(train_df[col].median()), 10),
        }

    ecdf_grids = {}
    for col in sorted(rank_cols):
        val = df[col].values.astype(np.float32)
        xp, fp = build_ecdf_grid_float32(val, n_knots=128)
        ecdf_grids[col] = {
            "xp": [round(float(v), 9) for v in xp],
            "fp": [round(float(v), 9) for v in fp],
        }

    # combo_stats: expanding mu/sigma over the FULL raw combo series
    # (matches expanding_zscore_numba statistics at the first live day)
    from utils import build_pool_feature_matrix  # noqa: E402
    X_raw, signs, names = build_pool_feature_matrix(df, features)
    combo_stats = {}
    for j, name in enumerate(names):
        col = X_raw[:, j]
        combo_stats[name] = {
            "mu": round(float(np.mean(col)), 10),
            "sigma": round(float(np.sqrt(np.mean((col - np.mean(col)) ** 2))), 10),
        }

    # seeds from index daily parquet
    idx_df = pd.read_parquet(REPO_ROOT / "data" / meta["index_1d"])
    idx_df = idx_df.sort_values("date").reset_index(drop=True)
    prev_close_seed = float(idx_df["close"].iloc[-1])
    vols = idx_df["volume"].iloc[-20:].astype(float)
    exp_bar_vol_seed = float(vols.mean() / 48.0)

    return {
        "qmt_underlying": meta["qmt_underlying"],
        "index_code": meta["index_code"],
        "is_20pct": meta["is_20pct"],
        "strike_mode": meta["strike_mode"],
        "z_th_long": sel["thresholds"]["z_th_long"],
        "z_th_short": sel["thresholds"]["z_th_short"],
        "z_clip": 3.0,
        "prev_close_seed": round(prev_close_seed, 6),
        "exp_bar_vol_seed": round(exp_bar_vol_seed, 6),
        "features": [
            {k: v for k, v in f.items() if k in ("feature_name", "sign", "recipe")}
            for f in features
        ],
        "train_stats": train_stats,
        "ecdf_grids": ecdf_grids,
        "combo_stats": combo_stats,
        "selection_meta": {
            "generated": sel.get("generated"),
            "oos_sharpe": sel.get("oos", {}).get("sharpe"),
            "oos_pnl": sel.get("oos", {}).get("pnl"),
            "per_year": sel.get("oos", {}).get("per_year"),
        },
    }


def _fmt_config(obj, indent=0):
    """Pretty-print the config as a Python literal with scalar lists INLINE
    (keeps 128-value ECDF grids on one line each instead of 128 lines)."""
    pad = "    " * indent
    if isinstance(obj, dict):
        if not obj:
            return "{}"
        lines = ["{"]
        items = list(obj.items())
        for i, (k, v) in enumerate(items):
            comma = "," if i < len(items) - 1 else ""
            lines.append(f"{pad}    {json.dumps(k)}: {_fmt_config(v, indent + 1)}{comma}")
        lines.append(pad + "}")
        return "\n".join(lines)
    if isinstance(obj, list):
        if all(not isinstance(x, (dict, list)) for x in obj):
            return json.dumps(obj)  # inline scalar list
        lines = ["["]
        for i, v in enumerate(obj):
            comma = "," if i < len(obj) - 1 else ""
            lines.append(pad + "    " + _fmt_config(v, indent + 1) + comma)
        lines.append(pad + "]")
        return "\n".join(lines)
    return json.dumps(obj)


# Concise legend emitted above QMT_CONFIG so auditors don't have to reverse
# engineer the baked structures.
CONFIG_NOTE = """\
# QMT_CONFIG legend (baked by newtrade/build_qmt_config.py; hand-editable):
#   etfs.<ETF>.features    : the 10 selected features (feature_name / sign / recipe)
#   etfs.<ETF>.train_stats : per raw component {mean, std(ddof=1), median} on pre-2022
#                            data -- standardization inputs used by recipe ops
#   etfs.<ETF>.ecdf_grids  : 128-knot ECDF grids for rank_min/rank_max components:
#                            xp = historical quantiles, fp = linspace(0,1,128).
#                            Live percentile rank = linear interpolation of fp over xp
#                            (see _rank_col); mirrors compute_recipe's get_rank_col.
#   etfs.<ETF>.combo_stats : per selected feature {mu, sigma} = expanding z-score
#                            statistics through the bake date (matches the offline
#                            expanding_zscore_numba at the first live day)
#   z_th_long/z_th_short   : production thresholds (train-optimal + 0.10/+0.20 buffer)
#   prev_close_seed/exp_bar_vol_seed : fallbacks if the live index history fetch fails"""


def main():
    config = {
        "generated": pd.Timestamp.now().isoformat(),
        "note": "Regenerate via newtrade/build_qmt_config.py; hand-editable after.",
        "account": "210889000248",  # STOCK_OPTION account (paper)
        "etfs": {},
    }
    for etf, meta in ETFS.items():
        print(f"baking {etf} ...")
        config["etfs"][etf] = bake_etf(etf, meta)
        n_feat = len(config["etfs"][etf]["features"])
        print(f"  {n_feat} features, {len(config['etfs'][etf]['train_stats'])} train-stat cols, "
              f"{len(config['etfs'][etf]['ecdf_grids'])} ecdf grids")

    block = ("QMT_CONFIG = " + _fmt_config(config))
    # JSON -> Python literals (config block must be importable Python)
    import re
    block = re.sub(r"\bfalse\b", "False", block)
    block = re.sub(r"\btrue\b", "True", block)
    block = re.sub(r"\bnull\b", "None", block)
    block = CONFIG_NOTE + "\n" + block

    strat_path = HERE / "qmt_strategy.py"
    src = strat_path.read_text(encoding="utf-8")
    i_begin = src.index(BEGIN_MARK)
    i_end = src.index(END_MARK)
    # keep the comment tail on the BEGIN line
    line_end = src.index("\n", i_begin)
    new_src = src[:line_end + 1] + block + "\n" + src[i_end:]
    strat_path.write_text(new_src, encoding="utf-8")
    print(f"config baked into {strat_path} "
          f"({len(block)} chars)")


if __name__ == "__main__":
    main()
