"""
500ETF Diagnostic: Per-cycle breakdown with multiple strategy variants.
Compares baseline vs alternative OTM levels, filters, put levels, and IVR-driven OTM.
"""
import pandas as pd
import numpy as np
import pandas_ta as ta
import argparse
import math
from datetime import datetime, timedelta
from research_otm_levels import select_etf, load_data, get_cycles, get_otm_strikes
from backtest_covered_call import (
    get_strike_by_level, get_atm_iv, get_30d_iv,
    SPREAD_HALF, COMMISSION, EXERCISE_COST, RISK_FREE, IV_THRESHOLD
)
from numba import njit

SPREAD_HALF = 0.02
COMMISSION = 2.0
EXERCISE_COST = 0.6


def calc_leg_pnl_standalone(leg, etf, expiry_date, side):
    if leg is None:
        return None
    K = float(leg["strike_price"])
    mult = float(leg["contract_multiplier"])
    entry_mid = float(leg["close"])
    otype = leg["option_type"]

    if side == "sell":
        exec_px = entry_mid * (1 - SPREAD_HALF)
        premium_rmb = exec_px * mult
    else:
        exec_px = entry_mid * (1 + SPREAD_HALF)
        premium_rmb = -exec_px * mult

    etf_expiry_dates = etf.index[etf.index <= expiry_date]
    if etf_expiry_dates.empty:
        etf_settle = None
    else:
        etf_settle = float(etf.loc[etf_expiry_dates[-1], "close"])

    exercise_pnl_rmb = 0.0
    note = "worthless"

    if etf_settle is not None:
        if otype == "C":
            intrinsic = max(0.0, etf_settle - K)
            itm = etf_settle > K
        else:
            intrinsic = max(0.0, K - etf_settle)
            itm = etf_settle < K

        if itm:
            if side == "sell":
                exercise_pnl_rmb = -intrinsic * mult
                note = f"assigned@{etf_settle:.3f}"
            else:
                exercise_pnl_rmb = intrinsic * mult - EXERCISE_COST
                note = f"exercised@{etf_settle:.3f}"

    net_rmb = premium_rmb + exercise_pnl_rmb - COMMISSION
    return {
        "K": K, "entry_mid": entry_mid, "premium_rmb": premium_rmb,
        "exercise_pnl_rmb": exercise_pnl_rmb, "net_rmb": net_rmb, "note": note,
        "otype": otype, "side": side, "mult": mult
    }


def run_variant(cycles, opt, etf, daily_ivs, config):
    results = []
    for cyc in cycles:
        entry = cyc["entry_date"]
        expiry = cyc["expiry_date"]

        idx = entry.normalize()
        if idx not in etf.index:
            continue

        etf_close = float(etf.loc[idx, "close"])
        rsi = etf.loc[idx, "rsi14"] if "rsi14" in etf.columns else np.nan
        bbu = etf.loc[idx, "bbu20"] if "bbu20" in etf.columns else np.nan
        roc20 = etf.loc[idx, "roc20"] if "roc20" in etf.columns else np.nan

        iv = daily_ivs.get(entry, IV_THRESHOLD)
        history = daily_ivs[daily_ivs.index <= entry]
        if len(history) >= 20:
            lookback = history.tail(252)
            min_iv = lookback.min()
            max_iv = lookback.max()
            ivr = (iv - min_iv) / (max_iv - min_iv) if max_iv > min_iv else 0.5
        else:
            ivr = 0.5

        filter_passed = config["filter_func"](etf, idx, etf_close, rsi, bbu, roc20)

        if config.get("ivr_driven", False):
            if ivr > 0.50:
                call_offsets = config["call_offsets_high_ivr"]
            elif ivr < 0.20:
                call_offsets = config["call_offsets_low_ivr"]
            else:
                if filter_passed:
                    call_offsets = config["call_offsets_pass"]
                else:
                    call_offsets = config["call_offsets_fail"]
        else:
            if filter_passed:
                call_offsets = config["call_offsets_pass"]
            else:
                call_offsets = config["call_offsets_fail"]

        call_legs = get_otm_strikes(opt, etf, entry, expiry, "C", call_offsets)
        put_leg = get_strike_by_level(opt, etf, entry, expiry, "P", config["put_level"])

        legs_pnl = []
        for i, cl in enumerate(call_legs):
            pnl = calc_leg_pnl_standalone(cl, etf, expiry, "sell")
            if pnl is not None:
                pnl["label"] = f"Call OTM{call_offsets[i]}"
                legs_pnl.append(pnl)

        if put_leg is not None:
            pnl = calc_leg_pnl_standalone(put_leg, etf, expiry, "buy")
            if pnl is not None:
                pnl["label"] = f"Put L{config['put_level']}"
                legs_pnl.append(pnl)

        total_net = sum(p["net_rmb"] for p in legs_pnl)
        total_premium = sum(p["premium_rmb"] for p in legs_pnl)
        call_net = sum(p["net_rmb"] for p in legs_pnl if p["otype"] == "C")
        put_net = sum(p["net_rmb"] for p in legs_pnl if p["otype"] == "P")

        etf_expiry_dates = etf.index[etf.index <= expiry]
        etf_settle = float(etf.loc[etf_expiry_dates[-1], "close"]) if not etf_expiry_dates.empty else np.nan
        etf_return = (etf_settle / etf_close - 1) * 100 if not np.isnan(etf_settle) else np.nan

        call_Ks = [p["K"] for p in legs_pnl if p["otype"] == "C"]
        max_call_K = max(call_Ks) if call_Ks else 0
        buffer_pct = ((max_call_K / etf_close) - 1) * 100 if max_call_K > 0 and etf_close > 0 else 0

        assigned = any("assigned" in p["note"] for p in legs_pnl)

        results.append({
            "entry": entry.date(),
            "expiry": expiry.date(),
            "etf_entry": etf_close,
            "etf_settle": etf_settle,
            "etf_return%": etf_return,
            "rsi": rsi,
            "bbu": bbu,
            "roc20": roc20,
            "iv": iv,
            "ivr": ivr,
            "filter": "PASS" if filter_passed else "FAIL",
            "call_offsets": call_offsets,
            "put_level": config["put_level"],
            "legs": legs_pnl,
            "call_net": call_net,
            "put_net": put_net,
            "total_net": total_net,
            "total_premium": total_premium,
            "buffer_pct": buffer_pct,
            "assigned": assigned,
        })

    return results


def print_diagnostic(results, name):
    print(f"\n{'='*150}")
    print(f"  VARIANT: {name}")
    print(f"{'='*150}")

    header = (f"{'Entry':>12} {'Expiry':>12} {'ETF_in':>7} {'ETF_out':>7} {'Ret%':>6} "
              f"{'RSI':>5} {'IVR':>5} {'Filt':>4} {'Calls':>8} {'PutL':>4} {'Buf%':>5} "
              f"{'CallNet':>9} {'PutNet':>9} {'TotalNet':>10} {'Notes'}")
    print(header)
    print("-" * 150)

    for r in results:
        call_offsets_str = "+".join(str(o) for o in r["call_offsets"])

        notes = []
        for p in r["legs"]:
            if "assigned" in p["note"] or "exercised" in p["note"]:
                notes.append(f"{p['label']}:{p['note']}")
        if r["assigned"]:
            notes.insert(0, "**ASSIGNED**")

        print(f"{str(r['entry']):>12} {str(r['expiry']):>12} {r['etf_entry']:>7.3f} {r['etf_settle']:>7.3f} "
              f"{r['etf_return%']:>6.1f} {r['rsi']:>5.1f} {r['ivr']:>5.2f} {r['filter']:>4} "
              f"{call_offsets_str:>8} {r['put_level']:>4} {r['buffer_pct']:>5.1f} "
              f"{r['call_net']:>9.1f} {r['put_net']:>9.1f} {r['total_net']:>10.1f} "
              f"{'; '.join(notes) if notes else ''}")

    nets = [r["total_net"] for r in results]
    wins = sum(1 for n in nets if n > 0)
    call_nets = [r["call_net"] for r in results]
    put_nets = [r["put_net"] for r in results]
    cumulative = list(np.cumsum(nets))
    max_dd = 0
    peak = 0
    for c in cumulative:
        if c > peak:
            peak = c
        dd = (c - peak) / peak if peak > 0 else 0
        if dd < max_dd:
            max_dd = dd

    assigned_cycles = sum(1 for r in results if r["assigned"])
    avg_buffer = np.mean([r["buffer_pct"] for r in results])

    print("-" * 150)
    print(f"  TOTALS: {len(results)} cycles, {wins}/{len(results)} wins ({wins/len(results):.0%}), "
          f"Assigned: {assigned_cycles}/{len(results)}, AvgBuf: {avg_buffer:.1f}%\n"
          f"  Total P&L: {sum(nets):>10.1f}, Avg: {np.mean(nets):>8.1f}, "
          f"AvgCall: {np.mean(call_nets):>8.1f}, AvgPut: {np.mean(put_nets):>8.1f}, "
          f"MaxDD: {max_dd:.1%}")


def print_leg_detail(results, name):
    print(f"\n{'='*160}")
    print(f"  LEG DETAIL: {name}")
    print(f"{'='*160}")

    header = (f"{'Entry':>12} {'Expiry':>12} {'ETF_in':>7} {'ETF_out':>7} "
              f"{'IVR':>5} {'Filt':>4} {'Leg':>14} {'Side':>4} {'K':>7} {'Mid':>6} "
              f"{'Prem':>8} {'ExerPnL':>9} {'Net':>9} {'Note'}")
    print(header)
    print("-" * 160)

    for r in results:
        for j, p in enumerate(r["legs"]):
            prefix = f"{str(r['entry']):>12} {str(r['expiry']):>12} {r['etf_entry']:>7.3f} {r['etf_settle']:>7.3f} " if j == 0 else f"{'':>12} {'':>12} {'':>7} {'':>7} "
            filter_str = r["filter"] if j == 0 else ""
            ivr_str = f"{r['ivr']:.2f}" if j == 0 else ""
            print(f"{prefix} {ivr_str:>5} {filter_str:>4} {p['label']:>14} {p['side']:>4} {p['K']:>7.3f} {p['entry_mid']:>6.4f} "
                  f"{p['premium_rmb']:>8.1f} {p['exercise_pnl_rmb']:>9.1f} {p['net_rmb']:>9.1f} {p['note']}")
        if len(r["legs"]) > 0:
            print(f"{'':>146} {'TOTAL':>9} {r['total_net']:>9.1f}")


def print_comparison(variants_results):
    print(f"\n{'='*120}")
    print(f"  HEAD-TO-HEAD COMPARISON")
    print(f"{'='*120}")

    header = f"{'Entry':>12} {'Expiry':>12} {'ETF%':>6} {'RSI':>5} {'IVR':>5}"
    for name, _ in variants_results:
        header += f" {name[:18]:>18}"
    print(header)
    print("-" * 120)

    first = variants_results[0][1]
    for i in range(len(first)):
        r0 = first[i]
        row = f"{str(r0['entry']):>12} {str(r0['expiry']):>12} {r0['etf_return%']:>6.1f} {r0['rsi']:>5.1f} {r0['ivr']:>5.2f}"
        for name, results in variants_results:
            r = results[i]
            marker = "*" if r["assigned"] else " "
            row += f" {marker}{r['total_net']:>8.0f}({r['filter']:>4})"
        print(row)

    row = f"{'TOTAL':>12} {'':>12} {'':>6} {'':>5} {'':>5}"
    for name, results in variants_results:
        nets = [r["total_net"] for r in results]
        wins = sum(1 for n in nets if n > 0)
        assigned = sum(1 for r in results if r["assigned"])
        row += f" {sum(nets):>7.0f}({wins:2d}w {assigned:2d}a)"
    print("-" * 120)
    print(row)


def print_loss_analysis(all_results):
    print(f"\n{'='*150}")
    print(f"  LOSS CYCLE DEEP DIVE (cycles where any variant loses >1000 RMB)")
    print(f"{'='*150}")

    first = all_results[0][1]
    for i, r0 in enumerate(first):
        baseline_net = r0["total_net"]
        if baseline_net > -1000:
            continue

        print(f"\n  --- Cycle {r0['entry']} → {r0['expiry']} ---")
        print(f"  ETF: {r0['etf_entry']:.3f} → {r0['etf_settle']:.3f} ({r0['etf_return%']:+.1f}%)  "
              f"RSI={r0['rsi']:.1f}  IVR={r0['ivr']:.2f}  Filter={r0['filter']}")

        for vname, vresults in all_results:
            r = vresults[i]
            call_str = "+".join(str(o) for o in r["call_offsets"])
            assigned_calls = [p for p in r["legs"] if p["otype"] == "C" and "assigned" in p["note"]]
            if assigned_calls:
                for ac in assigned_calls:
                    print(f"    {vname[:40]:<42} calls={call_str:>6} P&L={r['total_net']:>+9.0f}  "
                          f"assigned K={ac['K']:.3f} intrinsic={-ac['exercise_pnl_rmb']:.0f}")
            else:
                print(f"    {vname[:40]:<42} calls={call_str:>6} P&L={r['total_net']:>+9.0f}  (no assignment)")


def filter_rsi66_bbu(etf, idx, close, rsi, bbu, roc20):
    if pd.isna(rsi) or pd.isna(bbu):
        return False
    return (rsi < 66.0) and (close < bbu)


def filter_rsi66_bbu_roc(etf, idx, close, rsi, bbu, roc20):
    if pd.isna(rsi) or pd.isna(bbu) or pd.isna(roc20):
        return False
    return (rsi < 66.0) and (close < bbu) and (roc20 < 5.0)


def filter_rsi60_bbu(etf, idx, close, rsi, bbu, roc20):
    if pd.isna(rsi) or pd.isna(bbu):
        return False
    return (rsi < 60.0) and (close < bbu)


def filter_bbu_roc(etf, idx, close, rsi, bbu, roc20):
    if pd.isna(bbu) or pd.isna(roc20):
        return False
    return (close < bbu) and (roc20 < 5.0)


def filter_rsi70_bbu(etf, idx, close, rsi, bbu, roc20):
    if pd.isna(rsi) or pd.isna(bbu):
        return False
    return (rsi < 70.0) and (close < bbu)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="500ETF Diagnostic Tool")
    parser.add_argument("-e", "--etf", type=str, choices=["50", "300", "500"], default="500")
    args = parser.parse_args()

    select_etf(args.etf)
    inst, opt, etf = load_data()
    etf["roc20"] = ta.roc(etf["close"], length=20)

    cycles = get_cycles(opt, etf, years=None)
    print(f"Found {len(cycles)} cycles for {args.etf}ETF")

    import os
    from backtest_covered_call import PATH_IV_CACHE, select_underlying
    select_underlying(args.etf)

    if os.path.exists(PATH_IV_CACHE):
        daily_ivs = pd.read_parquet(PATH_IV_CACHE).iloc[:, 0]
        daily_ivs.index = pd.to_datetime(daily_ivs.index)
    else:
        print("Pre-calculating daily 30-day IVs...")
        trading_days = sorted(etf.index.unique())
        iv_data = {}
        for i, d in enumerate(trading_days):
            if i % 100 == 0:
                print(f"  Progress: {i}/{len(trading_days)}")
            iv_data[d] = get_30d_iv(opt, etf, d)
        daily_ivs = pd.Series(iv_data).sort_index()

    variants = [
        {
            "name": "Baseline",
            "filter_func": filter_rsi66_bbu,
            "call_offsets_pass": [2, 3],
            "call_offsets_fail": [4],
            "put_level": 1,
        },
        {
            "name": "RSI70+BBU",
            "filter_func": filter_rsi70_bbu,
            "call_offsets_pass": [2, 3],
            "call_offsets_fail": [4],
            "put_level": 1,
        },
        {
            "name": "IVR-Driven",
            "filter_func": filter_rsi66_bbu,
            "ivr_driven": True,
            "call_offsets_pass": [2, 3],
            "call_offsets_fail": [4],
            "call_offsets_high_ivr": [4, 5],
            "call_offsets_low_ivr": [1, 2],
            "put_level": 1,
        },
        {
            "name": "IVR-Driven+RSI70",
            "filter_func": filter_rsi70_bbu,
            "ivr_driven": True,
            "call_offsets_pass": [2, 3],
            "call_offsets_fail": [4],
            "call_offsets_high_ivr": [4, 5],
            "call_offsets_low_ivr": [1, 2],
            "put_level": 1,
        },
        {
            "name": "Wider OTM3+4/5",
            "filter_func": filter_rsi66_bbu,
            "call_offsets_pass": [3, 4],
            "call_offsets_fail": [5],
            "put_level": 1,
        },
        {
            "name": "Put L2",
            "filter_func": filter_rsi66_bbu,
            "call_offsets_pass": [2, 3],
            "call_offsets_fail": [4],
            "put_level": 2,
        },
        {
            "name": "BBU+ROC<5%",
            "filter_func": filter_bbu_roc,
            "call_offsets_pass": [2, 3],
            "call_offsets_fail": [4],
            "put_level": 1,
        },
        {
            "name": "All3 RSI66+BBU+ROC",
            "filter_func": filter_rsi66_bbu_roc,
            "call_offsets_pass": [2, 3],
            "call_offsets_fail": [4],
            "put_level": 1,
        },
        {
            "name": "IVR+Wider+RSI70",
            "filter_func": filter_rsi70_bbu,
            "ivr_driven": True,
            "call_offsets_pass": [3, 4],
            "call_offsets_fail": [5],
            "call_offsets_high_ivr": [4, 5],
            "call_offsets_low_ivr": [2, 3],
            "put_level": 1,
        },
        {
            "name": "IVR+Wider+Put2",
            "filter_func": filter_rsi66_bbu,
            "ivr_driven": True,
            "call_offsets_pass": [3, 4],
            "call_offsets_fail": [5],
            "call_offsets_high_ivr": [4, 5],
            "call_offsets_low_ivr": [2, 3],
            "put_level": 2,
        },
    ]

    all_results = []
    for v in variants:
        r = run_variant(cycles, opt, etf, daily_ivs, v)
        all_results.append((v["name"], r))
        print_diagnostic(r, v["name"])

    print_comparison(all_results)

    print_loss_analysis(all_results)

    print("\n\n--- LEG DETAIL: BASELINE ---")
    print_leg_detail(all_results[0][1], all_results[0][0])

    best_name = max(all_results, key=lambda x: sum(r["total_net"] for r in x[1]))[0]
    if best_name != all_results[0][0]:
        for name, r in all_results:
            if name == best_name:
                print(f"\n\n--- LEG DETAIL: BEST ({best_name}) ---")
                print_leg_detail(r, name)
                break

    print("\n\n--- FILTER CLASSIFICATION DIFF ---")
    short_names = [v["name"][:12] for v in variants]
    header = f"{'Entry':>12} {'Expiry':>12} {'RSI':>5} {'ROC':>6} {'IVR':>5}"
    for sn in short_names:
        header += f" {sn:>12}"
    print(header)
    print("-" * (30 + 13 * len(variants)))
    for i in range(len(cycles)):
        r0 = all_results[0][1][i]
        row = f"{str(r0['entry']):>12} {str(r0['expiry']):>12} {r0['rsi']:>5.1f} {r0['roc20']:>6.1f} {r0['ivr']:>5.2f}"
        for name, results in all_results:
            if i < len(results):
                row += f" {results[i]['filter']:>12}"
        print(row)
