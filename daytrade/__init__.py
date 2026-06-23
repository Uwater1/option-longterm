"""Daytrade: frozen-linear intraday alpha strategy.

Signal source: day-model trained LASSO/Huber/etc coefficients, frozen as constants.
Trade plan: decide at decision-bar close (per-ETF, see DECISION_BAR), enter at
the next bar's open, exit at 14:30 (bar 41 close).
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MODEL_DIR = ROOT / "day-model" / "models"
DATA_DIR = ROOT / "day-model" / "data"
ETF_5M_DIR = ROOT / "data"
DAYTRADING_DATA = ROOT / "day-trading" / "data"

# Single source of truth for DECISION_BAR / EXIT_BAR lives in day-model/build_features.py
# (so feature engineering and trading use identical timing). Import here.
sys.path.append(str(ROOT / "day-model"))
from build_features import DECISION_BAR, EXIT_BAR  # noqa: E402

ETFS = ["50ETF", "300ETF", "500ETF", "588000ETF", "159915ETF"]

# Per-ETF decision bar index on 5m frame (0-based).
# Bars are timestamped at END of period: bar 0 = 09:35 (covers 9:30-9:35).
# Bar 2 closes at 09:45, bar 5 closes at 10:00.
# Picked by bar-count experiment with trade_return target (see experiment_bars_results_trade_return.json).
# Decision at close[DECISION_BAR[etf]] -> entry at open[DECISION_BAR[etf] + 1] -> exit at close[EXIT_BAR=41].

# Costs (round-trip, in bps)
DEFAULT_COST_BPS = 15.0

# Holdout window (matches day-model for apples-to-apples)
HOLDOUT_START = "2024-03-19"
