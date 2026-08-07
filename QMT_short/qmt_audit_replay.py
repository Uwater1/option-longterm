#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
qmt_audit_replay.py — offline twin of qmt_strategy.py's decision pipeline.

Run AFTER market close (in the repo venv, NO QMT involved) once the day's
index 5m/1d data has been downloaded. It recomputes the exact same decision
path as qmt_strategy.py running inside QMT and emits the IDENTICAL AUDIT
lines into a replay log:

    AUDIT <date> DECISION <etf> prev_close=... exp_bar_vol=...
          FEATURES=[24 raw feature values]
          ZSIGNED=[10 signed z-scores]
          composite=... TH=... SIDE=...

Diff workflow (see 部署说明.md):
    1. Copy the QMT-side qmt_audit_log.txt off the QMT machine.
    2. python qmt_audit_replay.py --date YYYYMMDD
    3. Extract AUDIT lines from both files and diff them.
       Identical  -> QMT data feed + config + script all verified.
       Different  -> the differing key names the problem
                     (bars / prev_close / exp_bar_vol / config / API).

Extra REPLAY_* lines (xcheck vs features parquet, reference side) are
replay-only diagnostics and are NOT part of the diff contract.

Usage:
    python qmt_audit_replay.py --date 20260807
    python qmt_audit_replay.py --date 20260807 -e 500ETF -o replay.log
"""
import argparse
import datetime
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent

# Test the DEPLOYED script itself: import the qmt_strategy.py sitting in
# this same folder (the exact copy that runs inside QMT).
sys.path.insert(0, str(HERE))
import qmt_strategy as Q  # noqa: E402

# Repo-side imports (venv only; these never touch QMT)
sys.path.insert(0, str(REPO_ROOT / "newtrade"))
sys.path.insert(0, str(REPO_ROOT / "day-model-new" / "mining"))

INDEX_5M = {"500ETF": "000905_5m.parquet", "159915ETF": "399006_5m.parquet"}
INDEX_1D = {"500ETF": "000905_1d.parquet", "159915ETF": "399006_1d.parquet"}


def load_index_5m(etf: str) -> pd.DataFrame:
    d5 = pd.read_parquet(REPO_ROOT / "data" / INDEX_5M[etf])
    d5["datetime"] = pd.to_datetime(d5["datetime"])
    d5["date"] = d5["datetime"].dt.normalize()
    return d5.sort_values(["date", "datetime"]).reset_index(drop=True)


def load_index_1d(etf: str) -> pd.DataFrame:
    d1 = pd.read_parquet(REPO_ROOT / "data" / INDEX_1D[etf])
    d1["date"] = pd.to_datetime(d1["date"])
    return d1.sort_values("date").reset_index(drop=True)


def get_prev_context(d1: pd.DataFrame, date: pd.Timestamp, cfg: dict):
    """Mirror qmt_strategy._get_prev_context on repo daily data:
    history strictly before `date`; fallback to baked seeds."""
    hist = d1[d1["date"] < date]
    if len(hist) < 1:
        return cfg["prev_close_seed"], cfg["exp_bar_vol_seed"], "seed"
    prev_close = float(hist["close"].iloc[-1])
    vols = [float(v) for v in hist["volume"].iloc[-20:].values]
    exp_bar_vol = (sum(vols) / len(vols)) / 48.0
    if prev_close <= 0 or exp_bar_vol <= 0:
        return cfg["prev_close_seed"], cfg["exp_bar_vol_seed"], "seed"
    return prev_close, exp_bar_vol, "live"


def extend_ecdf_grids(etf: str, cfg: dict) -> dict:
    """Rank-op components missing from the baked grid (bake-date cutoff) get
    grids rebuilt on full repo history, so the replay can evaluate any date."""
    from recipe_utils import build_ecdf_grid_float32
    missing = set()
    for f in cfg["features"]:
        r = f.get("recipe")
        if r and r["op"] in ("rank_min", "rank_max"):
            for k in ("feature_a", "feature_b"):
                if r[k] not in cfg["ecdf_grids"]:
                    missing.add(r[k])
    if not missing:
        return cfg["ecdf_grids"]
    feats_df = pd.read_parquet(REPO_ROOT / "day-model" / "data" / f"features_{etf}.parquet")
    grids = dict(cfg["ecdf_grids"])
    for col in sorted(missing):
        xp, fp = build_ecdf_grid_float32(feats_df[col].values.astype(np.float32),
                                         n_knots=128)
        grids[col] = {"xp": [float(v) for v in xp], "fp": [float(v) for v in fp]}
    return grids


def xcheck_features(etf: str, date: pd.Timestamp, raw: dict) -> str:
    """Compare replay raw features against features parquet (built by
    day-model/build_features.py). Best-effort: SKIP if the date is absent."""
    path = REPO_ROOT / "day-model" / "data" / f"features_{etf}.parquet"
    f = pd.read_parquet(path).reset_index()
    if "date" not in f.columns:
        return "SKIP=no_date_col"
    f["date"] = pd.to_datetime(f["date"])
    rows = f[f["date"] == date]
    if len(rows) == 0:
        return "SKIP=date_not_in_parquet"
    ref = rows.iloc[0]
    max_diff, worst = 0.0, ""
    n_checked = 0
    for name in raw:
        if name not in f.columns:
            continue
        d = abs(float(raw[name]) - float(ref[name]))
        if d > max_diff:
            max_diff, worst = d, name
        n_checked += 1
    if n_checked == 0:
        return "SKIP=no_common_cols"
    return "OK n=%d max_diff=%.3e worst=%s" % (n_checked, max_diff, worst)


def replay_etf(etf: str, date: pd.Timestamp, date_str: str):
    cfg = Q.QMT_CONFIG["etfs"].get(etf)
    if cfg is None:
        print(f"[{etf}] not in QMT_CONFIG, skip")
        return

    d5 = load_index_5m(etf)
    day = d5[d5["date"] == date].head(6)
    if len(day) < 6:
        Q.audit_skip(etf, "no_bars")
        print(f"[{etf}] AUDIT SKIP no_bars (only {len(day)} bars downloaded)")
        return

    d1 = load_index_1d(etf)
    prev_close, exp_bar_vol, src = get_prev_context(d1, date, cfg)
    raw = Q.compute_raw_features(
        day["open"].values, day["high"].values, day["low"].values,
        day["close"].values, day["volume"].values,
        prev_close, exp_bar_vol, is_20pct=cfg.get("is_20pct", False))
    if raw is None:
        Q.audit_skip(etf, "bad_bars")
        print(f"[{etf}] AUDIT SKIP bad_bars")
        return

    cfg_ext = dict(cfg)
    cfg_ext["ecdf_grids"] = extend_ecdf_grids(etf, cfg)
    composite, detail = Q.compute_composite(cfg_ext, raw)
    side = Q.decide_side(composite, cfg["z_th_long"], cfg["z_th_short"])

    Q.audit_decision(etf, prev_close, exp_bar_vol, raw, composite, detail,
                     cfg["z_th_long"], cfg["z_th_short"], side)

    xc = xcheck_features(etf, date, raw)
    with open(Q.AUDIT_LOG_FILE, "a", encoding="utf-8") as fh:
        fh.write("REPLAY %s XCHECK %s %s (prevctx=%s)\n" % (date_str, etf, xc, src))
        fh.write("REPLAY %s SIDE_REF %s SIDE=%s composite=%.8f "
                 "spot_close=%.6f\n" % (date_str, etf, side, composite,
                                         float(day['close'].iloc[-1])))
    print(f"[{etf}] SIDE={side} composite={composite:+.6f} "
          f"prevctx={src} xcheck={xc}")


def main():
    ap = argparse.ArgumentParser(description="Offline twin of qmt_strategy decisions")
    ap.add_argument("--date", default=datetime.datetime.now().strftime("%Y%m%d"),
                    help="Trading day to replay (YYYYMMDD, default today)")
    ap.add_argument("-e", "--etf", default="all",
                    help="ETF to replay (500ETF / 159915ETF / all)")
    ap.add_argument("-o", "--output", default=None,
                    help="Replay log path (default qmt_audit_replay_<date>.log)")
    args = ap.parse_args()

    date = pd.Timestamp(datetime.datetime.strptime(args.date, "%Y%m%d"))
    out_path = Path(args.output) if args.output else HERE / f"qmt_audit_replay_{args.date}.log"

    # Point qmt_strategy's audit machinery at the replay log and pin the date.
    # Truncate first: re-running the same date must not be eaten by the
    # restart-safe DECISION dedup inside qmt_strategy.
    out_path.write_text("", encoding="utf-8")
    Q.AUDIT_LOG_FILE = str(out_path)
    Q.AUDIT_DATE_OVERRIDE = args.date

    etfs = (list(Q.QMT_CONFIG["etfs"].keys()) if args.etf == "all"
            else [args.etf])
    print(f"replay date={args.date} etfs={etfs} -> {out_path}")
    for etf in etfs:
        replay_etf(etf, date, args.date)
    print(f"done. Diff AUDIT lines: {out_path} vs QMT-side qmt_audit_log.txt")


if __name__ == "__main__":
    main()
