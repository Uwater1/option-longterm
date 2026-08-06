#!/usr/bin/env python3
"""
Main CLI Backtest Runner for NewTrade framework.
Runs full pipeline:
  1. Load admitted pools & raw ETF datasets.
  2. Compute zero-lookahead expanding z-score standardization over history.
  3. Aggregate composite signal Z_composite using chosen weighting scheme.
  4. Filter to target OOS period (default: 2022-01-01 to 2026-01-01).
  5. Apply conviction threshold & position sizing.
  6. Simulate ETF spot backtest with 8 bps friction.
  7. Output markdown performance report & JSON results.
"""

import sys
import json
import argparse
from pathlib import Path
import pandas as pd
import numpy as np

# Path resolution
HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent

from utils import load_admitted_pool, load_etf_dataset, build_pool_feature_matrix, expanding_zscore_numba, expanding_factor_ic_numba, expanding_factor_score_numba, rolling_tail_ic_numba, rolling_factor_risk_numba, composite_tailic_risk_score, load_future_trade_returns, load_cluster_assignments
from weighting import get_weighting_scheme, compute_icw_hysteresis, adaptive_exit_rank
from strategy import generate_positions, simulate_etf_spot, calculate_metrics, sweep_optimal_threshold, compute_production_threshold, build_trade_log_df
from robustness import deflated_sharpe_ratio, run_cpcv_backtest
from option_strategy import simulate_option_portfolio, DEFAULT_OPT_STOPLOSS_MODE, DEFAULT_OPT_STOPLOSS_PARAM, STRIKE_MODES, resolve_strike_mode
from research_stoploss import load_intraday_bars_dict, simulate_full_series

AVAILABLE_ETFS = ["300ETF", "500ETF", "50ETF", "159915ETF"]
ALL_SCHEMES = ["ensemble", "icw", "sortino", "ew"]  # --scheme all: ENSEMBLE primary (2026-08)
ENSEMBLE_SCHEMES = ["icw", "ew"]  # schemes averaged in ensemble
DEFAULT_SCORE_BLEND_W_IC = 1.0  # Pure 100% TailIC for EW selection (Sortino<=0 gate handles risk)


def resolve_ic_ema_span(etf: str, user_span: int | None = None) -> int:
    """Resolve ETF-adaptive EMA span: 60d for 300ETF/50ETF, 90d for 500ETF/159915ETF.
    (2026-08 span retest: 300ETF 30->60 wins yearly-consistently; 90 confirmed for 500/159915.)"""
    if user_span is not None:
        return user_span
    return 60 if etf in ["300ETF", "50ETF"] else 90


# ── Precompute cache (2026-08 runtime optimization) ──
# The heavy zero-lookahead matrices (z-scores, rolling tail IC, Sortino) are identical
# across schemes / --year / --decay calls for the same ETF+pool+window. Previously
# `--scheme all` recomputed them 4-7 times per ETF (minutes each on 500ETF).
_PRECOMP_CACHE: dict = {}
_PRECOMP_CACHE_MAX = 4


def _get_precomputed(etf, side, cluster_suffix, pool, df, use_future, tail_window, tail_pct, burn_in):
    """Return cache entry with Z_std/signs/feat_names (+ lazy tail_ic/sortino slots)."""
    import json as _json
    _pool_id = tuple(sorted(_json.dumps(p, sort_keys=True) if isinstance(p, dict) else str(p)
                            for p in pool))
    key = (etf, side, cluster_suffix, _pool_id, len(df), tail_window,
           round(float(tail_pct), 4), "fut" if use_future else "spot", burn_in)
    hit = _PRECOMP_CACHE.get(key)
    if hit is not None:
        return hit
    X_raw, signs, feat_names = build_pool_feature_matrix(df, pool)
    Z_std = expanding_zscore_numba(X_raw, burn_in=burn_in, clip=3.0)
    if len(_PRECOMP_CACHE) >= _PRECOMP_CACHE_MAX:
        _PRECOMP_CACHE.pop(next(iter(_PRECOMP_CACHE)))  # evict oldest
    hit = {"Z_std": Z_std, "signs": signs, "feat_names": feat_names,
           "tail_ic": None, "sortino": None}
    _PRECOMP_CACHE[key] = hit
    return hit


def _ensure_tail_ic(entry, full_trade_ret, tail_window, tail_pct, burn_in):
    if entry["tail_ic"] is None:
        entry["tail_ic"] = rolling_tail_ic_numba(entry["Z_std"], entry["signs"], full_trade_ret,
                                                 window=tail_window, tail_pct=tail_pct, burn_in=burn_in)
    return entry["tail_ic"]


def _ensure_sortino(entry, full_trade_ret, tail_window, burn_in):
    if entry["sortino"] is None:
        _, s = rolling_factor_risk_numba(entry["Z_std"], entry["signs"], full_trade_ret,
                                         window=tail_window, burn_in=burn_in)
        entry["sortino"] = s
    return entry["sortino"]


def run_single_backtest(etf: str, side: str = "single", scheme_name: str = "ew", z_th: float = 0.5, 
                        position_mode: str = "fast_ramp_quadratic", fee_bps: float = 0.0008, min_features: int = 10,
                        start_date: str = "2022-01-01", end_date: str = "2026-01-01",
                        z_buffer: float = 0.1, z_short_buffer: float = None, auto_threshold: bool = False,
                        rank_kwargs: dict = None, dynamic_ic: bool = False, long_only: bool = False,
                        use_future: bool = False, use_option: bool = False, use_stoploss: bool = True,
                        stoploss_mode: str = "time_decay_trailing", stoploss_param: float = 0.03,
                        pool_override: list = None, cluster_suffix: str = "", group_constraint: bool = None, max_per_group: int = 1,
                        ic_mode: str = "expanding", tail_window: int = 252, tail_pct: float = 0.10,
                        hysteresis: bool = True, exit_rank: int = 25, min_pos: float = 0.7, delta_z_full: float = 0.4,
                        opt_commission: float = 4.0, strike_mode: str = "otm",
                        ic_override: np.ndarray = None, weight_ic_override: np.ndarray = None,
                        score_blend_w_ic: float = DEFAULT_SCORE_BLEND_W_IC,
                        sortino_gate: bool = True) -> dict:
    """
    Run backtest for one ETF and side combination filtered to OOS date range.
    
    If auto_threshold=True, sweeps Z_th on training data and applies production buffer.
    If use_future=True, trades underlying Index Futures (IF88 for 300ETF, IC88 for 500ETF, IH88 for 50ETF).
    If pool_override is provided, uses that pool instead of admitted_pools.py.
    """
    # 1. Load admitted pool
    pool = pool_override if pool_override else load_admitted_pool(etf, side=side, min_features=min_features, suffix=cluster_suffix)
    if not pool:
        print(f"    [SKIP] Pool size {len(pool)} < {min_features} threshold.")
        return {
            "etf": etf,
            "side": side,
            "scheme": scheme_name,
            "asset_type": "Future" if use_future else "Spot ETF",
            "status": "SKIPPED_FEAT_FLOOR",
            "n_features": len(pool),
            "period": f"{start_date[:7]} ~ {end_date[:7]}" if end_date else f"{start_date[:7]} ~ present",
            "n_trades": 0,
            "cost_sharpe": 0.0,
            "raw_sharpe": 0.0,
            "total_pnl": 0.0,
            "max_drawdown": 0.0,
            "win_rate_pct": 0.0,
            "ann_turnover": 0.0,
            "trade_log_df": None,
        }

    # 2. Load ETF dataset
    df = load_etf_dataset(etf)

    # Handle --future underlying traded return loading
    asset_type = "Spot ETF"
    if use_future:
        fut_returns, fut_ok, fut_name = load_future_trade_returns(etf, df)
        if not fut_ok:
            print(f"--> [SKIP] {etf} has no Index Future mapping for --future mode.")
            return {
                "etf": etf,
                "side": side,
                "scheme": scheme_name,
                "asset_type": "Future (N/A)",
                "status": "SKIPPED_NO_FUTURE",
                "n_features": len(pool),
                "period": f"{start_date[:7]} ~ {end_date[:7]}" if end_date else f"{start_date[:7]} ~ present",
                "n_trades": 0,
                "cost_sharpe": 0.0,
                "raw_sharpe": 0.0,
                "total_pnl": 0.0,
                "max_drawdown": 0.0,
                "win_rate_pct": 0.0,
                "ann_turnover": 0.0,
                "trade_log_df": None,
            }
        full_trade_ret = fut_returns
        asset_type = f"Future ({fut_name})"
    else:
        full_trade_ret = df["trade_return"].values.astype(np.float64) if "trade_return" in df.columns else df["close"].pct_change().fillna(0.0).values

    print(f"--> Running Backtest: ETF={etf}, Asset={asset_type}, Side={side}, Scheme={scheme_name.upper()}, z_th={'auto' if auto_threshold else z_th}, Mode={position_mode}, LongOnly={long_only}, OOS=[{start_date} to {end_date}]")
    
    # 3. Heavy shared matrices (cached across scheme/--year/--decay calls)
    burn_in = 252 if len(df) > 500 else 100
    _pre = _get_precomputed(etf, side, cluster_suffix, pool, df, use_future,
                            tail_window, tail_pct, burn_in)
    signs, feat_names = _pre["signs"], _pre["feat_names"]
    Z_std = _pre["Z_std"]
    _need_tail = (ic_override is None) and (
        (dynamic_ic and ic_mode == "rolling_tail") or scheme_name in ("score", "sortino", "ew", "ensemble"))
    _shared_tail_ic = _ensure_tail_ic(_pre, full_trade_ret, tail_window, tail_pct, burn_in) if _need_tail else None
    _need_sortino = (ic_override is None) and (
        sortino_gate or scheme_name in ("score", "sortino", "ew"))
    _shared_sortino = _ensure_sortino(_pre, full_trade_ret, tail_window, burn_in) if _need_sortino else None

    # 3b. Build cluster_ids for group-constrained selection (if enabled)
    cluster_ids = None
    if group_constraint is not False:  # None (auto) or True
        feat_to_cluster = load_cluster_assignments(etf, side, suffix=cluster_suffix)
        if feat_to_cluster is None and cluster_suffix:
            feat_to_cluster = load_cluster_assignments(etf, side, suffix="")
        if feat_to_cluster is not None:
            # Build cluster_ids array aligned with feat_names
            cids = []
            next_unassigned_cid = (max(feat_to_cluster.values()) + 1) if feat_to_cluster else 1000
            n_missing = 0
            for fn in feat_names:
                if fn in feat_to_cluster:
                    cids.append(feat_to_cluster[fn])
                else:
                    cids.append(next_unassigned_cid)
                    next_unassigned_cid += 1
                    n_missing += 1
            cluster_ids = np.array(cids, dtype=np.int64)
            if n_missing > 0:
                print(f"    [INFO] {n_missing}/{len(feat_names)} features missing cluster assignments (assigned unique fallback IDs). Group constraint enabled.")
            elif group_constraint is None or group_constraint is True:
                print(f"    [INFO] Group constraint auto-enabled: {len(set(cluster_ids))} ONC clusters detected.")
    
    # 4. Z_std from shared cache (zero-lookahead expanding z-score standardizer)

    # 4b. Score blend matrix for score/sortino/ew schemes (zero-lookahead):
    #     Score = w_ic*rank(tailIC_480d) + (1-w_ic)*rank(Sortino_480d)
    score_blend_mat = None
    if scheme_name in ("score", "sortino", "ew") and ic_override is None:
        score_blend_mat = composite_tailic_risk_score(_shared_tail_ic, _shared_sortino, score_blend_w_ic)
        print(f"    [INFO] Score blend matrix: {score_blend_w_ic:.2f}*rank(tailIC) + {1-score_blend_w_ic:.2f}*rank(Sortino) @ {tail_window}d")
    
    # 5. Calculate Composite Signal using weighting scheme
    # Determine n_train for ICW shrinkage (days before start_date)
    t_start_ts = pd.Timestamp(start_date)
    n_train = int((df["date"] < t_start_ts).sum())
    if n_train < 252:
        n_train = 1700  # fallback ~7 years
    
    if scheme_name == "ensemble":
        # Ensemble: equal-weight average of all 4 schemes
        if ic_mode == "rolling_tail":
            IC_mat = _shared_tail_ic
        else:
            IC_mat = expanding_factor_ic_numba(Z_std, signs, full_trade_ret, burn_in=burn_in)
        rk = dict(rank_kwargs) if rank_kwargs else {}
        # Inject group constraint params
        if cluster_ids is not None:
            rk["cluster_ids"] = cluster_ids
            rk["max_per_group"] = max_per_group
        Z_composites = []
        for s_name in ENSEMBLE_SCHEMES:
            if hysteresis and s_name == "icw":
                ic_ema_span = rk.get("ic_ema_span", 30)
                raw_ic = IC_mat
                T_z, N_z = Z_std.shape
                if ic_ema_span and ic_ema_span > 1:
                    alpha_e = 2.0 / (ic_ema_span + 1.0)
                    ic_smoothed = np.zeros_like(raw_ic)
                    ic_smoothed[0] = raw_ic[0]
                    for t_i in range(1, T_z):
                        ic_smoothed[t_i] = alpha_e * raw_ic[t_i] + (1.0 - alpha_e) * ic_smoothed[t_i - 1]
                else:
                    ic_smoothed = raw_ic
                er = exit_rank if exit_rank is not None else adaptive_exit_rank(N_z, rk.get("top_k", 10))
                Z_comp_icw = compute_icw_hysteresis(
                    Z_std, signs, ic_smoothed,
                    cluster_ids=rk.get("cluster_ids", None),
                    n_train=n_train, top_k=rk.get("top_k", 10),
                    exit_rank=er, max_per_group=rk.get("max_per_group", 1)
                )
                Z_composites.append(Z_comp_icw)
            else:
                s_func = get_weighting_scheme(s_name)
                s_kwargs = dict(rk)
                s_kwargs["expanding_ic"] = IC_mat
                Z_composites.append(s_func(Z_std, signs, pool=pool, n_train=n_train, **s_kwargs))
        Z_composite = np.mean(Z_composites, axis=0)
    else:
        extra_kwargs = dict(rank_kwargs) if rank_kwargs else {}
        # Inject group constraint params
        if cluster_ids is not None:
            extra_kwargs["cluster_ids"] = cluster_ids
            extra_kwargs["max_per_group"] = max_per_group
        if dynamic_ic:
            metric_choice = extra_kwargs.get("dynamic_metric", "multi")
            if ic_override is not None:
                # Injected custom ranking/weight matrix (e.g. composite Score IC)
                exp_mat = ic_override
            elif metric_choice == "multi" and scheme_name in ("score", "icw", "rank", "ew"):
                sw = extra_kwargs.get("score_weights", (0.20, 0.15, 0.65))
                mw = extra_kwargs.get("mono_window", 750)
                exp_mat = expanding_factor_score_numba(Z_std, signs, full_trade_ret, burn_in=burn_in, score_weights=sw, mono_window=mw)
            elif ic_mode == "rolling_tail":
                exp_mat = _shared_tail_ic
            else:
                exp_mat = expanding_factor_ic_numba(Z_std, signs, full_trade_ret, burn_in=burn_in)
            # Scheme-level overrides (Score IC family):
            #   score   -> Score blend drives BOTH selection and weights
            #   sortino -> tail IC selects, Score blend gives weights (decomposition)
            #   ew      -> Score blend selects the top-K, then equal weights
            sortino_weight_src = None
            if scheme_name in ("score", "sortino", "ew") and score_blend_mat is not None:
                if scheme_name == "ew":
                    exp_mat = score_blend_mat  # selection metric only (weights are equal)
                elif scheme_name == "score":
                    exp_mat = score_blend_mat
                else:  # sortino: keep tail IC for selection
                    sortino_weight_src = score_blend_mat
            extra_kwargs["expanding_ic"] = exp_mat
        # Hysteresis path: use sticky feature selection for ICW/Score/Sortino schemes
        if hysteresis and scheme_name in ("icw", "score", "sortino") and dynamic_ic and "expanding_ic" in extra_kwargs:
            ic_ema_span = extra_kwargs.get("ic_ema_span", 30)
            raw_ic = extra_kwargs["expanding_ic"]
            # Build EMA-smoothed IC matrix for ranking
            T_z, N_z = Z_std.shape
            if ic_ema_span and ic_ema_span > 1:
                alpha_e = 2.0 / (ic_ema_span + 1.0)
                ic_smoothed = np.zeros_like(raw_ic)
                ic_smoothed[0] = raw_ic[0]
                for t_i in range(1, T_z):
                    ic_smoothed[t_i] = alpha_e * raw_ic[t_i] + (1.0 - alpha_e) * ic_smoothed[t_i - 1]
            else:
                ic_smoothed = raw_ic
            # Sortino gate (2026-08): mask factors with Sortino_480d <= 0 out of selection.
            # Applied AFTER EMA smoothing with a BOUNDED value (pre-EMA -1e9 masks cause a
            # multi-hundred-day banishment artifact). Zero-cost where it never fires
            # (300/500ETF at old spans), +0.135 Sharpe on 159915ETF where it does.
            if sortino_gate and ic_override is None:
                ic_smoothed = np.where(_shared_sortino <= 0.0, -10.0, ic_smoothed)
            # Optional separate weighting matrix (selection vs weighting decomposition).
            # Priority: explicit weight_ic_override > sortino scheme's Score blend.
            weight_src = weight_ic_override if weight_ic_override is not None else sortino_weight_src
            weight_smoothed = None
            if weight_src is not None:
                if ic_ema_span and ic_ema_span > 1:
                    alpha_w = 2.0 / (ic_ema_span + 1.0)
                    weight_smoothed = np.zeros_like(weight_src)
                    weight_smoothed[0] = weight_src[0]
                    for t_i in range(1, T_z):
                        weight_smoothed[t_i] = alpha_w * weight_src[t_i] + (1.0 - alpha_w) * weight_smoothed[t_i - 1]
                else:
                    weight_smoothed = weight_src
            er = exit_rank if exit_rank is not None else adaptive_exit_rank(N_z, extra_kwargs.get("top_k", 10))
            Z_composite = compute_icw_hysteresis(
                Z_std, signs, ic_smoothed,
                cluster_ids=extra_kwargs.get("cluster_ids", None),
                n_train=n_train, top_k=extra_kwargs.get("top_k", 10),
                exit_rank=er, max_per_group=extra_kwargs.get("max_per_group", 1),
                weight_mat=weight_smoothed
            )
        else:
            if scheme_name == "sortino" and not hysteresis:
                print("    [WARNING] 'sortino' requires hysteresis; falling back to icw weighting.")
                scheme_name_eff = "icw"
            else:
                scheme_name_eff = scheme_name
            scheme_func = get_weighting_scheme(scheme_name_eff)
            Z_composite = scheme_func(Z_std, signs, pool=pool, n_train=n_train, **extra_kwargs)

    # 6. Threshold Determination (auto-sweep or fixed)
    sweep_info = None
    if auto_threshold:
        # Get training-period composite signal and returns for sweep
        train_mask = df["date"] < t_start_ts
        Z_composite_train = Z_composite[train_mask.values]
        trade_returns_train = full_trade_ret[train_mask.values]
        
        # Sweep on training data
        sweep_info = sweep_optimal_threshold(
            Z_composite_train, trade_returns_train,
            mode=position_mode, fee_bps=fee_bps, long_only=long_only,
            min_pos=min_pos, delta_z_full=delta_z_full
        )
        z_th_prod, z_th_short = compute_production_threshold(sweep_info, z_buffer=z_buffer, z_short_buffer=z_short_buffer)
        eff_short_buf = z_short_buffer if z_short_buffer is not None else z_buffer
        opt_l = sweep_info.get("optimal_z_th_long", sweep_info.get("optimal_z_th", 0.5))
        opt_s = sweep_info.get("optimal_z_th_short", opt_l)
        print(f"    [THRESHOLD] Train-optimal Long Z_th={opt_l:.2f}, Short Z_th={opt_s:.2f} (Long Sharpe={sweep_info['best_sharpe']:.3f}) -> Prod Long Z_th={z_th_prod:.2f} (buf=+{z_buffer:.2f}), Short Z_th={z_th_short:.2f} (buf=+{eff_short_buf:.2f})")
    else:
        z_th_prod = z_th
        eff_short_buf = z_short_buffer if z_short_buffer is not None else z_buffer
        z_th_short = z_th + (eff_short_buf - z_buffer if z_short_buffer is not None else 0.0)

    # 7. Position Sizing with production thresholds
    positions_full = generate_positions(
        Z_composite, z_th=z_th_prod, z_th_short=z_th_short,
        mode=position_mode, long_only=long_only,
        min_pos=min_pos, delta_z_full=delta_z_full
    )

    # 8. Date Filtering to OOS Evaluation Period
    t_start = pd.Timestamp(start_date)
    if end_date:
        t_end = pd.Timestamp(end_date)
        mask = (df["date"] >= t_start) & (df["date"] < t_end)
    else:
        mask = df["date"] >= t_start
    
    if not mask.any():
        print(f"    [WARNING] No data available for date range starting {start_date}. Falling back to recent history.")
        mask = df["date"] >= df["date"].iloc[-1000]

    df_oos = df[mask].reset_index(drop=True)
    positions_oos = positions_full[mask.values if isinstance(mask, pd.Series) else mask]
    Z_composite_oos = Z_composite[mask.values if isinstance(mask, pd.Series) else mask]

    # 9. Backtest Simulation on OOS slice
    trade_returns_oos = full_trade_ret[mask.values if isinstance(mask, pd.Series) else mask]
    option_result = None
    if use_option:
        # Option portfolio simulation mode
        resolved_strike_mode = resolve_strike_mode(etf, strike_mode)
        iv_series = df_oos["iv"].values if "iv" in df_oos.columns else None
        option_result = simulate_option_portfolio(
            etf=etf,
            positions_oos=positions_oos,
            dates_oos=df_oos["date"],
            iv_series=iv_series,
            initial_capital=100_000.0,
            trade_budget=10_000.0,
            commission_per_side=opt_commission,
            min_days_to_maturity=7,
            use_stoploss=use_stoploss,
            stoploss_mode=stoploss_mode,
            stoploss_param=stoploss_param,
            strike_mode=resolved_strike_mode,
        )
        # Use option daily returns for metrics
        net_returns = option_result["daily_returns"]
        raw_returns = option_result["daily_gross_returns"]
        fees = (option_result["daily_gross_pnl"] - option_result["daily_pnl"]) / option_result["initial_capital"]
    elif use_stoploss:
        bars_dict = load_intraday_bars_dict(etf)
        if bars_dict:
            net_returns, raw_returns, fees, stop_hits, trig_pct = simulate_full_series(
                df_oos["date"], positions_oos, bars_dict, method=stoploss_mode, param=stoploss_param, fee_bps=fee_bps
            )
        else:
            print(f"    [WARNING] Could not load 1m bars for {etf}. Falling back to baseline simulation.")
            net_returns, raw_returns, fees = simulate_etf_spot(trade_returns_oos, positions_oos, fee_bps=fee_bps)
    else:
        net_returns, raw_returns, fees = simulate_etf_spot(trade_returns_oos, positions_oos, fee_bps=fee_bps)

    # 10. Trade log DataFrame creation & CSV export
    trade_log_df = build_trade_log_df(
        df_oos=df_oos,
        Z_composite_oos=Z_composite_oos,
        positions_oos=positions_oos,
        net_returns=net_returns,
        raw_returns=raw_returns,
        fees=fees,
        etf=etf,
        scheme=scheme_name,
        z_th=z_th_prod,
        asset_type=asset_type,
        trade_returns_arr=trade_returns_oos,
    )
    
    artifacts_dir = HERE / "artifacts"
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    fut_suffix = "_future" if use_future else ""
    trade_csv_path = artifacts_dir / f"trades_{scheme_name}_{etf}{fut_suffix}.csv"
    trade_log_df.to_csv(trade_csv_path, index=False)

    # 11. Calculate Metrics
    metrics = calculate_metrics(net_returns, raw_returns, positions_oos, dates=df_oos["date"])
    
    # Add option-specific metrics if in option mode
    if use_option and option_result is not None:
        metrics["option_final_capital"] = option_result["final_capital"]
        metrics["option_n_trades"] = option_result["n_trades"]
        metrics["option_n_stop_hits"] = option_result.get("n_stop_hits", 0)
        metrics["option_bankrupt_day"] = option_result["bankrupt_day"]
        metrics["option_initial_capital"] = option_result["initial_capital"]
        metrics["option_trade_log_df"] = option_result["trade_log_df"]
        # Total P&L in RMB for option mode
        metrics["option_total_pnl_rmb"] = round(float(option_result["daily_pnl"].sum()), 2)
    
    metrics.update({
        "etf": etf,
        "asset_type": asset_type,
        "side": side,
        "scheme": scheme_name,
        "status": "SUCCESS",
        "n_features": len(pool),
        "z_th": z_th_prod,
        "z_th_long": z_th_prod,
        "z_th_short": z_th_short,
        "z_th_train_long": sweep_info.get("optimal_z_th_long", sweep_info.get("optimal_z_th")) if sweep_info else None,
        "z_th_train_short": sweep_info.get("optimal_z_th_short") if sweep_info else None,
        "z_buffer": z_buffer if auto_threshold else 0.0,
        "long_only": long_only,
        "use_future": use_future,
        "position_mode": position_mode,
        "min_pos": min_pos,
        "delta_z_full": delta_z_full,
        "dates": df_oos["date"].dt.strftime("%Y-%m-%d").tolist() if "date" in df_oos.columns else [],
        "cum_pnl": np.cumsum(net_returns).tolist(),
        "trade_log_df": trade_log_df,
        # Arrays for validation (stripped before JSON save)
        "_net_returns": net_returns,
        "_Z_composite": Z_composite,
        "_trade_returns": full_trade_ret,
        "_dates_series": df["date"],
    })

    print(f"    [RESULT] OOS ({metrics['period']}) | Cost Sharpe: {metrics['cost_sharpe']} | PnL: {metrics['total_pnl']} | WinRate: {metrics['win_rate_pct']}% | Intraday Trades: {metrics['n_trades']}/{metrics['n_days']}")

    return metrics



def main():
    parser = argparse.ArgumentParser(description="NewTrade Day-Model Factor Monetization Backtest Runner")
    parser.add_argument("-e", "--etf", type=str, default="all", help="Target ETF (300ETF, 500ETF, 50ETF, 588000ETF, 159915ETF, or all)")
    parser.add_argument("-s", "--side", type=str, default="single", choices=["single", "long", "short"], help="Trading side")
    parser.add_argument("--scheme", type=str, default="all", choices=["ew", "icw", "score", "sortino", "rank", "ensemble", "all"], help="Factor weighting scheme (default: all = Score/ICW/Sortino/EW)")
    parser.add_argument("--z-th", type=str, default="auto", help="Conviction threshold Z score. 'auto' = train-sweep + buffer, or float value for fixed.")
    parser.add_argument("--z-buffer", type=float, default=0.1, help="Production buffer added to train-optimal threshold (default 0.1, walk-forward validated)")
    parser.add_argument("--z-short-buffer", type=float, default=None, help="Production buffer for short threshold (default: z_buffer + 0.1)")
    parser.add_argument("--position-mode", type=str, default="fast_ramp_quadratic",
                        choices=["binary", "fast_ramp_linear", "fast_ramp_quadratic", "fast_ramp_tanh", "quadratic", "tanh", "tanh_tuned"],
                        help="Position sizing mode (default: fast_ramp_quadratic)")
    parser.add_argument("--min-pos", type=float, default=0.7, help="Minimum position size floor when passing conviction threshold (default: 0.7)")
    parser.add_argument("--delta-z-full", type=float, default=0.4, help="Excess Z margin above threshold to reach full 1.0 position size (default: 0.4)")
    parser.add_argument("--fee-bps", type=float, default=None, help="Transaction fee in basis points (default: 8.0 for ETF, 4.0 for futures)")
    parser.add_argument("--start-date", type=str, default="2022-01-01", help="OOS Start Date (YYYY-MM-DD)")
    parser.add_argument("--end-date", type=str, default="2026-01-01", help="OOS End Date (YYYY-MM-DD)")
    parser.add_argument("-o", "--output", type=str, default=None, help="Output markdown report path (default: newtrade/REPORT.md)")

    
    # Scheme 4 (Rank Bounded Mapping) Options
    parser.add_argument("--rank-min-ratio", type=float, default=0.2, help="Scheme 4 w_min ratio relative to 1/N (default 0.2)")
    parser.add_argument("--rank-max-ratio", type=float, default=1.8, help="Scheme 4 w_max ratio relative to 1/N (default 1.8)")
    parser.add_argument("--rank-mapping", type=str, default="linear", choices=["linear", "power", "softmax", "top_k"], help="Scheme 4 rank mapping shape")
    parser.add_argument("--rank-power", type=float, default=2.0, help="Power exponent for 'power' rank mapping shape")
    parser.add_argument("--top-k", type=int, default=10, help="Top K factors feature truncation selection threshold (default: 10)")
    parser.add_argument("--rank-top-k", type=int, default=None, help="Top K factors truncation threshold for 'top_k' rank mapping shape")
    parser.add_argument("--dynamic-ic", "--dynamic-score", dest="dynamic_ic", action="store_true", default=True, help="Enable zero-lookahead expanding factor ranking (default: True)")
    parser.add_argument("--no-dynamic-ic", "--no-dynamic-score", dest="dynamic_ic", action="store_false", help="Disable dynamic ranking (use static pool metadata score)")
    parser.add_argument("--dynamic-metric", type=str, default="ic", choices=["ic", "multi"], help="Dynamic factor ranking metric: 'ic' (default: single expanding IC) or 'multi'")
    parser.add_argument("--ic-mode", type=str, default="rolling_tail", choices=["expanding", "rolling_tail"], help="IC computation mode: 'rolling_tail' (default: 480d rolling window tail Spearman) or 'expanding' (total history Pearson)")
    parser.add_argument("--tail-window", type=int, default=480, help="Rolling window size in trading days for rolling_tail IC mode (default: 480 = 2 China years)")
    parser.add_argument("--tail-pct", type=float, default=0.10, help="Tail fraction per side for rolling_tail IC mode (default: 0.10)")
    parser.add_argument("--mono-window", type=int, default=750, help="Rolling window for monotonicity calculation (default 750 trading days ~ 3 years, 0 for full expanding)")
    parser.add_argument("--score-w-ic", type=float, default=0.20, help="Score weight for IC component (default 0.20)")
    parser.add_argument("--score-w-ir", type=float, default=0.15, help="Score weight for IC_IR component (default 0.15)")
    parser.add_argument("--score-w-mono", type=float, default=0.65, help="Score weight for Monotonicity component (default 0.65)")
    parser.add_argument("--ic-ema-span", type=int, default=None, help="EMA span parameter for smoothing dynamic expanding metrics (default: auto, 30d for 300ETF/50ETF, 90d for 500ETF/159915ETF)")
    parser.add_argument("--weight-delta", type=float, default=None, help="Optional partial-adjustment delta parameter for smoothing daily target weight jumps (default: None)")
    parser.add_argument("--long-only", dest="long_only", action="store_true", default=False, help="Restrict to long-only trades (Spot ETF mode). Default: False (allows shorting).")
    parser.add_argument("--allow-short", dest="long_only", action="store_false", help="Allow short trades (default)")
    parser.add_argument("--future", action="store_true", help="Trade underlying Index Futures (IF88 for 300ETF, IC88 for 500ETF, IH88 for 50ETF) instead of Spot ETF.")
    parser.add_argument("--option", action="store_true", help="Simulate option portfolio (100k RMB, 10k per trade, nearest OTM, 7-day min DTM)")
    parser.add_argument("--opt-commission", type=float, default=4.0, help="Option commission in RMB per contract per side (default: 4.0)")
    parser.add_argument("--strike-mode", type=str, default="auto", choices=["auto"] + STRIKE_MODES,
                        help="Option strike selection mode (default: auto = ETF-adaptive). Options: auto, otm, nearest, vol_t1, vol_intraday, cascade")
    parser.add_argument("--strike-ab", action="store_true", default=False,
                        help="Run A/B comparison of all strike selection modes and print table")

    # Stop-Loss options
    parser.add_argument("--stoploss", dest="stoploss", action="store_true", default=True, help="Enable 3%% time decay trailing stop-loss (default: True).")
    parser.add_argument("--no-stoploss", dest="stoploss", action="store_false", help="Disable stop-loss (hold position to 14:35 PM close).")
    parser.add_argument("--stoploss-mode", type=str, default="time_decay_trailing", help="Stop-loss mode (default: time_decay_trailing).")
    parser.add_argument("--stoploss-param", type=float, default=0.03, help="Stop-loss threshold parameter (default: 0.03 = 3.0%%).")

    # Group-Constrained Feature Selection (ONC clustering)
    parser.add_argument("--group-constraint", dest="group_constraint", action="store_true", default=None,
                        help="Enable ONC group-constrained top-K selection (max 1 feature per cluster). Default: auto-detect from cluster file.")
    parser.add_argument("--no-group-constraint", dest="group_constraint", action="store_false",
                        help="Disable group constraint (use unconstrained top-K).")
    parser.add_argument("--max-per-group", type=int, default=1,
                        help="Max features allowed per ONC cluster (default: 1).")

    # Feature Selection Hysteresis
    parser.add_argument("--hysteresis", dest="hysteresis", action="store_true", default=True,
                        help="Enable sticky feature selection (enter top-10, exit at adaptive rank). Default: True.")
    parser.add_argument("--no-hysteresis", dest="hysteresis", action="store_false",
                        help="Disable hysteresis (use standard daily top-K reselection).")
    parser.add_argument("--exit-rank", type=int, default=25,
                        help="Override exit rank for hysteresis (default: 25, A/B validated fairest across all 3 ETFs).")
    parser.add_argument("--score-blend-w-ic", type=float, default=DEFAULT_SCORE_BLEND_W_IC,
                        help=f"Tail IC weight in the Score blend for score/sortino/ew schemes (default {DEFAULT_SCORE_BLEND_W_IC}: 75%% tailIC + 25%% Sortino).")
    parser.add_argument("--no-sortino-gate", dest="sortino_gate", action="store_false",
                        help="Disable the Sortino<=0 selection gate (default: enabled, post-EMA bounded mask).")

    # Validation options
    parser.add_argument("--validate", dest="validate", action="store_true", default=True, help="Run DSR + CPCV validation on results (default: True)")
    parser.add_argument("--no-validate", dest="validate", action="store_false", help="Disable DSR + CPCV validation")
    parser.add_argument("--trials", type=int, default=10, help="Number of trials for DSR correction (default: 10)")
    parser.add_argument("--cpcv-splits", type=int, default=6, help="CPCV number of splits (default: 6)")
    parser.add_argument("--cpcv-test", type=int, default=2, help="CPCV test chunks per fold (default: 2)")

    # Per-year pool evaluation
    parser.add_argument("--year", type=int, default=None, help="Run single-year backtest (e.g. --year 2024). Auto-sets start/end dates and output to REPORT_{year}.md")
    parser.add_argument("--pool-period", type=str, default=None, help="Use period-specific pool (e.g. '_p2016_2024', 'original' for baseline, 'old' for old vintage)")
    parser.add_argument("--decay", action="store_true", help="Decay analysis: run pool on each year from --year through 2025, generate multi-year chart")

    args = parser.parse_args()

    # Parse z_th: 'auto' or float
    auto_threshold = args.z_th.lower() == "auto"
    z_th_fixed = 0.5 if auto_threshold else float(args.z_th)

    etfs_to_run = AVAILABLE_ETFS if args.etf.lower() == "all" else [args.etf]
    schemes_to_run = ALL_SCHEMES if args.scheme.lower() == "all" else [args.scheme]
    # Default fee: 8 bps for ETF (conservative slippage), 4 bps for futures (tighter spreads)
    effective_fee_bps = args.fee_bps if args.fee_bps is not None else (4.0 if args.future else 8.0)
    fee_bps = effective_fee_bps / 10000.0

    # --year: set OOS start date from year (runs through end_date) and output path
    mode_prefix = "option" if args.option else ("future" if args.future else "")
    if args.year:
        args.start_date = f"{args.year}-01-01"
        if not args.output:
            stem = f"REPORT_{mode_prefix}_{args.year}" if mode_prefix else f"REPORT_{args.year}"
            args.output = str(HERE / f"{stem}.md")
    elif args.pool_period and args.start_date == "2022-01-01":
        import re
        match = re.search(r'_p\d{4}_(\d{4})', args.pool_period)
        if match:
            pool_end_yr = int(match.group(1))
            start_yr = pool_end_yr
            args.start_date = f"{start_yr}-01-01"
            if not args.output:
                stem = f"REPORT_{mode_prefix}_{pool_end_yr}" if mode_prefix else f"REPORT_{pool_end_yr}"
                args.output = str(HERE / f"{stem}.md")
            print(f"  [AUTO OOS] Inferred OOS start_date={args.start_date} from pool_period '{args.pool_period}' -> output {Path(args.output).name}")
        elif args.pool_period in ("old", "original") and not args.output:
            stem = f"REPORT_{mode_prefix}_{args.pool_period}" if mode_prefix else f"REPORT_{args.pool_period}"
            args.output = str(HERE / f"{stem}.md")

    # --pool-period: load period-specific pool override or handle 'all'
    if args.pool_period and args.pool_period.lower() == "all":
        periods = ["old", "_p2015_2023", "_p2016_2024", "_p2017_2025"]
        print("================================================================================")
        print(f"FULL POOL PERIOD BENCHMARK | Running periods: {periods}")
        print("================================================================================\n")
        argv_clean = []
        skip_next = False
        for arg in sys.argv[1:]:
            if skip_next:
                skip_next = False
                continue
            if arg == "--pool-period":
                skip_next = True
                continue
            if arg.startswith("--pool-period="):
                continue
            argv_clean.append(arg)

        for p_name in periods:
            print(f"\n" + "=" * 80)
            print(f"  >>> RUNNING POOL PERIOD: {p_name} <<<")
            print("=" * 80 + "\n")
            sys.argv = [sys.argv[0]] + argv_clean + ["--pool-period", p_name]
            main()
        return

    pool_period_override = None
    if args.pool_period:
        import json as _json
        dm_data = REPO_ROOT / "day-model-new" / "data"
        if args.pool_period == "old":
            # Load old vintage from backup
            import importlib.util
            spec = importlib.util.spec_from_file_location("_old", HERE / "data" / "old_admitted_pools_backup.py")
            _mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(_mod)
            pool_period_override = _mod.POOLS  # dict: etf -> {side -> [pool]}
        elif args.pool_period == "original":
            pool_period_override = "__original__"  # sentinel: load per-ETF from selected_pool_{etf}_single.json
        else:
            pool_period_override = args.pool_period  # suffix string like "_p2016_2024"

    # Set default option stop-loss mode & param if in option mode
    if args.option:
        if args.stoploss_mode == "time_decay_trailing":
            args.stoploss_mode = DEFAULT_OPT_STOPLOSS_MODE
        if args.stoploss_param == 0.03:
            args.stoploss_param = DEFAULT_OPT_STOPLOSS_PARAM

    print("================================================================================")
    mode_str = "Option Portfolio" if args.option else ("Future" if args.future else "Spot ETF")
    stoploss_info = f" | StopLoss={args.stoploss} ({args.stoploss_mode}={args.stoploss_param})"
    print(f"NewTrade Backtest Engine | Mode={mode_str} | Scheme={args.scheme.upper()} | z_th={args.z_th} | buffer={args.z_buffer}{stoploss_info} | LongOnly={args.long_only} | TopK={args.top_k} | OOS=[{args.start_date} ~ {args.end_date}]")
    if args.option:
        print(f"  Option Params: 100k RMB capital, 10k/trade, {args.opt_commission} RMB/contract/side commission, >=7 DTM")
    print("================================================================================")

    rank_kwargs = {
        "w_min_ratio": args.rank_min_ratio,
        "w_max_ratio": args.rank_max_ratio,
        "mapping_shape": args.rank_mapping,
        "power": args.rank_power,
        "top_k": args.top_k if args.top_k is not None else args.rank_top_k,
        "ic_ema_span": args.ic_ema_span,
        "dynamic_metric": args.dynamic_metric,
        "weight_delta": args.weight_delta,
        "score_weights": (args.score_w_ic, args.score_w_ir, args.score_w_mono),
        "mono_window": args.mono_window,
        "score_blend_w_ic": args.score_blend_w_ic,
    }

    # ─── Decay Mode: run pool across all future years ───
    if args.decay:
        if not args.pool_period:
            print("ERROR: --decay requires --pool-period")
            return
        start_year = args.year if args.year else 2022
        years = list(range(start_year, 2026))
        print(f"\n  DECAY ANALYSIS: pool='{args.pool_period}' across {years}")
        print(f"  {'Year':<6} | {'Sharpe':>8} {'PnL':>10} {'WR%':>6} {'Trades':>7}")
        print(f"  {'-'*6}-+-{'-'*34}")

        decay_results = []
        for yr in years:
            # Override dates for this year
            _start = f"{yr}-01-01"
            _end = f"{yr+1}-01-01"
            yr_results = []
            for etf in etfs_to_run:
                _pool_ov = None
                if isinstance(pool_period_override, dict):
                    _pool_ov = pool_period_override.get(etf, {}).get(args.side, [])
                elif pool_period_override == "__original__":
                    _fpath = REPO_ROOT / "day-model-new" / "data" / f"selected_pool_{etf}_{args.side}.json"
                    if _fpath.exists():
                        with open(_fpath, "r", encoding="utf-8") as _f:
                            _pool_ov = _json.load(_f)
                else:
                    _fpath = REPO_ROOT / "day-model-new" / "data" / f"selected_pool_{etf}_{args.side}{pool_period_override}.json"
                    if _fpath.exists():
                        with open(_fpath, "r", encoding="utf-8") as _f:
                            _pool_ov = _json.load(_f)

                _cluster_suf = pool_period_override if isinstance(pool_period_override, str) and pool_period_override.startswith("_p") else ""
                _rank_kw = dict(rank_kwargs)
                _rank_kw["ic_ema_span"] = resolve_ic_ema_span(etf, args.ic_ema_span)
                res = run_single_backtest(
                    etf=etf, side=args.side, scheme_name="icw", z_th=0.5,
                    position_mode=args.position_mode, fee_bps=fee_bps,
                    start_date=_start, end_date=_end,
                    z_buffer=args.z_buffer, z_short_buffer=args.z_short_buffer, auto_threshold=True,
                    rank_kwargs=_rank_kw, dynamic_ic=True, ic_mode=args.ic_mode,
                    tail_window=args.tail_window, tail_pct=args.tail_pct,
                    long_only=args.long_only, use_stoploss=args.stoploss,
                    stoploss_mode=args.stoploss_mode, stoploss_param=args.stoploss_param,
                    pool_override=_pool_ov, cluster_suffix=_cluster_suf,
                    group_constraint=args.group_constraint, max_per_group=args.max_per_group,
                    hysteresis=args.hysteresis, exit_rank=args.exit_rank,
                    min_pos=args.min_pos, delta_z_full=args.delta_z_full,
                    opt_commission=args.opt_commission,
                    score_blend_w_ic=args.score_blend_w_ic,
                    sortino_gate=args.sortino_gate,
                )
                yr_results.append(res)
            decay_results.append((yr, yr_results))

        # Print decay table per ETF
        for etf in etfs_to_run:
            print(f"\n  {etf} decay (pool={args.pool_period}):")
            print(f"    {'Year':<6} | {'Sharpe':>8} {'PnL':>10} {'WR%':>6} {'Trades':>7}")
            print(f"    {'-'*6}-+-{'-'*34}")
            for yr, yr_results in decay_results:
                r = next((x for x in yr_results if x.get("etf") == etf), None)
                if r and r.get("status") == "SUCCESS":
                    print(f"    {yr:<6} | {r['cost_sharpe']:>8.3f} {r['total_pnl']:>+10.4f} {r['win_rate_pct']:>6.1f} {r['n_trades']:>7}")
                else:
                    print(f"    {yr:<6} | {'SKIP':>8}")

        # Generate decay chart
        try:
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt
            n_etfs = len([e for e in etfs_to_run if any(r.get('etf') == e and r.get('status') == 'SUCCESS' for _, yrs in decay_results for r in yrs)])
            if n_etfs > 0:
                fig, axes = plt.subplots(n_etfs, 1, figsize=(11, 3.5 * n_etfs), dpi=150, squeeze=False)
                plot_idx = 0
                for etf in etfs_to_run:
                    has_data = any(r.get('etf') == etf and r.get('status') == 'SUCCESS' for _, yrs in decay_results for r in yrs)
                    if not has_data:
                        continue
                    ax = axes[plot_idx, 0]
                    for yr, yr_results in decay_results:
                        r = next((x for x in yr_results if x.get('etf') == etf and x.get('status') == 'SUCCESS'), None)
                        if r and r.get('dates') and r.get('cum_pnl'):
                            ax.plot(r['dates'], r['cum_pnl'], label=f"{yr} (SR={r['cost_sharpe']:.2f})", linewidth=1.3)
                    ax.set_title(f"{etf} — Pool Decay ({args.pool_period})", fontsize=10, fontweight='bold')
                    ax.set_ylabel("Cum PnL")
                    ax.legend(fontsize=8, loc='upper left')
                    ax.grid(True, alpha=0.3)
                    plot_idx += 1
                fig.tight_layout()
                artifacts_dir = HERE / "artifacts"
                artifacts_dir.mkdir(parents=True, exist_ok=True)
                chart_path = artifacts_dir / f"decay{args.pool_period}.png"
                fig.savefig(chart_path)
                plt.close(fig)
                print(f"\n  Saved decay chart: {chart_path}")
        except Exception as e:
            print(f"  [WARNING] Decay chart failed: {e}")
        return

    # ─── Strike Selection A/B Test Mode ───
    if args.strike_ab and args.option:
        print("\n" + "=" * 80)
        print("STRIKE SELECTION A/B TEST")
        print("=" * 80)
        ab_rows = []
        for etf in etfs_to_run:
            # Resolve pool override
            _pool_ov = None
            if pool_period_override is not None:
                if isinstance(pool_period_override, dict):
                    _pool_ov = pool_period_override.get(etf, {}).get(args.side, [])
                elif pool_period_override == "__original__":
                    _fpath = REPO_ROOT / "day-model-new" / "data" / f"selected_pool_{etf}_{args.side}.json"
                    if _fpath.exists():
                        with open(_fpath, "r", encoding="utf-8") as _f:
                            _pool_ov = json.load(_f)
                else:
                    _fpath = REPO_ROOT / "day-model-new" / "data" / f"selected_pool_{etf}_{args.side}{pool_period_override}.json"
                    if _fpath.exists():
                        with open(_fpath, "r", encoding="utf-8") as _f:
                            _pool_ov = json.load(_f)
            _cluster_suf = pool_period_override if isinstance(pool_period_override, str) and pool_period_override.startswith("_p") else ""
            _rank_kw = dict(rank_kwargs)
            _rank_kw["ic_ema_span"] = resolve_ic_ema_span(etf, args.ic_ema_span)
            
            for s_mode in STRIKE_MODES:
                res = run_single_backtest(
                    etf=etf, side=args.side, scheme_name="icw", z_th=z_th_fixed,
                    position_mode=args.position_mode, fee_bps=fee_bps,
                    start_date=args.start_date, end_date=args.end_date,
                    z_buffer=args.z_buffer, z_short_buffer=args.z_short_buffer,
                    auto_threshold=auto_threshold, rank_kwargs=_rank_kw,
                    dynamic_ic=args.dynamic_ic, long_only=args.long_only,
                    use_option=True, use_stoploss=args.stoploss,
                    stoploss_mode=args.stoploss_mode, stoploss_param=args.stoploss_param,
                    pool_override=_pool_ov, cluster_suffix=_cluster_suf,
                    group_constraint=args.group_constraint, max_per_group=args.max_per_group,
                    ic_mode=args.ic_mode, tail_window=args.tail_window, tail_pct=args.tail_pct,
                    hysteresis=args.hysteresis, exit_rank=args.exit_rank,
                    min_pos=args.min_pos, delta_z_full=args.delta_z_full,
                    opt_commission=args.opt_commission, strike_mode=s_mode,
                    score_blend_w_ic=args.score_blend_w_ic,
                    sortino_gate=args.sortino_gate,
                )
                if res.get("status") == "SUCCESS":
                    avg_comm = res.get("option_total_pnl_rmb", 0)
                    n_opt = res.get("option_n_trades", 0)
                    ab_rows.append({
                        "etf": etf, "mode": s_mode, "trades": n_opt,
                        "sharpe": res["cost_sharpe"], "pnl_rmb": res.get("option_total_pnl_rmb", 0),
                        "win_rate": res["win_rate_pct"], "max_dd": res["max_drawdown"],
                    })
                else:
                    ab_rows.append({"etf": etf, "mode": s_mode, "trades": 0, "sharpe": 0, "pnl_rmb": 0, "win_rate": 0, "max_dd": 0})
        
        # Print comparison table
        print(f"\n{'ETF':<12} | {'Mode':<14} | {'Trades':>6} | {'Sharpe':>7} | {'PnL (RMB)':>12} | {'WinRate':>7} | {'MaxDD':>7}")
        print(f"{'-'*12}-+-{'-'*14}-+-{'-'*6}-+-{'-'*7}-+-{'-'*12}-+-{'-'*7}-+-{'-'*7}")
        for row in ab_rows:
            print(f"{row['etf']:<12} | {row['mode']:<14} | {row['trades']:>6} | {row['sharpe']:>7.3f} | {row['pnl_rmb']:>+12,.0f} | {row['win_rate']:>6.1f}% | {row['max_dd']:>7.4f}")
        print()
        return

    results = []
    for scheme in schemes_to_run:
        for etf in etfs_to_run:
            # Resolve pool override for this ETF
            _pool_ov = None
            if pool_period_override is not None:
                if isinstance(pool_period_override, dict):
                    # 'old' mode: dict of pools
                    _pool_ov = pool_period_override.get(etf, {}).get(args.side, [])
                elif pool_period_override == "__original__":
                    _fpath = REPO_ROOT / "day-model-new" / "data" / f"selected_pool_{etf}_{args.side}.json"
                    if _fpath.exists():
                        with open(_fpath, "r", encoding="utf-8") as _f:
                            _pool_ov = _json.load(_f)
                else:
                    _fpath = REPO_ROOT / "day-model-new" / "data" / f"selected_pool_{etf}_{args.side}{pool_period_override}.json"
                    if _fpath.exists():
                        with open(_fpath, "r", encoding="utf-8") as _f:
                            _pool_ov = _json.load(_f)
                if _pool_ov is not None:
                    print(f"  [POOL] {etf}: using period pool '{args.pool_period}' ({len(_pool_ov)} features)")

            _cluster_suf = pool_period_override if isinstance(pool_period_override, str) and pool_period_override.startswith("_p") else ""
            _rank_kw = dict(rank_kwargs)
            _rank_kw["ic_ema_span"] = resolve_ic_ema_span(etf, args.ic_ema_span)
            res = run_single_backtest(
                etf=etf,
                side=args.side,
                scheme_name=scheme,
                z_th=z_th_fixed,
                position_mode=args.position_mode,
                fee_bps=fee_bps,
                start_date=args.start_date,
                end_date=args.end_date,
                z_buffer=args.z_buffer,
                z_short_buffer=args.z_short_buffer,
                auto_threshold=auto_threshold,
                rank_kwargs=_rank_kw,
                dynamic_ic=args.dynamic_ic,
                long_only=args.long_only,
                use_future=args.future,
                use_option=args.option,
                use_stoploss=args.stoploss,
                stoploss_mode=args.stoploss_mode,
                stoploss_param=args.stoploss_param,
                pool_override=_pool_ov,
                cluster_suffix=_cluster_suf,
                group_constraint=args.group_constraint,
                max_per_group=args.max_per_group,
                ic_mode=args.ic_mode,
                tail_window=args.tail_window,
                tail_pct=args.tail_pct,
                hysteresis=args.hysteresis,
                exit_rank=args.exit_rank,
                min_pos=args.min_pos,
                delta_z_full=args.delta_z_full,
                opt_commission=args.opt_commission,
                strike_mode=args.strike_mode,
                score_blend_w_ic=args.score_blend_w_ic,
                sortino_gate=args.sortino_gate,
            )
            results.append(res)

    # ─── Validation: DSR + CPCV ───
    if args.validate:
        from scipy.stats import skew, kurtosis
        from math import sqrt
        print("\n" + "=" * 70)
        print(f"VALIDATION (DSR trials={args.trials}, CPCV splits={args.cpcv_splits}/test={args.cpcv_test})")
        print("=" * 70)
        for r in results:
            if r.get("status") != "SUCCESS":
                continue
            net_ret = r.get("_net_returns")
            Z_comp = r.get("_Z_composite")
            trade_ret = r.get("_trade_returns")
            dates_s = r.get("_dates_series")
            if net_ret is None or Z_comp is None:
                continue
            
            # DSR
            std_n = np.std(net_ret)
            obs_sr = float((np.mean(net_ret) / std_n) * sqrt(252)) if std_n > 1e-12 else 0.0
            sk = float(skew(net_ret))
            kt = float(kurtosis(net_ret))
            dsr = deflated_sharpe_ratio(obs_sr, n_trials=args.trials, n_obs=len(net_ret),
                                         skewness=sk, kurtosis_excess=kt)
            r["dsr"] = dsr
            
            # CPCV
            cpcv = run_cpcv_backtest(Z_comp, trade_ret, dates_s,
                                      n_splits=args.cpcv_splits, n_test=args.cpcv_test,
                                      purge_gap=5, mode=r.get("position_mode", "binary"),
                                      fee_bps=effective_fee_bps / 10000.0,
                                      z_buffer=r.get("z_buffer", 0.1),
                                      long_only=r.get("long_only", False),
                                      min_pos=r.get("min_pos", 0.5),
                                      delta_z_full=r.get("delta_z_full", 0.3))
            r["cpcv"] = cpcv
            
            print(f"  {r['etf']} ({r['scheme']}): SR={obs_sr:.3f}, "
                  f"DSR={dsr['dsr']:.3f} ({dsr['verdict']}), "
                  f"CPCV median={cpcv['sharpe_median']:.3f}\u00b1{cpcv['sharpe_std']:.3f} "
                  f"({cpcv['pct_positive']:.0f}% pos)")
        print()

    # Save aggregated trades CSV artifact
    plot_results = [r for r in results if r.get("status") == "SUCCESS"]
    if plot_results:
        all_dfs = [r["trade_log_df"] for r in plot_results if r.get("trade_log_df") is not None]
        if all_dfs:
            combined_df = pd.concat(all_dfs, ignore_index=True)
            artifacts_dir = HERE / "artifacts"
            artifacts_dir.mkdir(parents=True, exist_ok=True)
            fut_suffix = "_future" if args.future else ""
            opt_suffix = "_option" if args.option else ""
            combined_csv = artifacts_dir / f"trade_log{fut_suffix}{opt_suffix}.csv"
            combined_df.to_csv(combined_csv, index=False)
            print(f"Saved primary trade log CSV to {combined_csv}")
        
        # Save option trade log CSV if in option mode
        if args.option:
            opt_dfs = [r["option_trade_log_df"] for r in plot_results if r.get("option_trade_log_df") is not None and not r["option_trade_log_df"].empty]
            if opt_dfs:
                combined_opt_df = pd.concat(opt_dfs, ignore_index=True)
                artifacts_dir = HERE / "artifacts"
                artifacts_dir.mkdir(parents=True, exist_ok=True)
                opt_csv = artifacts_dir / "option_trades.csv"
                combined_opt_df.to_csv(opt_csv, index=False)
                print(f"Saved option trade log CSV to {opt_csv}")

    # Resolve target markdown output path
    if args.output:
        out_path = Path(args.output)
    else:
        if args.option:
            out_path = HERE / "REPORT_option.md"
        elif args.future:
            out_path = HERE / "REPORT_future.md"
        else:
            out_path = HERE / "REPORT.md"

    # Generate equity curve plot artifact
    chart_rel_path = None
    if plot_results:
        try:
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt

            fig, ax = plt.subplots(figsize=(10, 4.5), dpi=150)
            # Chart prominence: primary scheme (ICW) bold; all others de-emphasized
            primary_scheme = "icw"
            for r in plot_results:
                if r.get("dates") and r.get("cum_pnl"):
                    dates = pd.to_datetime(r["dates"])
                    cum_pnl = r["cum_pnl"]
                    scheme_lbl = r.get('scheme', '').upper()
                    is_minor = (r.get('scheme') != primary_scheme)
                    ax.plot(dates, cum_pnl, label=f"{r['etf']} [{scheme_lbl}] ({r.get('asset_type', 'Spot ETF')}) (Sharpe: {r['cost_sharpe']:.3f}, PnL: {r['total_pnl']:+.4f})", linewidth=1.0 if is_minor else 1.8, alpha=0.35 if is_minor else 1.0, linestyle='--' if is_minor else '-')
            
            mode_title = "Option Portfolio" if args.option else ("Index Future" if args.future else "Spot ETF")
            scheme_title = args.scheme.upper()
            ax.set_title(f"NewTrade {scheme_title} — {mode_title} OOS Net PnL (10:00 - 14:35 Intraday)", fontsize=11, fontweight='bold')
            ax.set_xlabel("Date", fontsize=9)
            ax.set_ylabel("Cumulative Net PnL", fontsize=9)
            ax.grid(True, linestyle="--", alpha=0.5)
            ax.legend(loc="upper left", frameon=True, fontsize=9)
            fig.tight_layout()

            artifacts_dir = HERE / "artifacts"
            artifacts_dir.mkdir(parents=True, exist_ok=True)
            
            # Derive chart filename stem directly from out_path.stem
            stem = out_path.stem
            if stem.upper() == "REPORT":
                chart_stem = "equity_curve"
            elif stem.upper().startswith("REPORT_"):
                chart_stem = "equity_curve_" + stem[7:]
            elif "REPORT" in stem.upper():
                chart_stem = stem.replace("REPORT", "equity_curve").replace("report", "equity_curve")
            else:
                chart_stem = f"equity_curve_{stem}"

            chart_path = artifacts_dir / f"{chart_stem}.png"
            fig.savefig(chart_path)
            plt.close(fig)
            chart_rel_path = f"artifacts/{chart_stem}.png"
            print(f"Saved equity curve chart to {chart_path}")
        except Exception as e:
            print(f"[WARNING] Failed to generate plot: {e}")

    # Print summary table
    print("\n================================================================================")
    summary_mode = "OPTION PORTFOLIO" if args.option else ("INDEX FUTURE" if args.future else "SPOT ETF")
    print(f"NEWTRADE OOS BACKTEST PERFORMANCE SUMMARY ({summary_mode}) (10:00 - 14:35 Intraday Trades)")
    print("================================================================================")
    
    headers = ["ETF", "Asset", "Side", "OOS Period", "Z_th", "Features", "Trades", "Cost Sharpe", "Raw Sharpe", "Total PnL", "Long PnL", "Long Sharpe", "Short PnL", "Short Sharpe", "Max DD", "Win Rate", "Turnover"]
    
    SCHEME_TITLES = {
        "ensemble": "Ensemble (Equal-Weight Average)",
        "rank": f"Rank Bounded Weight ({args.rank_mapping.capitalize()})",
        "ew": "Equal Weight (EW, TailIC-selected top-K)",
        "icw": "IC Weight (ICW)",
        "score": f"Score Weight ({args.score_blend_w_ic:.0%} TailIC + {1-args.score_blend_w_ic:.0%} Sortino)",
        "sortino": "Sortino Weight (tail-IC selection + Score-blend weights)",
        "glm": "Linear GLM",
    }
    
    def _format_row(r):
        if r["status"] == "SUCCESS":
            z_l = r.get("z_th_long", r["z_th"])
            z_s = r.get("z_th_short", r["z_th"])
            tr_l = r.get("z_th_train_long")
            tr_s = r.get("z_th_train_short")
            
            if r.get("long_only", False):
                z_th_str = f"L:{z_l:.2f}"
                if tr_l is not None:
                    z_th_str += f" (train:{tr_l:.2f})"
            else:
                z_th_str = f"L:{z_l:.2f}/S:{z_s:.2f}"
                if tr_l is not None and tr_s is not None:
                    z_th_str += f" (train L:{tr_l:.2f}/S:{tr_s:.2f})"
                elif tr_l is not None:
                    z_th_str += f" (train L:{tr_l:.2f})"
            
            n_l = r.get("n_long_trades", 0)
            n_s = r.get("n_short_trades", 0)
            trades_str = f"{r.get('n_trades', 0)} ({n_l}L/{n_s}S)"
            
            # Option mode: show option-specific trade count
            if r.get("option_n_trades") is not None:
                trades_str = f"{r['option_n_trades']} opt"

            win_l = f"{r['win_rate_long_pct']:.1f}%" if r.get("win_rate_long_pct") is not None else "N/A"
            win_s = f"{r['win_rate_short_pct']:.1f}%" if r.get("win_rate_short_pct") is not None else "N/A"
            win_str = f"{r['win_rate_pct']:.1f}% (L:{win_l}, S:{win_s})"
            
            # Total PnL display: RMB for option mode, percentage for spot/future
            if r.get("option_total_pnl_rmb") is not None:
                total_pnl_str = f"{r['option_total_pnl_rmb']:+,.0f} RMB"
            else:
                total_pnl_str = f"{r['total_pnl']:+.4f}"

            return [
                r["etf"],
                r.get("asset_type", "Spot ETF"),
                r["side"],
                r["period"],
                z_th_str,
                str(r["n_features"]),
                trades_str,
                f"{r['cost_sharpe']:.3f}",
                f"{r['raw_sharpe']:.3f}",
                total_pnl_str,
                f"{r.get('long_pnl', 0):+.4f}",
                f"{r.get('long_sharpe', 0):.3f}",
                f"{r.get('short_pnl', 0):+.4f}",
                f"{r.get('short_sharpe', 0):.3f}",
                f"{r['max_drawdown']:.4f}",
                win_str,
                f"{r['ann_turnover']:.1f}x",
            ]
        else:
            return [
                r["etf"],
                r.get("asset_type", "N/A"),
                r["side"],
                r.get("period", "N/A"),
                "N/A",
                str(r["n_features"]),
                "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A"
            ]

    
    def _render_table(rows):
        lines = []
        lines.append("| " + " | ".join(headers) + " |")
        lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
        for row in rows:
            lines.append("| " + " | ".join(row) + " |")
        return "\n".join(lines)
    
    # Group results by scheme: ENSEMBLE first (primary, 2026-08), then ICW, sortino, others, ew last
    from collections import OrderedDict
    scheme_order_pref = ["ensemble", "icw", "sortino"]
    present_schemes = [r.get("scheme") for r in results]
    scheme_groups = OrderedDict()
    for s in scheme_order_pref:
        if s in present_schemes:
            scheme_groups[s] = [r for r in results if r.get("scheme") == s]
    for r in results:
        s = r.get("scheme", "?")
        if s not in scheme_order_pref and s != "ew":
            scheme_groups.setdefault(s, []).append(r)
    if "ew" in present_schemes:
        scheme_groups["ew"] = [r for r in results if r.get("scheme") == "ew"]

    # Primary scheme (uncollapsed section + bold chart line): first group in order
    primary_scheme = next(iter(scheme_groups), None)

    # Build report sections
    report_sections = []
    chart_img_included = False
    for scheme_key, scheme_results in scheme_groups.items():
        rows = [_format_row(r) for r in scheme_results]
        title = SCHEME_TITLES.get(scheme_key, scheme_key.upper())
        table_md = _render_table(rows)
        
        if scheme_key != primary_scheme:
            # Collapsed details block for all secondary schemes
            prefix = ""
            if chart_rel_path and not chart_img_included:
                prefix = f"![Cumulative Equity]({chart_rel_path})\n\n"
                chart_img_included = True
            section = f"{prefix}<details>\n<summary><b>{title}</b> (click to expand)</summary>\n\n{table_md}\n\n</details>"
        else:
            # Uncollapsed main section for the primary scheme
            img_md = ""
            if chart_rel_path and not chart_img_included:
                img_md = f"![Cumulative Equity]({chart_rel_path})\n\n"
                chart_img_included = True
            section = f"## {title}\n\n{img_md}{table_md}"
        report_sections.append(section)
    
    report_content = "\n\n".join(report_sections)
    print("\n" + report_content + "\n")

    # Clean results before saving JSON (drop large arrays & DataFrames to keep JSON clean)
    clean_results = []
    for r in results:
        r_copy = dict(r)
        r_copy.pop("dates", None)
        r_copy.pop("cum_pnl", None)
        r_copy.pop("trade_log_df", None)
        r_copy.pop("_net_returns", None)
        r_copy.pop("_Z_composite", None)
        r_copy.pop("_trade_returns", None)
        r_copy.pop("_dates_series", None)
        r_copy.pop("option_trade_log_df", None)
        clean_results.append(r_copy)

    # Save markdown report
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("# NewTrade OOS Backtest Report\n\n")
        end_date_disp = args.end_date if args.end_date else (results[0]["dates"][-1] if results and results[0].get("dates") else "present")
        f.write(f"- **OOS Evaluation Period**: `{args.start_date} ~ {end_date_disp}`\n")
        f.write(f"- **Intraday Trade Session**: `10:00 AM Open -> 14:35 PM Close`\n")
        f.write(f"- **Scheme(s)**: `{args.scheme.upper()}`\n")
        f.write(f"- **Conviction Threshold**: `{args.z_th}` (buffer=+{args.z_buffer})\n")
        f.write(f"- **Position Mode**: `{args.position_mode}`\n")
        if args.option:
            f.write(f"- **Mode**: `Option Portfolio`\n")
            f.write(f"- **Initial Capital**: `100,000 RMB per ETF`\n")
            f.write(f"- **Trade Budget**: `10% of portfolio capital per signal`\n")
            f.write(f"- **Commission**: `{args.opt_commission} RMB per contract per side ({args.opt_commission*2:.1f} RMB round-trip per contract)`\n")
            f.write(f"- **Option Selection**: `Nearest OTM, >=7 DTM`\n\n")
        else:
            if args.stoploss:
                f.write(f"- **Stop-Loss Execution**: `Enabled ({args.stoploss_mode}={args.stoploss_param})`\n")
                f.write(f"- **Transaction Friction**: `{effective_fee_bps * 2.0:.1f} bps roundtrip ({effective_fee_bps:.1f} bps/leg)`\n\n")
            else:
                f.write(f"- **Stop-Loss Execution**: `Disabled (Hold to 14:35 Close)`\n")
                f.write(f"- **Transaction Friction**: `{effective_fee_bps} bps`\n\n")
        f.write(report_content + "\n")
        
        # Append validation section if available
        if args.validate:
            val_rows = [r for r in results if r.get("status") == "SUCCESS" and "dsr" in r]
            if val_rows:
                f.write("\n---\n\n## Validation (DSR + CPCV)\n\n")
                f.write(f"- **DSR Trials**: `{args.trials}`\n")
                f.write(f"- **CPCV**: `{args.cpcv_splits}` splits, `{args.cpcv_test}` test chunks, purge=5\n\n")
                f.write("| ETF | Scheme | Sharpe | DSR | Verdict | CPCV Median | CPCV Std | % Positive |\n")
                f.write("| --- | --- | --- | --- | --- | --- | --- | --- |\n")
                for r in val_rows:
                    d = r["dsr"]
                    c = r["cpcv"]
                    f.write(f"| {r['etf']} | {r['scheme']} | {r['cost_sharpe']:.3f} | "
                            f"{d['dsr']:.3f} | {d['verdict']} | {c['sharpe_median']:.3f} | "
                            f"{c['sharpe_std']:.3f} | {c['pct_positive']:.0f}% |\n")
                f.write("\n")
    print(f"Saved backtest report to {out_path}")

    # Save JSON result artifact in newtrade/data/
    data_dir = HERE / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    scheme_label = args.scheme if args.scheme != "all" else "all_schemes"
    json_path = data_dir / f"backtest_results_{scheme_label}_{args.side}.json"
    with open(json_path, "w") as f:
        json.dump(clean_results, f, indent=2)
    print(f"Saved JSON results to {json_path}")


if __name__ == "__main__":
    main()

