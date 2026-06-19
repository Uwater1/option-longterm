"""Daytrade: frozen-linear intraday alpha strategy.

Signal source: day-model trained LASSO/Huber/etc coefficients, frozen as constants.
Trade plan: decide at 9:45 (159915/500) or 10:00 (300/50/588000), exit at 14:30.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MODEL_DIR = ROOT / "day-model" / "models"
DATA_DIR = ROOT / "day-model" / "data"
ETF_5M_DIR = ROOT / "data"
DAYTRADING_DATA = ROOT / "day-trading" / "data"

ETFS = ["50ETF", "300ETF", "500ETF", "588000ETF", "159915ETF"]

# Per-ETF decision bar index on 5m frame (0-based).
# Bars are timestamped at END of period: bar 0 = 09:35 (covers 9:30-9:35).
# Bar 2 closes at 09:45, bar 5 closes at 10:00.
DECISION_BAR = {
    "159915ETF": 2,  # 9:45 (per day-model §7: peak IC at 9:55, 9:45 also strong)
    "500ETF": 2,     # 9:45 (peak IC at 9:55)
    "300ETF": 5,     # 10:00 (blue-chip needs full 30min)
    "50ETF": 5,      # 10:00
    "588000ETF": 5,  # 10:00
}

# Exit bar: 14:30 close (i.e. the 5-min bar ending at 14:30).
# 5m bars are timestamped at the END of their period.
# AM: bars 0-23 (09:35 ... 11:30), PM: bars 24-47 (13:05 ... 15:00).
EXIT_BAR = 41  # bar at 14:30 = close of 14:25-14:30 interval

# Costs (round-trip, in bps)
DEFAULT_COST_BPS = 15.0

# Holdout window (matches day-model for apples-to-apples)
HOLDOUT_START = "2024-03-19"
