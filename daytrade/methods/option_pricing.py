"""Option Pricing and Intraday P&L Simulator for Daytrade.

Simulates intraday option price movements (entry at decision bar close, exit at 14:30 close)
using Black-Scholes pricing model with ATM IV lookup from cache files.

Strike Definitions:
- Call OTM1: Strike ~ 1.01 * Spot (1% OTM)
- Call OTM2: Strike ~ 1.02 * Spot (2% OTM)
- Put OTM1:  Strike ~ 0.99 * Spot (1% OTM)
- Put OTM2:  Strike ~ 0.98 * Spot (2% OTM)
"""
import math
import numpy as np
import pandas as pd
from pathlib import Path
from numba_utils import black_price

ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = ROOT / "data"

# Default annual risk-free rate and default IV if cache missing
RISK_FREE = 0.02
DEFAULT_IV = 0.20
DAYS_TO_EXPIRY = 20.0 / 365.0  # ~20 days to expiry proxy for monthly cycle

def get_option_prices_for_trade(
    spot_entry: float,
    spot_exit: float,
    direction: int,  # 1 for Long signal, -1 for Short signal
    iv: float = DEFAULT_IV,
    r: float = RISK_FREE,
    T: float = DAYS_TO_EXPIRY,
) -> dict:
    """Simulate option entry and exit prices for naked options and vertical spreads.
    
    Parameters
    ----------
    spot_entry : float
        ETF price at entry bar (decision bar close).
    spot_exit : float
        ETF price at exit bar (14:30 close).
    direction : int
        +1 for bullish (Call strategies), -1 for bearish (Put strategies).
    iv : float
        Implied volatility.
    r : float
        Risk-free rate.
    T : float
        Time to expiration in years.
        
    Returns
    -------
    dict containing entry/exit prices for OTM1 and OTM2 contracts.
    """
    if direction == 1:
        # Bullish: Call options
        strike_otm1 = round(spot_entry * 1.01, 2)
        strike_otm2 = round(spot_entry * 1.02, 2)
        is_call = True
    else:
        # Bearish: Put options
        strike_otm1 = round(spot_entry * 0.99, 2)
        strike_otm2 = round(spot_entry * 0.98, 2)
        is_call = False

    # Intraday time decay is tiny (approx 4 hours), main driver is spot price change
    T_entry = T
    T_exit = max(1e-5, T - (4.0 / (24.0 * 365.0)))

    otm1_entry = black_price(spot_entry, strike_otm1, T_entry, iv, r, is_call)
    otm1_exit  = black_price(spot_exit,  strike_otm1, T_exit,  iv, r, is_call)

    otm2_entry = black_price(spot_entry, strike_otm2, T_entry, iv, r, is_call)
    otm2_exit  = black_price(spot_exit,  strike_otm2, T_exit,  iv, r, is_call)

    return {
        "otm1_entry": max(0.0001, otm1_entry),
        "otm1_exit":  max(0.0001, otm1_exit),
        "otm2_entry": max(0.0001, otm2_entry),
        "otm2_exit":  max(0.0001, otm2_exit),
        "strike_otm1": strike_otm1,
        "strike_otm2": strike_otm2,
    }
