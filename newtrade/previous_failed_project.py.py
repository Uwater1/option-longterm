#encoding:gbk
"""
zhongjin_multi.py - Multi-Underlying LONG & SHORT-BOX arbitrage scanner + order placer.
Exchange: SHSE & SZSE  (ETF Options)
Platform: QMT (xtquant Python API)
Account are handled by xuntou QMT, do not modify

Strategy logic:
  1. init(): query all active ETF options via get_option_list/get_option_detail_data.
  2. handlebar(): update local bid/ask snapshot from get_full_tick, run evaluation.
  3. If return > MIN_RETURN and XGBoost prob >= XGB_THRESHOLD, compute dynamic
     contract_size, then place 4 limit orders via passorder().
  4. Track open positions; exit early if risk-free rate-adjusted close > payout.
  5. Shared capital pool across all underlyings with per-position sizing.

Multi-Underlying:
  Scans 510300, 510500, 588000 simultaneously in one process.
  Uses XGBoost-score-driven dynamic sizing (mirrors Rust backtest logic).

Long-Box construction (K1 < K2, same expiry, same underlying)
  Leg 1  Buy  Call K1  @ ask  (open)
  Leg 2  Sell Call K2  @ bid  (open)
  Leg 3  Buy  Put  K2  @ ask  (open)
  Leg 4  Sell Put  K1  @ bid  (open)

Short-Box construction (K1 < K2, same expiry, same underlying)
  Leg 1  Buy  Call K2  @ ask  (open)  -- buy first so broker sees covered spread
  Leg 2  Sell Call K1  @ bid  (open)
  Leg 3  Buy  Put  K1  @ ask  (open)  -- buy first so broker sees covered spread
  Leg 4  Sell Put  K2  @ bid  (open)
"""
import threading
import time
import numpy as np
import datetime
import math
from datetime import timezone, timedelta

CONTRACT_MULTIPLIER    = 10000
COMMISSION_PER_LEG_CNY = 1.0
COMMISSION_PER_LEG     = COMMISSION_PER_LEG_CNY / CONTRACT_MULTIPLIER
BOX_COMMISSION         = 4 * COMMISSION_PER_LEG

EVAL_INTERVAL_S    = 1  # Not used in LIVE MODE, live mode eval every price update
MAX_STALE_SECONDS  = 4  # Max acceptable quote age in seconds
MAX_STALE_SECONDS_EXIT = 3600  # Exit guard: last known price valid for up to 1 hour
MAX_EVAL_ORDER_GAP_S  = 4.0  # Skip box if time since evaluation start exceeds this
LATENCY_WARN_MEDIAN_S = 1.0  # Log warning if rolling median passorder() exceeds this
MIN_HOLDING_TIME   = 9  # Minimum holding time in seconds
MIN_VOL            = 2.0
MAX_EXP_DATE           = 100    
MAX_MONEYNESS          = 1.10  # Maximum moneyness (S/K) for both legs -- rejects deep ITM strikes
FAILED_BOX_COOLDOWN_S  = 1800   # Cooldown seconds after placement/fill failure before retrying box

INITIAL_CASH       = 100000.0
MIN_CASH_THRESHOLD = 50000.0

TARGET_UNDERLYINGS  = [
    '510300.SH', '510500.SH', '588000.SH'
]


MIN_RETURN         = 0.007  # Baseline pre-filter, XGBOOST MODEL PRE_ASSUMPTION
XGB_THRESHOLD      = 0.60  # Conservative cross-underlying threshold (510300=0.58, 510500=0.56, 588000=0.69)
MIN_EXIT_RETURN    = 0.001  # Must match close_order.py
EARLY_EXIT_ADJUSTMENT = 0.02   # From src/lib.rs
ORDER_VOLUME       = 1  # Base order volume (unused, kept for config reference)

# Dynamic sizing constants (mirror Rust src/lib.rs)
MAX_ORDER              = 1     # max contracts per leg; each box set = 4 legs
# SCORE_BOOST_FACTOR removed -- quality scaling removed from sizing
MAX_POSITIONS_PER_UNDERLYING = 2  # max open positions per underlying
MAX_OPEN_SETS          = 4     # max total open box sets (each = 4 legs) across all underlyings

# Account defaults (options account); overridden by QMT framework if set before init()
DEFAULT_ACCT      = '210889000248'
DEFAULT_ACCT_TYPE = 'STOCK_OPTION'


def compute_dynamic_size(min_leg_vol, avail_cash, cost_per_contract):
    """Direct sizing: vol and capital are 1:1 hard caps, no safety multipliers.
    size = min(floor(min_leg_vol), floor(avail_cash/cost), MAX_ORDER)
    """
    vol_cap = int(min_leg_vol)
    capital_cap = int(avail_cash / cost_per_contract) if cost_per_contract > 0 else 1
    return max(min(vol_cap, capital_cap, MAX_ORDER), 1)


import copy
import types

A = types.SimpleNamespace()  # Global strategy state bag (shared across all underlyings)


def evaluate_boxes(ca1, cb1, pa1, pb1, ks, dte, box_commission, underlying_price=0.0):
    N = len(ks)
    if N < 2:
        return -1, -1, 0.0, 0.0, 0.0, -999.0, -1, -1, 0.0, 0.0, 0.0, -999.0

    ann_factor = 365.0 / max(dte, 1.0)

    # Get indices for all pairs where j > i
    i_idx, j_idx = np.triu_indices(N, k=1)

    # Extract values for all pairs
    ks_i, ks_j = ks[i_idx], ks[j_idx]
    ca1_i, cb1_j = ca1[i_idx], cb1[j_idx]
    pa1_j, pb1_i = pa1[j_idx], pb1[i_idx]

    cb1_i, ca1_j = cb1[i_idx], cb1[j_idx]
    pb1_j, pa1_i = pb1[j_idx], pa1[i_idx]

    payout = (ks_j - ks_i).astype(np.float64)

    # --- Moneyness filter: reject deep ITM strike pairs (S/K > MAX_MONEYNESS) ---
    if underlying_price > 0:
        moneyness_ok = (underlying_price / ks_i <= MAX_MONEYNESS) & (underlying_price / ks_j <= MAX_MONEYNESS)
    else:
        moneyness_ok = np.ones(len(ks_i), dtype=bool)

    # --- Long Box ---
    long_cost = (ca1_i - cb1_j) + (pa1_j - pb1_i) + box_commission
    valid_long = (ca1_i > 0) & (cb1_j > 0) & (pa1_j > 0) & (pb1_i > 0) & moneyness_ok
    
    safe_long_cost = np.where(long_cost > 0, long_cost, 1.0)
    long_ret = np.where((long_cost > 0) & valid_long, (payout - long_cost) / safe_long_cost, -999.0)
    long_ann = long_ret * ann_factor
    long_ann = np.where(valid_long, long_ann, -999.0)

    # --- Short Box ---
    short_gain = (cb1_i - ca1_j) + (pb1_j - pa1_i) - box_commission
    short_profit = short_gain - payout
    margin = payout * 2.0
    valid_short = (cb1_i > 0) & (ca1_j > 0) & (pb1_j > 0) & (pa1_i > 0) & moneyness_ok
    
    safe_margin = np.where(margin > 0, margin, 1.0)
    short_ret = np.where((margin > 0) & valid_short, short_profit / safe_margin, -999.0)
    short_ann = short_ret * ann_factor
    short_ann = np.where(valid_short, short_ann, -999.0)

    # Find best
    best_long_idx = np.argmax(long_ann) if np.any(valid_long) else -1
    best_short_idx = np.argmax(short_ann) if np.any(valid_short) else -1

    # Extract results
    if best_long_idx >= 0 and long_ann[best_long_idx] > -999.0:
        l_i = int(i_idx[best_long_idx])
        l_j = int(j_idx[best_long_idx])
        l_cost = float(long_cost[best_long_idx])
        l_payout = float(payout[best_long_idx])
        l_ret = float(long_ret[best_long_idx])
        l_ann = float(long_ann[best_long_idx])
    else:
        l_i, l_j, l_cost, l_payout, l_ret, l_ann = -1, -1, 0.0, 0.0, 0.0, -999.0

    if best_short_idx >= 0 and short_ann[best_short_idx] > -999.0:
        s_i = int(i_idx[best_short_idx])
        s_j = int(j_idx[best_short_idx])
        s_cost = float(short_gain[best_short_idx])
        s_payout = float(payout[best_short_idx])
        s_ret = float(short_ret[best_short_idx])
        s_ann = float(short_ann[best_short_idx])
    else:
        s_i, s_j, s_cost, s_payout, s_ret, s_ann = -1, -1, 0.0, 0.0, 0.0, -999.0

    return (l_i, l_j, l_cost, l_payout, l_ret, l_ann,
            s_i, s_j, s_cost, s_payout, s_ret, s_ann)


def get_adj_suffix(opt_code, detail):
    # 1. Check if the code itself has a letter (useful for SZSE options or long codes)
    base = opt_code.split('.')[0]
    if base and base[-1].isalpha():
        return base[-1].upper()
        
    # 2. Check the contract name in detail (ends with 'A', 'B', etc. for adjusted options)
    name = detail.get('InstrumentName', detail.get('Name', '')).strip()
    if name and name[-1].isalpha():
        return name[-1].upper()
        
    # 3. Check contract unit / multiplier (standard options are 10000)
    opt_unit = detail.get('OptUnit', detail.get('VolumeMultiple', 10000))
    if opt_unit and int(opt_unit) != 10000:
        return "A"
        
    return ""


def _build_options_map(C):
    today = datetime.datetime.now().date()
    today_str = today.strftime('%Y%m%d')
    options_map = {}
    tick_data   = {}
    ctx_list = []
    oid_to_ctx_idx = {}

    print(f"=== _build_options_map start today={today_str} ===")

    for underlying in TARGET_UNDERLYINGS:
        print(f"Processing underlying: {underlying}")

        opt_list = None
        for date_param in [today_str, underlying]:
            for opttype in ['', 'CALL', 'PUT']:
                try:
                    result = C.get_option_list(underlying, date_param, opttype, True)
                    if result and len(result) > 0:
                        opt_list = result
                        print(f"  get_option_list OK: date={date_param}, type={opttype}, count={len(result)}")
                        break
                except Exception as e:
                    pass
            if opt_list:
                break

        if not opt_list:
            try:
                result = C.get_option_list(underlying, '', '', True)
                if result and len(result) > 0:
                    opt_list = result
                    print(f"  get_option_list OK (empty date): count={len(result)}")
            except Exception as e:
                print(f"  get_option_list error (empty date): {e}")

        if not opt_list:
            print(f"  [{underlying}] NO options returned by get_option_list")
            continue

        print(f"  Got {len(opt_list)} option codes")

        for opt_code in opt_list:
            try:
                detail = C.get_option_detail_data(opt_code)
            except Exception as e:
                print(f"  [{opt_code}] get_option_detail_data error: {e}")
                continue

            if not detail:
                print(f"  [{opt_code}] empty detail")
                continue

            expire_date_str = detail.get('ExpireDate', '')
            opt_type = detail.get('optType', '')
            strike_val = detail.get('OptExercisePrice', 0)
            undl_code = detail.get('OptUndlCode', '')
            undl_mkt = detail.get('OptUndlMarket', '')

            if not expire_date_str:
                print(f"  [{opt_code}] no ExpireDate in detail, keys={list(detail.keys())[:10]}")
                continue

            try:
                expire_date = datetime.datetime.strptime(str(expire_date_str)[:8], '%Y%m%d').date()
            except Exception:
                print(f"  [{opt_code}] bad ExpireDate format: {expire_date_str}")
                continue

            dte = (expire_date - today).days
            # Filter out expired options (dte < 0) and those beyond next quarter (dte > 100)
            if dte < 0 or dte > MAX_EXP_DATE:
                continue

            if not strike_val or not opt_type:
                continue

            undl_key = undl_code + '.' + undl_mkt if undl_code and undl_mkt else underlying
            suffix = get_adj_suffix(opt_code, detail)
            undl_key_adj = f"{undl_key}_{suffix}" if suffix else undl_key

            if undl_key_adj not in options_map:
                options_map[undl_key_adj] = {}
            if expire_date not in options_map[undl_key_adj]:
                options_map[undl_key_adj][expire_date] = {}

            strike_f = float(strike_val)
            if strike_f not in options_map[undl_key_adj][expire_date]:
                options_map[undl_key_adj][expire_date][strike_f] = {}

            opt_type_upper = opt_type.upper()
            if opt_type_upper in ('C', 'CALL'):
                options_map[undl_key_adj][expire_date][strike_f]['C'] = opt_code
            elif opt_type_upper in ('P', 'PUT'):
                options_map[undl_key_adj][expire_date][strike_f]['P'] = opt_code

            if opt_code not in tick_data:
                tick_data[opt_code] = {'a1': 0.0, 'b1': 0.0, 'a1_v': 0.0, 'b1_v': 0.0, 'time': 0}

    print(f"=== options_map underlyings: {list(options_map.keys())} ===")
    for undl in sorted(options_map.keys()):
        for exp in sorted(options_map[undl].keys()):
            n_strikes = len(options_map[undl][exp])
            n_contracts = sum(len(v) for v in options_map[undl][exp].values())
            dte = (exp - today).days
            print(f"  [{undl}] DTE={dte} strikes={n_strikes} contracts={n_contracts}")

    if not options_map:
        print("No contracts found for any target underlying.")
        return []

    A.options_map  = options_map
    A.tick_data    = tick_data
    A.placed_boxes = set()
    A.data_lock    = threading.Lock()
    A.order_box_map = {}
    A.box_orders = {}
    A.positions = []
    A.open_pos_set = set()  # (ctx_idx, pos_type) for O(1) already_in lookup
    A.available_cash = INITIAL_CASH
    A.locked_margin = 0.0
    A.last_long_box = {}
    A.last_short_box = {}
    A.oid_to_ctx_idx = {}
    A.ctx_list = []
    A.positions_per_underlying = {}  # underlying -> count of open positions (for limit)

    ctx_idx = 0
    for underlying in sorted(options_map.keys()):
        # Sort expiries chronologically to get the near_level (1 to 4)
        sorted_expiries = sorted(options_map[underlying].keys())
        for near_level, expiry in enumerate(sorted_expiries, start=1):
            strikes_dict = options_map[underlying][expiry]
            sorted_strikes = sorted(strikes_dict.keys())
            call_oids = []
            put_oids = []
            strike_vals = []
            for k in sorted_strikes:
                types = strikes_dict[k]
                if 'C' in types and 'P' in types:
                    call_oids.append(types['C'])
                    put_oids.append(types['P'])
                    strike_vals.append(k)
            if len(strike_vals) >= 2:
                dte_val = max((expiry - today).days, 1)
                ctx = {
                    'underlying': underlying,
                    'expiry': expiry,
                    'dte': dte_val,
                    'strikes': strike_vals,
                    'call_oids': call_oids,
                    'put_oids': put_oids,
                    'near_level': near_level,
                }
                A.ctx_list.append(ctx)
                for c_oid in call_oids:
                    if c_oid not in A.oid_to_ctx_idx:
                        A.oid_to_ctx_idx[c_oid] = []
                    A.oid_to_ctx_idx[c_oid].append(ctx_idx)
                for p_oid in put_oids:
                    if p_oid not in A.oid_to_ctx_idx:
                        A.oid_to_ctx_idx[p_oid] = []
                    A.oid_to_ctx_idx[p_oid].append(ctx_idx)
                ctx_idx += 1

    all_syms = list(tick_data.keys())
    print(f"Loaded {len(all_syms)} contracts across {len(options_map)} underlying(s), {len(A.ctx_list)} contexts")
    return all_syms


def _update_tick_data(C, symbols):
    if not symbols:
        return
    try:
        tick = C.get_full_tick(symbols)
    except Exception as e:
        if hasattr(A, 'log_queue'):
            A.log_queue.append(f"[get_full_tick error] {e}")
        return

    if not tick:
        return

    now_ts = int(datetime.datetime.now().timestamp())

    with A.data_lock:
        for sym, data in tick.items():
            if sym in A.tick_data and data:
                ask_list = data.get('askPrice', [])
                bid_list = data.get('bidPrice', [])
                ask_vol_list = data.get('askVol', [])
                bid_vol_list = data.get('bidVol', [])
                a1 = float(ask_list[0]) if ask_list and ask_list[0] else 0.0
                b1 = float(bid_list[0]) if bid_list and bid_list[0] else 0.0
                a1_v = float(ask_vol_list[0]) if ask_vol_list and ask_vol_list[0] else 0.0
                b1_v = float(bid_vol_list[0]) if bid_vol_list and bid_vol_list[0] else 0.0
                
                if a1_v < MIN_VOL and len(ask_list) > 1 and len(ask_vol_list) > 1:
                    l2_a = ask_list[1]
                    if l2_a:
                        a1 = float(l2_a)
                    a1_v += float(ask_vol_list[1]) if ask_vol_list[1] else 0.0
                if b1_v < MIN_VOL and len(bid_list) > 1 and len(bid_vol_list) > 1:
                    l2_b = bid_list[1]
                    if l2_b:
                        b1 = float(l2_b)
                    b1_v += float(bid_vol_list[1]) if bid_vol_list[1] else 0.0
                
                A.tick_data[sym]['a1']   = a1
                A.tick_data[sym]['b1']   = b1
                A.tick_data[sym]['a1_v'] = a1_v
                A.tick_data[sym]['b1_v'] = b1_v
                A.tick_data[sym]['time'] = now_ts


def _decrement_underlying_count(underlying):
    """Decrement open position count for an underlying after position close."""
    count = A.positions_per_underlying.get(underlying, 0)
    A.positions_per_underlying[underlying] = max(count - 1, 0)


def _prune_closed_positions():
    """Remove closed/errored positions from the list to prevent unbounded growth.
    Must be called with A.data_lock held."""
    if not A.positions:
        return
    keep = [p for p in A.positions if p.get('state', 'Open') == 'Open']
    removed = len(A.positions) - len(keep)
    if removed > 0:
        A.positions = keep
        ts_str = datetime.datetime.now().strftime('%H:%M:%S')
        A.log_queue.append(f"[{ts_str}] Pruned {removed} closed/errored positions, {len(keep)} remaining")


# ---------------------------------------------------------------------------
# Broker position / order sync  (detect boxes held at broker from prior runs)
# ---------------------------------------------------------------------------

def _normalize_code(raw_code):
    """Normalize broker instrument ID to match get_option_list codes.

    Broker positions use .SHO suffix while get_option_list returns .SH.
    Strips the exchange suffix and returns the bare numeric code.
    """
    return raw_code.split('.')[0]


def _get_position_direction(pos_obj):
    """Determine if a QMT position is LONG (+1) or SHORT (-1).

    Tries several known field names across QMT versions.
    Falls back to signed m_nVolume convention.

    QMT option direction enum values:
      48 = long (bought to open), 49 = short (sold to open)
    """
    for attr in ('m_nPositionDirection', 'm_nDirection', 'm_nBsFlag'):
        if hasattr(pos_obj, attr):
            val = getattr(pos_obj, attr)
            if attr == 'm_nBsFlag':
                return -1 if val == 1 else 1
            # QMT option direction: 48=long, 49=short
            if val == 49:
                return -1
            if val == 48:
                return 1
            # Generic signed convention
            if val < 0:
                return -1
            if val > 0:
                return 1
    vol = getattr(pos_obj, 'm_nVolume', 0)
    if vol < 0:
        return -1
    return 1


def _get_can_use_volume(pos_obj):
    """Get the closeable volume for a position."""
    return getattr(pos_obj, 'm_nCanUseVolume', getattr(pos_obj, 'm_nVolume', 0))


def _query_broker_positions():
    """Fetch all option positions from the broker via QMT API."""
    try:
        positions = get_trade_detail_data(A.acct, str(A.acct_type), 'position')
        return positions if positions else []
    except Exception as e:
        A.log_queue.append(f"[SYNC] get_trade_detail_data(position) error: {e}")
        return []


def _query_broker_orders():
    """Fetch all open orders from the broker via QMT API."""
    try:
        orders = get_trade_detail_data(A.acct, str(A.acct_type), 'order')
        return orders if orders else []
    except Exception as e:
        A.log_queue.append(f"[SYNC] get_trade_detail_data(order) error: {e}")
        return []


def _sync_broker_positions(C):
    """Detect box spreads held at the broker and sync into A.positions.

    Called once during init() after _build_options_map and an initial tick
    update.  For every complete 4-leg box found among broker positions that
    is NOT already tracked locally, a synthetic position entry is created so
    that _check_exits can monitor and close it on subsequent ticks.

    Also reports any pending open orders for operator awareness.
    """
    broker_positions = _query_broker_positions()
    if not broker_positions:
        A.log_queue.append("[SYNC] No broker positions found at startup.")
        return

    # Build lookup: normalized_code -> list of {volume, direction, can_use}
    pos_by_code = {}
    for pos in broker_positions:
        raw_code = getattr(pos, 'm_strInstrumentID', '')
        code = _normalize_code(raw_code)
        vol = abs(getattr(pos, 'm_nVolume', 0))
        direction = _get_position_direction(pos)
        can_use = abs(_get_can_use_volume(pos))
        if vol > 0 and code:
            if code not in pos_by_code:
                pos_by_code[code] = []
            pos_by_code[code].append({
                'volume': vol,
                'direction': direction,
                'can_use': can_use,
            })

    A.log_queue.append(
        f"[SYNC] Broker has {len(broker_positions)} position(s) across "
        f"{len(pos_by_code)} distinct contract(s)"
    )

    synced_count = 0
    already_tracked = set()
    # Collect already-tracked (ctx_idx, pos_type) pairs
    for p in A.positions:
        if p.get('state', 'Open') == 'Open':
            already_tracked.add((p['ctx_idx'], p['pos_type']))

    for ctx_idx, ctx in enumerate(A.ctx_list):
        n_strikes = len(ctx['strikes'])
        if n_strikes < 2:
            continue

        for si in range(n_strikes):
            for sj in range(si + 1, n_strikes):
                c_lo_code = ctx['call_oids'][si]
                c_hi_code = ctx['call_oids'][sj]
                p_lo_code = ctx['put_oids'][si]
                p_hi_code = ctx['put_oids'][sj]

                all_codes = [c_lo_code, c_hi_code, p_lo_code, p_hi_code]
                all_codes_norm = [_normalize_code(c) for c in all_codes]
                if not all(code in pos_by_code for code in all_codes_norm):
                    continue

                # Get first entry for each leg (using normalized codes)
                leg_entries = {}
                for code_n in all_codes_norm:
                    for entry in pos_by_code[code_n]:
                        leg_entries[code_n] = entry
                        break
                if len(leg_entries) < 4:
                    continue

                volumes = [leg_entries[code_n]['volume'] for code_n in all_codes_norm]
                contract_size = min(volumes)
                if contract_size < 1:
                    continue

                # Determine box type from leg directions
                d_c_lo = leg_entries[all_codes_norm[0]]['direction']
                d_c_hi = leg_entries[all_codes_norm[1]]['direction']
                d_p_lo = leg_entries[all_codes_norm[2]]['direction']
                d_p_hi = leg_entries[all_codes_norm[3]]['direction']

                if d_c_lo > 0 and d_c_hi < 0 and d_p_hi > 0 and d_p_lo < 0:
                    pos_type = 'LongBox'
                elif d_c_lo < 0 and d_c_hi > 0 and d_p_hi < 0 and d_p_lo > 0:
                    pos_type = 'ShortBox'
                else:
                    pos_type = 'LongBox' if d_c_lo > 0 else 'ShortBox'
                    A.log_queue.append(
                        f"[SYNC] WARNING: Ambiguous directions at ctx={ctx_idx} "
                        f"K{ctx['strikes'][si]:.2f}/{ctx['strikes'][sj]:.2f} "
                        f"[{d_c_lo:+d},{d_c_hi:+d},{d_p_hi:+d},{d_p_lo:+d}] "
                        f"-- assuming {pos_type}"
                    )

                # Skip if already tracked locally
                if (ctx_idx, pos_type) in already_tracked:
                    continue

                payout = ctx['strikes'][sj] - ctx['strikes'][si]
                dte = max(ctx['dte'], 1)
                now_ts = int(datetime.datetime.now().timestamp())

                # Estimate entry_cost from current tick snapshot
                snapshot = A.tick_data
                entry_cost = 0.0
                margin_rmb = 0.0
                c_lo_t = snapshot.get(ctx['call_oids'][si])
                c_hi_t = snapshot.get(ctx['call_oids'][sj])
                p_hi_t = snapshot.get(ctx['put_oids'][sj])
                p_lo_t = snapshot.get(ctx['put_oids'][si])

                if pos_type == 'LongBox':
                    if (c_lo_t and c_hi_t and p_hi_t and p_lo_t
                            and c_lo_t['a1'] > 0 and c_hi_t['b1'] > 0
                            and p_hi_t['a1'] > 0 and p_lo_t['b1'] > 0):
                        entry_cost = ((c_lo_t['a1'] - c_hi_t['b1'])
                                      + (p_hi_t['a1'] - p_lo_t['b1'])
                                      + BOX_COMMISSION)
                    cost_rmb = entry_cost * CONTRACT_MULTIPLIER * contract_size
                    A.sim_cash -= cost_rmb
                    A.local_available_cash -= cost_rmb
                else:
                    margin_rmb = 2.0 * payout * CONTRACT_MULTIPLIER * contract_size
                    if (c_lo_t and c_hi_t and p_hi_t and p_lo_t
                            and c_lo_t['b1'] > 0 and c_hi_t['a1'] > 0
                            and p_hi_t['b1'] > 0 and p_lo_t['a1'] > 0):
                        gain = ((c_lo_t['b1'] - c_hi_t['a1'])
                                + (p_hi_t['b1'] - p_lo_t['a1'])
                                - BOX_COMMISSION)
                        entry_cost = gain
                    A.sim_cash -= (margin_rmb - entry_cost * CONTRACT_MULTIPLIER * contract_size)
                    A.local_available_cash -= margin_rmb

                # Register position and tracking sets
                with A.data_lock:
                    A.positions.append({
                        'pos_type': pos_type,
                        'ctx_idx': ctx_idx,
                        'strike_i': si,
                        'strike_j': sj,
                        'entry_cost': entry_cost,
                        'payout': payout,
                        'margin_rmb': margin_rmb,
                        'dte_at_entry': dte,
                        'entry_time': 0,  # unknown -- bypasses MIN_HOLDING_TIME
                        'state': 'Open',
                        'contract_size': contract_size,
                        'synced': True,
                    })
                    A.open_pos_set.add((ctx_idx, pos_type))
                    underlying = ctx['underlying']
                    A.positions_per_underlying[underlying] = (
                        A.positions_per_underlying.get(underlying, 0) + 1
                    )
                    box_key = (underlying, ctx['expiry'],
                               ctx['strikes'][si], ctx['strikes'][sj],
                               "LONG" if pos_type == 'LongBox' else "SHORT")
                    A.placed_boxes.add(box_key)
                    already_tracked.add((ctx_idx, pos_type))

                synced_count += 1
                ts_str = datetime.datetime.now().strftime('%H:%M:%S')
                A.log_queue.append(
                    f"[{ts_str}] [SYNC] Imported {pos_type} [{underlying}] "
                    f"K{ctx['strikes'][si]:.2f}/{ctx['strikes'][sj]:.2f} "
                    f"DTE={dte} size={contract_size} payout={payout:.4f} "
                    f"entry_cost={entry_cost:.4f} SimCash={A.sim_cash:.0f}"
                )

    if synced_count > 0:
        A.log_queue.append(
            f"[SYNC] Imported {synced_count} box position(s) from broker. "
            f"Total positions now: {len(A.positions)}"
        )
    else:
        A.log_queue.append("[SYNC] No new box positions found at broker.")

    # --- Report pending open orders ---
    broker_orders = _query_broker_orders()
    if broker_orders:
        pending = []
        for o in broker_orders:
            status = getattr(o, 'm_nOrderStatus', 0)
            if status in (54, 56, 57, 50):
                continue  # terminal states
            code = getattr(o, 'm_strInstrumentID', '')
            vol = getattr(o, 'm_nVolume', 0)
            price = getattr(o, 'm_dPrice', 0)
            remark = getattr(o, 'm_strRemark', '')
            pending.append(f"{code} status={status} vol={vol} @ {price:.4f} ({remark})")
        if pending:
            A.log_queue.append(
                f"[SYNC] WARNING: {len(pending)} pending order(s) at broker "
                f"-- review manually:"
            )
            for desc in pending[:10]:
                A.log_queue.append(f"[SYNC]   {desc}")
            if len(pending) > 10:
                A.log_queue.append(f"[SYNC]   ... and {len(pending) - 10} more")
        else:
            A.log_queue.append("[SYNC] No pending open orders (all terminal).")
    else:
        A.log_queue.append("[SYNC] No open orders at broker.")


def _check_exits(snapshot, now_ts, C):
    with A.data_lock:
        for pi, pos in enumerate(A.positions):
            if pos.get('state', 'Open') != 'Open':
                continue
            if 'entry_time' in pos and (now_ts - pos['entry_time']) < MIN_HOLDING_TIME:
                continue
            ctx = A.ctx_list[pos['ctx_idx']]
            si = pos['strike_i']
            sj = pos['strike_j']
            contract_size = pos.get('contract_size', 1)
            c_lo = snapshot.get(ctx['call_oids'][si])
            c_hi = snapshot.get(ctx['call_oids'][sj])
            p_hi = snapshot.get(ctx['put_oids'][sj])
            p_lo = snapshot.get(ctx['put_oids'][si])
            quotes = [c_lo, c_hi, p_hi, p_lo]
            if not all(q is not None and (now_ts - q['time']) <= MAX_STALE_SECONDS_EXIT for q in quotes):
                continue
            c_lo, c_hi, p_hi, p_lo = quotes
            
            # Maturity Exit logic
            if ctx['dte'] == 0:
                pnl = 0.0
                if pos['pos_type'] == 'LongBox':
                    pnl = (pos['payout'] - pos['entry_cost'] - BOX_COMMISSION) * CONTRACT_MULTIPLIER * contract_size
                    A.sim_cash += (pos['payout'] - BOX_COMMISSION) * CONTRACT_MULTIPLIER * contract_size
                elif pos['pos_type'] == 'ShortBox':
                    pnl = (pos['entry_cost'] - pos['payout'] - BOX_COMMISSION) * CONTRACT_MULTIPLIER * contract_size
                    A.sim_cash += pos['margin_rmb'] - (pos['payout'] + BOX_COMMISSION) * CONTRACT_MULTIPLIER * contract_size
                
                pos['state'] = 'Closing'
                box_type = "LONG" if pos['pos_type'] == 'LongBox' else "SHORT"
                pos_key = (pos['ctx_idx'], pos['pos_type'])
                A.open_pos_set.discard(pos_key)
                _decrement_underlying_count(ctx['underlying'])
                box_key = (ctx['underlying'], ctx['expiry'], ctx['strikes'][si], ctx['strikes'][sj], box_type)
                if box_key in A.placed_boxes:
                    A.placed_boxes.remove(box_key)
                ts_str = datetime.datetime.now().strftime('%H:%M:%S')
                A.log_queue.append(f"[{ts_str}] *** MATURITY EXIT {pos['pos_type']} [{ctx['underlying']}] K{ctx['strikes'][si]:.2f}/{ctx['strikes'][sj]:.2f} "
                      f"size={contract_size} payout={pos['payout']:.4f} PnL={pnl:+.2f} RMB SimCash={A.sim_cash:.0f}")
                
                # Send closing orders for maturity if desired, or let it expire.
                remark = f"zj_exit_{now_ts}_{box_type}_{ctx['underlying']}_{ctx['strikes'][si]}_{ctx['strikes'][sj]}"
                if box_type == "LONG":
                    legs_to_close = [
                        (ctx['call_oids'][si], 51, c_lo['b1']),
                        (ctx['call_oids'][sj], 53, c_hi['a1']),
                        (ctx['put_oids'][sj], 51, p_hi['b1']),
                        (ctx['put_oids'][si], 53, p_lo['a1']),
                    ]
                else:
                    legs_to_close = [
                        (ctx['call_oids'][si], 53, c_lo['a1']),
                        (ctx['call_oids'][sj], 51, c_hi['b1']),
                        (ctx['put_oids'][sj], 53, p_hi['a1']),
                        (ctx['put_oids'][si], 51, p_lo['b1']),
                    ]
                for sym, op_type, price in legs_to_close:
                    try:
                        t0 = time.perf_counter()
                        passorder(op_type, 1101, A.acct, sym, 14, round(price, 4), contract_size, remark, 2, '', C)
                        dt = time.perf_counter() - t0
                        _append_latency(dt)
                    except Exception as e:
                        pass
                continue
    
            if pos['pos_type'] == 'LongBox':
                if c_lo['b1'] > 0 and c_hi['a1'] > 0 and p_hi['b1'] > 0 and p_lo['a1'] > 0:
                    close_value = (c_lo['b1'] - c_hi['a1']) + (p_hi['b1'] - p_lo['a1'])
                    close_net = close_value - BOX_COMMISSION
                    exit_threshold = MIN_EXIT_RETURN
                    # This part has been go wrong for so many times, different AI said different things
                    if ctx['dte'] <= 4:
                        # Near expiry (DTE <= 4), increase exit_threshold to allow a smaller required close_net, encouraging early exit.
                        exit_threshold += EARLY_EXIT_ADJUSTMENT
                    # If close_net is close enough to payout (close_net * (1 + exit_threshold) > payout), exit to lock in profit & release capital.
                    if close_net * (1.0 + exit_threshold) > pos['payout']:
                        pnl = (close_net - pos['entry_cost']) * CONTRACT_MULTIPLIER * contract_size
                        A.sim_cash += close_net * CONTRACT_MULTIPLIER * contract_size
                        pos['state'] = 'Closing'
                        A.open_pos_set.discard((pos['ctx_idx'], 'LongBox'))
                        _decrement_underlying_count(ctx['underlying'])
                        box_key = (ctx['underlying'], ctx['expiry'], ctx['strikes'][si], ctx['strikes'][sj], "LONG")
                        if box_key in A.placed_boxes:
                            A.placed_boxes.remove(box_key)
    
                        ts_str = datetime.datetime.now().strftime('%H:%M:%S')
                        A.log_queue.append(f"[{ts_str}] *** EXIT LongBox [{ctx['underlying']}] K{ctx['strikes'][si]:.2f}/{ctx['strikes'][sj]:.2f} "
                              f"size={contract_size} close_net={close_net:.4f} payout={pos['payout']:.4f} PnL={pnl:+.2f} RMB SimCash={A.sim_cash:.0f}")
                              
                        remark = f"zj_exit_{now_ts}_LONG_{ctx['underlying']}_{ctx['strikes'][si]}_{ctx['strikes'][sj]}"
                        legs_to_close = [
                            (ctx['call_oids'][si], 51, c_lo['b1']),
                            (ctx['call_oids'][sj], 53, c_hi['a1']),
                            (ctx['put_oids'][sj], 51, p_hi['b1']),
                            (ctx['put_oids'][si], 53, p_lo['a1']),
                        ]
                        for sym, op_type, price in legs_to_close:
                            try:
                                t0 = time.perf_counter()
                                passorder(op_type, 1101, A.acct, sym, 14, round(price, 4), contract_size, remark, 2, '', C)
                                dt = time.perf_counter() - t0
                                _append_latency(dt)
                                if dt > LATENCY_WARN_MEDIAN_S:
                                    if hasattr(A, 'log_queue'):
                                        A.log_queue.append(f"[LATENCY] Exit leg {sym} took {dt*1000:.0f}ms")
                            except Exception as e:
                                if hasattr(A, 'log_queue'):
                                    A.log_queue.append(f"[passorder exit error] {sym} {e}")
                                        
            elif pos['pos_type'] == 'ShortBox':
                if c_lo['a1'] > 0 and c_hi['b1'] > 0 and p_hi['a1'] > 0 and p_lo['b1'] > 0:
                    buy_back = (c_lo['a1'] - c_hi['b1']) + (p_hi['a1'] - p_lo['b1']) + BOX_COMMISSION
                    exit_threshold = MIN_EXIT_RETURN
                    # This part has been go wrong for so many times, different AI said different things
                    if ctx['dte'] <= 4:
                        # Near expiry (DTE <= 4), decrease exit_threshold to allow a larger acceptable buy_back cost, encouraging early exit to free locked margin.
                        exit_threshold = max(exit_threshold - EARLY_EXIT_ADJUSTMENT, 0.0)
                    # If buy_back cost is low enough relative to payout, exit early to release the high margin required by ShortBox.
                    if buy_back > 0 and buy_back * (1.0 + exit_threshold) < pos['payout']:
                        pnl = (pos['entry_cost'] - buy_back) * CONTRACT_MULTIPLIER * contract_size
                        A.sim_cash += pos['margin_rmb'] - buy_back * CONTRACT_MULTIPLIER * contract_size
                        pos['state'] = 'Closing'
                        A.open_pos_set.discard((pos['ctx_idx'], 'ShortBox'))
                        _decrement_underlying_count(ctx['underlying'])
                        box_key = (ctx['underlying'], ctx['expiry'], ctx['strikes'][si], ctx['strikes'][sj], "SHORT")
                        if box_key in A.placed_boxes:
                            A.placed_boxes.remove(box_key)
    
                        ts_str = datetime.datetime.now().strftime('%H:%M:%S')
                        A.log_queue.append(f"[{ts_str}] *** EXIT ShortBox [{ctx['underlying']}] K{ctx['strikes'][si]:.2f}/{ctx['strikes'][sj]:.2f} "
                              f"size={contract_size} buy_back={buy_back:.4f} payout={pos['payout']:.4f} PnL={pnl:+.2f} RMB SimCash={A.sim_cash:.0f}")
    
                        remark = f"zj_exit_{now_ts}_SHORT_{ctx['underlying']}_{ctx['strikes'][si]}_{ctx['strikes'][sj]}"
                        legs_to_close = [
                            (ctx['call_oids'][si], 53, c_lo['a1']),
                            (ctx['call_oids'][sj], 51, c_hi['b1']),
                            (ctx['put_oids'][sj], 53, p_hi['a1']),
                            (ctx['put_oids'][si], 51, p_lo['b1']),
                        ]
                        for sym, op_type, price in legs_to_close:
                            try:
                                t0 = time.perf_counter()
                                passorder(op_type, 1101, A.acct, sym, 14, round(price, 4), contract_size, remark, 2, '', C)
                                dt = time.perf_counter() - t0
                                _append_latency(dt)
                                if dt > LATENCY_WARN_MEDIAN_S:
                                    if hasattr(A, 'log_queue'):
                                        A.log_queue.append(f"[LATENCY] Exit leg {sym} took {dt*1000:.0f}ms")
                            except Exception as e:
                                if hasattr(A, 'log_queue'):
                                    A.log_queue.append(f"[passorder exit error] {sym} {e}")


def _append_latency(dt):
    """Record a passorder() round-trip sample; keep rolling window of 200."""
    if hasattr(A, 'latency_samples'):
        A.latency_samples.append(dt)
        if len(A.latency_samples) > 200:
            A.latency_samples = A.latency_samples[-100:]


def _get_rollback_price(sym, close_op, fallback_price):
    with A.data_lock:
        t_data = A.tick_data.get(sym)
        if t_data:
            if close_op == 53:  # Sell Close: want to hit bid
                p = t_data.get('b1', 0.0)
                if p > 0.0:
                    return p
            elif close_op == 51:  # Buy Close: want to hit ask
                p = t_data.get('a1', 0.0)
                if p > 0.0:
                    return p
    return fallback_price


def _place_box_orders(C, ctx, orig_i, orig_j, prices, cost_or_credit, payout, ret, ann, now, is_long=True, eval_start=0.0, contract_size=1):
    if getattr(A, 'stop_arbitrage', False):
        return

    if eval_start > 0:
        eval_gap = time.perf_counter() - eval_start
        if eval_gap > MAX_EVAL_ORDER_GAP_S:
            if hasattr(A, 'log_queue'):
                A.log_queue.append(f"[STALE EVAL] {eval_gap*1000:.0f}ms since evaluation start -- skipping box")
            return

    underlying = ctx['underlying']
    expiry = ctx['expiry']
    
    k1 = ctx['strikes'][orig_i]
    k2 = ctx['strikes'][orig_j]
    box_type = "LONG" if is_long else "SHORT"
    box_key = (underlying, expiry, k1, k2, box_type)

    with A.data_lock:
        if box_key in A.placed_boxes:
            return
        if hasattr(A, 'failed_boxes') and box_key in A.failed_boxes:
            last_fail = A.failed_boxes[box_key]
            if time.time() - last_fail < FAILED_BOX_COOLDOWN_S:
                ts_str = now.strftime('%H:%M:%S')
                if hasattr(A, 'log_queue'):
                    A.log_queue.append(
                        f"[{ts_str}] [COOLDOWN] Skipping {box_type} Box [{underlying}] K{k1}/{k2} "
                        f"-- failed recently, cooling down"
                    )
                return
            else:
                A.failed_boxes.pop(box_key, None)
        A.placed_boxes.add(box_key)

    c1_sym = ctx['call_oids'][orig_i]
    c2_sym = ctx['call_oids'][orig_j]
    p1_sym = ctx['put_oids'][orig_i]
    p2_sym = ctx['put_oids'][orig_j]

    if is_long:
        c1_ask = prices['c1_ask']
        c2_bid = prices['c2_bid']
        p2_ask = prices['p2_ask']
        p1_bid = prices['p1_bid']

        legs = [
            (c1_sym, 50, c1_ask),
            (c2_sym, 52, c2_bid),
            (p2_sym, 50, p2_ask),
            (p1_sym, 52, p1_bid),
        ]
        log_legs = f"BuyC({c1_sym})@{round(c1_ask, 4)} | SellC({c2_sym})@{round(c2_bid, 4)} | BuyP({p2_sym})@{round(p2_ask, 4)} | SellP({p1_sym})@{round(p1_bid, 4)}"
    else:
        c1_bid = prices['c1_bid']
        c2_ask = prices['c2_ask']
        p2_bid = prices['p2_bid']
        p1_ask = prices['p1_ask']

        # Buy legs FIRST so broker sees covered spreads, not naked shorts.
        # Buy Call K2 first -> then Sell Call K1 is a bear call spread (covered).
        # Buy Put K1 first  -> then Sell Put K2 is a bull put spread (covered).
        legs = [
            (c2_sym, 50, c2_ask),   # Buy Call K2 @ ask
            (c1_sym, 52, c1_bid),   # Sell Call K1 @ bid
            (p1_sym, 50, p1_ask),   # Buy Put K1 @ ask
            (p2_sym, 52, p2_bid),   # Sell Put K2 @ bid
        ]
        log_legs = f"BuyC({c2_sym})@{round(c2_ask, 4)} | SellC({c1_sym})@{round(c1_bid, 4)} | BuyP({p1_sym})@{round(p1_ask, 4)} | SellP({p2_sym})@{round(p2_bid, 4)}"

    # -- Pre-placement profitability guard --
    # Recompute cost/credit from the ACTUAL prices about to be sent to passorder().
    # Abort if tick drift made the trade unprofitable (payout <= cost + commissions).
    if is_long:
        actual_cost = (prices['c1_ask'] - prices['c2_bid']) + (prices['p2_ask'] - prices['p1_bid']) + BOX_COMMISSION
        actual_ret = (payout - actual_cost) / actual_cost if actual_cost > 0 else -999.0
        if actual_cost <= 0 or payout <= actual_cost or actual_ret < MIN_RETURN:
            ts_str = now.strftime('%H:%M:%S')
            with A.data_lock:
                A.placed_boxes.discard(box_key)
            A.log_queue.append(
                f"[{ts_str}] [GUARD] ABORT {box_type} [{underlying}] K{k1}/{k2} "
                f"actual_cost={actual_cost:.4f} payout={payout:.4f} ret={actual_ret*100:.2f}% "
                f"-- tick drifted, no longer profitable"
            )
            return
    else:
        actual_credit = (prices['c1_bid'] - prices['c2_ask']) + (prices['p2_bid'] - prices['p1_ask']) - BOX_COMMISSION
        actual_profit = actual_credit - payout
        margin = payout * 2.0
        actual_ret = actual_profit / margin if margin > 0 else -999.0
        if actual_credit <= 0 or actual_credit <= payout or actual_ret < MIN_RETURN:
            ts_str = now.strftime('%H:%M:%S')
            with A.data_lock:
                A.placed_boxes.discard(box_key)
            A.log_queue.append(
                f"[{ts_str}] [GUARD] ABORT {box_type} [{underlying}] K{k1}/{k2} "
                f"actual_credit={actual_credit:.4f} payout={payout:.4f} ret={actual_ret*100:.2f}% "
                f"-- tick drifted, no longer profitable"
            )
            return

    remark = f"zj_open_{int(now.timestamp())}_{box_type}_{underlying}_{k1}_{k2}"
    
    order_ids = []
    placed_legs = []  # Track successfully placed legs for rollback on partial failure
    any_leg_failed = False
    for leg_idx, (sym, op_type, price) in enumerate(legs):
        try:
            t0 = time.perf_counter()
            passorder(op_type, 1101, A.acct, sym, 14, round(price, 4), contract_size, remark, 2, '', C)
            dt = time.perf_counter() - t0
            _append_latency(dt)
            if dt > LATENCY_WARN_MEDIAN_S:
                if hasattr(A, 'log_queue'):
                    A.log_queue.append(f"[LATENCY] Leg{leg_idx} {sym} passorder took {dt*1000:.0f}ms")
            order_ids.append(sym)
            placed_legs.append((leg_idx, sym, op_type, price))
        except Exception as e:
            any_leg_failed = True
            if hasattr(A, 'log_queue'):
                A.log_queue.append(f"[passorder error] Leg{leg_idx} {sym} {e}")

    # Rollback or clean up if any leg failed to place
    if any_leg_failed:
        ts_str_r = now.strftime('%H:%M:%S')
        if hasattr(A, 'log_queue'):
            A.log_queue.append(
                f"[{ts_str_r}] [!!] ORDER PLACING FAILED for {box_type} box "
                f"[{underlying}] K{k1}/{k2} - successfully sent {len(placed_legs)}/4 legs."
            )
        
        if placed_legs:
            if hasattr(A, 'log_queue'):
                A.log_queue.append(
                    f"[{ts_str_r}] PARTIAL PLACEMENT - rolling back {len(placed_legs)} placed leg(s)"
                )
            # Reverse op_type: Buy-Open(50)->Sell-Close(53), Sell-Open(52)->Buy-Close(51)
            _rollback_map = {50: 53, 52: 51}
            for leg_idx, sym, op_type, entry_price in placed_legs:
                try:
                    close_op = _rollback_map.get(op_type, op_type)
                    rollback_price = _get_rollback_price(sym, close_op, entry_price)
                    passorder(close_op, 1101, A.acct, sym, 14,
                              round(rollback_price, 4), contract_size, remark + "_ROLLBACK", 2, '', C)
                    if hasattr(A, 'log_queue'):
                        A.log_queue.append(
                            f"[{ts_str_r}] ROLLBACK: close leg{leg_idx} {sym} op={close_op} @ {rollback_price:.4f} (entry was {entry_price:.4f})"
                        )
                except Exception as e:
                    if hasattr(A, 'log_queue'):
                        A.log_queue.append(
                            f"[{ts_str_r}] ROLLBACK FAILED: {sym} {e} -- MANUAL INTERVENTION REQUIRED"
                        )

        # Set virtual position to Errored and restore cash
        with A.data_lock:
            if not hasattr(A, 'failed_boxes'):
                A.failed_boxes = {}
            A.failed_boxes[box_key] = time.time()
            A.placed_boxes.discard(box_key)
            
            # Find the virtual position we just added in A.positions
            target_pos = None
            for p in reversed(A.positions):
                ptype = "LONG" if p['pos_type'] == 'LongBox' else "SHORT"
                ctx = A.ctx_list[p['ctx_idx']]
                pk = (ctx['underlying'], ctx['expiry'], ctx['strikes'][p['strike_i']], ctx['strikes'][p['strike_j']], ptype)
                if pk == box_key and p.get('entry_time') == int(now.timestamp()) and p.get('state') == 'Open':
                    target_pos = p
                    break
            
            if target_pos:
                target_pos['state'] = 'Errored'
                cs = target_pos.get('contract_size', 1)
                if target_pos['pos_type'] == 'LongBox':
                    restore = target_pos['entry_cost'] * CONTRACT_MULTIPLIER * cs
                else:
                    restore = target_pos.get('margin_rmb', 0.0)
                A.sim_cash += restore
                A.local_available_cash += restore
                _decrement_underlying_count(underlying)
                if hasattr(A, 'log_queue'):
                    A.log_queue.append(
                        f"[{ts_str_r}] STATE UPDATE: Marked failed position for {box_key} as 'Errored'. Restored {restore:.0f} RMB."
                    )
        return

    # -- Register for asynchronous fill verification --
    if len(placed_legs) == 4:
        with A.data_lock:
            if not hasattr(A, 'pending_box_verifications'):
                A.pending_box_verifications = []
            A.pending_box_verifications.append({
                'box_key': box_key,
                'placed_legs': placed_legs,
                'remark': remark,
                'placed_time': time.time(),
                'contract_size': contract_size,
                'box_type': box_type,
                'underlying': underlying,
                'k1': k1,
                'k2': k2,
                'entry_time': int(now.timestamp()),
                'ctx_idx': ctx['idx'],
            })

    with A.data_lock:
        A.box_orders[box_key] = order_ids
        if not hasattr(A, 'order_remark_to_box'):
            A.order_remark_to_box = {}
        A.order_remark_to_box[remark] = box_key

    ts_str = now.strftime('%H:%M:%S')
    dte    = (expiry - now.date()).days
    lbl    = "Cost" if is_long else "Credit"
    A.log_queue.append(f"[{ts_str}] >>> PLACED {box_type} Box [{underlying}] "
          f"DTE={dte} K1={k1} K2={k2} size={contract_size} "
          f"{lbl}={cost_or_credit:.4f} Payout={payout:.4f} "
          f"Ret={ret*100:.2f}% Ann={ann*100:.2f}% SimCash={A.sim_cash:.0f}")
    A.log_queue.append(f"          Legs: {log_legs}")

    # Risk control is now performed before order placement via get_real_available_cash


def _verify_pending_box_fills(C):
    if not hasattr(A, 'pending_box_verifications') or not A.pending_box_verifications:
        return

    now_time = time.time()
    still_pending = []
    
    # Check fills after 2.0 seconds from placement
    CHECK_DELAY = 2.0
    
    for entry in A.pending_box_verifications:
        if now_time - entry['placed_time'] < CHECK_DELAY:
            still_pending.append(entry)
            continue
            
        box_key = entry['box_key']
        placed_legs = entry['placed_legs']
        remark = entry['remark']
        contract_size = entry['contract_size']
        box_type = entry['box_type']
        underlying = entry['underlying']
        k1 = entry['k1']
        k2 = entry['k2']
        entry_time = entry['entry_time']
        
        # Check if callback already handled it
        with A.data_lock:
            target_pos = None
            for p in A.positions:
                ptype = "LONG" if p['pos_type'] == 'LongBox' else "SHORT"
                ctx = A.ctx_list[p['ctx_idx']]
                pk = (ctx['underlying'], ctx['expiry'], ctx['strikes'][p['strike_i']], ctx['strikes'][p['strike_j']], ptype)
                if pk == box_key and p.get('entry_time') == entry_time:
                    target_pos = p
                    break
            
            if target_pos is None or target_pos.get('state') != 'Open':
                # Skip if already marked as Errored or Closed by callbacks
                continue
                
        # Query broker positions
        try:
            broker_pos = _query_broker_positions()
            # Direction-aware position map: (code, direction) -> total volume
            # m_nDirection: 48 = long (bought), 49 = short (sold)
            pos_by_code_dir = {}
            for p in broker_pos:
                code = _normalize_code(getattr(p, 'm_strInstrumentID', ''))
                vol = abs(getattr(p, 'm_nVolume', 0))
                direction = getattr(p, 'm_nDirection', -1)
                if code and vol > 0:
                    key = (code, direction)
                    pos_by_code_dir[key] = pos_by_code_dir.get(key, 0) + vol

            # op_type 50 (Buy-Open) expects direction 48 (long)
            # op_type 52 (Sell-Open) expects direction 49 (short)
            _expected_dir = {50: 48, 52: 49}
            unfilled = []
            for _, sym, op_type, _ in placed_legs:
                sym_norm = _normalize_code(sym)
                exp_dir = _expected_dir.get(op_type, -1)
                actual_vol = pos_by_code_dir.get((sym_norm, exp_dir), 0)
                if actual_vol < contract_size:
                    unfilled.append(f"{sym_norm}(dir={exp_dir},have={actual_vol},need={contract_size})")

            ts_fill = datetime.datetime.now().strftime('%H:%M:%S')
            if unfilled:
                print(f"[{ts_fill}] [!!] ASYNC UNFILLED LEG(S) for {box_type} box [{underlying}] K{k1}/{k2}: {', '.join(unfilled)} -- rolling back filled legs.")
                
                # Rollback filled legs to remove partial exposure
                _rb_map = {50: 53, 52: 51}
                for leg_idx, sym, op_type, entry_price in placed_legs:
                    try:
                        close_op = _rb_map.get(op_type, op_type)
                        rollback_price = _get_rollback_price(sym, close_op, entry_price)
                        passorder(close_op, 1101, A.acct, sym, 14,
                                  round(rollback_price, 4), contract_size,
                                  remark + "_UNFILLED_RB", 2, '', C)
                        print(f"[{ts_fill}] ROLLBACK(unfilled): {sym} op={close_op} @ {rollback_price:.4f} (entry was {entry_price:.4f})")
                    except Exception as e:
                        print(f"[{ts_fill}] ROLLBACK(unfilled) FAILED: {sym} {e} -- MANUAL INTERVENTION REQUIRED")
                
                # Set virtual position to Errored and restore cash
                with A.data_lock:
                    if not hasattr(A, 'failed_boxes'):
                        A.failed_boxes = {}
                    A.failed_boxes[box_key] = time.time()
                    if box_key in A.placed_boxes:
                        A.placed_boxes.discard(box_key)
                    if target_pos:
                        target_pos['state'] = 'Errored'
                        cs = target_pos.get('contract_size', 1)
                        if target_pos['pos_type'] == 'LongBox':
                            restore = target_pos['entry_cost'] * CONTRACT_MULTIPLIER * cs
                        else:
                            restore = target_pos.get('margin_rmb', 0.0)
                        A.sim_cash += restore
                        A.local_available_cash += restore
                        _decrement_underlying_count(underlying)
                        print(f"[{ts_fill}] STATE UPDATE: Marked position for {box_key} as 'Errored'. Restored {restore:.0f} RMB.")
            else:
                print(f"[{ts_fill}] [OK] ASYNC FILL VERIFIED for {box_type} box [{underlying}] K{k1}/{k2} - fully filled.")
        except Exception as e:
            ts_fill = datetime.datetime.now().strftime('%H:%M:%S')
            print(f"[{ts_fill}] FILL VERIFY ERROR for {box_type} box [{underlying}] K{k1}/{k2}: {e} -- proceeding with caution")
            still_pending.append(entry)
            
    A.pending_box_verifications = still_pending


def _evaluate_context(ctx_idx, snapshot, now_ts, now, C):
    ctx = A.ctx_list[ctx_idx]
    underlying = ctx['underlying']
    expiry = ctx['expiry']
    dte = max(ctx['dte'], 1)

    if dte <= 5 or ctx.get('near_level', 1) > 4:
        A.last_long_box.pop(ctx_idx, None)
        A.last_short_box.pop(ctx_idx, None)
        return None, None

    n_strikes = len(ctx['strikes'])

    # Pass 1: collect valid liquid strikes (freshness + volume checks)
    raw = []
    for si in range(n_strikes):
        c_sym = ctx['call_oids'][si]
        p_sym = ctx['put_oids'][si]
        c_data = snapshot.get(c_sym)
        p_data = snapshot.get(p_sym)
        if not c_data or not p_data:
            continue
        if (now_ts - c_data['time']) > MAX_STALE_SECONDS:
            continue
        if (now_ts - p_data['time']) > MAX_STALE_SECONDS:
            continue
        ca1, cb1 = c_data['a1'], c_data['b1']
        pa1, pb1 = p_data['a1'], p_data['b1']
        if ca1 > 0 and cb1 > 0 and pa1 > 0 and pb1 > 0:
            c_liquid = c_data['a1_v'] >= MIN_VOL and c_data['b1_v'] >= MIN_VOL
            p_liquid = p_data['a1_v'] >= MIN_VOL and p_data['b1_v'] >= MIN_VOL
            if c_liquid and p_liquid:
                raw.append((si, ca1, cb1, pa1, pb1))

    if len(raw) < 2:
        return None, None

    # Compute approximate underlying via put-call parity from first valid strike
    si0, ca1_0, cb1_0, pa1_0, pb1_0 = raw[0]
    c_mid = (ca1_0 + cb1_0) / 2.0
    p_mid = (pa1_0 + pb1_0) / 2.0
    approx_underlying = float(ctx['strikes'][si0]) + c_mid - p_mid

    # Pass 2: filter by moneyness and pack into arrays
    ca1_arr = np.zeros(len(raw), dtype=np.float32)
    cb1_arr = np.zeros(len(raw), dtype=np.float32)
    pa1_arr = np.zeros(len(raw), dtype=np.float32)
    pb1_arr = np.zeros(len(raw), dtype=np.float32)
    ks_arr  = np.zeros(len(raw), dtype=np.float32)
    orig_idx_arr = np.zeros(len(raw), dtype=np.int32)

    count = 0
    for si, ca1, cb1, pa1, pb1 in raw:
        strike = float(ctx['strikes'][si])
        if approx_underlying > 0 and approx_underlying / strike > MAX_MONEYNESS:
            continue
        ca1_arr[count] = ca1
        cb1_arr[count] = cb1
        pa1_arr[count] = pa1
        pb1_arr[count] = pb1
        ks_arr[count]  = strike
        orig_idx_arr[count] = si
        count += 1

    if count < 2:
        return None, None

    l_idx_i, l_idx_j, l_cost, l_payout, l_ret, l_ann, s_idx_i, s_idx_j, s_credit, s_payout, s_ret, s_ann = evaluate_boxes(
        ca1_arr[:count], cb1_arr[:count], pa1_arr[:count], pb1_arr[:count], ks_arr[:count], float(dte), BOX_COMMISSION, approx_underlying
    )

    best_context_long = None
    if l_idx_i >= 0:
        orig_i = orig_idx_arr[l_idx_i]
        orig_j = orig_idx_arr[l_idx_j]
        best_context_long = {
            'type': 'Long', 'ctx_idx': ctx_idx, 'orig_i': orig_i, 'orig_j': orig_j,
            'cost': l_cost, 'payout': l_payout, 'ret': l_ret, 'ann': l_ann,
            'c1_ask': float(ca1_arr[l_idx_i]), 'c2_bid': float(cb1_arr[l_idx_j]),
            'p2_ask': float(pa1_arr[l_idx_j]), 'p1_bid': float(pb1_arr[l_idx_i]),
            'ctx': ctx
        }

    best_context_short = None
    if s_idx_i >= 0:
        orig_i = orig_idx_arr[s_idx_i]
        orig_j = orig_idx_arr[s_idx_j]
        best_context_short = {
            'type': 'Short', 'ctx_idx': ctx_idx, 'orig_i': orig_i, 'orig_j': orig_j,
            'cost': s_credit, 'payout': s_payout, 'ret': s_ret, 'ann': s_ann,
            'c1_bid': float(cb1_arr[s_idx_i]), 'c2_ask': float(ca1_arr[s_idx_j]),
            'p2_bid': float(pb1_arr[s_idx_j]), 'p1_ask': float(pa1_arr[s_idx_i]),
            'ctx': ctx
        }

    return best_context_long, best_context_short


def get_real_available_cash(C):
    now_ts = int(datetime.datetime.now().timestamp())
    if not hasattr(A, 'local_available_cash'):
        A.local_available_cash = -1.0
        A.last_cash_sync_time = 0

    if A.local_available_cash < 0 or (now_ts - getattr(A, 'last_cash_sync_time', 0)) > 60:
        try:
            acct_info = get_trade_detail_data(A.acct, str(A.acct_type), 'account')
            if acct_info:
                real_cash = getattr(acct_info[0], 'm_dAvailable', 0.0)
            else:
                real_cash = A.local_available_cash if A.local_available_cash > 0 else INITIAL_CASH
            
            if real_cash > 0:
                A.local_available_cash = real_cash
                A.last_cash_sync_time = now_ts
        except Exception as e:
            if hasattr(A, 'log_queue'):
                A.log_queue.append(f"[get_real_available_cash error] {e}")
            if A.local_available_cash < 0:
                A.local_available_cash = INITIAL_CASH
    
    return getattr(A, 'local_available_cash', INITIAL_CASH)


import math

# Native Python inference for trained XGBoost model.
# Zero dependencies, microsecond latency execution.
def predict_xgboost_probability(features):
    # Feature indices map:
    # f0: underlying
    # f1: is_long_box
    # f2: dte
    # f3: strike_width
    # f4: moneyness_lo
    # f5: moneyness_hi
    # f6: entry_return
    # f7: spread_pct
    # f8: min_entry_vol
    # f9: min_bid_vol
    # f10: min_ask_vol
    # f11: mean_leg_volume
    # f12: time_of_day_seconds
    # f13: near_level
    # f14: entry_return_vs_session_mean
    # f15: strike_width_normalized
    # f16: time_to_close_seconds
    # f17: bid_ask_imbalance
    # f18: dte_bucket
    # f19: volume_to_spread_ratio
    # f20: day_of_week
    # f21: freshness_score
    val_sum = 0.0

    # Tree 0
    if features[16] < 25048.00000000:
        if features[14] < 0.00276691:
            if features[2] < 26.00000000:
                if features[2] < 8.00000000:
                    val_sum += 0.02688484
                else:
                    val_sum += 0.02044290
            else:
                if features[7] < 0.00400001:
                    val_sum += 0.01807985
                else:
                    val_sum += -0.00067989
        else:
            if features[15] < 0.10869561:
                if features[14] < 0.02145395:
                    val_sum += 0.02760533
                else:
                    val_sum += 0.03710724
            else:
                val_sum += 0.00073388
    else:
        if features[0] < 3.00000000:
            if features[15] < 0.03991225:
                if features[2] < 7.00000000:
                    val_sum += 0.02692993
                else:
                    val_sum += 0.01268927
            else:
                if features[20] < 4.00000000:
                    val_sum += 0.00578501
                else:
                    val_sum += -0.02079411
        else:
            if features[11] < 43.25000000:
                if features[14] < 0.00766032:
                    val_sum += -0.01651788
                else:
                    val_sum += 0.02267028
            else:
                if features[15] < 0.02714438:
                    val_sum += 0.02472775
                else:
                    val_sum += -0.00046077

    # Tree 1
    if features[19] < 600000000.00000000:
        if features[18] < 1.00000000:
            if features[20] < 3.00000000:
                if features[4] < 1.09687495:
                    val_sum += 0.01271867
                else:
                    val_sum += -0.02752366
            else:
                if features[15] < 0.02954733:
                    val_sum += 0.03093535
                else:
                    val_sum += 0.02084054
        else:
            if features[1] < 1.00000000:
                if features[4] < 0.94455558:
                    val_sum += -0.00905803
                else:
                    val_sum += 0.01338161
            else:
                if features[14] < 0.00718502:
                    val_sum += -0.01022812
                else:
                    val_sum += 0.02092360
    else:
        if features[14] < 0.01600849:
            if features[14] < 0.00276691:
                if features[5] < 1.04764700:
                    val_sum += 0.02112361
                else:
                    val_sum += -0.01089326
            else:
                if features[15] < 0.08551880:
                    val_sum += 0.02739964
                else:
                    val_sum += 0.01768782
        else:
            if features[14] < 0.04267346:
                val_sum += 0.03253793
            else:
                val_sum += 0.04241486

    # Tree 2
    if features[11] < 50.75000000:
        if features[3] < 0.20000029:
            if features[14] < 0.00718502:
                if features[14] < -0.00430902:
                    val_sum += 0.00292787
                else:
                    val_sum += -0.01366391
            else:
                if features[14] < 0.01795221:
                    val_sum += 0.01356907
                else:
                    val_sum += 0.03052615
        else:
            if features[15] < 0.08870489:
                if features[2] < 7.00000000:
                    val_sum += 0.02589956
                else:
                    val_sum += 0.01216690
            else:
                if features[2] < 100.00000000:
                    val_sum += 0.00013412
                else:
                    val_sum += -0.03280854
    else:
        if features[14] < 0.00363849:
            if features[2] < 7.00000000:
                if features[15] < 0.02931520:
                    val_sum += 0.03069058
                else:
                    val_sum += 0.01961765
            else:
                if features[5] < 0.93011117:
                    val_sum += -0.00252680
                else:
                    val_sum += 0.01061491
        else:
            if features[14] < 0.01600849:
                if features[14] < 0.00954316:
                    val_sum += 0.02163845
                else:
                    val_sum += 0.02735047
            else:
                if features[14] < 0.04267346:
                    val_sum += 0.03186826
                else:
                    val_sum += 0.04263166

    # Tree 3
    if features[12] < -10648.00000000:
        if features[0] < 3.00000000:
            if features[5] < 0.93011117:
                if features[5] < 0.92925709:
                    val_sum += -0.00214326
                else:
                    val_sum += -0.05712210
            else:
                if features[13] < 2.00000000:
                    val_sum += 0.01299988
                else:
                    val_sum += -0.00458844
        else:
            if features[1] < 1.00000000:
                if features[5] < 0.94461536:
                    val_sum += 0.00145267
                else:
                    val_sum += 0.01653531
            else:
                if features[14] < 0.00766032:
                    val_sum += -0.01517989
                else:
                    val_sum += 0.02292804
    else:
        if features[14] < 0.01600849:
            if features[18] < 2.00000000:
                if features[5] < 0.97500002:
                    val_sum += 0.01861452
                else:
                    val_sum += 0.02558807
            else:
                if features[19] < 6666.75537000:
                    val_sum += 0.00669116
                else:
                    val_sum += 0.01931526
        else:
            if features[14] < 0.04267346:
                val_sum += 0.03135437
            else:
                val_sum += 0.04240579

    # Tree 4
    if features[16] < 25048.00000000:
        if features[2] < 26.00000000:
            if features[4] < 1.09885716:
                if features[0] < 3.00000000:
                    val_sum += 0.02690471
                else:
                    val_sum += 0.01972330
            else:
                if features[3] < 0.15000009:
                    val_sum += 0.05051124
                else:
                    val_sum += 0.03451793
        else:
            if features[19] < 2799.92114000:
                if features[2] < 28.00000000:
                    val_sum += -0.00512699
                else:
                    val_sum += 0.01998699
            else:
                if features[16] < 23430.00000000:
                    val_sum += 0.01462166
                else:
                    val_sum += 0.02262939
    else:
        if features[0] < 3.00000000:
            if features[2] < 50.00000000:
                if features[2] < 7.00000000:
                    val_sum += 0.02075200
                else:
                    val_sum += 0.00758295
            else:
                if features[7] < 0.00742851:
                    val_sum += -0.05104098
                else:
                    val_sum += -0.02359084
        else:
            if features[1] < 1.00000000:
                if features[4] < 0.99599993:
                    val_sum += 0.00092389
                else:
                    val_sum += 0.01844857
            else:
                if features[13] < 2.00000000:
                    val_sum += -0.01554529
                else:
                    val_sum += 0.00402492

    # Tree 5
    if features[12] < -10648.00000000:
        if features[18] < 1.00000000:
            if features[12] < -14128.00000000:
                if features[5] < 1.04378378:
                    val_sum += 0.01138578
                else:
                    val_sum += -0.01356622
            else:
                if features[15] < 0.05232863:
                    val_sum += 0.02676521
                else:
                    val_sum += 0.01602739
        else:
            if features[6] < 0.01626005:
                if features[5] < 0.95789480:
                    val_sum += -0.00162504
                else:
                    val_sum += -0.01259983
            else:
                if features[6] < 0.03413012:
                    val_sum += 0.01690898
                else:
                    val_sum += 0.03511685
    else:
        if features[6] < 0.01200046:
            if features[18] < 2.00000000:
                if features[12] < -9679.00000000:
                    val_sum += 0.02723132
                else:
                    val_sum += 0.01921071
            else:
                if features[7] < 0.00240010:
                    val_sum += 0.01650825
                else:
                    val_sum += 0.00590915
        else:
            if features[15] < 0.10869561:
                if features[6] < 0.02880559:
                    val_sum += 0.02546824
                else:
                    val_sum += 0.03465248
            else:
                if features[15] < 0.11402505:
                    val_sum += -0.01356080
                else:
                    val_sum += 0.02037444

    # Tree 6
    if features[16] < 25048.00000000:
        if features[6] < 0.01200046:
            if features[11] < 41.25000000:
                if features[5] < 1.04764700:
                    val_sum += 0.01326456
                else:
                    val_sum += -0.01917713
            else:
                if features[19] < 627.44805900:
                    val_sum += 0.03054075
                else:
                    val_sum += 0.01923768
        else:
            if features[14] < 0.01600849:
                if features[5] < 0.93333334:
                    val_sum += -0.00254700
                else:
                    val_sum += 0.02495098
            else:
                if features[6] < 0.05708386:
                    val_sum += 0.03027244
                else:
                    val_sum += 0.04265057
    else:
        if features[0] < 3.00000000:
            if features[5] < 0.93011117:
                if features[20] < 4.00000000:
                    val_sum += 0.00009185
                else:
                    val_sum += -0.03849896
            else:
                if features[6] < 0.01010093:
                    val_sum += 0.00937450
                else:
                    val_sum += 0.02019230
        else:
            if features[1] < 1.00000000:
                if features[5] < 0.98500001:
                    val_sum += 0.00588666
                else:
                    val_sum += 0.02086636
            else:
                if features[6] < 0.01699986:
                    val_sum += -0.01512232
                else:
                    val_sum += 0.01968451

    # Tree 7
    if features[12] < -10648.00000000:
        if features[1] < 1.00000000:
            if features[4] < 0.96918917:
                if features[13] < 2.00000000:
                    val_sum += 0.00122888
                else:
                    val_sum += -0.04876602
            else:
                if features[11] < 17.00000000:
                    val_sum += 0.00723236
                else:
                    val_sum += 0.01538441
        else:
            if features[3] < 0.20000029:
                if features[11] < 73.00000000:
                    val_sum += -0.01498748
                else:
                    val_sum += 0.00973125
            else:
                if features[15] < 0.05976572:
                    val_sum += 0.01357947
                else:
                    val_sum += -0.00451565
    else:
        if features[15] < 0.04029817:
            if features[15] < 0.02905963:
                if features[11] < 41.25000000:
                    val_sum += 0.01383627
                else:
                    val_sum += 0.02469645
            else:
                if features[4] < 1.03490913:
                    val_sum += 0.02777166
                else:
                    val_sum += 0.03978395
        else:
            if features[4] < 1.09777772:
                if features[4] < 1.06545460:
                    val_sum += 0.01953729
                else:
                    val_sum += 0.01028927
            else:
                if features[20] < 4.00000000:
                    val_sum += 0.01982381
                else:
                    val_sum += 0.04338370

    # Tree 8
    if features[16] < 25048.00000000:
        if features[14] < 0.00310125:
            if features[18] < 2.00000000:
                if features[5] < 0.97466672:
                    val_sum += 0.01675403
                else:
                    val_sum += 0.02438630
            else:
                if features[14] < -0.00292722:
                    val_sum += 0.01612793
                else:
                    val_sum += 0.00524297
        else:
            if features[14] < 0.02145395:
                if features[5] < 0.93566662:
                    val_sum += 0.00950133
                else:
                    val_sum += 0.02504187
            else:
                if features[14] < 0.04267346:
                    val_sum += 0.03048348
                else:
                    val_sum += 0.03940784
    else:
        if features[0] < 3.00000000:
            if features[5] < 0.93011117:
                if features[5] < 0.92925709:
                    val_sum += -0.00099209
                else:
                    val_sum += -0.05602625
            else:
                if features[0] < 2.00000000:
                    val_sum += 0.00618987
                else:
                    val_sum += 0.01419583
        else:
            if features[11] < 50.25000000:
                if features[5] < 0.95641023:
                    val_sum += 0.00083963
                else:
                    val_sum += -0.01727774
            else:
                if features[14] < 0.00718502:
                    val_sum += 0.00474678
                else:
                    val_sum += 0.02775743

    # Tree 9
    if features[12] < -10648.00000000:
        if features[0] < 3.00000000:
            if features[15] < 0.03991225:
                if features[18] < 2.00000000:
                    val_sum += 0.01616240
                else:
                    val_sum += 0.00898749
            else:
                if features[20] < 4.00000000:
                    val_sum += 0.00483970
                else:
                    val_sum += -0.01113554
        else:
            if features[1] < 1.00000000:
                if features[11] < 34.00000000:
                    val_sum += 0.00324813
                else:
                    val_sum += 0.01559925
            else:
                if features[18] < 1.00000000:
                    val_sum += 0.01551661
                else:
                    val_sum += -0.01408643
    else:
        if features[15] < 0.04029817:
            if features[15] < 0.02774699:
                if features[15] < 0.02745741:
                    val_sum += 0.02015748
                else:
                    val_sum += -0.00078350
            else:
                if features[17] < 0.10344828:
                    val_sum += 0.02755222
                else:
                    val_sum += 0.01469992
        else:
            if features[18] < 2.00000000:
                if features[15] < 0.08870489:
                    val_sum += 0.02144957
                else:
                    val_sum += 0.01212363
            else:
                if features[20] < 3.00000000:
                    val_sum += 0.01631886
                else:
                    val_sum += 0.00342820

    # Tree 10
    if features[12] < -10648.00000000:
        if features[0] < 3.00000000:
            if features[5] < 0.93011117:
                if features[20] < 4.00000000:
                    val_sum += 0.00089408
                else:
                    val_sum += -0.03744449
            else:
                if features[13] < 2.00000000:
                    val_sum += 0.01238037
                else:
                    val_sum += -0.00095772
        else:
            if features[13] < 2.00000000:
                if features[5] < 0.95700002:
                    val_sum += 0.00141499
                else:
                    val_sum += -0.01612496
            else:
                if features[21] < 1.00000000:
                    val_sum += 0.02254334
                else:
                    val_sum += 0.00289808
    else:
        if features[15] < 0.04029817:
            if features[15] < 0.02903263:
                if features[19] < 1833.33081000:
                    val_sum += 0.01432377
                else:
                    val_sum += 0.02383453
            else:
                if features[12] < -9066.00000000:
                    val_sum += 0.03487726
                else:
                    val_sum += 0.02305990
        else:
            if features[0] < 3.00000000:
                if features[9] < 7.00000000:
                    val_sum += 0.01502771
                else:
                    val_sum += 0.02267465
            else:
                if features[20] < 3.00000000:
                    val_sum += 0.01752768
                else:
                    val_sum += 0.01011670

    # Tree 11
    if features[16] < 25048.00000000:
        if features[6] < 0.01000054:
            if features[18] < 2.00000000:
                if features[4] < 1.09777772:
                    val_sum += 0.01747202
                else:
                    val_sum += 0.03922054
            else:
                if features[14] < -0.00249870:
                    val_sum += 0.01392463
                else:
                    val_sum += 0.00049056
        else:
            if features[14] < 0.01600849:
                if features[15] < 0.10869561:
                    val_sum += 0.02278728
                else:
                    val_sum += 0.00810291
            else:
                if features[6] < 0.05708386:
                    val_sum += 0.02811597
                else:
                    val_sum += 0.03865776
    else:
        if features[1] < 1.00000000:
            if features[4] < 0.99657142:
                if features[3] < 0.05000007:
                    val_sum += -0.01047439
                else:
                    val_sum += 0.00834084
            else:
                if features[6] < 0.00887809:
                    val_sum += 0.01290485
                else:
                    val_sum += 0.02083112
        else:
            if features[18] < 1.00000000:
                if features[4] < 1.09485710:
                    val_sum += 0.01684429
                else:
                    val_sum += -0.02374150
            else:
                if features[6] < 0.01626005:
                    val_sum += -0.01213226
                else:
                    val_sum += 0.02072042

    # Tree 12
    if features[7] < 0.00000005:
        if features[19] < -2249.93408000:
            if features[0] < 3.00000000:
                if features[4] < 0.98845714:
                    val_sum += 0.02030198
                else:
                    val_sum += 0.01275467
            else:
                if features[2] < 15.00000000:
                    val_sum += 0.01633764
                else:
                    val_sum += -0.00866971
        else:
            if features[15] < 0.08620688:
                if features[19] < 900000000.00000000:
                    val_sum += 0.01824942
                else:
                    val_sum += 0.02257779
            else:
                if features[4] < 1.03941166:
                    val_sum += -0.00526780
                else:
                    val_sum += 0.01627689
    else:
        if features[2] < 9.00000000:
            if features[2] < 7.00000000:
                if features[4] < 1.07030308:
                    val_sum += 0.02557274
                else:
                    val_sum += 0.01175109
            else:
                if features[0] < 3.00000000:
                    val_sum += 0.00974299
                else:
                    val_sum += 0.01802905
        else:
            if features[0] < 3.00000000:
                if features[2] < 13.00000000:
                    val_sum += -0.01736496
                else:
                    val_sum += 0.00672897
            else:
                if features[2] < 28.00000000:
                    val_sum += -0.01102401
                else:
                    val_sum += 0.00609839

    # Tree 13
    if features[12] < -10648.00000000:
        if features[0] < 3.00000000:
            if features[2] < 56.00000000:
                if features[6] < 0.00908191:
                    val_sum += 0.00610416
                else:
                    val_sum += 0.01657475
            else:
                if features[6] < 0.00583386:
                    val_sum += -0.04959079
                else:
                    val_sum += -0.02315674
        else:
            if features[6] < 0.01699986:
                if features[1] < 1.00000000:
                    val_sum += 0.00830843
                else:
                    val_sum += -0.01417247
            else:
                if features[6] < 0.02880559:
                    val_sum += 0.01550665
                else:
                    val_sum += 0.03057620
    else:
        if features[6] < 0.01200046:
            if features[2] < 22.00000000:
                if features[12] < -9679.00000000:
                    val_sum += 0.02365348
                else:
                    val_sum += 0.01648214
            else:
                if features[14] < -0.00286621:
                    val_sum += 0.01454858
                else:
                    val_sum += 0.00123149
        else:
            if features[14] < 0.01600849:
                if features[6] < 0.03413012:
                    val_sum += 0.02319082
                else:
                    val_sum += -0.03250774
            else:
                if features[6] < 0.05708386:
                    val_sum += 0.02916397
                else:
                    val_sum += 0.03933667

    # Tree 14
    if features[16] < 25048.00000000:
        if features[4] < 1.06470585:
            if features[5] < 1.01918364:
                if features[2] < 8.00000000:
                    val_sum += 0.02514232
                else:
                    val_sum += 0.01833628
            else:
                if features[5] < 1.02484846:
                    val_sum += 0.03960152
                else:
                    val_sum += 0.02481923
        else:
            if features[4] < 1.08514285:
                if features[11] < 42.50000000:
                    val_sum += -0.00324077
                else:
                    val_sum += 0.01470824
            else:
                if features[20] < 4.00000000:
                    val_sum += 0.01786092
                else:
                    val_sum += 0.03386565
    else:
        if features[1] < 1.00000000:
            if features[5] < 0.87435895:
                if features[16] < 30072.00000000:
                    val_sum += -0.07485845
                else:
                    val_sum += 0.01102630
            else:
                if features[14] < 0.01252617:
                    val_sum += 0.01115181
                else:
                    val_sum += 0.02819901
        else:
            if features[2] < 9.00000000:
                if features[16] < 26671.00000000:
                    val_sum += 0.02180616
                else:
                    val_sum += 0.01264919
            else:
                if features[14] < 0.00766032:
                    val_sum += -0.01173297
                else:
                    val_sum += 0.02175041

    # Tree 15
    if features[12] < -10648.00000000:
        if features[6] < 0.01626005:
            if features[2] < 9.00000000:
                if features[12] < -13210.00000000:
                    val_sum += 0.01075105
                else:
                    val_sum += 0.01985004
            else:
                if features[14] < -0.00430902:
                    val_sum += 0.00537472
                else:
                    val_sum += -0.01264882
        else:
            if features[6] < 0.03413012:
                if features[19] < 562.50073200:
                    val_sum += 0.02057007
                else:
                    val_sum += 0.00935933
            else:
                if features[6] < 0.05708386:
                    val_sum += 0.02674301
                else:
                    val_sum += 0.03895358
    else:
        if features[6] < 0.01200046:
            if features[2] < 22.00000000:
                if features[4] < 1.09777772:
                    val_sum += 0.01612253
                else:
                    val_sum += 0.03759933
            else:
                if features[4] < 1.06649995:
                    val_sum += 0.01580990
                else:
                    val_sum += -0.00254745
        else:
            if features[6] < 0.05041923:
                if features[20] < 1.00000000:
                    val_sum += 0.02653197
                else:
                    val_sum += 0.02036971
            else:
                val_sum += 0.03605578

    # Tree 16
    if features[12] < -10648.00000000:
        if features[0] < 3.00000000:
            if features[5] < 0.93011117:
                if features[20] < 4.00000000:
                    val_sum += 0.00286382
                else:
                    val_sum += -0.04425779
            else:
                if features[13] < 2.00000000:
                    val_sum += 0.01181110
                else:
                    val_sum += -0.00318796
        else:
            if features[14] < 0.00718502:
                if features[5] < 0.95641023:
                    val_sum += 0.00097646
                else:
                    val_sum += -0.01491768
            else:
                if features[14] < 0.01387087:
                    val_sum += 0.01121638
                else:
                    val_sum += 0.02831361
    else:
        if features[4] < 1.06470585:
            if features[15] < 0.10976944:
                if features[14] < 0.02664262:
                    val_sum += 0.01984226
                else:
                    val_sum += 0.03181226
            else:
                if features[15] < 0.11761939:
                    val_sum += -0.02825687
                else:
                    val_sum += 0.01277291
        else:
            if features[4] < 1.08514285:
                if features[11] < 47.25000000:
                    val_sum += -0.00429049
                else:
                    val_sum += 0.01589064
            else:
                if features[5] < 0.97675675:
                    val_sum += 0.01273137
                else:
                    val_sum += 0.02776693

    # Tree 17
    if features[19] < 600000000.00000000:
        if features[0] < 3.00000000:
            if features[5] < 0.93011117:
                if features[14] < -0.00280164:
                    val_sum += 0.00636931
                else:
                    val_sum += -0.01908483
            else:
                if features[0] < 2.00000000:
                    val_sum += 0.00667679
                else:
                    val_sum += 0.01516962
        else:
            if features[6] < 0.01626164:
                if features[1] < 1.00000000:
                    val_sum += 0.00969998
                else:
                    val_sum += -0.00988075
            else:
                if features[6] < 0.02880559:
                    val_sum += 0.01471700
                else:
                    val_sum += 0.02952026
    else:
        if features[14] < 0.01600849:
            if features[5] < 0.93566662:
                if features[14] < 0.00160026:
                    val_sum += 0.00844602
                else:
                    val_sum += -0.02421186
            else:
                if features[6] < 0.01214472:
                    val_sum += 0.01584950
                else:
                    val_sum += 0.02181948
        else:
            if features[6] < 0.05708386:
                val_sum += 0.02640951
            else:
                val_sum += 0.03568480

    # Tree 18
    if features[12] < -10648.00000000:
        if features[6] < 0.01419873:
            if features[2] < 9.00000000:
                if features[12] < -13210.00000000:
                    val_sum += 0.00981061
                else:
                    val_sum += 0.01931102
            else:
                if features[1] < 1.00000000:
                    val_sum += 0.00734779
                else:
                    val_sum += -0.01188844
        else:
            if features[6] < 0.03413012:
                if features[6] < 0.02040727:
                    val_sum += 0.01105608
                else:
                    val_sum += 0.01985177
            else:
                if features[6] < 0.05708386:
                    val_sum += 0.02635264
                else:
                    val_sum += 0.03708313
    else:
        if features[6] < 0.01010008:
            if features[2] < 22.00000000:
                if features[2] < 8.00000000:
                    val_sum += 0.02405599
                else:
                    val_sum += 0.01482281
            else:
                if features[13] < 2.00000000:
                    val_sum += 0.00223007
                else:
                    val_sum += 0.01653263
        else:
            if features[6] < 0.05041923:
                if features[15] < 0.10869561:
                    val_sum += 0.02147755
                else:
                    val_sum += 0.00944061
            else:
                val_sum += 0.03343486

    # Tree 19
    if features[16] < 25130.00000000:
        if features[2] < 21.00000000:
            if features[5] < 0.98263156:
                if features[4] < 0.99771434:
                    val_sum += 0.02286497
                else:
                    val_sum += 0.01598038
            else:
                if features[14] < -0.00344515:
                    val_sum += 0.01715327
                else:
                    val_sum += 0.02661058
        else:
            if features[14] < 0.00718502:
                if features[4] < 1.07764709:
                    val_sum += 0.01403464
                else:
                    val_sum += 0.00357747
            else:
                if features[14] < 0.01491051:
                    val_sum += 0.01971747
                else:
                    val_sum += 0.02770955
    else:
        if features[2] < 9.00000000:
            if features[12] < -13210.00000000:
                if features[14] < -0.00257848:
                    val_sum += 0.00461989
                else:
                    val_sum += 0.01307738
            else:
                if features[15] < 0.05241092:
                    val_sum += 0.02577757
                else:
                    val_sum += 0.01442440
        else:
            if features[14] < 0.00718502:
                if features[14] < -0.00430902:
                    val_sum += 0.00457716
                else:
                    val_sum += -0.01110316
            else:
                if features[14] < 0.01387087:
                    val_sum += 0.00924835
                else:
                    val_sum += 0.02609013

    # Tree 20
    if features[7] < 0.00000005:
        if features[19] < -1538.46497000:
            if features[2] < 14.00000000:
                if features[8] < 10.00000000:
                    val_sum += 0.01691113
                else:
                    val_sum += 0.00998844
            else:
                if features[19] < -17500.14060000:
                    val_sum += -0.01810123
                else:
                    val_sum += 0.00287255
        else:
            if features[15] < 0.02992937:
                if features[15] < 0.02964896:
                    val_sum += 0.01990800
                else:
                    val_sum += 0.03346714
            else:
                if features[15] < 0.10976944:
                    val_sum += 0.01631550
                else:
                    val_sum += 0.00719778
    else:
        if features[2] < 9.00000000:
            if features[2] < 7.00000000:
                if features[4] < 1.07030308:
                    val_sum += 0.02418571
                else:
                    val_sum += 0.01091013
            else:
                if features[4] < 0.99965709:
                    val_sum += 0.00510318
                else:
                    val_sum += 0.01192200
        else:
            if features[1] < 1.00000000:
                if features[4] < 0.96918917:
                    val_sum += -0.00174559
                else:
                    val_sum += 0.01198566
            else:
                if features[2] < 16.00000000:
                    val_sum += -0.01418925
                else:
                    val_sum += -0.00256181

    # Tree 21
    if features[16] < 25048.00000000:
        if features[6] < 0.01010093:
            if features[2] < 22.00000000:
                if features[4] < 1.09777772:
                    val_sum += 0.01557817
                else:
                    val_sum += 0.03252188
            else:
                if features[4] < 1.06649995:
                    val_sum += 0.01555319
                else:
                    val_sum += -0.00365672
        else:
            if features[15] < 0.10869561:
                if features[6] < 0.05708386:
                    val_sum += 0.02167650
                else:
                    val_sum += 0.03528256
            else:
                if features[2] < 14.00000000:
                    val_sum += -0.02487121
                else:
                    val_sum += 0.01709292
    else:
        if features[1] < 1.00000000:
            if features[4] < 0.96918917:
                if features[15] < 0.02807415:
                    val_sum += -0.02647291
                else:
                    val_sum += 0.00544128
            else:
                if features[6] < 0.01112143:
                    val_sum += 0.01057584
                else:
                    val_sum += 0.02037503
        else:
            if features[6] < 0.00806437:
                if features[2] < 12.00000000:
                    val_sum += 0.01118055
                else:
                    val_sum += -0.01350066
            else:
                if features[14] < 0.00766032:
                    val_sum += 0.00082977
                else:
                    val_sum += 0.02094997

    # Tree 22
    if features[16] < 25048.00000000:
        if features[15] < 0.04162337:
            if features[15] < 0.02579977:
                if features[15] < 0.02560168:
                    val_sum += 0.01676502
                else:
                    val_sum += -0.02710327
            else:
                if features[17] < 0.26315790:
                    val_sum += 0.02460731
                else:
                    val_sum += 0.00281120
        else:
            if features[18] < 2.00000000:
                if features[15] < 0.08870489:
                    val_sum += 0.01835720
                else:
                    val_sum += 0.01071266
            else:
                if features[7] < 0.00520002:
                    val_sum += 0.01312660
                else:
                    val_sum += 0.00316521
    else:
        if features[0] < 3.00000000:
            if features[15] < 0.03991225:
                if features[18] < 3.00000000:
                    val_sum += 0.01339566
                else:
                    val_sum += -0.01339355
            else:
                if features[18] < 3.00000000:
                    val_sum += 0.00434337
                else:
                    val_sum += -0.01705879
        else:
            if features[1] < 1.00000000:
                if features[11] < 33.00000000:
                    val_sum += 0.00185681
                else:
                    val_sum += 0.01444176
            else:
                if features[18] < 1.00000000:
                    val_sum += 0.01572365
                else:
                    val_sum += -0.01251276

    # Tree 23
    if features[12] < -10648.00000000:
        if features[0] < 3.00000000:
            if features[2] < 56.00000000:
                if features[2] < 7.00000000:
                    val_sum += 0.01701084
                else:
                    val_sum += 0.00555378
            else:
                if features[11] < 12.75000000:
                    val_sum += -0.02154157
                else:
                    val_sum += -0.05194826
        else:
            if features[11] < 50.25000000:
                if features[2] < 28.00000000:
                    val_sum += -0.01353010
                else:
                    val_sum += 0.00233230
            else:
                if features[2] < 30.00000000:
                    val_sum += 0.00358426
                else:
                    val_sum += 0.02356344
    else:
        if features[2] < 26.00000000:
            if features[4] < 1.09885716:
                if features[2] < 8.00000000:
                    val_sum += 0.02303004
                else:
                    val_sum += 0.01610218
            else:
                if features[2] < 16.00000000:
                    val_sum += 0.01523091
                else:
                    val_sum += 0.04498795
        else:
            if features[4] < 1.05941176:
                if features[2] < 28.00000000:
                    val_sum += 0.02254166
                else:
                    val_sum += 0.01477282
            else:
                if features[2] < 28.00000000:
                    val_sum += -0.00614756
                else:
                    val_sum += 0.01704153

    # Tree 24
    if features[12] < -10648.00000000:
        if features[2] < 12.00000000:
            if features[4] < 1.09687495:
                if features[12] < -13210.00000000:
                    val_sum += 0.00988872
                else:
                    val_sum += 0.01888196
            else:
                val_sum += -0.01764773
        else:
            if features[1] < 1.00000000:
                if features[4] < 0.96918917:
                    val_sum += -0.01150781
                else:
                    val_sum += 0.01164967
            else:
                if features[14] < 0.00718502:
                    val_sum += -0.01043614
                else:
                    val_sum += 0.01821219
    else:
        if features[2] < 26.00000000:
            if features[4] < 1.09777772:
                if features[14] < 0.02145395:
                    val_sum += 0.01577014
                else:
                    val_sum += 0.02724235
            else:
                if features[14] < -0.00377448:
                    val_sum += 0.00832697
                else:
                    val_sum += 0.03793748
        else:
            if features[4] < 1.05485713:
                if features[2] < 28.00000000:
                    val_sum += 0.02307758
                else:
                    val_sum += 0.01409661
            else:
                if features[4] < 1.08514285:
                    val_sum += -0.00341521
                else:
                    val_sum += 0.02082934

    # Tree 25
    if features[16] < 25048.00000000:
        if features[6] < 0.00633992:
            if features[2] < 22.00000000:
                if features[5] < 1.03333342:
                    val_sum += 0.01325699
                else:
                    val_sum += 0.02809157
            else:
                if features[13] < 2.00000000:
                    val_sum += -0.00428541
                else:
                    val_sum += 0.01468372
        else:
            if features[6] < 0.05041923:
                if features[3] < 0.24300003:
                    val_sum += 0.01638212
                else:
                    val_sum += 0.02087450
            else:
                val_sum += 0.03245802
    else:
        if features[0] < 3.00000000:
            if features[5] < 0.93011117:
                if features[16] < 36376.00000000:
                    val_sum += 0.00447794
                else:
                    val_sum += -0.01738240
            else:
                if features[6] < 0.00908191:
                    val_sum += 0.00757502
                else:
                    val_sum += 0.01707639
        else:
            if features[1] < 1.00000000:
                if features[5] < 0.97435892:
                    val_sum += 0.00491465
                else:
                    val_sum += 0.01709863
            else:
                if features[6] < 0.01699986:
                    val_sum += -0.01236325
                else:
                    val_sum += 0.01989664

    # Tree 26
    if features[11] < 50.25000000:
        if features[18] < 1.00000000:
            if features[4] < 1.09749997:
                if features[20] < 3.00000000:
                    val_sum += 0.01151763
                else:
                    val_sum += 0.01908864
            else:
                val_sum += -0.01441651
        else:
            if features[14] < 0.00766032:
                if features[1] < 1.00000000:
                    val_sum += 0.00697465
                else:
                    val_sum += -0.00818288
            else:
                if features[14] < 0.02145395:
                    val_sum += 0.01204138
                else:
                    val_sum += 0.02952373
    else:
        if features[14] < 0.00261718:
            if features[15] < 0.05961607:
                if features[7] < 0.04199971:
                    val_sum += 0.01251634
                else:
                    val_sum += -0.00500467
            else:
                if features[15] < 0.06040836:
                    val_sum += -0.04466643
                else:
                    val_sum += 0.00510604
        else:
            if features[14] < 0.01600849:
                if features[15] < 0.10869561:
                    val_sum += 0.01843788
                else:
                    val_sum += 0.00617041
            else:
                if features[14] < 0.04267346:
                    val_sum += 0.02426195
                else:
                    val_sum += 0.03212575

    # Tree 27
    if features[12] < -10648.00000000:
        if features[1] < 1.00000000:
            if features[4] < 0.94455558:
                if features[6] < 0.00800054:
                    val_sum += -0.02758889
                else:
                    val_sum += 0.00882448
            else:
                if features[14] < 0.01252617:
                    val_sum += 0.01024941
                else:
                    val_sum += 0.02509663
        else:
            if features[2] < 12.00000000:
                if features[4] < 1.09485710:
                    val_sum += 0.01355981
                else:
                    val_sum += -0.02828385
            else:
                if features[6] < 0.01626005:
                    val_sum += -0.01067062
                else:
                    val_sum += 0.01733367
    else:
        if features[2] < 26.00000000:
            if features[4] < 1.09885716:
                if features[15] < 0.08790436:
                    val_sum += 0.01876674
                else:
                    val_sum += 0.00823068
            else:
                if features[2] < 16.00000000:
                    val_sum += 0.01251971
                else:
                    val_sum += 0.04147553
        else:
            if features[4] < 1.05485713:
                if features[14] < -0.00085033:
                    val_sum += 0.01336235
                else:
                    val_sum += 0.02299785
            else:
                if features[4] < 1.08424246:
                    val_sum += -0.00374828
                else:
                    val_sum += 0.01828233

    # Tree 28
    if features[6] < 0.01010093:
        if features[2] < 9.00000000:
            if features[2] < 7.00000000:
                if features[4] < 1.06242430:
                    val_sum += 0.01912325
                else:
                    val_sum += 0.00957662
            else:
                if features[6] < 0.00603601:
                    val_sum += 0.00710208
                else:
                    val_sum += 0.01422898
        else:
            if features[14] < -0.00416705:
                if features[1] < 1.00000000:
                    val_sum += 0.01363027
                else:
                    val_sum += 0.00265513
            else:
                if features[7] < 0.00199997:
                    val_sum += 0.00789977
                else:
                    val_sum += -0.01072401
    else:
        if features[6] < 0.01699986:
            if features[7] < 0.00000005:
                if features[6] < 0.01214472:
                    val_sum += 0.01266933
                else:
                    val_sum += 0.01778578
            else:
                if features[2] < 9.00000000:
                    val_sum += 0.02207349
                else:
                    val_sum += 0.00011656
        else:
            if features[6] < 0.05708386:
                if features[17] < 0.28571430:
                    val_sum += 0.01999895
                else:
                    val_sum += -0.00110224
            else:
                val_sum += 0.03482825

    # Tree 29
    if features[16] < 25048.00000000:
        if features[6] < 0.01200046:
            if features[4] < 1.09777772:
                if features[4] < 1.06545460:
                    val_sum += 0.01417241
                else:
                    val_sum += 0.00242708
            else:
                if features[20] < 4.00000000:
                    val_sum += 0.01354113
                else:
                    val_sum += 0.03780210
        else:
            if features[6] < 0.05708386:
                if features[3] < 0.24300003:
                    val_sum += 0.01664972
                else:
                    val_sum += 0.02276209
            else:
                val_sum += 0.03164757
    else:
        if features[0] < 3.00000000:
            if features[3] < 0.25000012:
                if features[3] < 0.24800015:
                    val_sum += 0.00507068
                else:
                    val_sum += 0.01385944
            else:
                if features[20] < 4.00000000:
                    val_sum += 0.00497623
                else:
                    val_sum += -0.02231251
        else:
            if features[6] < 0.01626005:
                if features[11] < 51.50000000:
                    val_sum += -0.01230334
                else:
                    val_sum += 0.00256923
            else:
                if features[6] < 0.02880559:
                    val_sum += 0.01233609
                else:
                    val_sum += 0.02713810

    # Tree 30
    if features[12] < -10860.00000000:
        if features[1] < 1.00000000:
            if features[4] < 0.96918917:
                if features[13] < 2.00000000:
                    val_sum += 0.00314194
                else:
                    val_sum += -0.04442695
            else:
                if features[14] < -0.02113055:
                    val_sum += 0.03975024
                else:
                    val_sum += 0.01050225
        else:
            if features[14] < 0.00919058:
                if features[18] < 1.00000000:
                    val_sum += 0.01012426
                else:
                    val_sum += -0.00970445
            else:
                if features[14] < 0.01491051:
                    val_sum += 0.01050654
                else:
                    val_sum += 0.02658073
    else:
        if features[14] < 0.00223959:
            if features[4] < 1.09885716:
                if features[4] < 1.06470585:
                    val_sum += 0.01410545
                else:
                    val_sum += 0.00534217
            else:
                if features[12] < -9816.00000000:
                    val_sum += 0.02110917
                else:
                    val_sum += 0.03760852
        else:
            if features[14] < 0.02948420:
                if features[15] < 0.10869561:
                    val_sum += 0.01909372
                else:
                    val_sum += 0.00414921
            else:
                val_sum += 0.02949067

    # Tree 31
    if features[16] < 25048.00000000:
        if features[6] < 0.01200046:
            if features[2] < 26.00000000:
                if features[4] < 1.09777772:
                    val_sum += 0.01350510
                else:
                    val_sum += 0.03024071
            else:
                if features[4] < 1.05941176:
                    val_sum += 0.01257989
                else:
                    val_sum += -0.00131433
        else:
            if features[6] < 0.03659170:
                if features[16] < 23781.00000000:
                    val_sum += 0.01754201
                else:
                    val_sum += 0.02739947
            else:
                if features[6] < 0.05708386:
                    val_sum += 0.02359437
                else:
                    val_sum += 0.03152793
    else:
        if features[0] < 3.00000000:
            if features[5] < 0.93011117:
                if features[16] < 37326.00000000:
                    val_sum += 0.00487484
                else:
                    val_sum += -0.01692783
            else:
                if features[6] < 0.00704836:
                    val_sum += 0.00576530
                else:
                    val_sum += 0.01391958
        else:
            if features[11] < 51.50000000:
                if features[5] < 0.95641023:
                    val_sum += 0.00159342
                else:
                    val_sum += -0.01347705
            else:
                if features[15] < 0.02701247:
                    val_sum += 0.02666488
                else:
                    val_sum += 0.00342301

    # Tree 32
    if features[12] < -10648.00000000:
        if features[0] < 3.00000000:
            if features[5] < 0.93011117:
                if features[20] < 4.00000000:
                    val_sum += 0.00083482
                else:
                    val_sum += -0.04572073
            else:
                if features[6] < 0.00765821:
                    val_sum += 0.00622891
                else:
                    val_sum += 0.01540040
        else:
            if features[5] < 0.95700002:
                if features[6] < 0.00908079:
                    val_sum += 0.00032628
                else:
                    val_sum += 0.01415849
            else:
                if features[13] < 2.00000000:
                    val_sum += -0.01349989
                else:
                    val_sum += 0.00472404
    else:
        if features[4] < 1.09885716:
            if features[6] < 0.00806839:
                if features[4] < 1.06470585:
                    val_sum += 0.01413299
                else:
                    val_sum += 0.00417710
            else:
                if features[6] < 0.05041923:
                    val_sum += 0.01634989
                else:
                    val_sum += 0.02810993
        else:
            if features[12] < -9816.00000000:
                val_sum += 0.01780293
            else:
                val_sum += 0.03848093

    # Tree 33
    if features[16] < 25048.00000000:
        if features[6] < 0.01200046:
            if features[4] < 1.06470585:
                if features[20] < 3.00000000:
                    val_sum += 0.00936671
                else:
                    val_sum += 0.01722235
            else:
                if features[4] < 1.08685708:
                    val_sum += -0.00220155
                else:
                    val_sum += 0.01817971
        else:
            if features[15] < 0.10840105:
                if features[6] < 0.03413012:
                    val_sum += 0.01792317
                else:
                    val_sum += 0.02702434
            else:
                if features[15] < 0.11086477:
                    val_sum += -0.01630500
                else:
                    val_sum += 0.01233696
    else:
        if features[6] < 0.01010093:
            if features[1] < 1.00000000:
                if features[4] < 0.96918917:
                    val_sum += -0.00802279
                else:
                    val_sum += 0.00904074
            else:
                if features[0] < 3.00000000:
                    val_sum += 0.00229924
                else:
                    val_sum += -0.01185874
        else:
            if features[6] < 0.02040727:
                if features[0] < 3.00000000:
                    val_sum += 0.01331851
                else:
                    val_sum += 0.00214767
            else:
                if features[6] < 0.03413012:
                    val_sum += 0.01708108
                else:
                    val_sum += 0.02906902

    # Tree 34
    if features[12] < -10648.00000000:
        if features[6] < 0.01419873:
            if features[18] < 1.00000000:
                if features[12] < -13210.00000000:
                    val_sum += 0.00651547
                else:
                    val_sum += 0.01800095
            else:
                if features[1] < 1.00000000:
                    val_sum += 0.00780376
                else:
                    val_sum += -0.01008855
        else:
            if features[6] < 0.03177876:
                if features[3] < 0.09700012:
                    val_sum += 0.00444473
                else:
                    val_sum += 0.01650313
            else:
                if features[6] < 0.05708386:
                    val_sum += 0.02270792
                else:
                    val_sum += 0.03445582
    else:
        if features[6] < 0.00633992:
            if features[18] < 2.00000000:
                if features[18] < 1.00000000:
                    val_sum += 0.02094905
                else:
                    val_sum += 0.01139467
            else:
                if features[6] < 0.00603681:
                    val_sum += 0.00532653
                else:
                    val_sum += -0.01830350
        else:
            if features[6] < 0.05041923:
                if features[3] < 0.20000029:
                    val_sum += 0.01399664
                else:
                    val_sum += 0.01931619
            else:
                val_sum += 0.02853357

    # Tree 35
    if features[12] < -10648.00000000:
        if features[0] < 3.00000000:
            if features[15] < 0.03991225:
                if features[4] < 1.08228576:
                    val_sum += 0.01172317
                else:
                    val_sum += -0.02194894
            else:
                if features[2] < 100.00000000:
                    val_sum += 0.00255352
                else:
                    val_sum += -0.03225449
        else:
            if features[1] < 1.00000000:
                if features[4] < 0.99142855:
                    val_sum += -0.00374644
                else:
                    val_sum += 0.01362304
            else:
                if features[2] < 28.00000000:
                    val_sum += -0.01188257
                else:
                    val_sum += 0.00439523
    else:
        if features[2] < 26.00000000:
            if features[4] < 1.09885716:
                if features[15] < 0.08870489:
                    val_sum += 0.01680516
                else:
                    val_sum += 0.00695612
            else:
                if features[2] < 16.00000000:
                    val_sum += 0.01295016
                else:
                    val_sum += 0.03958925
        else:
            if features[7] < 0.00320000:
                if features[4] < 0.99771434:
                    val_sum += 0.02329220
                else:
                    val_sum += 0.01270339
            else:
                if features[2] < 28.00000000:
                    val_sum += -0.00629201
                else:
                    val_sum += 0.01582096

    # Tree 36
    if features[16] < 25048.00000000:
        if features[15] < 0.05015041:
            if features[19] < 471.69818100:
                if features[2] < 19.00000000:
                    val_sum += 0.03384991
                else:
                    val_sum += 0.02166661
            else:
                if features[7] < 0.01200001:
                    val_sum += 0.01766948
                else:
                    val_sum += 0.00485365
        else:
            if features[2] < 26.00000000:
                if features[15] < 0.08790436:
                    val_sum += 0.01457096
                else:
                    val_sum += 0.00727283
            else:
                if features[2] < 28.00000000:
                    val_sum += -0.00038879
                else:
                    val_sum += 0.01521469
    else:
        if features[1] < 1.00000000:
            if features[5] < 0.94461536:
                if features[2] < 29.00000000:
                    val_sum += 0.00633736
                else:
                    val_sum += -0.02485224
            else:
                if features[2] < 30.00000000:
                    val_sum += 0.01099854
                else:
                    val_sum += 0.01826242
        else:
            if features[3] < 0.20000029:
                if features[15] < 0.02714438:
                    val_sum += 0.00579191
                else:
                    val_sum += -0.01195428
            else:
                if features[15] < 0.05910167:
                    val_sum += 0.01117359
                else:
                    val_sum += -0.00102673

    # Tree 37
    if features[12] < -10648.00000000:
        if features[1] < 1.00000000:
            if features[4] < 0.96918917:
                if features[13] < 2.00000000:
                    val_sum += 0.00142965
                else:
                    val_sum += -0.03632794
            else:
                if features[14] < 0.00551502:
                    val_sum += 0.01015599
                else:
                    val_sum += 0.02106002
        else:
            if features[18] < 1.00000000:
                if features[4] < 1.08555555:
                    val_sum += 0.01348733
                else:
                    val_sum += -0.01477147
            else:
                if features[14] < 0.00718502:
                    val_sum += -0.00929455
                else:
                    val_sum += 0.01633302
    else:
        if features[14] < 0.01600849:
            if features[18] < 2.00000000:
                if features[14] < 0.01491051:
                    val_sum += 0.01541814
                else:
                    val_sum += -0.02276155
            else:
                if features[4] < 1.07212126:
                    val_sum += 0.01285214
                else:
                    val_sum += 0.00271928
        else:
            if features[14] < 0.04267346:
                if features[4] < 0.97729725:
                    val_sum += 0.01420661
                else:
                    val_sum += 0.02096027
            else:
                val_sum += 0.02796144

    # Tree 38
    if features[12] < -10648.00000000:
        if features[2] < 9.00000000:
            if features[12] < -12271.00000000:
                if features[6] < 0.00704928:
                    val_sum += 0.00606463
                else:
                    val_sum += 0.01346980
            else:
                if features[15] < 0.05232863:
                    val_sum += 0.02461666
                else:
                    val_sum += 0.01287976
        else:
            if features[1] < 1.00000000:
                if features[5] < 0.89842105:
                    val_sum += -0.00791629
                else:
                    val_sum += 0.00949661
            else:
                if features[6] < 0.01626005:
                    val_sum += -0.00904937
                else:
                    val_sum += 0.01543782
    else:
        if features[6] < 0.01200046:
            if features[2] < 23.00000000:
                if features[5] < 0.97333336:
                    val_sum += 0.00911057
                else:
                    val_sum += 0.01682229
            else:
                if features[14] < -0.00249870:
                    val_sum += 0.00997658
                else:
                    val_sum += -0.00196992
        else:
            if features[15] < 0.10869561:
                if features[6] < 0.03659170:
                    val_sum += 0.01725059
                else:
                    val_sum += 0.02493391
            else:
                if features[15] < 0.11402505:
                    val_sum += -0.01029031
                else:
                    val_sum += 0.01365815

    # Tree 39
    if features[16] < 25048.00000000:
        if features[2] < 21.00000000:
            if features[15] < 0.08790436:
                if features[3] < 0.19999993:
                    val_sum += 0.01508049
                else:
                    val_sum += 0.01975148
            else:
                if features[14] < 0.00580741:
                    val_sum += 0.01077290
                else:
                    val_sum += -0.01268269
        else:
            if features[14] < 0.00617226:
                if features[20] < 3.00000000:
                    val_sum += 0.00902000
                else:
                    val_sum += 0.00032908
            else:
                if features[15] < 0.05015041:
                    val_sum += 0.02100198
                else:
                    val_sum += 0.01378273
    else:
        if features[0] < 3.00000000:
            if features[2] < 100.00000000:
                if features[15] < 0.04054324:
                    val_sum += 0.01071684
                else:
                    val_sum += 0.00167028
            else:
                if features[14] < -0.00166068:
                    val_sum += -0.02147266
                else:
                    val_sum += -0.04607674
        else:
            if features[11] < 43.25000000:
                if features[16] < 42198.00000000:
                    val_sum += -0.01386826
                else:
                    val_sum += -0.00038727
            else:
                if features[15] < 0.02714438:
                    val_sum += 0.02142378
                else:
                    val_sum += 0.00021861

    # Tree 40
    if features[6] < 0.00806437:
        if features[0] < 3.00000000:
            if features[2] < 28.00000000:
                if features[5] < 0.93011117:
                    val_sum += -0.00171597
                else:
                    val_sum += 0.00969888
            else:
                if features[14] < -0.00018671:
                    val_sum += -0.00397822
                else:
                    val_sum += -0.04846036
        else:
            if features[14] < -0.00416705:
                if features[14] < -0.01789844:
                    val_sum += -0.03583850
                else:
                    val_sum += 0.00687118
            else:
                if features[5] < 0.95789480:
                    val_sum += -0.00081742
                else:
                    val_sum += -0.01216637
    else:
        if features[6] < 0.01626005:
            if features[11] < 34.25000000:
                if features[0] < 3.00000000:
                    val_sum += 0.01062556
                else:
                    val_sum += -0.00420558
            else:
                if features[2] < 7.00000000:
                    val_sum += 0.02080293
                else:
                    val_sum += 0.01065020
        else:
            if features[6] < 0.05708386:
                if features[2] < 16.00000000:
                    val_sum += 0.01240083
                else:
                    val_sum += 0.01931040
            else:
                if features[0] < 2.00000000:
                    val_sum += 0.02134229
                else:
                    val_sum += 0.03292138

    # Tree 41
    if features[12] < -10648.00000000:
        if features[6] < 0.01626005:
            if features[1] < 1.00000000:
                if features[4] < 0.96918917:
                    val_sum += -0.00659665
                else:
                    val_sum += 0.00955181
            else:
                if features[18] < 1.00000000:
                    val_sum += 0.00915357
                else:
                    val_sum += -0.00948544
        else:
            if features[6] < 0.03413012:
                if features[11] < 26.25000000:
                    val_sum += 0.01001417
                else:
                    val_sum += 0.01749890
            else:
                if features[6] < 0.05708386:
                    val_sum += 0.02231229
                else:
                    val_sum += 0.03257128
    else:
        if features[6] < 0.00806839:
            if features[18] < 2.00000000:
                if features[4] < 1.09777772:
                    val_sum += 0.01202737
                else:
                    val_sum += 0.03040467
            else:
                if features[4] < 1.08787882:
                    val_sum += 0.00207794
                else:
                    val_sum += 0.01632378
        else:
            if features[15] < 0.10869561:
                if features[6] < 0.02880559:
                    val_sum += 0.01574544
                else:
                    val_sum += 0.02297445
            else:
                if features[15] < 0.11389524:
                    val_sum += -0.03070176
                else:
                    val_sum += 0.01368738

    # Tree 42
    if features[12] < -10648.00000000:
        if features[1] < 1.00000000:
            if features[4] < 0.96918917:
                if features[5] < 0.93833327:
                    val_sum += 0.00030933
                else:
                    val_sum += -0.03625213
            else:
                if features[5] < 0.87435895:
                    val_sum += -0.01830885
                else:
                    val_sum += 0.00976242
        else:
            if features[18] < 1.00000000:
                if features[4] < 1.09485710:
                    val_sum += 0.01130921
                else:
                    val_sum += -0.02164478
            else:
                if features[14] < 0.00766032:
                    val_sum += -0.00834457
                else:
                    val_sum += 0.01516437
    else:
        if features[14] < 0.01600849:
            if features[18] < 2.00000000:
                if features[4] < 1.09818184:
                    val_sum += 0.01401972
                else:
                    val_sum += 0.03040148
            else:
                if features[4] < 1.07212126:
                    val_sum += 0.01211821
                else:
                    val_sum += 0.00334893
        else:
            if features[14] < 0.04267346:
                if features[5] < 0.98948574:
                    val_sum += 0.01745353
                else:
                    val_sum += 0.02230061
            else:
                val_sum += 0.02851537

    # Return raw regression sum
    return val_sum

def construct_features(cand, snapshot, now, session_mean_return=0.0):
    ctx = cand['ctx']
    si, sj = cand['orig_i'], cand['orig_j']
    c1, c2 = ctx['call_oids'][si], ctx['call_oids'][sj]
    p1, p2 = ctx['put_oids'][si], ctx['put_oids'][sj]
    
    c1_t, c2_t = snapshot[c1], snapshot[c2]
    p1_t, p2_t = snapshot[p1], snapshot[p2]
    
    # 2. Extract underlying price (S_t) via put-call parity: S ~ K + call_mid - put_mid
    c_mid_si = (c1_t['a1'] + c1_t['b1']) / 2.0
    p_mid_si = (p1_t['a1'] + p1_t['b1']) / 2.0
    underlying_price = float(ctx['strikes'][si]) + c_mid_si - p_mid_si
    
    # 3. Spreads
    c1_spread = c1_t['a1'] - c1_t['b1']
    c2_spread = c2_t['a1'] - c2_t['b1']
    p1_spread = p1_t['a1'] - p1_t['b1']
    p2_spread = p2_t['a1'] - p2_t['b1']
    spread_pct = (c1_spread + c2_spread + p1_spread + p2_spread) / cand['payout']
    
    # 4. Volumes
    vol_c1 = c1_t['a1_v'] if cand['type'] == 'Long' else c1_t['b1_v']
    vol_c2 = c2_t['b1_v'] if cand['type'] == 'Long' else c2_t['a1_v']
    vol_p2 = p2_t['a1_v'] if cand['type'] == 'Long' else p2_t['b1_v']
    vol_p1 = p1_t['b1_v'] if cand['type'] == 'Long' else p1_t['a1_v']
    
    min_entry_vol = min(vol_c1, vol_c2, vol_p2, vol_p1)
    mean_leg_volume = (vol_c1 + vol_c2 + vol_p2 + vol_p1) / 4.0
    
    min_bid_vol = min(c1_t['b1_v'], c2_t['b1_v'], p1_t['b1_v'], p2_t['b1_v'])
    min_ask_vol = min(c1_t['a1_v'], c2_t['a1_v'], p1_t['a1_v'], p2_t['a1_v'])
    
    # 5. Time elements
    time_of_day = (now.hour * 3600 + now.minute * 60 + now.second + now.microsecond / 1e6) - 34200.0
    now_ts = int(now.timestamp())
    t1, t2, t3, t4 = c1_t['time'], c2_t['time'], p1_t['time'], p2_t['time']
    max_leg_age = float(max(t1, t2, t3, t4) - min(t1, t2, t3, t4))

    und = ctx['underlying']
    underlying_val = 1.0 if "510300" in und else (2.0 if "510500" in und else 3.0)

    entry_return_vs_session_mean = float(cand['ret'] - session_mean_return)
    strike_width_normalized = float(cand['payout'] / underlying_price)
    time_to_close_seconds = 14400.0 - float(time_of_day)
    bid_ask_imbalance = float((min_ask_vol - min_bid_vol) / (min_ask_vol + min_bid_vol + 1e-8))
    
    dte = float(ctx['dte'])
    dte_bucket = 0.0 if dte <= 10.0 else (1.0 if dte <= 20.0 else (2.0 if dte <= 40.0 else 3.0))
    volume_to_spread_ratio = float(min_entry_vol / (spread_pct + 1e-8))
    day_of_week = float(now.weekday())
    freshness_score = float(math.exp(-max_leg_age / 2.0))

    features = [
        underlying_val,                               # f0: underlying
        1.0 if cand['type'] == 'Long' else 0.0,       # f1: is_long_box
        float(ctx['dte']),                            # f2: dte
        float(cand['payout']),                         # f3: strike_width
        float(underlying_price / ctx['strikes'][si]), # f4: moneyness_lo
        float(underlying_price / ctx['strikes'][sj]), # f5: moneyness_hi
        float(cand['ret']),                           # f6: entry_return
        float(spread_pct),                            # f7: spread_pct
        float(min_entry_vol),                         # f8: min_entry_vol
        float(min_bid_vol),                           # f9: min_bid_vol
        float(min_ask_vol),                           # f10: min_ask_vol
        float(mean_leg_volume),                       # f11: mean_leg_volume
        float(time_of_day),                           # f12: time_of_day_seconds
        float(ctx.get('near_level', 1)),              # f13: near_level
        entry_return_vs_session_mean,                 # f14: entry_return_vs_session_mean
        strike_width_normalized,                       # f15: strike_width_normalized
        time_to_close_seconds,                        # f16: time_to_close_seconds
        bid_ask_imbalance,                            # f17: bid_ask_imbalance
        dte_bucket,                                   # f18: dte_bucket
        volume_to_spread_ratio,                       # f19: volume_to_spread_ratio
        day_of_week,                                  # f20: day_of_week
        freshness_score                               # f21: freshness_score
    ]
    return features


_CST = timezone(timedelta(hours=8))

def _evaluate_boxes_inner(C):
    eval_start = time.perf_counter()
    now = datetime.datetime.now(tz=_CST)
    now_ts = int(now.timestamp())

    A._eval_count = getattr(A, '_eval_count', 0) + 1

    # Thread-safe deep copy of tick data snapshot to avoid races with _update_tick_data
    with A.data_lock:
        snapshot = {sym: dict(td) for sym, td in A.tick_data.items()}
        _prune_closed_positions()  # Remove closed/errored positions under the same lock
    _check_exits(snapshot, now_ts, C)

    trade_candidates = []
    global_best_cand = None

    for ctx_idx in range(len(A.ctx_list)):
        l_cand, s_cand = _evaluate_context(ctx_idx, snapshot, now_ts, now, C)
        for cand in [l_cand, s_cand]:
            if cand:
                if global_best_cand is None or cand['ret'] > global_best_cand['ret']:
                    global_best_cand = cand
                if cand['ret'] >= MIN_RETURN:
                    # Construct features and evaluate via compiled XGBoost model
                    feats = construct_features(cand, snapshot, now,
                                                 getattr(A, 'session_mean_return', 0.0) or 0.0)
                    prob = predict_xgboost_probability(feats)
                    # Update rolling session mean (EMA) with all qualifying returns
                    sess = getattr(A, 'session_mean_return', None)
                    if sess is None:
                        A.session_mean_return = cand['ret']
                    else:
                        A.session_mean_return = 0.9 * sess + 0.1 * cand['ret']
                    if prob >= XGB_THRESHOLD:
                        cand['utility'] = prob
                        # Store min_entry_vol for dynamic sizing (same as in construct_features)
                        si, sj = cand['orig_i'], cand['orig_j']
                        cand_ctx = cand['ctx']
                        c1_t, c2_t = snapshot[cand_ctx['call_oids'][si]], snapshot[cand_ctx['call_oids'][sj]]
                        p1_t, p2_t = snapshot[cand_ctx['put_oids'][si]], snapshot[cand_ctx['put_oids'][sj]]
                        if cand['type'] == 'Long':
                            vols = [c1_t['a1_v'], c2_t['b1_v'], p2_t['a1_v'], p1_t['b1_v']]
                        else:
                            vols = [c1_t['b1_v'], c2_t['a1_v'], p2_t['b1_v'], p1_t['a1_v']]
                        cand['min_entry_vol'] = min(vols)
                        trade_candidates.append(cand)

    # Logging best trade of the second
    if global_best_cand and now_ts > A.last_log_ts:
        hz = getattr(A, '_eval_count', 0)
        A._eval_count = 0
        A.last_log_ts = now_ts
        ctx = global_best_cand['ctx']
        dte = max(ctx['dte'], 1)
        ts_str = now.strftime('%H:%M:%S')
        lbl = "Cost" if global_best_cand['type'] == 'Long' else "Credit"
        val = global_best_cand['cost']
        latency_ms = ""
        if A.latency_samples:
            recent = sorted(A.latency_samples[-100:])
            median_ms = recent[len(recent) // 2] * 1000
            latency_ms = f" Latency={median_ms:.0f}ms"
        A.log_queue.append(f"[{ts_str}] Best {global_best_cand['type']} [{ctx['underlying']}] "
                           f"DTE={dte} K{ctx['strikes'][global_best_cand['orig_i']]:.2f}/{ctx['strikes'][global_best_cand['orig_j']]:.2f} "
                           f"{lbl}={val:.4f} Ret={global_best_cand['ret']*100:.2f}% SimCash={A.sim_cash:.0f} Hz={hz}{latency_ms}")

    if not trade_candidates:
        return

    # Sort by predicted utility descending to prioritize lower-risk, faster realizers
    trade_candidates.sort(key=lambda x: x['utility'], reverse=True)
    
    # Try to place order on the best one
    ts_str = now.strftime('%H:%M:%S')
    
    for best_cand in trade_candidates:
        ctx_idx = best_cand['ctx_idx']
        ctx = best_cand['ctx']
        orig_i = best_cand['orig_i']
        orig_j = best_cand['orig_j']
        dte = max(ctx['dte'], 1)
        underlying = ctx['underlying']

        # Per-underlying position limit check
        undl_count = A.positions_per_underlying.get(underlying, 0)
        if undl_count >= MAX_POSITIONS_PER_UNDERLYING:
            continue

        # Global max open sets check (each set = 4 contracts/legs)
        if len(A.open_pos_set) >= MAX_OPEN_SETS:
            continue

        if best_cand['type'] == 'Long':
            l_cost = best_cand['cost']
            l_payout = best_cand['payout']
            l_ret = best_cand['ret']
            l_ann = best_cand['ann']

            already_in = (ctx_idx, 'LongBox') in A.open_pos_set
            cost_rmb_per = l_cost * CONTRACT_MULTIPLIER
            real_cash = get_real_available_cash(C)
            min_leg_vol = best_cand.get('min_entry_vol', MIN_VOL)
            contract_size = compute_dynamic_size(min_leg_vol, real_cash, cost_rmb_per)
            cost_rmb = cost_rmb_per * contract_size
            
            if not already_in and real_cash - cost_rmb >= MIN_CASH_THRESHOLD:
                with A.data_lock:
                    A.local_available_cash -= cost_rmb
                    A.sim_cash -= cost_rmb
                    A.positions_per_underlying[underlying] = undl_count + 1
                    A.open_pos_set.add((ctx_idx, 'LongBox'))
                    A.positions.append({
                        'pos_type': 'LongBox',
                        'ctx_idx': ctx_idx,
                        'strike_i': orig_i,
                        'strike_j': orig_j,
                        'entry_cost': l_cost,
                        'payout': l_payout,
                        'margin_rmb': 0.0,
                        'dte_at_entry': dte,
                        'entry_time': now_ts,
                        'state': 'Open',
                        'contract_size': contract_size,
                    })
                A.log_queue.append(f"[{ts_str}] >>> ENTER LongBox [{underlying}] K{ctx['strikes'][orig_i]:.2f}/{ctx['strikes'][orig_j]:.2f} "
                      f"size={contract_size} cost={l_cost:.4f} payout={l_payout:.4f} ann={l_ann*100:.2f}%  "
                      f"Cash={real_cash:.0f} SimCash={A.sim_cash:.0f} Pos={len(A.positions)}")
                
                prices = {
                    'c1_ask': best_cand['c1_ask'],
                    'c2_bid': best_cand['c2_bid'],
                    'p2_ask': best_cand['p2_ask'],
                    'p1_bid': best_cand['p1_bid']
                }
                _place_box_orders(C, ctx, orig_i, orig_j, prices, l_cost, l_payout, l_ret, l_ann, now, is_long=True, eval_start=eval_start, contract_size=contract_size)
                break # Hit and run: take the best one and stop searching this tick
                
        elif best_cand['type'] == 'Short':
            s_credit = best_cand['cost']
            s_payout = best_cand['payout']
            s_ret = best_cand['ret']
            s_ann = best_cand['ann']

            already_in = (ctx_idx, 'ShortBox') in A.open_pos_set
            margin_rmb_per = 2.0 * s_payout * CONTRACT_MULTIPLIER
            real_cash = get_real_available_cash(C)
            min_leg_vol = best_cand.get('min_entry_vol', MIN_VOL)
            contract_size = compute_dynamic_size(min_leg_vol, real_cash, margin_rmb_per)
            margin_rmb = margin_rmb_per * contract_size
            
            if not already_in and real_cash - margin_rmb >= MIN_CASH_THRESHOLD:
                with A.data_lock:
                    A.local_available_cash -= margin_rmb
                    gain_rmb = s_credit * CONTRACT_MULTIPLIER * contract_size
                    A.sim_cash -= (margin_rmb - gain_rmb)
                    A.positions_per_underlying[underlying] = undl_count + 1
                    A.open_pos_set.add((ctx_idx, 'ShortBox'))
                    A.positions.append({
                        'pos_type': 'ShortBox',
                        'ctx_idx': ctx_idx,
                        'strike_i': orig_i,
                        'strike_j': orig_j,
                        'entry_cost': s_credit,
                        'payout': s_payout,
                        'margin_rmb': margin_rmb,
                        'dte_at_entry': dte,
                        'entry_time': now_ts,
                        'state': 'Open',
                        'contract_size': contract_size,
                    })
                A.log_queue.append(f"[{ts_str}] >>> ENTER ShortBox [{underlying}] K{ctx['strikes'][orig_i]:.2f}/{ctx['strikes'][orig_j]:.2f} "
                      f"size={contract_size} gain={s_credit:.4f} payout={s_payout:.4f} ann={s_ann*100:.2f}%  "
                      f"Cash={real_cash:.0f} SimCash={A.sim_cash:.0f} Pos={len(A.positions)}")
                
                prices = {
                    'c1_bid': best_cand['c1_bid'],
                    'c2_ask': best_cand['c2_ask'],
                    'p2_bid': best_cand['p2_bid'],
                    'p1_ask': best_cand['p1_ask']
                }
                _place_box_orders(C, ctx, orig_i, orig_j, prices, s_credit, s_payout, s_ret, s_ann, now, is_long=False, eval_start=eval_start, contract_size=contract_size)
                break # Hit and run: take the best one and stop searching this tick


def _evaluate_boxes(C):
    try:
        _evaluate_boxes_inner(C)
    except Exception as e:
        import traceback
        A.log_queue.append(f"[_evaluate_boxes CRASH] {e}")
        # We still want to see the traceback in the console immediately for crashes
        traceback.print_exc()
    finally:
        if hasattr(A, 'log_queue') and A.log_queue:
            for msg in A.log_queue:
                print(msg)
            A.log_queue.clear()


def init(C):
    print(f"zhongjin_multi init stockcode={C.stockcode}  market={C.market}")

    # Set account if QMT framework hasn't already injected it
    if not getattr(A, 'acct', None):
        A.acct = DEFAULT_ACCT
    if not getattr(A, 'acct_type', None):
        A.acct_type = DEFAULT_ACCT_TYPE
    print(f"Using account: {A.acct} (type={A.acct_type})")

    symbols = _build_options_map(C)

    if not symbols:
        print("WARNING: No option contracts loaded. Strategy will not trade.")
        A.symbols = []
        return

    A.symbols = symbols
    A.sim_cash = INITIAL_CASH
    A.log_queue = []
    A.last_log_ts = 0
    A.latency_samples = []
    A.pending_box_verifications = []
    A.failed_boxes = {}
    A.session_mean_return = None  # Rolling EMA of observed qualifying returns for XGB feature f14

    # Pre-initialise virtual cash so _sync_broker_positions can adjust them
    A.local_available_cash = INITIAL_CASH
    A.last_cash_sync_time = 0

    # Initial tick update so we have live prices for position sync
    _update_tick_data(C, A.symbols)

    # Detect and import any existing box positions held at the broker
    # (from prior runs or manual trades) so _check_exits can manage them.
    _sync_broker_positions(C)

    # Flush sync log messages
    if A.log_queue:
        for msg in A.log_queue:
            print(msg)
        A.log_queue.clear()

    print(f"Ready {len(symbols)} contracts across {len(TARGET_UNDERLYINGS)} underlyings. "
          f"min_ret={MIN_RETURN*100:.2f}% xgb_thr={XGB_THRESHOLD} "
          f"MAX_ORDER={MAX_ORDER} "
          f"MAX_POS_PER_UNDERLYING={MAX_POSITIONS_PER_UNDERLYING} MAX_OPEN_SETS={MAX_OPEN_SETS} SimCash={A.sim_cash:.0f}")


def handlebar(C):
    if not hasattr(A, 'symbols') or not A.symbols:
        return

    if not C.is_last_bar():
        return

    CST = timezone(timedelta(hours=8))
    now = datetime.datetime.now(tz=CST)
    hm = int(now.strftime('%H%M%S'))
    
    # ETF Options trading hours: 09:30-11:29 and 13:00-14:59 (No placing Order At the last minute)
    if not (93010 <= hm <= 112800 or 130010 <= hm <= 145800):
        return

    _update_tick_data(C, A.symbols)
    _evaluate_boxes(C)
    _verify_pending_box_fills(C)

    if hasattr(A, 'latency_samples') and A.latency_samples:
        recent = sorted(A.latency_samples[-100:])
        median_ms = recent[len(recent) // 2] * 1000
        if median_ms > LATENCY_WARN_MEDIAN_S * 1000:
            now_str = now.strftime('%H:%M:%S')
            mn = recent[0] * 1000
            mx = recent[-1] * 1000
            print(f"[{now_str}] LATENCY WARNING median={median_ms:.0f}ms min={mn:.0f}ms max={mx:.0f}ms (n={len(recent)})")

def order_callback(C, orderInfo):
    status = getattr(orderInfo, 'm_nOrderStatus', 0)
    symbol = getattr(orderInfo, 'm_strInstrumentID', '')
    volume = getattr(orderInfo, 'm_nVolume', 0)
    price = getattr(orderInfo, 'm_dPrice', 0)
    remark = getattr(orderInfo, 'm_strRemark', '')

    now_str = datetime.datetime.now().strftime('%H:%M:%S')

    if status == 54 or status == 57:
        action = "CANCELED" if status == 54 else f"REJECTED: {getattr(orderInfo, 'm_strRejectReason', 'Unknown')}"
        print(f"[{now_str}] {action}: {symbol} {volume}@{price} (remark: {remark})")
        
        if remark.startswith("zj_open_") and hasattr(A, 'order_remark_to_box'):
            box_key = A.order_remark_to_box.get(remark)
            if box_key:
                with A.data_lock:
                    # Update virtual position state instead of removing
                    for p in A.positions:
                        ptype = "LONG" if p['pos_type'] == 'LongBox' else "SHORT"
                        ctx = A.ctx_list[p['ctx_idx']]
                        pk = (ctx['underlying'], ctx['expiry'], ctx['strikes'][p['strike_i']], ctx['strikes'][p['strike_j']], ptype)
                        if pk == box_key:
                            if p.get('state') != 'Errored':
                                p['state'] = 'Errored'
                                if not hasattr(A, 'failed_boxes'):
                                    A.failed_boxes = {}
                                A.failed_boxes[box_key] = time.time()
                                if box_key in A.placed_boxes:
                                    A.placed_boxes.remove(box_key)
                                # Restore virtual cash reserves freed by the failed position
                                cs = p.get('contract_size', 1)
                                if p['pos_type'] == 'LongBox':
                                    restore = p['entry_cost'] * CONTRACT_MULTIPLIER * cs
                                else:
                                    restore = p.get('margin_rmb', 0.0)
                                A.sim_cash += restore
                                A.local_available_cash += restore
                                # Free the per-underlying slot so new positions can be opened
                                _decrement_underlying_count(ctx['underlying'])
                                print(f"[{now_str}] STATE UPDATE: Marked position for {box_key} as 'Errored' due to leg failure. Restored {restore:.0f} RMB.")
                            break


def deal_callback(C, dealInfo):
    symbol = getattr(dealInfo, 'm_strInstrumentID', '')
    volume = getattr(dealInfo, 'm_nVolume', 0)
    price = getattr(dealInfo, 'm_dPrice', 0)
    now_str = datetime.datetime.now().strftime('%H:%M:%S')
    print(f"[{now_str}] DEAL: {symbol} {volume}@{price}")


def stop(C):
    print('strategy stopped')
