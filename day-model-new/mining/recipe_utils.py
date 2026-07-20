import numpy as np
import pandas as pd
from scipy.stats import rankdata


def compute_recipe(df: pd.DataFrame, recipe: dict, train_means: dict = None, train_stds: dict = None, train_medians: dict = None) -> np.ndarray:
    """
    Dynamically compute feature values from a recipe dictionary.
    Aligns scale by standardizing inputs for min/max/diff/ifelse using train_means/train_stds if provided.

    Supported 2-way ops: min, max, diff, ratio, ifelse, mean, product, abs_diff,
                         rank_min, rank_max, clamp_diff
    Supported 3-way ops: tri_mean, tri_min, tri_max, tri_median, tri_ifelse
    """
    op = recipe["op"]

    # Helper to get standardized column
    def get_std_col(col_name):
        val = df[col_name].values.astype(np.float64)
        if train_means is not None and col_name in train_means:
            mean = train_means[col_name]
            std = train_stds[col_name]
        else:
            mean = np.nanmean(val)
            std = np.nanstd(val)
        if std < 1e-12:
            std = 1.0
        return (val - mean) / std

    def get_rank_col(col_name):
        """Return percentile-ranked column in [0, 1]."""
        val = df[col_name].values.astype(np.float64)
        n = len(val)
        if n < 2:
            return np.zeros(n)
        # Handle NaNs by filling with median before ranking
        med = np.nanmedian(val)
        val_filled = np.where(np.isnan(val), med, val)
        return rankdata(val_filled) / n

    # ─── 2-way operations ───────────────────────────────────────────────

    if op == "min":
        a_std = get_std_col(recipe["feature_a"])
        b_std = get_std_col(recipe["feature_b"])
        return np.minimum(a_std, b_std)

    elif op == "max":
        a_std = get_std_col(recipe["feature_a"])
        b_std = get_std_col(recipe["feature_b"])
        return np.maximum(a_std, b_std)

    elif op == "diff":
        a_std = get_std_col(recipe["feature_a"])
        b_std = get_std_col(recipe["feature_b"])
        return a_std - b_std

    elif op == "ratio":
        # Ratio uses raw values because B is assumed to be a positive-only scaling feature (vol/volume)
        a_val = df[recipe["feature_a"]].values.astype(np.float64)
        b_val = df[recipe["feature_b"]].values.astype(np.float64)
        return a_val / (np.abs(b_val) + 1e-5)

    elif op == "ifelse":
        cond_col = recipe["feature_cond"]
        cond_val = df[cond_col].values.astype(np.float64)

        # Get threshold (median of condition column)
        if train_medians is not None and cond_col in train_medians:
            thresh = train_medians[cond_col]
        else:
            thresh = np.nanmedian(cond_val)

        a_std = get_std_col(recipe["feature_a"])
        b_std = get_std_col(recipe["feature_b"])
        return np.where(cond_val > thresh, a_std, b_std)

    elif op == "mean":
        a_std = get_std_col(recipe["feature_a"])
        b_std = get_std_col(recipe["feature_b"])
        return (a_std + b_std) / 2.0

    elif op == "product":
        a_std = get_std_col(recipe["feature_a"])
        b_std = get_std_col(recipe["feature_b"])
        return a_std * b_std

    elif op == "abs_diff":
        a_std = get_std_col(recipe["feature_a"])
        b_std = get_std_col(recipe["feature_b"])
        return np.abs(a_std - b_std)

    elif op == "rank_min":
        a_rank = get_rank_col(recipe["feature_a"])
        b_rank = get_rank_col(recipe["feature_b"])
        return np.minimum(a_rank, b_rank)

    elif op == "rank_max":
        a_rank = get_rank_col(recipe["feature_a"])
        b_rank = get_rank_col(recipe["feature_b"])
        return np.maximum(a_rank, b_rank)

    elif op == "clamp_diff":
        a_std = get_std_col(recipe["feature_a"])
        b_std = get_std_col(recipe["feature_b"])
        return np.clip(a_std - b_std, -2.0, 2.0)

    # ─── 3-way operations ───────────────────────────────────────────────

    elif op == "tri_mean":
        a_std = get_std_col(recipe["feature_a"])
        b_std = get_std_col(recipe["feature_b"])
        c_std = get_std_col(recipe["feature_c"])
        return (a_std + b_std + c_std) / 3.0

    elif op == "tri_min":
        a_std = get_std_col(recipe["feature_a"])
        b_std = get_std_col(recipe["feature_b"])
        c_std = get_std_col(recipe["feature_c"])
        return np.minimum(np.minimum(a_std, b_std), c_std)

    elif op == "tri_max":
        a_std = get_std_col(recipe["feature_a"])
        b_std = get_std_col(recipe["feature_b"])
        c_std = get_std_col(recipe["feature_c"])
        return np.maximum(np.maximum(a_std, b_std), c_std)

    elif op == "tri_median":
        a_std = get_std_col(recipe["feature_a"])
        b_std = get_std_col(recipe["feature_b"])
        c_std = get_std_col(recipe["feature_c"])
        stacked = np.stack([a_std, b_std, c_std], axis=0)
        return np.median(stacked, axis=0)

    elif op == "tri_ifelse":
        # Nested regime: IfElse(cond1, A, IfElse(cond2, B, C))
        cond1_col = recipe["feature_cond"]
        cond2_col = recipe["feature_cond2"]
        cond1_val = df[cond1_col].values.astype(np.float64)
        cond2_val = df[cond2_col].values.astype(np.float64)

        if train_medians is not None and cond1_col in train_medians:
            thresh1 = train_medians[cond1_col]
        else:
            thresh1 = np.nanmedian(cond1_val)

        if train_medians is not None and cond2_col in train_medians:
            thresh2 = train_medians[cond2_col]
        else:
            thresh2 = np.nanmedian(cond2_val)

        a_std = get_std_col(recipe["feature_a"])
        b_std = get_std_col(recipe["feature_b"])
        c_std = get_std_col(recipe["feature_c"])

        inner = np.where(cond2_val > thresh2, b_std, c_std)
        return np.where(cond1_val > thresh1, a_std, inner)

    else:
        raise ValueError(f"Unknown operation in recipe: {op}")


def simulate_returns(y_true: np.ndarray, y_pred: np.ndarray, side: str, position_mode: str = "binary", enforce_absolute_sign: bool = True):
    """Simulate strategy daily returns based on tail signals.
    
    Supports binary vs score-weighted position sizing, absolute sign leg checks,
    and per-entry transition cost calculation (15 bps on position state changes).
    
    Returns (ann_return, sharpe, sortino, max_dd, raw_ann_return, raw_sharpe).
    """
    n = len(y_pred)
    if n < 10:
        return 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
        
    if np.max(y_pred) - np.min(y_pred) < 1e-12:
        return 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
        
    order = np.argsort(y_pred, kind="quicksort")
    pos = np.zeros(n, dtype=np.float64)
    
    std_pred = np.std(y_pred)
    mean_pred = np.mean(y_pred)
    
    if side == "long":
        pct = 0.15
        n_tail = max(5, int(n * pct))
        long_idx = order[-n_tail:]
        long_mean = float(np.mean(y_true[long_idx]))
        if not enforce_absolute_sign or long_mean > 0.0:
            if position_mode == "score_weighted" and std_pred > 1e-12:
                z = (y_pred[long_idx] - mean_pred) / std_pred
                pos[long_idx] = np.clip(z / 2.0, 0.0, 1.0)
            else:
                pos[long_idx] = 1.0

    elif side == "short":
        pct = 0.15
        n_tail = max(5, int(n * pct))
        short_idx = order[:n_tail]
        short_mean = float(np.mean(-y_true[short_idx]))  # expected short return
        if not enforce_absolute_sign or short_mean > 0.0:
            if position_mode == "score_weighted" and std_pred > 1e-12:
                z = (y_pred[short_idx] - mean_pred) / std_pred
                pos[short_idx] = -np.clip(-z / 2.0, 0.0, 1.0)
            else:
                pos[short_idx] = -1.0

    else:  # single (two-sided)
        pct = 0.10
        n_tail = max(5, int(n * pct))
        long_idx = order[-n_tail:]
        short_idx = order[:n_tail]
        long_mean = float(np.mean(y_true[long_idx]))
        short_mean = float(np.mean(-y_true[short_idx]))
        
        if not enforce_absolute_sign or long_mean > 0.0:
            if position_mode == "score_weighted" and std_pred > 1e-12:
                z = (y_pred[long_idx] - mean_pred) / std_pred
                pos[long_idx] = np.clip(z / 2.0, 0.0, 1.0)
            else:
                pos[long_idx] = 1.0
                
        if not enforce_absolute_sign or short_mean > 0.0:
            if position_mode == "score_weighted" and std_pred > 1e-12:
                z = (y_pred[short_idx] - mean_pred) / std_pred
                pos[short_idx] = -np.clip(-z / 2.0, 0.0, 1.0)
            else:
                pos[short_idx] = -1.0
        
    # Raw daily returns (pre-cost)
    raw_returns = pos * y_true
    raw_ann_return = float(np.mean(raw_returns) * 244)
    raw_ann_vol = float(np.std(raw_returns) * np.sqrt(244))
    raw_sharpe = float(raw_ann_return / (raw_ann_vol + 1e-10))

    # Per-entry transaction cost (15 bps = 0.0015 per position state transition)
    pos_prev = np.roll(pos, 1)
    pos_prev[0] = 0.0
    transitions = np.abs(pos - pos_prev)
    cost = transitions * 0.0015
    cost_returns = raw_returns - cost
    
    ann_return = float(np.mean(cost_returns) * 244)
    ann_vol = float(np.std(cost_returns) * np.sqrt(244))
    
    # Sharpe
    sharpe = float(ann_return / (ann_vol + 1e-10))
    
    # Sortino
    downside_returns = np.minimum(cost_returns, 0.0)
    downside_vol = float(np.std(downside_returns) * np.sqrt(244))
    sortino = float(ann_return / (downside_vol + 1e-10))
    
    # Max DD
    cum_returns = np.cumsum(cost_returns)
    running_max = np.maximum.accumulate(cum_returns)
    drawdowns = running_max - cum_returns
    max_dd = float(np.max(drawdowns)) if len(drawdowns) > 0 else 0.0
    
    return float(ann_return), float(sharpe), float(sortino), float(max_dd), float(raw_ann_return), float(raw_sharpe)



