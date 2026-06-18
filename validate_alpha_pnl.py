"""
validate_alpha_pnl.py — Put P&L Validator for the Alpha Model
=============================================================
Validates the 4-regime alpha model by computing ACTUAL put option P&L per
trigger (not just statistical lift), using historical option prices.

Three baselines per regime:
  A. No hedge         (P&L = 0)
  B. Hedge every cycle (always buy put at each monthly cycle start)
  C. Existing static filter (PutStrategy.evaluate_filter at cycle starts)

Walk-forward: only triggers in test folds (year >= 2021) count toward OOS P&L.

A regime variant is DEPLOYABLE only if:
  - OOS net P&L per trigger > 0
  - OOS lift CI lower bound > 1.0 (crash) OR mean_ret < baseline (fall)
  - Beats Baseline C (static filter) on net P&L

Usage:
  python validate_alpha_pnl.py -e 300 --phase 1
  python validate_alpha_pnl.py -e all --phase 1
  python validate_alpha_pnl.py -e 300 --phase 2   # after Phase 2 models built
"""

import os
import json
import argparse
import numpy as np
import pandas as pd
from backtest_engine import (select_underlying, load_data, get_strike_by_level,
                             calc_leg_pnl, NUM_CONTRACTS, COMMISSION,
                             get_cycles)
from alpha_model import AlphaModel
from backtest_strategies import PutStrategy

OOS_START_YEAR = 2021
MODEL_FILE = "backtest/alpha_put_models.json"
ML_MODEL_DIR = "backtest/alpha_ml_models"

# Regime → OTM put level (Fall=ATM/OTM1, Crash=OTM2). Per AGENTS.md decision matrix.
REGIME_PUT_LEVEL = {"reg1": 1, "reg2": 1, "reg3": 2, "reg4": 2}
REGIME_NAMES = {
    "reg1": "ST Fall", "reg2": "MT Fall",
    "reg3": "ST Crash", "reg4": "MT Crash",
}
REGIME_IS_CRASH = {"reg1": False, "reg2": False, "reg3": True, "reg4": True}


def _next_expiry(trigger_date, expiries):
    """First monthly expiry strictly after trigger_date."""
    for exp in expiries:
        if exp > trigger_date:
            return exp
    return None


def _threshold_aware_vec(scores, iv_vol_ratio, thresh_base, gamma):
    return thresh_base + gamma * (np.nan_to_num(iv_vol_ratio, nan=1.0) - 1.0)


def put_pnl_for_trigger(opt, etf, trigger_date, expiry, put_level, num_contracts=NUM_CONTRACTS):
    """Buy OTM put at trigger day close, hold to expiry. Returns net RMB or None."""
    try:
        leg = get_strike_by_level(opt, etf, trigger_date, expiry, "P", put_level)
    except Exception:
        return None
    if leg is None:
        return None
    try:
        res = calc_leg_pnl(leg, opt, etf, expiry, "buy", is_buyer_at_expiry=True)
    except Exception:
        return None
    if res is None:
        return None
    return res["net_rmb"] * num_contracts


def _summarize_pnl(pnls):
    """Aggregate P&L list → dict."""
    pnls = np.array([p for p in pnls if p is not None], dtype=float)
    n = len(pnls)
    if n == 0:
        return {"n": 0, "net_pnl": 0.0, "win_rate": 0.0, "mean_per_trigger": 0.0,
                "sharpe": 0.0, "max_dd": 0.0}
    net = float(pnls.sum())
    mean = float(pnls.mean())
    std = float(pnls.std(ddof=1)) if n > 1 else 0.0
    sharpe = (mean / std * np.sqrt(12)) if std > 0 else 0.0  # ~monthly triggers
    cumsum = np.cumsum(pnls)
    running_max = np.maximum.accumulate(cumsum)
    max_dd = float(np.min(cumsum - running_max))
    win_rate = float((pnls > 0).mean())
    return {"n": n, "net_pnl": net, "win_rate": win_rate,
            "mean_per_trigger": mean, "sharpe": float(sharpe), "max_dd": max_dd}


def static_filter_cycle_pnls(opt, etf, etf_choice, put_level, cycles, oos_only=True):
    """Baseline C: existing PutStrategy static filter at monthly cycle starts.
    Returns list of per-cycle net P&L for triggered cycles (OOS only if oos_only)."""
    strat = PutStrategy(etf_choice=etf_choice, put_level=put_level)
    pnls = []
    for cyc in cycles:
        entry = cyc["entry_date"]
        expiry = cyc["expiry_date"]
        if oos_only and pd.Timestamp(entry).year < OOS_START_YEAR:
            continue
        idx = pd.Timestamp(entry).normalize()
        if idx not in etf.index:
            continue
        ind = _indicators_at(etf, idx)
        etf_close = float(etf.loc[idx, "close_adj"]) if "close_adj" in etf.columns else float(etf.loc[idx, "close"])
        passed, _ = strat.evaluate_filter(etf, idx, etf_close, ind)
        if not passed:
            continue
        leg = get_strike_by_level(opt, etf, entry, expiry, "P", put_level)
        if leg is None:
            continue
        res = calc_leg_pnl(leg, opt, etf, expiry, "buy", is_buyer_at_expiry=True)
        if res is not None:
            pnls.append(res["net_rmb"] * NUM_CONTRACTS)
    return pnls


def all_hedge_cycle_pnls(opt, etf, put_level, cycles, oos_only=True):
    """Baseline B: hedge EVERY monthly cycle start (no filter)."""
    pnls = []
    for cyc in cycles:
        entry = cyc["entry_date"]
        expiry = cyc["expiry_date"]
        if oos_only and pd.Timestamp(entry).year < OOS_START_YEAR:
            continue
        leg = get_strike_by_level(opt, etf, entry, expiry, "P", put_level)
        if leg is None:
            continue
        res = calc_leg_pnl(leg, opt, etf, expiry, "buy", is_buyer_at_expiry=True)
        if res is not None:
            pnls.append(res["net_rmb"] * NUM_CONTRACTS)
    return pnls


def _indicators_at(etf, idx):
    """Build the indicators dict expected by PutStrategy.evaluate_filter."""
    row = etf.loc[idx]
    return {
        "rsi": row.get("rsi14"), "bbu": row.get("bbu20"), "bbl": row.get("bbl20"),
        "sma20": row.get("sma20"), "sma50": row.get("sma50"), "sma200": row.get("sma200"),
        "atr20": row.get("atr20"), "roc10": row.get("roc10"), "roc20": row.get("roc20"),
        "vol20": row.get("vol20"), "vol20_median": row.get("vol20_median"),
        "macd_hist": row.get("macd_hist"), "skew_20": row.get("skew_20"),
        "kurt_20": row.get("kurt_20"), "vol_accel": row.get("vol_accel"),
        "dd_252": row.get("dd_252"), "dist_sma200": row.get("dist_sma200"),
        "dist_sma50": row.get("dist_sma50"), "iv_vol_ratio": row.get("iv_vol_ratio"),
    }


def get_phase1_scores(df_norm, model_cfg, regime_key):
    """Phase 1: linear weighted score from JSON config. Returns (scores, threshold, gamma)."""
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
    """Phase 2: LightGBM calibrated probabilities. Returns (scores, threshold, gamma=0)."""
    from alpha_model_ml import predict_proba_all
    preds, thresholds = predict_proba_all(df_norm, etf_choice, walk_forward=True)
    if regime_key not in preds:
        raise KeyError(f"Phase 2 has no model for {regime_key}")
    return preds[regime_key], thresholds.get(regime_key, 0.5), 0.0


def get_phase3_scores(df_norm, etf_choice, regime_key):
    """Phase 3: hybrid stack. Returns (scores, threshold, gamma=0)."""
    from alpha_model_hybrid import predict_all as hyb_predict
    preds, thresholds = hyb_predict(df_norm, etf_choice)
    if regime_key not in preds:
        raise KeyError(f"Phase 3 has no model for {regime_key}")
    return preds[regime_key], thresholds.get(regime_key, 0.5), 0.0


SCORE_PROVIDERS = {
    1: ("phase1", get_phase1_scores),
    2: ("phase2", get_phase2_scores),
    3: ("phase3", get_phase3_scores),
}


def evaluate_regime_pnl(df_norm, opt, etf, etf_choice, regime_key, model_cfg,
                        score_provider, expiries, cycles, oos_only=True, cadence="cycle"):
    """
    For a single regime: find trigger days, compute put P&L, compare baselines.
    score_provider(df_norm, model_cfg, regime_key) → (scores Series, threshold, gamma).
    cadence: 'cycle' = evaluate alpha at monthly cycle starts (fair vs baselines B/C);
             'daily' = evaluate alpha every trading day (requires TODO 4 daily scanning).
    """
    scores, threshold, gamma = score_provider(df_norm, model_cfg, regime_key)
    put_level = REGIME_PUT_LEVEL[regime_key]
    dates = pd.to_datetime(df_norm.index)

    trigger_pnls = []
    trigger_dates = []
    skipped = 0

    if cadence == "cycle":
        # Evaluate alpha at each monthly cycle entry (production-relevant).
        for cyc in cycles:
            entry = cyc["entry_date"]
            expiry = cyc["expiry_date"]
            idx = pd.Timestamp(entry).normalize()
            if idx not in scores.index:
                continue
            if oos_only and idx.year < OOS_START_YEAR:
                continue
            sc = float(scores.loc[idx])
            ivr = float(df_norm.loc[idx, "iv_vol_ratio"]) if "iv_vol_ratio" in df_norm.columns else 1.0
            if np.isnan(ivr):
                ivr = 1.0
            thr_t = threshold + gamma * (ivr - 1.0)
            if sc <= thr_t:
                continue
            leg = get_strike_by_level(opt, etf, entry, expiry, "P", put_level)
            if leg is None:
                skipped += 1
                continue
            res = calc_leg_pnl(leg, opt, etf, expiry, "buy", is_buyer_at_expiry=True)
            if res is None:
                skipped += 1
                continue
            trigger_pnls.append(res["net_rmb"] * NUM_CONTRACTS)
            trigger_dates.append(idx)
    else:
        # Daily cadence: trigger on any trading day, buy put to next expiry.
        iv_vol_ratio = (df_norm["iv_vol_ratio"].values if "iv_vol_ratio" in df_norm.columns
                        else np.ones(len(df_norm)))
        thr_t = _threshold_aware_vec(scores.values, iv_vol_ratio, threshold, gamma)
        triggered_mask = scores.values > thr_t
        for i, trig in enumerate(triggered_mask):
            if not trig:
                continue
            tdate = dates[i]
            if oos_only and tdate.year < OOS_START_YEAR:
                continue
            expiry = _next_expiry(tdate, expiries)
            if expiry is None:
                skipped += 1
                continue
            pnl = put_pnl_for_trigger(opt, etf, tdate, expiry, put_level)
            if pnl is None:
                skipped += 1
                continue
            trigger_pnls.append(pnl)
            trigger_dates.append(tdate)

    alpha_summary = _summarize_pnl(trigger_pnls)
    # Baselines use the SAME put level and same OOS window, at cycle-start granularity.
    base_all = _summarize_pnl(all_hedge_cycle_pnls(opt, etf, put_level, cycles, oos_only=oos_only))
    base_static = _summarize_pnl(static_filter_cycle_pnls(opt, etf, etf_choice, put_level, cycles, oos_only=oos_only))
    coverage = 1.0 - (skipped / max(len(trigger_pnls) + skipped, 1))

    return {
        "regime": regime_key,
        "name": REGIME_NAMES[regime_key],
        "is_crash": REGIME_IS_CRASH[regime_key],
        "put_level": put_level,
        "cadence": cadence,
        "alpha": alpha_summary,
        "baseline_no_hedge": {"n": 0, "net_pnl": 0.0},
        "baseline_all_hedge": base_all,
        "baseline_static_filter": base_static,
        "trigger_dates": trigger_dates,
        "coverage": coverage,
        "oos_stat_metric": model_cfg.get("metrics", {}),
    }


def _deployable(rep):
    """Apply deployability decision rule."""
    a = rep["alpha"]
    stat = rep["oos_stat_metric"]
    is_crash = rep["is_crash"]
    rules = []
    # 1. Net P&L per trigger > 0
    r1 = a["mean_per_trigger"] > 0
    rules.append(("pnl_per_trigger>0", r1))
    # 2. OOS stat gate (lift>1 for crash; mean_ret<baseline for fall) — read from JSON metrics
    if is_crash:
        r2 = stat.get("passed_gate", False) and stat.get("mean_oos_raw", 0) > 1.0
    else:
        r2 = stat.get("passed_gate", False) and stat.get("mean_oos_raw", 0) < 0
    rules.append(("oos_stat_gate", r2))
    # 3. Sharpe > 0
    r3 = a["sharpe"] > 0
    rules.append(("sharpe>0", r3))
    # 4. Beats static filter on net P&L (or matches when static has 0 triggers)
    static_net = rep["baseline_static_filter"]["net_pnl"]
    r4 = a["net_pnl"] >= static_net
    rules.append(("beats_static_pnl", r4))
    passed = all(r for _, r in rules)
    return passed, rules


def print_report(etf_choice, reports, phase, cadence="cycle"):
    print("\n" + "=" * 92)
    print(f"  PUT P&L VALIDATION — {etf_choice}ETF — Phase {phase} — cadence={cadence} (OOS years >= {OOS_START_YEAR})")
    print("=" * 92)
    for rep in reports:
        a = rep["alpha"]
        b_all = rep["baseline_all_hedge"]
        b_stat = rep["baseline_static_filter"]
        deployed, rules = _deployable(rep)
        tag = "DEPLOYABLE" if deployed else "NO EDGE"
        print(f"\n  {rep['name']:<10} (reg put level {rep['put_level']})  [{tag}]  coverage={rep['coverage']:.0%}")
        print(f"    {'Variant':<22}{'N':>5}{'NetPnL':>12}{'WinRate':>9}{'PerTrig':>10}{'Sharpe':>8}{'MaxDD':>10}")
        print(f"    {'-'*76}")
        print(f"    {'ALPHA (model)':<22}{a['n']:>5}{a['net_pnl']:>12.1f}{a['win_rate']:>9.1%}"
              f"{a['mean_per_trigger']:>10.1f}{a['sharpe']:>8.2f}{a['max_dd']:>10.1f}")
        print(f"    {'Baseline B (all hedge)':<22}{b_all['n']:>5}{b_all['net_pnl']:>12.1f}{b_all['win_rate']:>9.1%}"
              f"{b_all['mean_per_trigger']:>10.1f}{b_all['sharpe']:>8.2f}{b_all['max_dd']:>10.1f}")
        print(f"    {'Baseline C (static flt)':<22}{b_stat['n']:>5}{b_stat['net_pnl']:>12.1f}{b_stat['win_rate']:>9.1%}"
              f"{b_stat['mean_per_trigger']:>10.1f}{b_stat['sharpe']:>8.2f}{b_stat['max_dd']:>10.1f}")
        rule_str = ", ".join(f"{'Y' if r else 'N'}:{n}" for n, r in rules)
        print(f"    Decision rules: {rule_str}")


def main():
    parser = argparse.ArgumentParser(description="Put P&L validator for alpha model")
    parser.add_argument("-e", "--etf", type=str, choices=["50", "300", "500", "all"], default="300")
    parser.add_argument("--phase", type=int, choices=[1, 2, 3], default=1)
    parser.add_argument("--no-oos-only", action="store_true",
                        help="Use full history (not just OOS years) for P&L")
    parser.add_argument("--cadence", type=str, choices=["cycle", "daily"], default="cycle",
                        help="Trigger cadence: 'cycle' (monthly cycle start, fair vs baselines) "
                             "or 'daily' (any trading day, requires TODO 4 daily scanning)")
    args = parser.parse_args()

    etfs = ["50", "300", "500"] if args.etf == "all" else [args.etf]
    phase_label, provider_fn = SCORE_PROVIDERS[args.phase]
    oos_only = not args.no_oos_only

    all_out = {}
    for etf_choice in etfs:
        select_underlying(etf_choice)
        inst, opt, etf = load_data()

        # Monthly expiries (both C & P traded) sorted ascending
        expiries = sorted(
            opt.groupby(["maturity_date", "option_type"])["order_book_id"]
            .nunique().unstack("option_type").dropna().index.tolist()
        )
        cycles = get_cycles(opt, etf)

        model = AlphaModel()
        df_norm = model.compute_normalized_indicators(etf)

        with open(MODEL_FILE) as f:
            all_models = json.load(f)
        etf_models = all_models.get(etf_choice, {})

        # For phases 2/3, precompute all-regime predictions ONCE (training is expensive).
        cache = None
        if args.phase == 2:
            from alpha_model_ml import predict_proba_all
            cache = predict_proba_all(df_norm, etf_choice, walk_forward=True)
        elif args.phase == 3:
            from alpha_model_hybrid import predict_all as hyb_predict
            cache = hyb_predict(df_norm, etf_choice)

        def provider(dn, mc, rk):
            if args.phase == 1:
                return provider_fn(dn, mc, rk)
            preds, thresholds = cache
            if rk not in preds:
                raise KeyError(f"phase {args.phase} has no model for {rk}")
            return preds[rk], thresholds.get(rk, 0.5), 0.0

        reports = []
        for r_key in ["reg1", "reg2", "reg3", "reg4"]:
            if r_key not in etf_models:
                print(f"  SKIP {r_key}: no model in {MODEL_FILE}")
                continue
            cfg = etf_models[r_key]
            rep = evaluate_regime_pnl(df_norm, opt, etf, etf_choice, r_key, cfg,
                                      provider, expiries, cycles, oos_only=oos_only,
                                      cadence=args.cadence)
            reports.append(rep)

        print_report(etf_choice, reports, args.phase, cadence=args.cadence)
        all_out[etf_choice] = {
            rep["regime"]: {
                "deployable_rules": dict(_deployable(rep)[1]),
                "deployable": _deployable(rep)[0],
                "alpha": rep["alpha"],
                "baseline_all_hedge": rep["baseline_all_hedge"],
                "baseline_static_filter": rep["baseline_static_filter"],
                "coverage": rep["coverage"],
            } for rep in reports
        }

    out_file = f"backtest/validate_pnl_phase{args.phase}.json"
    os.makedirs("backtest", exist_ok=True)
    with open(out_file, "w") as f:
        json.dump(all_out, f, indent=2)
    print(f"\n  Saved P&L validation → {out_file}")


if __name__ == "__main__":
    main()
