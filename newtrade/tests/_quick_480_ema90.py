#!/usr/bin/env python3
"""Quick test: Rolling Tail 480d + EMA90 vs 480d raw vs expanding."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from run_backtest import run_single_backtest, resolve_ic_ema_span

ETFS = ["300ETF", "500ETF", "159915ETF"]

configs = [
    ("Expanding (baseline)", "expanding", 480, None),
    ("Rolling 480d raw", "rolling_tail", 480, None),
    ("Rolling 480d + EMA90", "rolling_tail", 480, 90),
]

print("=" * 70)
print("480d + EMA90 COMPARISON (ICW, OOS 2022-2026)")
print("=" * 70)

for name, ic_mode, window, ema in configs:
    print(f"\n--- {name} ---")
    for etf in ETFS:
        ema_span = ema if ema else resolve_ic_ema_span(etf, None)
        res = run_single_backtest(
            etf=etf, side="single", scheme_name="icw", z_th=0.5,
            position_mode="binary", fee_bps=0.0008,
            start_date="2022-01-01", end_date="2026-01-01",
            z_buffer=0.1, auto_threshold=True, dynamic_ic=True,
            rank_kwargs={"top_k": 10, "ic_ema_span": ema_span},
            ic_mode=ic_mode, tail_window=window, tail_pct=0.10,
        )
        if res.get("status") == "SUCCESS":
            print(f"  {etf:12s}: Sharpe={res['cost_sharpe']:.3f}  PnL={res['total_pnl']:+.4f}  WR={res['win_rate_pct']:.1f}%  Trades={res['n_trades']}")
