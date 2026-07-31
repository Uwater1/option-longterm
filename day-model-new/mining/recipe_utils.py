import numpy as np
import pandas as pd
from scipy.stats import rankdata
from numba import njit, prange


@njit(cache=True)
def build_ecdf_grid_float32(val: np.ndarray, n_knots: int = 128):
    """Build 1D knots (xp, fp) for float32 linear interpolation from values."""
    clean = val[~np.isnan(val)].astype(np.float32)
    if len(clean) == 0:
        return np.array([0.0, 1.0], dtype=np.float32), np.array([0.5, 0.5], dtype=np.float32)
    clean.sort()
    quantiles = np.linspace(0.0, 1.0, n_knots).astype(np.float32)
    # Quantile interpolation over sorted clean array
    n = len(clean)
    xp = np.empty(n_knots, dtype=np.float32)
    for i in range(n_knots):
        q = quantiles[i]
        idx = q * (n - 1)
        i_low = int(idx)
        i_high = min(i_low + 1, n - 1)
        w = idx - i_low
        xp[i] = clean[i_low] * (1.0 - w) + clean[i_high] * w
    return xp, quantiles


@njit(parallel=True, cache=True)
def fast_ecdf_interp_float32(x: np.ndarray, xp: np.ndarray, fp: np.ndarray) -> np.ndarray:
    """Numba-accelerated fast 1D linear interpolation for ECDF mapping (fp32)."""
    n = len(x)
    out = np.empty(n, dtype=np.float32)
    n_knots = len(xp)
    for i in prange(n):
        v = x[i]
        if np.isnan(v):
            out[i] = np.float32(0.5)
        elif v <= xp[0]:
            out[i] = fp[0]
        elif v >= xp[n_knots - 1]:
            out[i] = fp[n_knots - 1]
        else:
            low = 0
            high = n_knots - 1
            while high - low > 1:
                mid = (low + high) // 2
                if xp[mid] <= v:
                    low = mid
                else:
                    high = mid
            denom = xp[high] - xp[low]
            if denom < 1e-12:
                out[i] = fp[low]
            else:
                t = (v - xp[low]) / denom
                out[i] = fp[low] + t * (fp[high] - fp[low])
    return out


def compute_recipe(df: pd.DataFrame, recipe: dict, train_means: dict = None, train_stds: dict = None, train_medians: dict = None, train_ecdfs: dict = None) -> np.ndarray:
    """
    Dynamically compute feature values from a recipe dictionary in FP32 single precision.
    Aligns scale by standardizing inputs for min/max/diff/ifelse using train_means/train_stds/train_ecdfs if provided.

    Supported 2-way ops: min, max, diff, ratio, ifelse, mean, product, abs_diff,
                         rank_min, rank_max, clamp_diff, z_sum, z_diff, sig_product, rel_diff
    Supported 3-way ops: tri_mean, tri_z_mean, tri_sig_max, tri_min, tri_max, tri_median, tri_ifelse
    """
    op = recipe["op"]

    # Helper to get standardized column in float32
    def get_std_col(col_name):
        val = df[col_name].values.astype(np.float32)
        if train_means is not None and col_name in train_means:
            mean = np.float32(train_means[col_name])
            std = np.float32(train_stds[col_name])
        else:
            mean = np.nanmean(val).astype(np.float32)
            std = np.nanstd(val).astype(np.float32)
        if std < 1e-7:
            std = np.float32(1.0)
        return (val - mean) / std

    def get_rank_col(col_name):
        """Return percentile-ranked column in [0, 1] via Numba fp32 ECDF mapping."""
        val32 = df[col_name].values.astype(np.float32)
        if train_ecdfs is not None and col_name in train_ecdfs:
            xp, fp = train_ecdfs[col_name]
        else:
            xp, fp = build_ecdf_grid_float32(val32, n_knots=128)
        return fast_ecdf_interp_float32(val32, xp, fp)


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
        a_val = df[recipe["feature_a"]].values.astype(np.float32)
        b_val = df[recipe["feature_b"]].values.astype(np.float32)
        return a_val / (np.abs(b_val) + np.float32(1e-5))

    elif op == "ifelse":
        cond_col = recipe["feature_cond"]
        cond_val = df[cond_col].values.astype(np.float32)

        # Get threshold (median of condition column)
        if train_medians is not None and cond_col in train_medians:
            thresh = np.float32(train_medians[cond_col])
        else:
            thresh = np.nanmedian(cond_val).astype(np.float32)

        a_std = get_std_col(recipe["feature_a"])
        b_std = get_std_col(recipe["feature_b"])
        return np.where(cond_val > thresh, a_std, b_std)

    elif op == "mean":
        a_std = get_std_col(recipe["feature_a"])
        b_std = get_std_col(recipe["feature_b"])
        return (a_std + b_std) * np.float32(0.5)

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
        return np.clip(a_std - b_std, np.float32(-2.0), np.float32(2.0))

    elif op == "z_sum":
        a_std = get_std_col(recipe["feature_a"])
        b_std = get_std_col(recipe["feature_b"])
        return a_std + b_std

    elif op == "z_diff":
        a_std = get_std_col(recipe["feature_a"])
        b_std = get_std_col(recipe["feature_b"])
        return a_std - b_std

    elif op == "sig_product":
        a_std = get_std_col(recipe["feature_a"])
        b_std = get_std_col(recipe["feature_b"])
        return np.sign(a_std) * np.abs(b_std)

    elif op == "rel_diff":
        a_std = get_std_col(recipe["feature_a"])
        b_std = get_std_col(recipe["feature_b"])
        return (a_std - b_std) / (np.abs(a_std) + np.abs(b_std) + np.float32(1e-5))

    # ─── 3-way operations ───────────────────────────────────────────────

    elif op == "tri_mean":
        a_std = get_std_col(recipe["feature_a"])
        b_std = get_std_col(recipe["feature_b"])
        c_std = get_std_col(recipe["feature_c"])
        return (a_std + b_std + c_std) / np.float32(3.0)

    elif op == "tri_z_mean":
        a_std = get_std_col(recipe["feature_a"])
        b_std = get_std_col(recipe["feature_b"])
        c_std = get_std_col(recipe["feature_c"])
        return (a_std + b_std + c_std) / np.float32(3.0)

    elif op == "tri_sig_max":
        a_std = get_std_col(recipe["feature_a"])
        b_std = get_std_col(recipe["feature_b"])
        c_std = get_std_col(recipe["feature_c"])
        sig_c = np.sign(c_std)
        return np.maximum(a_std * sig_c, b_std * sig_c)

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
        return np.median(stacked, axis=0).astype(np.float32)

    elif op == "tri_ifelse":
        # Nested regime: IfElse(cond1, A, IfElse(cond2, B, C))
        cond1_col = recipe["feature_cond"]
        cond2_col = recipe["feature_cond2"]
        cond1_val = df[cond1_col].values.astype(np.float32)
        cond2_val = df[cond2_col].values.astype(np.float32)

        if train_medians is not None and cond1_col in train_medians:
            thresh1 = np.float32(train_medians[cond1_col])
        else:
            thresh1 = np.nanmedian(cond1_val).astype(np.float32)

        if train_medians is not None and cond2_col in train_medians:
            thresh2 = np.float32(train_medians[cond2_col])
        else:
            thresh2 = np.nanmedian(cond2_val).astype(np.float32)

        a_std = get_std_col(recipe["feature_a"])
        b_std = get_std_col(recipe["feature_b"])
        c_std = get_std_col(recipe["feature_c"])

        inner = np.where(cond2_val > thresh2, b_std, c_std)
        return np.where(cond1_val > thresh1, a_std, inner)

    else:
        raise ValueError(f"Unknown operation in recipe: {op}")


def simulate_returns(y_true: np.ndarray, y_pred: np.ndarray, side: str, position_mode: str = "binary", enforce_absolute_sign: bool = True, conviction_z: float = 0.5):
    """Simulate strategy daily returns based on tail signals.
    
    Position modes:
      - "binary": Full position (1.0) on all tail-selected days.
      - "score_weighted": Scale position by z-score (legacy z/2 clip).
      - "conviction_weighted": Conviction gate + smooth tanh sizing.
        Only trades when prediction z-score > conviction_z threshold.
        Position size = tanh((z - conviction_z) / 1.5), giving smooth
        ramp from 0 at threshold to ~1.0 for strong signals.
        Reduces turnover by skipping low-conviction days.
    
    Args:
        conviction_z: Minimum z-score threshold for taking a position.
            Only used in "conviction_weighted" mode. Default 0.5.
    
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
    
    def _assign_positions(idx, direction, y_check_mean):
        """Assign positions to tail indices based on mode."""
        if enforce_absolute_sign and y_check_mean <= 0.0:
            return
        if position_mode == "conviction_weighted" and std_pred > 1e-12:
            z = direction * (y_pred[idx] - mean_pred) / std_pred
            # Conviction gate: only trade when z > threshold
            mask = z > conviction_z
            if np.any(mask):
                # Smooth tanh sizing: 0 at threshold, ~1.0 for strong signals
                sizes = np.tanh((z[mask] - conviction_z) / 1.5)
                pos[idx[mask]] = direction * sizes
        elif position_mode == "score_weighted" and std_pred > 1e-12:
            z = (y_pred[idx] - mean_pred) / std_pred
            if direction > 0:
                pos[idx] = np.clip(z / 2.0, 0.0, 1.0)
            else:
                pos[idx] = -np.clip(-z / 2.0, 0.0, 1.0)
        else:  # binary
            pos[idx] = direction * 1.0
    
    if side == "long":
        pct = 0.15
        n_tail = max(5, int(n * pct))
        long_idx = order[-n_tail:]
        long_mean = float(np.mean(y_true[long_idx]))
        _assign_positions(long_idx, 1.0, long_mean)

    elif side == "short":
        pct = 0.15
        n_tail = max(5, int(n * pct))
        short_idx = order[:n_tail]
        short_mean = float(np.mean(-y_true[short_idx]))
        _assign_positions(short_idx, -1.0, short_mean)

    else:  # single (two-sided)
        pct = 0.10
        n_tail = max(5, int(n * pct))
        long_idx = order[-n_tail:]
        short_idx = order[:n_tail]
        long_mean = float(np.mean(y_true[long_idx]))
        short_mean = float(np.mean(-y_true[short_idx]))
        _assign_positions(long_idx, 1.0, long_mean)
        _assign_positions(short_idx, -1.0, short_mean)
        
    # Raw daily returns (pre-cost)
    raw_returns = pos * y_true
    raw_ann_return = float(np.mean(raw_returns) * 244)
    raw_ann_vol = float(np.std(raw_returns) * np.sqrt(244))
    raw_sharpe = float(raw_ann_return / (raw_ann_vol + 1e-10))

    # Flat transaction cost per active trade day under strict intraday trading (10:00-14:35)
    # Round-trip cost = 8 bps (0.0008) per unit position active on that day
    cost = np.abs(pos) * 0.0008
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



