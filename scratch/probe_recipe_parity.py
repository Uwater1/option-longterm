# -*- coding: utf-8 -*-
"""Pinpoint the recipe-parity divergence in test_qmt_features (probe only)."""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "newtrade" / "tests"))
sys.path.insert(0, str(REPO / "newtrade"))
sys.path.insert(0, str(REPO / "day-model-new" / "mining"))

import test_qmt_features as T  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import qmt_strategy as Q  # noqa: E402
from utils import build_pool_feature_matrix  # noqa: E402

etf = "500ETF"
feats_df, dates = T.test_feature_parity(etf, 5)
cfg = Q.QMT_CONFIG["etfs"][etf]
features = cfg["features"]
names = [f["feature_name"] for f in features]
X_ret = build_pool_feature_matrix(feats_df, features)
X_raw = X_ret[0] if isinstance(X_ret, tuple) else X_ret
date_idx = {d: i for i, d in enumerate(feats_df["date"].tolist())}
d5, d1 = T._idx_cache(etf)

worst = (0.0, "", None)
for d in dates:
    i = date_idx[d]
    row = feats_df.iloc[i]
    day = d5[d5["date"] == d].head(6)
    if len(day) < 6:
        continue
    prev_close = d1.loc[d1["date"] == d, "prev_close_adj"]
    exp_daily = d1.loc[d1["date"] == d, "expected_daily_volume"]
    if len(prev_close) == 0 or pd.isna(prev_close.iloc[0]):
        continue
    exp_daily_v = exp_daily.iloc[0] if len(exp_daily) else np.nan
    if pd.isna(exp_daily_v) or exp_daily_v <= 0:
        exp_daily_v = d1["volume"].median()
    raw = Q.compute_raw_features(
        day["open"].values, day["high"].values, day["low"].values,
        day["close"].values, day["volume"].values,
        float(prev_close.iloc[0]), exp_daily_v / 48.0,
        is_20pct=cfg.get("is_20pct", False))
    for j, feat in enumerate(features):
        lv = Q.compute_feature_value(feat, raw, cfg["train_stats"], cfg["ecdf_grids"])
        diff = abs(lv - float(X_raw[i, j]))
        if diff > worst[0]:
            worst = (diff, feat["feature_name"], d)
        if diff > 1e-4:
            print(f"  {d.date()} {feat['feature_name']}: live={lv:.8f} "
                  f"pipeline={float(X_raw[i, j]):.8f} diff={diff:.3e}")
print("worst:", worst)
