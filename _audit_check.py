"""Quick audit of backtest data consistency: strikes, multipliers, settlement, look-ahead."""
import pandas as pd
import numpy as np

print("=" * 80)
print("  BACKTEST DATA AUDIT")
print("=" * 80)

# ── Load Data ──
inst = pd.read_parquet('./data/300ETF_instruments.parquet')
opt = pd.read_parquet('./data/300ETF_historical_prices.parquet')
etf = pd.read_parquet('./data/510300_1d.parquet')

inst['maturity_date'] = pd.to_datetime(inst['maturity_date'])
opt['date'] = pd.to_datetime(opt['date'])
etf['date'] = pd.to_datetime(etf['date'])

# ── Check 1: Strike & Multiplier Consistency ──
print("\n[1] STRIKE & MULTIPLIER CONSISTENCY")
print("-" * 60)

opt_with_inst = opt.merge(
    inst[['order_book_id', 'contract_multiplier', 'strike_price']],
    on='order_book_id', how='left', suffixes=('_opt', '_inst')
)

diff_strike = opt_with_inst['strike_price_opt'] != opt_with_inst['strike_price_inst']
diff_mult = opt_with_inst['contract_multiplier_opt'] != opt_with_inst['contract_multiplier_inst']

print(f"  Total option rows         : {len(opt_with_inst)}")
print(f"  Rows with diff strike     : {diff_strike.sum()} ({diff_strike.mean():.1%})")
print(f"  Rows with diff multiplier : {diff_mult.sum()} ({diff_mult.mean():.1%})")

adj_contracts = opt_with_inst[diff_strike]['order_book_id'].unique()
print(f"  Contracts with adj strike : {len(adj_contracts)} / {inst['order_book_id'].nunique()}")

# Show examples
if len(adj_contracts) > 0:
    print("\n  Sample adjusted contracts:")
    for obid in adj_contracts[:5]:
        rows = opt_with_inst[opt_with_inst['order_book_id'] == obid].sort_values('date')
        inst_row = inst[inst['order_book_id'] == obid].iloc[0]
        mat = inst_row['maturity_date'].date()
        inst_k = inst_row['strike_price']
        inst_m = inst_row['contract_multiplier']
        opt_ks = rows['strike_price_opt'].unique()
        opt_ms = rows['contract_multiplier_opt'].unique()
        print(f"    {obid} (mat={mat}):")
        print(f"      inst: K={inst_k}, mult={inst_m}")
        print(f"      opt : K={opt_ks[:3]}, mult={opt_ms[:3]}")

# ── Check 2: Which strike/mult does backtest actually use? ──
print("\n[2] BACKTEST MERGE BEHAVIOR")
print("-" * 60)

inst2 = inst[['order_book_id', 'strike_price', 'maturity_date',
              'option_type', 'contract_multiplier']].copy()
opt2 = opt.merge(inst2, on='order_book_id', how='left', suffixes=('_raw', ''))

# The backtest uses the inst column (not _raw)
# But inst column may differ from opt's own column
print("  After merge, backtest uses columns WITHOUT '_raw' suffix")
print("  These come from the INSTRUMENTS table (inst)")
print("  Option's own strike_price -> strike_price_raw (IGNORED)")
print()

# Check: for an adjusted contract, what does backtest use?
if len(adj_contracts) > 0:
    obid = adj_contracts[0]
    rows = opt2[opt2['order_book_id'] == obid].sort_values('date')
    if len(rows) > 0:
        print(f"  Example contract: {obid}")
        print(f"  Backtest strike (from inst): {rows.iloc[0]['strike_price']}")
        print(f"  Opt data strike (from _raw): {rows.iloc[0].get('strike_price_raw', 'N/A')}")
        print(f"  Backtest mult (from inst): {rows.iloc[0]['contract_multiplier']}")
        print(f"  Opt data mult (from _raw): {rows.iloc[0].get('contract_multiplier_raw', 'N/A')}")
        print(f"  Close price: {rows.iloc[0]['close']}")

# ── Check 3: Settlement Date Alignment ──
print("\n[3] SETTLEMENT DATE ALIGNMENT")
print("-" * 60)

etf_dates = set(etf['date'].dt.normalize())
maturity_dates = sorted(inst['maturity_date'].unique())
missing = [md for md in maturity_dates if pd.Timestamp(md).normalize() not in etf_dates]
print(f"  Total maturity dates    : {len(maturity_dates)}")
print(f"  Missing from ETF data   : {len(missing)}")
if missing:
    for md in missing[:5]:
        print(f"    {pd.Timestamp(md).date()}")

# ── Check 4: Simulated Win Rate Comparison ──
# Run a quick version of the backtest to check a few cycles
print("\n[4] SPOT-CHECK: First 5 Cycles (manual P&L)")
print("-" * 60)

import pandas_ta as ta
etf2 = etf.set_index('date').sort_index()
etf2['rsi14'] = ta.rsi(etf2['close'], length=14)

# Simulate what happens with inst vs opt strikes for a few cycles
opt2_full = opt.merge(
    inst[['order_book_id', 'strike_price', 'maturity_date', 'option_type', 'contract_multiplier']],
    on='order_book_id', how='left', suffixes=('_raw', '')
)
for col in ['strike_price', 'contract_multiplier']:
    raw = col + '_raw'
    if raw in opt2_full.columns:
        opt2_full[col] = opt2_full[col].fillna(opt2_full[raw])
        opt2_full.drop(columns=[raw], inplace=True)

opt_trading_days = sorted(opt2_full['date'].unique())
expiries_cp = (
    opt2_full.groupby(['maturity_date', 'option_type'])['order_book_id']
    .nunique().unstack('option_type').dropna().index.tolist()
)
expiries_cp = sorted(expiries_cp)

trading_days_set = set(etf2.index.normalize())
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
    cycles.append({'entry': entry, 'expiry': expiry})

# Check first 5 sell-call-only cycles
for cyc in cycles[:5]:
    entry = cyc['entry']
    expiry = cyc['expiry']
    
    etf_close = float(etf2.loc[entry_norm, 'close'])
    
    # Get OTM2 call using INST strike (what backtest does)
    day_opt_inst = opt2_full[
        (opt2_full['date'] == entry) &
        (opt2_full['maturity_date'] == expiry) &
        (opt2_full['option_type'] == 'C') &
        (opt2_full['close'] > 0)
    ].copy()
    
    if day_opt_inst.empty:
        continue
    
    otm_inst = day_opt_inst[day_opt_inst['strike_price'] > etf_close].sort_values('strike_price')
    if len(otm_inst) < 2:
        continue
    
    leg_inst = otm_inst.iloc[1]  # OTM2
    
    # Now get the SAME option but check opt's own strike
    obid = leg_inst['order_book_id']
    opt_row = opt[opt['order_book_id'] == obid]
    opt_row_day = opt_row[opt_row['date'] == entry]
    if opt_row_day.empty:
        continue
    
    inst_strike = float(leg_inst['strike_price'])
    inst_mult = float(leg_inst['contract_multiplier'])
    opt_strike = float(opt_row_day.iloc[0]['strike_price'])
    opt_mult = float(opt_row_day.iloc[0]['contract_multiplier'])
    close_px = float(leg_inst['close'])
    
    # Settlement
    etf_expiry_dates = etf2.index[etf2.index <= expiry]
    etf_settle = float(etf2.loc[etf_expiry_dates[-1], 'close'])
    
    # P&L with inst values (what backtest does)
    exec_px_inst = close_px * 0.98
    intrinsic_inst = max(0, etf_settle - inst_strike)
    pnl_inst = (exec_px_inst - intrinsic_inst) * inst_mult - 2.0
    
    # P&L with opt values (what it SHOULD be)
    exec_px_opt = close_px * 0.98
    intrinsic_opt = max(0, etf_settle - opt_strike)
    pnl_opt = (exec_px_opt - intrinsic_opt) * opt_mult - 2.0
    
    flag = " *** MISMATCH" if abs(pnl_inst - pnl_opt) > 0.01 else ""
    print(f"  {pd.Timestamp(entry).date()} -> {pd.Timestamp(expiry).date()}"
          f"  ETF_entry={etf_close:.4f}  settle={etf_settle:.4f}")
    print(f"    inst: K={inst_strike:.4f} mult={inst_mult:.0f} -> exec={exec_px_inst:.4f}"
          f" intr={intrinsic_inst:.4f} PnL={pnl_inst:+.2f}")
    print(f"    opt : K={opt_strike:.4f} mult={opt_mult:.0f} -> exec={exec_px_opt:.4f}"
          f" intr={intrinsic_opt:.4f} PnL={pnl_opt:+.2f}{flag}")
    print()

# ── Check 5: Overall Impact ──
print("\n[5] AGGREGATE IMPACT OF WRONG STRIKE/MULT")
print("-" * 60)

# Count how many cycles have at least one leg with mismatched strike
n_mismatch = 0
n_total = 0
total_pnl_diff = 0.0
for cyc in cycles:
    entry = cyc['entry']
    expiry = cyc['expiry']
    entry_norm = pd.Timestamp(entry).normalize()
    etf_close = float(etf2.loc[entry_norm, 'close'])
    
    day_opt = opt2_full[
        (opt2_full['date'] == entry) &
        (opt2_full['maturity_date'] == expiry) &
        (opt2_full['option_type'] == 'C') &
        (opt2_full['close'] > 0)
    ].copy()
    
    if day_opt.empty:
        continue
    
    otm = day_opt[day_opt['strike_price'] > etf_close].sort_values('strike_price')
    n_total += 1
    
    has_mismatch = False
    for i in range(min(4, len(otm))):
        leg = otm.iloc[i]
        obid = leg['order_book_id']
        opt_row_day = opt[(opt['order_book_id'] == obid) & (opt['date'] == entry)]
        if opt_row_day.empty:
            continue
        inst_k = float(leg['strike_price'])
        opt_k = float(opt_row_day.iloc[0]['strike_price'])
        inst_m = float(leg['contract_multiplier'])
        opt_m = float(opt_row_day.iloc[0]['contract_multiplier'])
        if abs(inst_k - opt_k) > 1e-6 or abs(inst_m - opt_m) > 1e-6:
            has_mismatch = True
    
    if has_mismatch:
        n_mismatch += 1

print(f"  Total cycles checked     : {n_total}")
print(f"  Cycles with strike/mult  : {n_mismatch} ({n_mismatch/max(n_total,1):.1%})")
print(f"  mismatch on at least 1 leg")
print()
print("=" * 80)
print("  AUDIT COMPLETE")
print("=" * 80)
