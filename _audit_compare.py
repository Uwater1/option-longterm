"""Compare backtest win rate: WRONG (inst strike/mult) vs CORRECT (opt daily strike/mult)."""
import pandas as pd
import numpy as np
import pandas_ta as ta
import math

SPREAD_HALF    = 0.02
COMMISSION     = 2.0
EXERCISE_COST  = 0.6
ETF_SHARES     = 20_000
NUM_CONTRACTS  = 1
RISK_FREE      = 0.02
PUT_BUY_LEVEL  = 1

def load_data_correct():
    """Load data using OPT's daily strike_price and contract_multiplier (CORRECT)."""
    inst = pd.read_parquet('./data/300ETF_instruments.parquet')
    opt = pd.read_parquet('./data/300ETF_historical_prices.parquet')
    etf = pd.read_parquet('./data/510300_1d.parquet')
    
    inst['maturity_date'] = pd.to_datetime(inst['maturity_date'])
    opt['date'] = pd.to_datetime(opt['date'])
    etf['date'] = pd.to_datetime(etf['date'])
    
    # Only get maturity_date and option_type from instruments
    inst_slim = inst[['order_book_id', 'maturity_date', 'option_type']].drop_duplicates()
    opt = opt.merge(inst_slim, on='order_book_id', how='left')
    
    # Use opt's OWN strike_price and contract_multiplier (daily-correct values)
    # opt already has these columns from the parquet
    
    etf = etf.set_index('date').sort_index()
    etf['rsi14'] = ta.rsi(etf['close'], length=14)
    bb = ta.bbands(etf['close'], length=20, std=2)
    if bb is not None:
        etf['bbu20'] = bb['BBU_20_2.0_2.0']
    else:
        etf['bbu20'] = np.nan
    
    return opt, etf

def load_data_current():
    """Load data using INST strike_price and contract_multiplier (CURRENT/BUGGY)."""
    inst = pd.read_parquet('./data/300ETF_instruments.parquet')
    opt = pd.read_parquet('./data/300ETF_historical_prices.parquet')
    etf = pd.read_parquet('./data/510300_1d.parquet')
    
    inst['maturity_date'] = pd.to_datetime(inst['maturity_date'])
    opt['date'] = pd.to_datetime(opt['date'])
    etf['date'] = pd.to_datetime(etf['date'])
    
    inst2 = inst[['order_book_id', 'strike_price', 'maturity_date',
                  'option_type', 'contract_multiplier']].copy()
    opt = opt.merge(inst2, on='order_book_id', how='left', suffixes=('_raw', ''))
    for col in ['strike_price', 'contract_multiplier']:
        raw = col + '_raw'
        if raw in opt.columns:
            opt[col] = opt[col].fillna(opt[raw])
            opt.drop(columns=[raw], inplace=True)
    
    etf = etf.set_index('date').sort_index()
    etf['rsi14'] = ta.rsi(etf['close'], length=14)
    bb = ta.bbands(etf['close'], length=20, std=2)
    if bb is not None:
        etf['bbu20'] = bb['BBU_20_2.0_2.0']
    else:
        etf['bbu20'] = np.nan
    
    return opt, etf

def get_cycles(opt, etf):
    trading_days_set = set(etf.index.normalize())
    opt_trading_days = sorted(opt['date'].unique())
    expiries_cp = (
        opt.groupby(['maturity_date', 'option_type'])['order_book_id']
        .nunique().unstack('option_type').dropna().index.tolist()
    )
    expiries_cp = sorted(expiries_cp)
    cycles = []
    for i, expiry in enumerate(expiries_cp):
        if i == 0:
            entry = opt_trading_days[0]
        else:
            prev_expiry = expiries_cp[i - 1]
            candidates = [d for d in opt_trading_days if d > prev_expiry]
            if not candidates:
                continue
            entry = candidates[0]
        if entry >= expiry:
            continue
        entry_norm = pd.Timestamp(entry).normalize()
        if entry_norm not in trading_days_set:
            continue
        cycles.append({'entry_date': entry, 'expiry_date': expiry})
    return cycles

def get_otm_strikes(opt, etf, entry_date, expiry_date, option_type, offsets):
    etf_close = float(etf.loc[entry_date.normalize(), 'close'])
    day_opt = opt[
        (opt['date'] == entry_date) &
        (opt['maturity_date'] == expiry_date) &
        (opt['option_type'] == option_type) &
        (opt['close'] > 0)
    ].copy()
    if day_opt.empty:
        return [None] * len(offsets)
    if option_type == 'C':
        otm = day_opt[day_opt['strike_price'] > etf_close].sort_values('strike_price')
    else:
        otm = day_opt[day_opt['strike_price'] < etf_close].sort_values('strike_price', ascending=False)
    results = []
    for off in offsets:
        idx = off - 1
        if idx < len(otm):
            results.append(otm.iloc[idx].to_dict())
        else:
            results.append(None)
    return results

def get_strike_by_level(opt, etf, entry_date, expiry_date, option_type, level):
    etf_close = float(etf.loc[entry_date.normalize(), 'close'])
    day_opt = opt[
        (opt['date'] == entry_date) &
        (opt['maturity_date'] == expiry_date) &
        (opt['option_type'] == option_type) &
        (opt['close'] > 0)
    ].copy()
    if day_opt.empty:
        return None
    if option_type == 'C':
        if level == 0:
            candidates = day_opt[day_opt['strike_price'] <= etf_close].sort_values('strike_price', ascending=False)
            idx = 0
        else:
            candidates = day_opt[day_opt['strike_price'] > etf_close].sort_values('strike_price')
            idx = level - 1
    else:
        if level == 0:
            candidates = day_opt[day_opt['strike_price'] >= etf_close].sort_values('strike_price', ascending=True)
            idx = 0
        else:
            candidates = day_opt[day_opt['strike_price'] < etf_close].sort_values('strike_price', ascending=False)
            idx = level - 1
    if 0 <= idx < len(candidates):
        return candidates.iloc[idx].to_dict()
    return None

def calc_leg_pnl(leg, etf, expiry_date, side):
    if leg is None:
        return None
    K = float(leg['strike_price'])
    mult = float(leg['contract_multiplier'])
    entry_mid = float(leg['close'])
    otype = leg['option_type']
    
    if side == 'sell':
        exec_px = entry_mid * (1 - SPREAD_HALF)
        premium_rmb = exec_px * mult
    else:
        exec_px = entry_mid * (1 + SPREAD_HALF)
        premium_rmb = -exec_px * mult
    
    etf_expiry_dates = etf.index[etf.index <= expiry_date]
    if etf_expiry_dates.empty:
        return {'net_rmb': 0, 'note': 'no_settle'}
    etf_settle = float(etf.loc[etf_expiry_dates[-1], 'close'])
    
    exercise_pnl_rmb = 0.0
    exercise_cost_rmb = 0.0
    note = 'expires_worthless'
    
    if otype == 'C':
        in_the_money = etf_settle > K
        intrinsic = max(0.0, etf_settle - K)
    else:
        in_the_money = etf_settle < K
        intrinsic = max(0.0, K - etf_settle)
    
    if in_the_money:
        if side == 'sell':
            exercise_pnl_rmb = -intrinsic * mult
            note = f'assigned ETF={etf_settle:.4f} K={K:.4f}'
        else:
            exercise_pnl_rmb = intrinsic * mult
            exercise_cost_rmb = EXERCISE_COST
            note = f'exercised ETF={etf_settle:.4f} K={K:.4f}'
    
    net_rmb = premium_rmb + exercise_pnl_rmb - COMMISSION - exercise_cost_rmb
    return {'net_rmb': net_rmb, 'note': note, 'K': K, 'mult': mult}

def run_simple_backtest(opt, etf, label):
    cycles = get_cycles(opt, etf)
    results = []
    for cyc in cycles:
        entry = cyc['entry_date']
        expiry = cyc['expiry_date']
        idx = entry.normalize()
        
        rsi = etf.loc[idx, 'rsi14']
        bbu = etf.loc[idx, 'bbu20']
        etf_close_entry = float(etf.loc[idx, 'close'])
        
        filter_passed = False
        if pd.notna(rsi) and pd.notna(bbu):
            filter_passed = (rsi < 66.0) and (etf_close_entry < bbu)
        
        if filter_passed:
            call_offsets = [2, 3]
        else:
            call_offsets = [4]
        
        call_legs = get_otm_strikes(opt, etf, entry, expiry, 'C', call_offsets)
        put_leg = get_strike_by_level(opt, etf, entry, expiry, 'P', PUT_BUY_LEVEL)
        
        legs_to_process = []
        for leg in call_legs:
            legs_to_process.append((leg, 'sell'))
        if put_leg is not None:
            legs_to_process.append((put_leg, 'buy'))
        
        cycle_net = 0.0
        for leg, side in legs_to_process:
            res = calc_leg_pnl(leg, etf, expiry, side)
            if res is not None:
                cycle_net += res['net_rmb']
        
        results.append({
            'entry': entry,
            'expiry': expiry,
            'net_rmb': cycle_net,
            'filter_passed': filter_passed,
        })
    
    nets = [r['net_rmb'] for r in results]
    win_rate = sum(1 for n in nets if n > 0) / len(nets) if nets else 0
    total = sum(nets)
    wins = sum(1 for n in nets if n > 0)
    losses = sum(1 for n in nets if n <= 0)
    
    print(f"\n  [{label}]")
    print(f"  Cycles: {len(results)}, Wins: {wins}, Losses: {losses}")
    print(f"  Win Rate: {win_rate:.1%}")
    print(f"  Total P&L: {total:+.2f} RMB")
    print(f"  Avg P&L/cycle: {np.mean(nets):+.2f} RMB")
    
    return results

# ── Run comparison ──
print("=" * 80)
print("  WIN RATE COMPARISON: Current (inst strike/mult) vs Corrected (opt daily)")
print("=" * 80)

print("\n  Loading data (current/broken)...")
opt_current, etf_current = load_data_current()
print("  Loading data (corrected)...")
opt_correct, etf_correct = load_data_correct()

print("\n  Running backtest (current)...")
res_current = run_simple_backtest(opt_current, etf_current, "CURRENT (inst strike/mult - BUGGY)")

print("\n  Running backtest (corrected)...")
res_correct = run_simple_backtest(opt_correct, etf_correct, "CORRECTED (opt daily strike/mult)")

# ── Cycle-by-cycle comparison ──
print("\n" + "=" * 80)
print("  CYCLE DIFFERENCES")
print("=" * 80)

diffs = []
for rc, rr in zip(res_current, res_correct):
    d = rr['net_rmb'] - rc['net_rmb']
    if abs(d) > 0.01:
        diffs.append({
            'entry': rc['entry'],
            'expiry': rc['expiry'],
            'current': rc['net_rmb'],
            'corrected': rr['net_rmb'],
            'diff': d,
        })

print(f"\n  Cycles with P&L difference: {len(diffs)} / {len(res_current)}")
if diffs:
    print(f"  Max positive diff (corrected better): {max(d['diff'] for d in diffs):+.2f}")
    print(f"  Max negative diff (corrected worse) : {min(d['diff'] for d in diffs):+.2f}")
    print(f"  Total diff                          : {sum(d['diff'] for d in diffs):+.2f}")
    print(f"\n  Top 10 biggest differences:")
    diffs.sort(key=lambda x: abs(x['diff']), reverse=True)
    for d in diffs[:10]:
        print(f"    {pd.Timestamp(d['entry']).date()} -> {pd.Timestamp(d['expiry']).date()}"
              f"  current={d['current']:+8.2f}  corrected={d['corrected']:+8.2f}  diff={d['diff']:+8.2f}")

# ── Win rate flip analysis ──
print(f"\n  Win rate flip analysis:")
win_to_loss = 0
loss_to_win = 0
for rc, rr in zip(res_current, res_correct):
    if rc['net_rmb'] > 0 and rr['net_rmb'] <= 0:
        win_to_loss += 1
    elif rc['net_rmb'] <= 0 and rr['net_rmb'] > 0:
        loss_to_win += 1
print(f"  Wins that become losses after fix : {win_to_loss}")
print(f"  Losses that become wins after fix : {loss_to_win}")
