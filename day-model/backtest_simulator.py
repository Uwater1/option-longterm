"""
Lightweight look-ahead free trading simulator inside day-model.
Indicators are calculated using the index (features_{ETF}.parquet),
and trades are executed on the actual ETF 5m bars.
Strictly out-of-sample (OOS) evaluation (date >= 2024-03-01).
"""

import argparse
import sys
import os
import bisect
from pathlib import Path
import warnings

import numpy as np
import pandas as pd
import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Suppress sklearn/joblib warnings
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

# Add parent path to import custom penalties if needed
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))
try:
    from penalties import MCP_plus_L2
except ImportError:
    pass

try:
    from backtest_engine import select_underlying, load_data as load_engine_data, get_strike_by_level, _bs_price
except ImportError:
    pass


# Constants
LOCKBOX_DATE = "2024-03-01"
DEFAULT_COST_BPS = 15.0

# Files and columns mapping
ETF_5M_FILE = {
    "50ETF": "50ETF_5m.parquet",
    "300ETF": "510300_5m.parquet",
    "500ETF": "500ETF_5m.parquet",
    "588000ETF": "588000ETF_5m.parquet",
    "159915ETF": "159915ETF_5m.parquet",
}

# Single source of truth for decision and exit bars (from day-model/build_features.py)
EXIT_BAR = 42  # 14:35 close
DECISION_BAR = {
    "50ETF": 5,      # 10:00 close of bar 5, entry at open of bar 6
    "300ETF": 5,
    "500ETF": 5,
    "588000ETF": 5,
    "159915ETF": 5,
}

MODELS_DIR = ROOT_DIR / "day-model" / "models"
FEATURES_DIR = ROOT_DIR / "day-model" / "data"
ETF_5M_DIR = ROOT_DIR / "data"
PLOTS_DIR = ROOT_DIR / "day-model" / "plots"
ROLLING_MODELS_DIR = MODELS_DIR / "rolling"
ROLLING_DATA_DIR = ROOT_DIR / "day-model" / "data" / "rolling"

PLOTS_DIR.mkdir(parents=True, exist_ok=True)


def expanding_pct_rank(series: pd.Series, min_periods: int = 60) -> pd.Series:
    """Walk-forward percentile rank of each value relative to prior history.
    At time t, ranks series[t] against series[0 .. t-1].
    Output is in [0, 1].
    """
    vals = series.values
    n = len(vals)
    out = np.full(n, np.nan, dtype=float)
    sorted_buf = []
    for i in range(n):
        v = vals[i]
        if np.isnan(v):
            continue
        if len(sorted_buf) >= min_periods:
            out[i] = bisect.bisect_left(sorted_buf, v) / len(sorted_buf)
        bisect.insort(sorted_buf, float(v))
    return pd.Series(out, index=series.index)


def load_predictions(etf: str, target_transform: str = "gauss", early: bool = False, sharpe_objective: bool = False) -> tuple[pd.Series, pd.Series]:
    """Load static model predictions for both long and short sides."""
    # Load features
    feat_path = FEATURES_DIR / (f"features_{etf}_early.parquet" if early else f"features_{etf}.parquet")
    if not feat_path.exists():
        raise FileNotFoundError(f"Feature parquet not found: {feat_path}")
    df = pd.read_parquet(feat_path)

    suffix = f"_{target_transform}" if target_transform != "none" else ""
    if sharpe_objective:
        suffix += "_sharpe"
    early_suffix = "_early" if early else ""

    # 1. Long side
    long_model_path = MODELS_DIR / f"linear_{etf}_long{suffix}{early_suffix}.joblib"
    long_scaler_path = MODELS_DIR / f"scaler_{etf}_long{suffix}{early_suffix}.joblib"
    
    if not (long_model_path.exists() and long_scaler_path.exists()):
        raise FileNotFoundError(f"Long model/scaler not found for {etf} (transform: {target_transform}, early: {early})")
        
    long_model = joblib.load(long_model_path)
    long_scaler_meta = joblib.load(long_scaler_path)
    long_sel_feats = long_scaler_meta["selected_features"]
    
    X_long = df[long_sel_feats].copy()
    X_long = X_long.fillna(X_long.median().fillna(0.0))
    X_long_scaled = long_scaler_meta["scaler"].transform(X_long.values)
    long_pred = X_long_scaled @ long_model.coef_ + long_model.intercept_
    long_scores = pd.Series(long_pred, index=df.index)

    # 2. Short side
    short_model_path = MODELS_DIR / f"linear_{etf}_short{suffix}{early_suffix}.joblib"
    short_scaler_path = MODELS_DIR / f"scaler_{etf}_short{suffix}{early_suffix}.joblib"
    
    if not (short_model_path.exists() and short_scaler_path.exists()):
        raise FileNotFoundError(f"Short model/scaler not found for {etf} (transform: {target_transform}, early: {early})")
        
    short_model = joblib.load(short_model_path)
    short_scaler_meta = joblib.load(short_scaler_path)
    short_sel_feats = short_scaler_meta["selected_features"]
    
    X_short = df[short_sel_feats].copy()
    X_short = X_short.fillna(X_short.median().fillna(0.0))
    X_short_scaled = short_scaler_meta["scaler"].transform(X_short.values)
    short_pred = X_short_scaled @ short_model.coef_ + short_model.intercept_
    # Negate short predictions so high score = strong short conviction
    short_scores = -pd.Series(short_pred, index=df.index)

    return long_scores, short_scores


def load_predictions_rolling(etf: str, max_age_months: int = 6, target_transform: str = "gauss", early: bool = False, sharpe_objective: bool = False) -> tuple[pd.Series, pd.Series]:
    """Load rolling model predictions, auto-selecting the best model per date."""
    # Load features
    feat_path = FEATURES_DIR / (f"features_{etf}_early.parquet" if early else f"features_{etf}.parquet")
    if not feat_path.exists():
        raise FileNotFoundError(f"Feature parquet not found: {feat_path}")
    df = pd.read_parquet(feat_path)
    if "date" not in df.columns:
        df = df.reset_index()
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)

    suffix = f"_{target_transform}" if target_transform != "none" else ""
    if sharpe_objective:
        suffix += "_sharpe"
    early_suffix = "_early" if early else ""

    # Discover rolling models for this ETF
    rolling_models = []  # list of (lockbox_date, long_model, long_scaler, short_model, short_scaler)
    if ROLLING_MODELS_DIR.exists():
        glob_pattern = f"linear_{etf}_long_r*{suffix}{early_suffix}.joblib"
        for model_path in sorted(ROLLING_MODELS_DIR.glob(glob_pattern)):
            tag = model_path.stem.replace("linear_", "")
            
            # For rolling models, only use the champion sortino_blended configuration
            if "_sortino_blended" not in tag:
                continue
                
            scaler_path = ROLLING_MODELS_DIR / f"scaler_{tag}.joblib"
            
            parts = tag.split("_r")
            r_suffix = parts[1]
            
            short_tag = tag.replace("_long", "_short")
            short_model_path = ROLLING_MODELS_DIR / f"linear_{short_tag}.joblib"
            short_scaler_path = ROLLING_MODELS_DIR / f"scaler_{short_tag}.joblib"

            if not (scaler_path.exists() and short_model_path.exists() and short_scaler_path.exists()):
                continue

            # Parse lockbox date from tag suffix: YYYYMM
            lb_date = pd.Timestamp(f"{r_suffix[:4]}-{r_suffix[4:6]}-01")

            long_model = joblib.load(model_path)
            long_scaler_meta = joblib.load(scaler_path)
            short_model = joblib.load(short_model_path)
            short_scaler_meta = joblib.load(short_scaler_path)

            rolling_models.append({
                "lockbox": lb_date,
                "long_model": long_model, "long_scaler": long_scaler_meta,
                "short_model": short_model, "short_scaler": short_scaler_meta,
            })

    if not rolling_models:
        print(f"  [WARNING] No rolling models found for {etf} (transform: {target_transform}), falling back to static.")
        return load_predictions(etf, target_transform=target_transform, early=early, sharpe_objective=sharpe_objective)

    # Sort by lockbox date descending (most recent first)
    rolling_models.sort(key=lambda m: m["lockbox"], reverse=True)

    # Compute predictions for each model and stitch together
    long_scores = pd.Series(dtype=float)
    short_scores = pd.Series(dtype=float)
    remaining_mask = pd.Series(True, index=df.index)

    max_age = pd.DateOffset(months=max_age_months)

    for m in rolling_models:
        lb = m["lockbox"]
        # This model covers dates in [lb, lb + max_age)
        applicable_mask = remaining_mask & (df["date"] >= lb) & (df["date"] < lb + max_age)
        if not applicable_mask.any():
            continue

        # Long predictions
        long_sel = m["long_scaler"]["selected_features"]
        X_long = df.loc[applicable_mask, long_sel].copy()
        X_long = X_long.fillna(X_long.median().fillna(0.0))
        X_long_scaled = m["long_scaler"]["scaler"].transform(X_long.values)
        long_pred = X_long_scaled @ m["long_model"].coef_ + m["long_model"].intercept_
        long_s = pd.Series(long_pred, index=df.loc[applicable_mask, "date"])

        # Short predictions
        short_sel = m["short_scaler"]["selected_features"]
        X_short = df.loc[applicable_mask, short_sel].copy()
        X_short = X_short.fillna(X_short.median().fillna(0.0))
        X_short_scaled = m["short_scaler"]["scaler"].transform(X_short.values)
        short_pred = X_short_scaled @ m["short_model"].coef_ + m["short_model"].intercept_
        short_s = -pd.Series(short_pred, index=df.loc[applicable_mask, "date"])

        long_scores = pd.concat([long_scores, long_s])
        short_scores = pd.concat([short_scores, short_s])
        remaining_mask[applicable_mask] = False

    # Fill remaining dates with static model (if any)
    if remaining_mask.any():
        static_long_path = MODELS_DIR / f"linear_{etf}_long{suffix}.joblib"
        static_short_path = MODELS_DIR / f"linear_{etf}_short{suffix}.joblib"
        if static_long_path.exists() and static_short_path.exists():
            print(f"  [INFO] {remaining_mask.sum()} dates not covered by rolling, using static model.")
            static_long, static_short = load_predictions(etf, target_transform=target_transform, sharpe_objective=sharpe_objective)
            static_long = static_long[static_long.index.isin(df.loc[remaining_mask, "date"])]
            static_short = static_short[static_short.index.isin(df.loc[remaining_mask, "date"])]
            long_scores = pd.concat([long_scores, static_long])
            short_scores = pd.concat([short_scores, static_short])

    long_scores = long_scores.sort_index()
    short_scores = short_scores.sort_index()
    return long_scores, short_scores


def get_option_price(
    contract_id: str,
    bar_dt: pd.Timestamp,
    spot_px: float,
    strike_px: float,
    option_type: str,
    T: float,
    iv: float,
    r: float,
    opt_5m_by_id: dict | None,
    is_entry: bool = True,
) -> float:
    """Find option price at bar_dt (from opt_5m_by_id dict) or fall back to Black-Scholes pricing."""
    if opt_5m_by_id is not None and contract_id in opt_5m_by_id:
        contract_data = opt_5m_by_id[contract_id]
        # Try to match exact datetime first (O(1) index lookup)
        if bar_dt in contract_data.index:
            row_val = contract_data.loc[bar_dt]
            if isinstance(row_val, pd.DataFrame):
                row_val = row_val.iloc[0]
            val = float(row_val["open"]) if is_entry else float(row_val["close"])
            if val > 0:
                return val
        
        # Fallback to closest bar on the same day
        day_data = contract_data[contract_data.index.date == bar_dt.date()]
        if not day_data.empty:
            time_diff = (day_data.index - bar_dt).abs()
            closest_idx = time_diff.idxmin()
            closest_row = day_data.loc[closest_idx]
            if isinstance(closest_row, pd.DataFrame):
                closest_row = closest_row.iloc[0]
            val = float(closest_row["open"]) if is_entry else float(closest_row["close"])
            if val > 0:
                return val
    # Black-Scholes pricing fallback
    is_call = (option_type == "C")
    T_calc = max(1e-5, T)
    price = _bs_price(spot_px, strike_px, T_calc, r, iv, is_call)
    return max(0.0001, price)



def simulate_etf_trades(
    etf: str,
    signals: pd.DataFrame,
    stop_type: str | None,
    stop_val: float | None,
    cost_bps: float,
    asset_type: str = "ETF",
) -> pd.DataFrame:
    """Run trade simulation on the actual 5-minute ETF or Future bars."""
    # Load 5m ETF or Future data
    if asset_type == "Future":
        future_file_map = {
            "50ETF": "IH88_5m.parquet",
            "300ETF": "IF88_5m.parquet",
            "500ETF": "IC88_5m.parquet",
        }
        if etf not in future_file_map:
            print(f"  [WARNING] ETF {etf} has no corresponding future mapped.")
            return pd.DataFrame()
        path_5m = ETF_5M_DIR / future_file_map[etf]
    else:
        path_5m = ETF_5M_DIR / ETF_5M_FILE[etf]

    if not path_5m.exists():
        print(f"  [WARNING] 5m file not found: {path_5m}")
        return pd.DataFrame()
        
    df_5m = pd.read_parquet(path_5m)
    df_5m["datetime"] = pd.to_datetime(df_5m["datetime"])
    df_5m = df_5m.set_index("datetime").sort_index()

    # Precompute daily ATR14 (look-ahead free)
    daily_tr = df_5m.groupby(df_5m.index.date).agg(
        high=("high", "max"),
        low=("low", "min")
    )
    daily_tr["tr"] = daily_tr["high"] - daily_tr["low"]
    daily_tr["atr14"] = daily_tr["tr"].rolling(window=14, min_periods=1).mean()
    daily_tr["atr14_prev"] = daily_tr["atr14"].shift(1)
    atr_map = daily_tr["atr14_prev"].to_dict()

    # Group 5m data by date for quick access
    df_5m["date"] = df_5m.index.date
    grouped_5m = {d: g for d, g in df_5m.groupby("date")}

    decision_bar = DECISION_BAR[etf]
    entry_idx = decision_bar + 1

    trades = []
    
    for date, row in signals.iterrows():
        date_d = date.date()
        direction = int(row["direction"])
        if direction == 0:
            continue
            
        if date_d not in grouped_5m:
            continue
            
        day_bars = grouped_5m[date_d].reset_index(drop=True)
        L = len(day_bars)
        if L <= EXIT_BAR or entry_idx >= L:
            continue
            
        entry_price = float(day_bars.iloc[entry_idx]["open"])
        if entry_price <= 0:
            continue
            
        # Determine exit price & exit type
        exit_price = float(day_bars.iloc[EXIT_BAR]["close"])
        exit_type = "target"
        stop_level = np.nan
        
        # Check Stop Loss
        if stop_type == "pct" and stop_val is not None:
            if direction > 0:
                stop_level = entry_price * (1.0 - stop_val)
            else:
                stop_level = entry_price * (1.0 + stop_val)
        elif stop_type == "atr" and stop_val is not None:
            atr = atr_map.get(date_d, np.nan)
            if not np.isnan(atr):
                if direction > 0:
                    stop_level = entry_price - stop_val * atr
                else:
                    stop_level = entry_price + stop_val * atr
        elif stop_type == "struct":
            morning_bars = day_bars.iloc[:entry_idx]
            struct_low = float(morning_bars["low"].min())
            struct_high = float(morning_bars["high"].max())
            if direction > 0:
                stop_level = min(struct_low, entry_price * 0.999)
            else:
                stop_level = max(struct_high, entry_price * 1.001)
        elif stop_type == "struct_atr" and stop_val is not None:
            morning_bars = day_bars.iloc[:entry_idx]
            struct_low = float(morning_bars["low"].min())
            struct_high = float(morning_bars["high"].max())
            atr = atr_map.get(date_d, np.nan)
            if not np.isnan(atr):
                if direction > 0:
                    stop_level = struct_low - stop_val * atr
                else:
                    stop_level = struct_high + stop_val * atr

        # Scan for stop-loss hit from entry to exit
        if not np.isnan(stop_level):
            trade_bars = day_bars.iloc[entry_idx : EXIT_BAR + 1]
            for _, bar in trade_bars.iterrows():
                hi = float(bar["high"])
                lo = float(bar["low"])
                if direction > 0 and lo <= stop_level:
                    exit_price = stop_level
                    exit_type = "stop"
                    break
                elif direction < 0 and hi >= stop_level:
                    exit_price = stop_level
                    exit_type = "stop"
                    break

        # Calculate returns
        size = float(row.get("size", 1.0))
        gross = direction * (exit_price / entry_price - 1.0) * size
        net = gross - (cost_bps / 1e4) * size

        trades.append({
            "date": date,
            "direction": direction,
            "side": "long" if direction > 0 else "short",
            "entry_price": entry_price,
            "exit_price": exit_price,
            "exit_type": exit_type,
            "stop_level": stop_level,
            "gross_ret": gross,
            "net_ret": net,
            "long_rank": row["long_rank"],
            "short_rank": row["short_rank"],
            "size": size,
        })

    return pd.DataFrame(trades).set_index("date").sort_index()


def get_strike_by_level_lookahead_free(opt, entry_date, expiry_date, option_type, level, spot_price):
    """Select option strike price dynamically based on actual spot price at entry time."""
    day_opt = opt[
        (opt["date"] == entry_date) &
        (opt["maturity_date"] == expiry_date) &
        (opt["option_type"] == option_type) &
        (opt["close"] > 0)
    ].copy()
    if day_opt.empty:
        return None
    if option_type == "C":
        if level == 0:
            candidates = day_opt[day_opt["strike_price"] <= spot_price].sort_values("strike_price", ascending=False)
            idx = 0
        else:
            candidates = day_opt[day_opt["strike_price"] > spot_price].sort_values("strike_price")
            idx = level - 1
    else:
        if level == 0:
            candidates = day_opt[day_opt["strike_price"] >= spot_price].sort_values("strike_price", ascending=True)
            idx = 0
        else:
            candidates = day_opt[day_opt["strike_price"] < spot_price].sort_values("strike_price", ascending=False)
            idx = level - 1
    if idx >= 0 and idx < len(candidates):
        return candidates.iloc[idx].to_dict()
    return None


def simulate_option_trades(
    etf: str,
    signals: pd.DataFrame,
    stop_type: str | None,
    stop_val: float | None,
    opt: pd.DataFrame,
    etf_daily: pd.DataFrame,
    opt_5m: pd.DataFrame | None,
) -> pd.DataFrame:
    """Run option trade simulation, buying the nearest OTM call/put contract.
    Assumes 2 RMB commission per contract per side (4 RMB round-trip) and 1% slippage.
    """
    path_5m = ETF_5M_DIR / ETF_5M_FILE[etf]
    if not path_5m.exists():
        print(f"  [WARNING] 5m file not found: {path_5m}")
        return pd.DataFrame()

    df_5m = pd.read_parquet(path_5m)
    df_5m["datetime"] = pd.to_datetime(df_5m["datetime"])
    df_5m = df_5m.set_index("datetime").sort_index()

    # Precompute daily ATR14 (look-ahead free)
    daily_tr = df_5m.groupby(df_5m.index.date).agg(
        high=("high", "max"),
        low=("low", "min")
    )
    daily_tr["tr"] = daily_tr["high"] - daily_tr["low"]
    daily_tr["atr14"] = daily_tr["tr"].rolling(window=14, min_periods=1).mean()
    daily_tr["atr14_prev"] = daily_tr["atr14"].shift(1)
    atr_map = daily_tr["atr14_prev"].to_dict()

    # Group 5m data by date for quick access
    df_5m["date"] = df_5m.index.date
    grouped_5m = {d: g for d, g in df_5m.groupby("date")}

    expiries = (
        opt.groupby(["maturity_date", "option_type"])["order_book_id"]
        .nunique()
        .unstack("option_type")
        .dropna()
        .index.tolist()
    )
    expiries = sorted(expiries)

    # Pre-group opt_5m by order_book_id for O(1) dictionary lookups
    opt_5m_by_id = None
    if opt_5m is not None and not opt_5m.empty:
        opt_5m_by_id = {}
        for cid, g in opt_5m.groupby("order_book_id"):
            opt_5m_by_id[cid] = g.set_index("datetime").sort_index()

    decision_bar = DECISION_BAR[etf]
    entry_idx = decision_bar + 1

    trades = []

    for date, row in signals.iterrows():
        date_d = date.date()
        direction = int(row["direction"])
        if direction == 0:
            continue

        if date_d not in grouped_5m:
            continue

        day_bars = grouped_5m[date_d].reset_index()
        L = len(day_bars)
        if L <= EXIT_BAR or entry_idx >= L:
            continue

        spot_entry = float(day_bars.iloc[entry_idx]["open"])
        spot_exit = float(day_bars.iloc[EXIT_BAR]["close"])
        if spot_entry <= 0 or spot_exit <= 0:
            continue

        # Find next expiry with at least 5 days to maturity (Avoid 5 day to maturity rule)
        expiry_date = None
        for exp in expiries:
            if exp > date:
                if (exp - date).days >= 5:
                    expiry_date = exp
                    break
        if expiry_date is None:
            continue

        # Select closest OTM option
        option_type = "C" if direction > 0 else "P"
        leg = get_strike_by_level_lookahead_free(opt, date, expiry_date, option_type, level=1, spot_price=spot_entry)
        if leg is None:
            continue

        contract_id = leg["order_book_id"]
        strike_price = float(leg["strike_price"])
        contract_multiplier = float(leg.get("contract_multiplier", 10000.0))

        # Time to expiry
        T_entry = (expiry_date - date).days / 365.0
        elapsed_hours = (EXIT_BAR - entry_idx) * 5 / 60.0
        T_exit = max(1e-5, T_entry - (elapsed_hours / (24.0 * 365.0)))

        # IV fallback
        iv = etf_daily.loc[date.normalize(), "iv"] if "iv" in etf_daily.columns else np.nan
        if pd.isna(iv) or iv <= 0:
            iv = 0.20

        # Entry option price
        entry_px = get_option_price(
            contract_id, day_bars.iloc[entry_idx]["datetime"],
            spot_entry, strike_price, option_type, T_entry, iv, 0.02, opt_5m_by_id, is_entry=True
        )

        exit_spot = spot_exit
        exit_type = "target"
        stop_level = np.nan
        exit_bar_idx = EXIT_BAR

        # Check Stop Loss on ETF price
        if stop_type == "pct" and stop_val is not None:
            if direction > 0:
                stop_level = spot_entry * (1.0 - stop_val)
            else:
                stop_level = spot_entry * (1.0 + stop_val)
        elif stop_type == "atr" and stop_val is not None:
            atr = atr_map.get(date_d, np.nan)
            if not np.isnan(atr):
                if direction > 0:
                    stop_level = spot_entry - stop_val * atr
                else:
                    stop_level = spot_entry + stop_val * atr
        elif stop_type == "struct":
            morning_bars = day_bars.iloc[:entry_idx]
            struct_low = float(morning_bars["low"].min())
            struct_high = float(morning_bars["high"].max())
            if direction > 0:
                stop_level = min(struct_low, spot_entry * 0.999)
            else:
                stop_level = max(struct_high, spot_entry * 1.001)
        elif stop_type == "struct_atr" and stop_val is not None:
            morning_bars = day_bars.iloc[:entry_idx]
            struct_low = float(morning_bars["low"].min())
            struct_high = float(morning_bars["high"].max())
            atr = atr_map.get(date_d, np.nan)
            if not np.isnan(atr):
                if direction > 0:
                    stop_level = struct_low - stop_val * atr
                else:
                    stop_level = struct_high + stop_val * atr

        if not np.isnan(stop_level):
            trade_bars = day_bars.iloc[entry_idx : EXIT_BAR + 1]
            for idx_bar, bar in enumerate(trade_bars.itertuples()):
                hi = float(bar.high)
                lo = float(bar.low)
                if direction > 0 and lo <= stop_level:
                    exit_spot = stop_level
                    exit_type = "stop"
                    exit_bar_idx = entry_idx + idx_bar
                    break
                elif direction < 0 and hi >= stop_level:
                    exit_spot = stop_level
                    exit_type = "stop"
                    exit_bar_idx = entry_idx + idx_bar
                    break

        # Calculate decay/time at exit bar
        elapsed_hours_exit = (exit_bar_idx - entry_idx) * 5 / 60.0
        T_exit_actual = max(1e-5, T_entry - (elapsed_hours_exit / (24.0 * 365.0)))

        exit_px = get_option_price(
            contract_id, day_bars.iloc[exit_bar_idx]["datetime"],
            exit_spot, strike_price, option_type, T_exit_actual, iv, 0.02, opt_5m_by_id, is_entry=False
        )

        # Apply 1% slippage & 2 RMB commission per side
        entry_px_slip = entry_px * 1.01
        exit_px_slip = exit_px * 0.99

        size = float(row.get("size", 1.0))
        gross_pnl_rmb = (exit_px_slip - entry_px_slip) * contract_multiplier
        net_pnl_rmb = (gross_pnl_rmb - 4.0) * size  # 2 RMB round-trip per leg/contract = 4 RMB total

        # Return relative to the premium paid (option capital outlay)
        premium_paid = entry_px_slip * contract_multiplier
        # Note: both return and absolute P&L are scaled by size
        net_ret = (net_pnl_rmb / premium_paid if premium_paid > 0 else 0.0)
        gross_ret = ((exit_px - entry_px) / entry_px if entry_px > 0 else 0.0) * size

        trades.append({
            "date": date,
            "direction": direction,
            "side": "long" if direction > 0 else "short",
            "entry_price": entry_px,
            "exit_price": exit_px,
            "exit_type": exit_type,
            "stop_level": stop_level,
            "gross_ret": gross_ret,
            "net_ret": net_ret,
            "long_rank": row["long_rank"],
            "short_rank": row["short_rank"],
            "contract": contract_id,
            "strike": strike_price,
            "multiplier": contract_multiplier,
            "spot_entry": spot_entry,
            "spot_exit": exit_spot,
            "net_pnl_rmb": net_pnl_rmb,
            "size": size,
        })

    if not trades:
        return pd.DataFrame()

    return pd.DataFrame(trades).set_index("date").sort_index()


def summarize_trades(trades: pd.DataFrame, etf_name: str) -> dict:
    """Compute backtest metrics from a trades DataFrame."""
    if trades.empty:
        return {
            "n_trades": 0, "n_long": 0, "n_short": 0, "win_rate": 0.0,
            "mean_net_ret": 0.0, "total_net_ret": 0.0, "sharpe": 0.0,
            "max_dd": 0.0, "n_stopped": 0,
        }
        
    rets = trades["net_ret"].values
    n = len(rets)
    n_long = int((trades["direction"] > 0).sum())
    n_short = int((trades["direction"] < 0).sum())
    n_stopped = int((trades["exit_type"] == "stop").sum())
    
    win_rate = float((rets > 0).mean()) if n > 0 else 0.0
    mean_ret = float(np.mean(rets)) if n > 0 else 0.0
    total_ret = float(np.sum(rets)) if n > 0 else 0.0
    
    # Sharpe ratio
    std_ret = np.std(rets, ddof=1) if n > 1 else 0.0
    sharpe = float(mean_ret / std_ret * np.sqrt(252)) if std_ret > 1e-8 else 0.0
    
    # Drawdown
    cum_ret = np.cumsum(rets)
    cum_peak = np.maximum.accumulate(cum_ret)
    dd = cum_peak - cum_ret
    max_dd = float(np.max(dd)) if len(dd) > 0 else 0.0

    return {
        "n_trades": n,
        "n_long": n_long,
        "n_short": n_short,
        "win_rate": win_rate,
        "mean_net_ret": mean_ret,
        "total_net_ret": total_ret,
        "sharpe": sharpe,
        "max_dd": max_dd,
        "n_stopped": n_stopped,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-e", "--etf", default="all", help="ETF name: 300ETF|50ETF|500ETF|588000ETF|159915ETF|all")
    ap.add_argument("--type", choices=["ETF", "Future"], default="ETF", help="Asset type: ETF or Future")
    ap.add_argument("--long-thr", type=float, default=90.0, help="Long rank threshold (percentile: 0 to 100)")
    ap.add_argument("--short-thr", type=float, default=90.0, help="Short rank threshold (percentile: 0 to 100)")
    ap.add_argument("--cost-bps", type=float, default=DEFAULT_COST_BPS, help="Transaction cost in bps")
    ap.add_argument("--min-periods", type=int, default=60, help="Expanding rank warmup period")
    ap.add_argument("--stop-type", choices=["pct", "atr", "struct", "struct_atr"], default=None, help="Stop loss type")
    ap.add_argument("--stop-val", type=float, default=None, help="Stop loss parameter value (pct like 0.005 or ATR multiplier like 1.0)")
    ap.add_argument("--rolling", action="store_true",
                    help="Use rolling models for predictions (auto-select per date, fall back to static).")
    ap.add_argument("--max-age-months", type=int, default=6,
                    help="Max age in months for rolling model coverage (default 6).")
    ap.add_argument("--target-transform", default="none", choices=["none", "rank", "gauss"],
                    help="Target transform to load: none|rank|gauss")
    ap.add_argument("--early", action="store_true",
                    help="Use early-window models & features (10:00 to 13:05)")
    ap.add_argument("--sharpe-objective", action="store_true", dest="sharpe_objective", default=False,
                    help="Use models trained with validation set tail-Sharpe objective instead of Tail IC. Set to False by default, use --sharpe-objective to enable.")
    ap.add_argument("--option", action="store_true",
                    help="Trade nearest OTM option instead of ETF/Future")
    ap.add_argument("--garch-gate", action="store_true",
                    help="Enable look-ahead free multi-scale GARCH gating layer")
    ap.add_argument("--turbulent-thr", type=float, default=92.0,
                    help="Signal threshold in Turbulent volatility regime")
    ap.add_argument("--turbulent-size", type=float, default=0.8,
                    help="Position sizing scale in Turbulent volatility regime")
    ap.add_argument("--crisis-thr", type=float, default=98.0,
                    help="Signal threshold in Crisis volatility regime")
    ap.add_argument("--crisis-size", type=float, default=0.2,
                    help="Position sizing scale in Crisis volatility regime")
    ap.add_argument("--hmm-gate", action="store_true",
                    help="Enable look-ahead free HMM gating layer (3D: returns, vol20, amihud)")
    args = ap.parse_args()

    if args.hmm_gate and args.garch_gate:
        ap.error("Cannot specify both --hmm-gate and --garch-gate")

    global EXIT_BAR
    if args.early:
        EXIT_BAR = 24

    etfs = ["50ETF", "300ETF", "500ETF", "588000ETF", "159915ETF"]
    if args.etf != "all":
        # Handle formats like "300", "300ETF", "IH", "IF", "IC", "IM"
        val = args.etf.upper()
        mapping = {
            "50": "50ETF", "50ETF": "50ETF", "IH": "50ETF", "IH88": "50ETF",
            "300": "300ETF", "300ETF": "300ETF", "IF": "300ETF", "IF88": "300ETF",
            "500": "500ETF", "500ETF": "500ETF", "IC": "500ETF", "IC88": "500ETF",
            "588000": "588000ETF", "588000ETF": "588000ETF",
            "159915": "159915ETF", "159915ETF": "159915ETF",
        }
        if val in ["IM", "IM88"]:
            print(f"[ERROR] IM (CSI 1000) future is not supported/traded in this simulator.")
            sys.exit(1)
        if val in mapping:
            target_etf = mapping[val]
        else:
            print(f"[ERROR] Unknown ETF/Future: {args.etf}")
            sys.exit(1)
        etfs = [target_etf]

    print("=" * 80)
    print(f"DAY-MODEL WALK-FORWARD OOS SIMULATOR")
    print(f"OOS Period : {LOCKBOX_DATE} onwards")
    print(f"Asset Type : {args.type}")
    print(f"Models     : {'ROLLING (auto-select per date)' if args.rolling else 'STATIC'} (Early: {args.early})")
    print(f"Thresholds : Long={args.long_thr}%, Short={args.short_thr}%")
    print(f"Stops      : Type={args.stop_type}, Val={args.stop_val}")
    print(f"Cost       : {args.cost_bps} bps")
    print(f"Exit Bar   : {EXIT_BAR}")
    print("=" * 80)

    all_trades = {}
    combined_df_list = []

    for etf in etfs:
        if args.type == "Future" and etf not in ["50ETF", "300ETF", "500ETF"]:
            print(f"[{etf}] Not traded as Future. Skipping.")
            print("-" * 50)
            continue

        name_map = {
            "50ETF": "IH",
            "300ETF": "IF",
            "500ETF": "IC",
        }
        display_name = name_map.get(etf, etf) if args.type == "Future" else etf

        try:
            # 1. Predictions
            if args.rolling:
                long_scores, short_scores = load_predictions_rolling(
                    etf, max_age_months=args.max_age_months, target_transform=args.target_transform, early=args.early, sharpe_objective=args.sharpe_objective
                )
            else:
                long_scores, short_scores = load_predictions(etf, target_transform=args.target_transform, early=args.early, sharpe_objective=args.sharpe_objective)
            
            # 2. Expanding Percentile Ranks (walk-forward, look-ahead free)
            long_rank = expanding_pct_rank(long_scores, min_periods=args.min_periods)
            short_rank = expanding_pct_rank(short_scores, min_periods=args.min_periods)
            
            # Align indices
            common_idx = long_rank.index.intersection(short_rank.index)
            long_rank = long_rank.loc[common_idx]
            short_rank = short_rank.loc[common_idx]
            
            # Generate signals
            if args.hmm_gate:
                from hmm_regime import generate_hmm_regimes
                regime_df = generate_hmm_regimes(etf, force=False)
                # Map date (as pd.Timestamp) to look-ahead free state signal
                regime_map = regime_df.set_index("date")["state_signal"].to_dict()
                
                # We need dynamic thresholding and sizing per timestamp
                direction_vals = []
                size_vals = []
                
                for t in common_idx:
                    # Look up HMM regime state (0=Calm, 1=Steady, 2=Turbulent, 3=Crisis)
                    state = regime_map.get(t, 0)
                    
                    if state == 0 or state == 1: # Calm or Steady
                        l_thr = args.long_thr
                        s_thr = args.short_thr
                        sz = 1.0
                    elif state == 2: # Turbulent
                        l_thr = args.turbulent_thr
                        s_thr = args.turbulent_thr
                        sz = args.turbulent_size
                    elif state == 3: # Crisis
                        # Dynamic category routing: Value ETFs (50, 300, 500) vs Growth/Tech ETFs (588000, 159915)
                        if etf in ["50ETF", "300ETF", "500ETF"]:
                            l_thr = 101.0 # Shut down long trading completely
                            s_thr = args.crisis_thr
                            sz = args.crisis_size
                        else:
                            # Growth ETFs (STAR 50, Chinext) keep trading long during Crisis
                            l_thr = args.crisis_thr
                            s_thr = args.crisis_thr
                            sz = 1.0 # Full size for tech crisis alpha!
                    else:
                        l_thr = args.long_thr
                        s_thr = args.short_thr
                        sz = 1.0
                        
                    l_val = long_rank.loc[t]
                    s_val = short_rank.loc[t]
                    
                    l_fire = l_val >= (l_thr / 100.0)
                    s_fire = s_val >= (s_thr / 100.0)
                    
                    if l_fire and not s_fire:
                        d = 1
                    elif s_fire and not l_fire:
                        d = -1
                    elif l_fire and s_fire:
                        l_margin = l_val / max(l_thr / 100.0, 1e-12)
                        s_margin = s_val / max(s_thr / 100.0, 1e-12)
                        d = 1 if l_margin >= s_margin else -1
                    else:
                        d = 0
                        
                    direction_vals.append(d)
                    size_vals.append(sz)
                    
                direction = pd.Series(direction_vals, index=common_idx, dtype=int)
                size = pd.Series(size_vals, index=common_idx, dtype=float)
            elif args.garch_gate:
                from garch_regime import generate_garch_regimes
                regime_df = generate_garch_regimes(etf, force=False)
                # Map date (as pd.Timestamp) to look-ahead free state signal
                regime_map = regime_df.set_index("date")["state_signal"].to_dict()
                
                # We need dynamic thresholding and sizing per timestamp
                direction_vals = []
                size_vals = []
                
                for t in common_idx:
                    # Look up regime state
                    state = regime_map.get(t, 0) # default to Calm (0) if missing
                    
                    if state == 0: # Calm
                        l_thr = args.long_thr
                        s_thr = args.short_thr
                        sz = 1.0
                    elif state == 1: # Turbulent
                        l_thr = args.turbulent_thr
                        s_thr = args.turbulent_thr
                        sz = args.turbulent_size
                    elif state == 2: # Crisis
                        l_thr = args.crisis_thr
                        s_thr = args.crisis_thr
                        sz = args.crisis_size
                    else:
                        l_thr = args.long_thr
                        s_thr = args.short_thr
                        sz = 1.0
                        
                    l_val = long_rank.loc[t]
                    s_val = short_rank.loc[t]
                    
                    l_fire = l_val >= (l_thr / 100.0)
                    s_fire = s_val >= (s_thr / 100.0)
                    
                    if l_fire and not s_fire:
                        d = 1
                    elif s_fire and not l_fire:
                        d = -1
                    elif l_fire and s_fire:
                        # Conflict resolution: higher margin wins
                        l_margin = l_val / max(l_thr / 100.0, 1e-12)
                        s_margin = s_val / max(s_thr / 100.0, 1e-12)
                        d = 1 if l_margin >= s_margin else -1
                    else:
                        d = 0
                        
                    direction_vals.append(d)
                    size_vals.append(sz)
                    
                direction = pd.Series(direction_vals, index=common_idx, dtype=int)
                size = pd.Series(size_vals, index=common_idx, dtype=float)
            else:
                long_fires = long_rank >= (args.long_thr / 100.0)
                short_fires = short_rank >= (args.short_thr / 100.0)
                
                long_margin = long_rank / max(args.long_thr / 100.0, 1e-12)
                short_margin = short_rank / max(args.short_thr / 100.0, 1e-12)
                both_fire = long_fires & short_fires
                
                direction = pd.Series(0, index=common_idx, dtype=int)
                direction[long_fires & ~both_fire] = 1
                direction[short_fires & ~both_fire] = -1
                # Conflict resolution: higher margin wins
                direction[both_fire & (long_margin >= short_margin)] = 1
                direction[both_fire & (long_margin < short_margin)] = -1
                
                size = pd.Series(1.0, index=common_idx, dtype=float)
                
            signals = pd.DataFrame({
                "direction": direction,
                "long_rank": long_rank,
                "short_rank": short_rank,
                "size": size
            })
            
            # Filter strictly for OOS period
            signals_oos = signals[signals.index >= pd.Timestamp(LOCKBOX_DATE)]
            
            # 3. Simulate execution on ETF 5m or Future 5m, or Options
            if args.option:
                # Load option daily data using backtest_engine
                from backtest_engine import select_underlying, load_data as load_engine_data
                etf_choice = {"50ETF": "50", "300ETF": "300", "500ETF": "500", "588000ETF": "588000", "159915ETF": "159915"}[etf]
                select_underlying(etf_choice)
                inst, opt_daily, etf_daily = load_engine_data()
                
                # Reindex to prevent KeyErrors on missing dates
                all_dates = signals_oos.index.normalize().union(etf_daily.index)
                etf_daily = etf_daily.reindex(all_dates).ffill()
                
                # Check for 5m option price data and download if missing
                opt_5m_path = ETF_5M_DIR / f"{etf}_historical_prices_5m.parquet"
                if not opt_5m_path.exists():
                    print(f"  [INFO] 5m option data not found for {etf}. Attempting to download...")
                    try:
                        import subprocess
                        subprocess.run([sys.executable, str(ROOT_DIR / "download_5m_data.py")], check=True)
                    except Exception as e:
                        print(f"  [WARNING] Failed to run download_5m_data.py: {e}")
                
                if opt_5m_path.exists():
                    print(f"Loading 5m option data from {opt_5m_path}...")
                    opt_5m = pd.read_parquet(opt_5m_path)
                    opt_5m["datetime"] = pd.to_datetime(opt_5m["datetime"])
                else:
                    print(f"  [INFO] 5m option data still not found for {etf}, using Black-Scholes pricing fallback.")
                    opt_5m = None
                
                trades = simulate_option_trades(
                    etf, signals_oos, args.stop_type, args.stop_val,
                    opt_daily, etf_daily, opt_5m
                )
            else:
                trades = simulate_etf_trades(
                    etf, signals_oos, args.stop_type, args.stop_val, args.cost_bps, asset_type=args.type
                )
            
            if not trades.empty:
                all_trades[etf] = trades
                # Save details for combined portfolio
                # Add etf column
                t_df = trades[["net_ret"]].copy()
                t_df.columns = [f"{display_name}_net"]
                combined_df_list.append(t_df)
                
                # Print single ETF/Future summary
                metrics = summarize_trades(trades, display_name)
                
                is_option = args.option
                ret_unit = "%" if is_option else "bps"
                ret_scale = 100.0 if is_option else 1e4
                
                print(f"[{display_name}] OOS Summary:")
                print(f"  Trades  : {metrics['n_trades']} (Long: {metrics['n_long']}, Short: {metrics['n_short']})")
                print(f"  Win Rate: {metrics['win_rate']:.1%} | Avg Net Return: {metrics['mean_net_ret']*ret_scale:.2f} {ret_unit}")
                print(f"  P&L     : {metrics['total_net_ret']*ret_scale:+.2f} {ret_unit} | Sharpe: {metrics['sharpe']:.2f} | MaxDD: {metrics['max_dd']*ret_scale:.2f} {ret_unit}")
                if args.stop_type:
                    print(f"  Stopped : {metrics['n_stopped']} times ({metrics['n_stopped'] / metrics['n_trades']:.1%})")
                
                # Yearly OOS breakdown
                print("  Yearly Breakdown:")
                for year, g in trades.groupby(trades.index.year):
                    y_metrics = summarize_trades(g, display_name)
                    print(f"    {year}: n={y_metrics['n_trades']:>3}, wr={y_metrics['win_rate']:.1%}, pnl={y_metrics['total_net_ret']*ret_scale:+.2f}{ret_unit}, sharpe={y_metrics['sharpe']:.2f}")
                print("-" * 50)
            else:
                print(f"[{display_name}] No OOS trades triggered.")
                print("-" * 50)
                
        except Exception as e:
            print(f"[ERROR] Failed simulating {etf}: {e}")
            import traceback
            traceback.print_exc()

    # 4. Combined Portfolio Simulation (Equal capital distribution on active trades)
    if len(combined_df_list) > 1:
        # Merge all returns side by side
        merged = pd.concat(combined_df_list, axis=1).fillna(0.0)
        # Average return for days when there is at least one trade
        # Capital is equally split among all ETFs traded on that day
        # To compute this correctly: daily portfolio return is mean of daily returns across all 5 ETFs.
        # (If an ETF is not trading, its return is 0 on that day).
        portfolio_rets = merged.mean(axis=1)
        
        # Build a synthetic trade frame to use summarize_trades helper
        port_trades = pd.DataFrame({
            "direction": np.ones(len(portfolio_rets)),  # dummy direction
            "exit_type": ["target"] * len(portfolio_rets),
            "net_ret": portfolio_rets.values
        }, index=portfolio_rets.index)
        
        metrics = summarize_trades(port_trades, "Portfolio")
        
        # Calculate active days count
        active_days = (merged != 0).any(axis=1).sum()
        
        is_option = args.option
        ret_unit = "%" if is_option else "bps"
        ret_scale = 100.0 if is_option else 1e4

        print("\n" + "=" * 80)
        print("COMBINED EQUAL-WEIGHT PORTFOLIO SUMMARY (OOS ONLY)")
        print("=" * 80)
        print(f"  Active Days     : {active_days} days")
        print(f"  Avg Net Return  : {metrics['mean_net_ret']*ret_scale:.2f} {ret_unit}")
        print(f"  Cumulative P&L  : {metrics['total_net_ret']*ret_scale:+.2f} {ret_unit}")
        print(f"  Annual Sharpe   : {metrics['sharpe']:.2f}")
        print(f"  Max Drawdown    : {metrics['max_dd']*ret_scale:.2f} {ret_unit}")
        
        print("  Yearly Breakdown:")
        for year, g in port_trades.groupby(port_trades.index.year):
            y_metrics = summarize_trades(g, "Portfolio")
            print(f"    {year}: n_days={len(g)}, pnl={y_metrics['total_net_ret']*ret_scale:+.2f}{ret_unit}, sharpe={y_metrics['sharpe']:.2f}")
        print("=" * 80)

        # Plot cumulative performance
        plt.figure(figsize=(10, 6))
        for col in merged.columns:
            plt.plot(np.cumsum(merged[col]) * 100, label=col.replace("_net", ""), alpha=0.5)
        plt.plot(np.cumsum(portfolio_rets) * 100, label="COMBINED PORTFOLIO", color="black", linewidth=2.5)
        plt.title(f"Out-of-Sample Walk-Forward Cumulative Net P&L (from {LOCKBOX_DATE}) ({'Option' if is_option else args.type})")
        plt.xlabel("Date")
        plt.ylabel("Net Return (%)")
        plt.grid(True, linestyle="--", alpha=0.6)
        plt.legend()
        
        asset_type = "option" if is_option else args.type.lower()
        model_type = "roll" if args.rolling else "stat"
        early_suffix = "_early" if args.early else ""
        plot_path = PLOTS_DIR / f"bs_oos_{asset_type}_{model_type}{early_suffix}.png"
        plt.savefig(plot_path, dpi=150, bbox_inches="tight")
        print(f"Saved performance chart to: {plot_path}")
        plt.close()


if __name__ == "__main__":
    main()
