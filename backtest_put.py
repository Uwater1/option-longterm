"""
Protective Put Backtester — Daily Position-Tracking & Multi-Regime Alpha Integration.
====================================================================================
Evaluates signals daily, executes entries mid-cycle, and holds until expiry.
Supports Phase 1, Phase 2, and Phase 3 models across all 4 regimes:
  - Regime 1: Short-Term Fall (OTM Level 1)
  - Regime 2: Medium-Term Fall (OTM Level 1)
  - Regime 3: Short-Term Crash (OTM Level 2)
  - Regime 4: Medium-Term Crash (OTM Level 2)
"""

import sys
import os
import argparse
import json
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Ensure project root is on path for imports
sys.path.insert(0, os.path.abspath("."))

from backtest_engine import (
    select_underlying, load_data, get_strike_by_level, get_cycles,
    simulate_limit_order, RISK_FREE, COMMISSION, NUM_CONTRACTS,
    SPREAD_HALF, EXERCISE_COST, Tee, ETF_NAME
)
from alpha_model import AlphaModel

# Optimal deployable alpha configurations (regime and phase) per ETF
# based on OOS validation (backtest/alpha_phase_comparison.md)
DEFAULT_ALPHA_CONFIGS = {
    "50": [
        {"regime": "reg4", "phase": 3}  # MT Crash -> Phase 3
    ],
    "300": [
        {"regime": "reg1", "phase": 1}, # ST Fall -> Phase 1
        {"regime": "reg2", "phase": 3}  # MT Fall -> Phase 3
    ],
    "500": [
        {"regime": "reg3", "phase": 2}  # ST Crash -> Phase 2
    ]
}

# Regime names and levels (1=OTM1, 2=OTM2)
REGIME_PUT_LEVEL = {"reg1": 1, "reg2": 1, "reg3": 2, "reg4": 2}
REGIME_NAMES = {
    "reg1": "ST Fall", "reg2": "MT Fall",
    "reg3": "ST Crash", "reg4": "MT Crash",
}


def get_phase1_scores(df_norm, model_cfg):
    """Phase 1: linear weighted score from JSON config."""
    weights = model_cfg["weights"]
    ws = pd.Series(0.0, index=df_norm.index)
    tw = 0.0
    for col, w in weights.items():
        if col in df_norm.columns:
            vals = df_norm[col].fillna(0.5)
            ws += vals * w
            tw += w
    scores = (ws / tw) if tw > 0 else ws
    return scores, float(model_cfg.get("threshold", 0.5)), float(model_cfg.get("gamma", 0.0))


def get_phase2_scores(df_norm, etf_choice, regime_key):
    """Phase 2: LightGBM calibrated probabilities."""
    from alpha_model_ml import predict_proba_all
    preds, thresholds = predict_proba_all(df_norm, etf_choice, walk_forward=True)
    if regime_key not in preds:
        raise KeyError(f"Phase 2 has no model for {regime_key}")
    return preds[regime_key], thresholds.get(regime_key, 0.5), 0.0


def get_phase3_scores(df_norm, etf_choice, regime_key):
    """Phase 3: hybrid stack."""
    from alpha_model_hybrid import predict_all as hyb_predict
    preds, thresholds = hyb_predict(df_norm, etf_choice)
    if regime_key not in preds:
        raise KeyError(f"Phase 3 has no model for {regime_key}")
    return preds[regime_key], thresholds.get(regime_key, 0.5), 0.0


def _indicators_at_row(df, idx):
    """Build indicators dictionary at the given row."""
    row = df.loc[idx]
    return {
        "rsi": row.get("rsi14"),
        "bbu": row.get("bbu20"),
        "bbl": row.get("bbl20"),
        "sma20": row.get("sma20"),
        "sma50": row.get("sma50"),
        "sma200": row.get("sma200"),
        "atr20": row.get("atr20"),
        "roc10": row.get("roc10"),
        "roc20": row.get("roc20"),
        "vol20": row.get("vol20"),
        "vol20_median": row.get("vol20_median"),
        "macd_hist": row.get("macd_hist"),
        "skew_20": row.get("skew_20"),
        "kurt_20": row.get("kurt_20"),
        "vol_accel": row.get("vol_accel"),
        "dd_252": row.get("dd_252"),
        "dist_sma200": row.get("dist_sma200"),
        "dist_sma50": row.get("dist_sma50"),
        "iv_vol_ratio": row.get("iv_vol_ratio"),
    }


def main():
    parser = argparse.ArgumentParser(description="New Protective Put Backtest - Daily Position-Tracking")
    parser.add_argument("etf", type=str, choices=["50", "300", "500"], default="300", nargs="?", help="ETF choice")
    parser.add_argument("--alpha", action="store_true", help="Use optimized alpha models (deployable configurations)")
    parser.add_argument("--regime", type=str, choices=["reg1", "reg2", "reg3", "reg4"], help="Use specific alpha regime")
    parser.add_argument("--phase", type=int, choices=[1, 2, 3], help="Force a specific alpha model phase")
    parser.add_argument("--limit-entry", action="store_true", help="Use Black-Scholes limit orders for entries")
    parser.add_argument("--no-filter", action="store_true", help="Cycle-start entry baseline (hedge every cycle)")
    parser.add_argument("--level", type=int, help="Override option OTM level (1=closest OTM, etc.)")
    parser.add_argument("--no-plot", action="store_true", help="Skip saving P&L chart")
    args = parser.parse_args()

    etf_choice = args.etf
    select_underlying(etf_choice)

    # Determine alpha config settings
    use_alpha = args.alpha or (args.regime is not None) or (args.phase is not None)
    
    active_configs = []
    if use_alpha:
        if args.regime is not None:
            phase_val = args.phase
            if phase_val is None:
                # Default to the winning phase if deployable, else default to phase 1
                phase_val = 1
                for cfg in DEFAULT_ALPHA_CONFIGS.get(etf_choice, []):
                    if cfg["regime"] == args.regime:
                        phase_val = cfg["phase"]
                        break
            active_configs = [{"regime": args.regime, "phase": phase_val}]
        else:
            active_configs = DEFAULT_ALPHA_CONFIGS.get(etf_choice, [])

    # Suffix for files/logs
    suffix_parts = [f"{etf_choice}ETF"]
    if args.no_filter:
        suffix_parts.append("nofilter")
    elif use_alpha:
        suffix_parts.append("alpha")
        for cfg in active_configs:
            suffix_parts.append(f"{cfg['regime']}_p{cfg['phase']}")
    else:
        suffix_parts.append("static")
    if args.limit_entry:
        suffix_parts.append("limit")
    suffix = "_".join(suffix_parts)

    # Setup Logging
    orig_stdout = sys.stdout
    log_file = f"backtest/backtest_put_{suffix}.log"
    os.makedirs("backtest", exist_ok=True)
    f_log = open(log_file, 'w', encoding='utf-8')
    sys.stdout = Tee(sys.stdout, f_log)

    print("=" * 80)
    print(f"  Protective Put Daily Backtest System — Running {etf_choice}ETF")
    print(f"  Suffix: {suffix}")
    print("=" * 80)

    # Load Data
    inst, opt, etf_data = load_data()

    # Precompute Indicator normalization & Alpha scores
    model = AlphaModel()
    df_norm = model.compute_normalized_indicators(etf_data)

    # Expiries list (monthly contracts with both call and puts traded)
    expiries = sorted(
        opt.groupby(["maturity_date", "option_type"])["order_book_id"]
        .nunique().unstack("option_type").dropna().index.tolist()
    )

    # Daily IVs for dynamic thresholds and calculations
    from backtest_engine import PATH_IV_CACHE
    if os.path.exists(PATH_IV_CACHE):
        daily_ivs = pd.read_parquet(PATH_IV_CACHE).iloc[:, 0]
        daily_ivs.index = pd.to_datetime(daily_ivs.index)
    else:
        daily_ivs = pd.Series(0.20, index=df_norm.index)
    df_norm["iv"] = daily_ivs.reindex(df_norm.index).ffill()
    df_norm["iv_vol_ratio"] = df_norm["iv"] / df_norm["vol20"]

    # Precompute scores, thresholds, gammas for all active regimes
    scores_dict = {}
    thresholds_dict = {}
    gammas_dict = {}

    cache_p2 = None
    cache_p3 = None

    if use_alpha:
        print("\nPrecomputing Alpha Scores:")
        for cfg in active_configs:
            reg = cfg["regime"]
            ph = cfg["phase"]
            print(f"  - Loading {REGIME_NAMES[reg]} ({reg}) using Phase {ph}...")
            
            if ph == 1:
                with open("backtest/alpha_put_models.json") as f_cfg:
                    all_models = json.load(f_cfg)
                model_cfg = all_models.get(etf_choice, {}).get(reg)
                if not model_cfg:
                    raise ValueError(f"No Phase 1 configuration found for {etf_choice} {reg}")
                scores, threshold, gamma = get_phase1_scores(df_norm, model_cfg)
            elif ph == 2:
                if cache_p2 is None:
                    from alpha_model_ml import predict_proba_all
                    cache_p2 = predict_proba_all(df_norm, etf_choice, walk_forward=True)
                preds, thresholds = cache_p2
                scores = preds[reg]
                threshold = thresholds.get(reg, 0.5)
                gamma = 0.0
            elif ph == 3:
                if cache_p3 is None:
                    from alpha_model_hybrid import predict_all as hyb_predict
                    cache_p3 = hyb_predict(df_norm, etf_choice)
                preds, thresholds = cache_p3
                scores = preds[reg]
                threshold = thresholds.get(reg, 0.5)
                gamma = 0.0

            scores_dict[reg] = scores
            thresholds_dict[reg] = threshold
            gammas_dict[reg] = gamma

    # Load 5m data if limit entry is requested
    opt_5m = None
    etf_5m = None
    if args.limit_entry:
        opt_5m_path = f"./data/{etf_choice}ETF_historical_prices_5m.parquet"
        etf_5m_path = f"./data/{etf_choice}ETF_5m.parquet" if etf_choice != "300" else "./data/510300_5m.parquet"
        if os.path.exists(opt_5m_path) and os.path.exists(etf_5m_path):
            print(f"\nLoading 5m option data from {opt_5m_path}...")
            opt_5m = pd.read_parquet(opt_5m_path)
            opt_5m["datetime"] = pd.to_datetime(opt_5m["datetime"])
            print(f"Loading 5m ETF data from {etf_5m_path}...")
            etf_5m = pd.read_parquet(etf_5m_path)
            etf_5m["datetime"] = pd.to_datetime(etf_5m["datetime"])
        else:
            print("\n  WARNING: 5m data files not found, limit order simulation disabled.")
            args.limit_entry = False

    # Backtest Loop
    active_position = None
    trades_log = []
    trading_days = sorted(df_norm.index.unique())

    print("\n" + "=" * 110)
    print(f"  Trade Log:")
    print("=" * 110)
    print(f"  {'EntryDate':<11} {'ExitDate':<11} {'Regime':<12} {'Phase':<5} {'Strike':<7} {'EntryPx':<8} {'ExitPx':<8} {'NetPnL':<8} {'FillType':<12}")
    print("  " + "-" * 106)

    for tdate in trading_days:
        tdate = pd.Timestamp(tdate)
        idx = tdate.normalize()

        # 1. Handle Active Position Settlement
        if active_position is not None:
            if tdate >= active_position["expiry_date"]:
                leg = active_position["leg"]
                entry_px = active_position["entry_px"]
                mult = leg["contract_multiplier"]
                strike = leg["strike_price"]
                
                etf_settle = float(df_norm.loc[idx, "close"])
                intrinsic = max(0.0, strike - etf_settle)
                
                exercise_cost = EXERCISE_COST if intrinsic > 0 else 0.0
                net_rmb = (intrinsic - entry_px) * mult * NUM_CONTRACTS - COMMISSION - exercise_cost
                
                trade_record = {
                    "entry_date": active_position["entry_date"],
                    "exit_date": tdate,
                    "regime": active_position["regime"],
                    "phase": active_position["phase"],
                    "strike": strike,
                    "entry_px": entry_px,
                    "exit_px": intrinsic,
                    "net_pnl": net_rmb,
                    "note": f"expiry_settle ETF={etf_settle:.4f}",
                    "put_filled": active_position["put_filled"]
                }
                trades_log.append(trade_record)
                
                fill_tag = "LIMIT" if trade_record["put_filled"] else ("FORCE" if args.limit_entry else "MARKET")
                print(f"  {trade_record['entry_date'].strftime('%Y-%m-%d')} "
                      f"{trade_record['exit_date'].strftime('%Y-%m-%d')} "
                      f"{trade_record['regime']:<12} "
                      f"{trade_record['phase']:<5} "
                      f"{trade_record['strike']:<7.3f} "
                      f"{trade_record['entry_px']:<8.4f} "
                      f"{trade_record['exit_px']:<8.4f} "
                      f"{trade_record['net_pnl']:>8.1f} "
                      f"{fill_tag:<12}")
                active_position = None

        # 2. Check for Entry
        if active_position is None:
            # Find next expiry
            expiry_date = None
            for exp in expiries:
                if exp > tdate:
                    if (exp - tdate).days >= 3: # Avoid near-immediate maturity contracts
                        expiry_date = exp
                        break
            if expiry_date is None:
                continue

            triggered_regime = None
            triggered_phase = None

            if args.no_filter:
                # Cycle start entry logic
                is_cycle_start = False
                for cyc in get_cycles(opt, etf_data):
                    if pd.Timestamp(cyc["entry_date"]).normalize() == idx:
                        is_cycle_start = True
                        break
                if is_cycle_start:
                    triggered_regime = "no_filter"
                    triggered_phase = 0
            elif use_alpha:
                # Alpha models scanning
                for cfg in active_configs:
                    reg = cfg["regime"]
                    ph = cfg["phase"]
                    score = scores_dict[reg].loc[idx]
                    threshold = thresholds_dict[reg]
                    gamma = gammas_dict[reg]
                    ivr = df_norm.loc[idx, "iv_vol_ratio"] if "iv_vol_ratio" in df_norm.columns else 1.0
                    if pd.isna(ivr):
                        ivr = 1.0
                    thr_t = threshold + gamma * (ivr - 1.0)
                    
                    if score > thr_t:
                        triggered_regime = reg
                        triggered_phase = ph
                        break
            else:
                # Fallback: daily static filter
                ind_dict = _indicators_at_row(df_norm, idx)
                etf_close = float(df_norm.loc[idx, "close_adj"]) if "close_adj" in df_norm.columns else float(df_norm.loc[idx, "close"])
                from backtest_strategies import PutStrategy
                strat = PutStrategy(etf_choice=etf_choice, put_level=args.level if args.level is not None else 1)
                passed, _ = strat.evaluate_filter(etf_data, idx, etf_close, ind_dict)
                if passed:
                    triggered_regime = "static_filter"
                    triggered_phase = 0

            if triggered_regime is not None:
                # OTM Put Strike Level mapping
                if args.level is not None:
                    lvl = args.level
                elif triggered_regime in ["reg1", "reg2"]:
                    lvl = 1 # Fall regimes -> ATM/OTM1
                elif triggered_regime in ["reg3", "reg4"]:
                    lvl = 2 # Crash regimes -> OTM2
                else:
                    lvl = 1 # Static fallback level

                leg = get_strike_by_level(opt, etf_data, tdate, expiry_date, "P", lvl)
                if leg is not None:
                    entry_mid = float(leg["close"])
                    exec_px = entry_mid * (1 + SPREAD_HALF)
                    put_filled = True
                    put_limit_px = None
                    put_exec_px = None

                    if args.limit_entry:
                        from backtest_strategies import _predict_put_limit_price
                        sim_res = simulate_limit_order(
                            leg, "buy", tdate, expiry_date, etf_data, opt_5m, etf_5m,
                            _predict_put_limit_price, float(df_norm.loc[idx, "close"])
                        )
                        put_filled = sim_res["filled"]
                        put_limit_px = sim_res["limit_px"]
                        put_exec_px = sim_res["exec_px"]
                        
                        if put_filled:
                            exec_px = put_exec_px
                        else:
                            # If not filled, buy at the close of the entry window (force fill)
                            exec_px = entry_mid * (1 + SPREAD_HALF)
                            put_filled = False

                    active_position = {
                        "entry_date": tdate,
                        "expiry_date": expiry_date,
                        "leg": leg,
                        "entry_px": exec_px,
                        "regime": triggered_regime,
                        "phase": triggered_phase,
                        "put_filled": put_filled,
                        "put_limit_px": put_limit_px,
                        "put_exec_px": put_exec_px,
                    }

    print("=" * 110)

    # Compute & Print statistics
    n_trades = len(trades_log)
    if n_trades > 0:
        pnls = np.array([t["net_pnl"] for t in trades_log])
        net_pnl = pnls.sum()
        win_rate = (pnls > 0).mean()
        mean_pnl = pnls.mean()
        std_pnl = pnls.std(ddof=1) if n_trades > 1 else 0.0
        
        # Sharpe (using annualization matching cycle counts)
        sharpe = (mean_pnl / std_pnl * np.sqrt(12)) if std_pnl > 0 else 0.0
        
        # Max drawdown
        cumsum = np.cumsum(pnls)
        running_max = np.maximum.accumulate(cumsum)
        drawdowns = cumsum - running_max
        max_dd = drawdowns.min()
        
        # Limit filled rate
        n_limit = sum(1 for t in trades_log if t["put_filled"] is not None)
        n_filled = sum(1 for t in trades_log if t["put_filled"] is True)
        fill_rate = n_filled / n_limit if n_limit > 0 else 0.0
    else:
        net_pnl = 0.0
        win_rate = 0.0
        mean_pnl = 0.0
        sharpe = 0.0
        max_dd = 0.0
        fill_rate = 0.0

    print("\n" + "=" * 50)
    print(f"  SUMMARY STATISTICS — {etf_choice}ETF — Mode: {suffix}")
    print("=" * 50)
    print(f"  Total Trades           : {n_trades}")
    print(f"  Win Rate               : {win_rate:.1%}")
    print(f"  Total Net P&L          : {net_pnl:,.2f} RMB")
    print(f"  Average P&L per Trade  : {mean_pnl:,.2f} RMB")
    print(f"  Sharpe Ratio (ann.)    : {sharpe:.2f}")
    print(f"  Max Drawdown           : {max_dd:,.2f} RMB")
    if args.limit_entry:
        print(f"  Put limit fill rate    : {fill_rate:.1%} ({n_filled}/{n_limit} cycles)")
    print("=" * 50)

    # Save to CSV
    csv_path = f"backtest/backtest_put_{suffix}.csv"
    pd.DataFrame(trades_log).to_csv(csv_path, index=False)
    print(f"\n  CSV saved   → {csv_path}")

    # Plot
    if not args.no_plot and n_trades > 0:
        dates = [t["exit_date"] for t in trades_log]
        cumulative = np.cumsum(pnls)
        etf_sub = df_norm.reindex(dates, method='ffill')["close"]
        etf_norm = (etf_sub / etf_sub.iloc[0] - 1) * 100

        fig, ax1 = plt.subplots(figsize=(10, 6))
        
        color = '#2980b9'
        ax1.set_xlabel('Exit Date', fontweight='bold')
        ax1.set_ylabel('Cumulative P&L (RMB)', color=color, fontweight='bold')
        ax1.plot(dates, cumulative, color=color, linewidth=2.5, marker='o', label="Put Hedging P&L")
        ax1.tick_params(axis='y', labelcolor=color)
        ax1.grid(True, linestyle='--', alpha=0.5)
        
        ax2 = ax1.twinx()  
        color = '#f39c12'
        ax2.set_ylabel('Underlying ETF Return (%)', color=color, fontweight='bold')
        ax2.plot(dates, etf_norm, color=color, linestyle='--', linewidth=1.5, label=f"{etf_choice}ETF Return")
        ax2.tick_params(axis='y', labelcolor=color)
        
        plt.title(f"New Protective Put Backtest — {etf_choice}ETF\nCadence: Daily, Mode: {suffix}", fontsize=12, fontweight='bold')
        fig.tight_layout()
        
        png_path = f"backtest/backtest_put_{suffix}.png"
        plt.savefig(png_path, dpi=200, bbox_inches='tight')
        print(f"  Chart saved → {png_path}")

    sys.stdout = orig_stdout
    f_log.close()


if __name__ == "__main__":
    main()
