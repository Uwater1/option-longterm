"""
Protective Put Backtest — Thin wrapper using Engine + Strategy pattern.
========================================================================
Selective hedging: only buy puts when filter signals danger.

Usage:
  python backtest_put.py [50|300|500] [--no-filter] [--limit-entry] [--level N]
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

    # Parse --level N (overrides per-ETF defaults below)
    level_override = None
    for i, arg in enumerate(sys.argv):
        if arg == "--level" and i + 1 < len(sys.argv):
            try:
                level_override = int(sys.argv[i + 1])
            except ValueError:
                pass

    # Remove flags before parsing ETF choice
    clean_argv = [a for a in sys.argv if a not in ["--no-filter", "--limit-entry"]
                  and not (a == "--level" or (sys.argv.index(a) > 0
                           and sys.argv[sys.argv.index(a)-1] == "--level"))]
    if len(clean_argv) > 1:
        etf_choice = clean_argv[1]

    # Per-ETF optimized OTM level defaults (from profit-first optimizer sweep)
    ETF_DEFAULT_LEVELS = {"300": 1, "50": 2, "500": 2}
    put_level = level_override if level_override is not None else ETF_DEFAULT_LEVELS.get(etf_choice, 1)

    select_underlying(etf_choice)

    # ── Setup logging ──────────────────────────────────────────────────────
    strategy = PutStrategy(
        etf_choice=etf_choice,
        no_filter=no_filter,
        limit_entry=limit_entry,
        put_level=put_level,
    )

    suffix = strategy.file_suffix()
    log_file = f"backtest/backtest_{suffix}.log"
    os.makedirs("backtest", exist_ok=True)
    f = open(log_file, 'w', encoding='utf-8')
    sys.stdout = Tee(sys.stdout, f)

    # ── Run ────────────────────────────────────────────────────────────────
    inst, opt, etf = load_data()
    run_backtest(strategy, opt, etf)
