"""
Protective Put Backtest — Thin wrapper using Engine + Strategy pattern.
========================================================================
Selective hedging: only buy puts when filter signals danger.

Usage:
  python backtest_put.py [50|300|500] [--no-filter] [--limit-entry]
"""
import sys
import os

# Ensure project root is on path for imports
sys.path.insert(0, os.path.abspath("."))

from backtest_engine import (
    select_underlying, load_data, run_backtest, Tee, ETF_NAME,
)
from backtest_strategies import PutStrategy


if __name__ == "__main__":
    # ── Parse CLI ──────────────────────────────────────────────────────────
    etf_choice = "300"
    no_filter = "--no-filter" in sys.argv
    limit_entry = "--limit-entry" in sys.argv

    # Remove flags before parsing ETF choice
    clean_argv = [a for a in sys.argv if a not in ["--no-filter", "--limit-entry"]]
    if len(clean_argv) > 1:
        etf_choice = clean_argv[1]

    select_underlying(etf_choice)

    # ── Setup logging ──────────────────────────────────────────────────────
    strategy = PutStrategy(
        etf_choice=etf_choice,
        no_filter=no_filter,
        limit_entry=limit_entry,
    )

    suffix = strategy.file_suffix()
    log_file = f"backtest/backtest_{suffix}.log"
    os.makedirs("backtest", exist_ok=True)
    f = open(log_file, 'w', encoding='utf-8')
    sys.stdout = Tee(sys.stdout, f)

    # ── Run ────────────────────────────────────────────────────────────────
    inst, opt, etf = load_data()
    run_backtest(strategy, opt, etf)
