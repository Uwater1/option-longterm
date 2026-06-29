"""Transaction Cost & Slippage Models for Daytrade Trade Execution.

Cost Specs:
- ETF Direct / Futures: 15 bps round-trip (0.0015).
- Naked Options (Buy OTM1 Call/Put):
    * Open Buy: 2.0 RMB commission + 2.0 RMB slippage per contract.
    * Close Sell: 2.0 RMB commission + 2.0 RMB slippage per contract.
    * Total round-trip per contract: 8.0 RMB (4 RMB open + 4 RMB close).
- Vertical Debit Spreads (Buy OTM1 + Sell OTM2):
    * Leg 1 (Buy OTM1): Open (2 comm + 2 slip), Close (2 comm + 2 slip) -> 8 RMB/contract.
    * Leg 2 (Sell OTM2): Open (2 slip), Close (2 comm + 2 slip) -> 6 RMB/contract.
    * Net spread round-trip cost: 14 RMB per spread contract bundle.
"""
from typing import NamedTuple

class OptionTradeCost(NamedTuple):
    open_comm: float
    open_slip: float
    close_comm: float
    close_slip: float

    @property
    def total_round_trip(self) -> float:
        return self.open_comm + self.open_slip + self.close_comm + self.close_slip

# Naked Long Option (Buy to open, Sell to close)
NAKED_LONG_COST = OptionTradeCost(open_comm=2.0, open_slip=2.0, close_comm=2.0, close_slip=2.0)

# Naked Short Option (Sell to open, Buy to close)
NAKED_SHORT_COST = OptionTradeCost(open_comm=0.0, open_slip=2.0, close_comm=2.0, close_slip=2.0)

ETF_COST_BPS = 15.0  # 15 bps round-trip
FUTURES_COST_BPS = 15.0  # 15 bps round-trip baseline

def calc_etf_net_return(gross_return: float, cost_bps: float = ETF_COST_BPS) -> float:
    """Calculate net return for ETF or Futures trade."""
    return gross_return - (cost_bps / 10000.0)

def calc_naked_option_pnl(
    entry_price: float,
    exit_price: float,
    multiplier: float = 10000.0,
    cost_spec: OptionTradeCost = NAKED_LONG_COST,
) -> dict:
    """Calculate absolute RMB P&L and net return on premium for a naked long option trade.
    
    Parameters
    ----------
    entry_price : float
        Option premium per share at entry (e.g. 0.0500 RMB).
    exit_price : float
        Option premium per share at exit.
    multiplier : float
        Contract size (e.g. 10000 ETF shares per option contract).
    cost_spec : OptionTradeCost
        Cost structure per contract.
        
    Returns
    -------
    dict: gross_pnl_rmb, net_pnl_rmb, net_ret_premium, total_cost_rmb
    """
    gross_pnl_rmb = (exit_price - entry_price) * multiplier
    total_cost_rmb = cost_spec.total_round_trip
    net_pnl_rmb = gross_pnl_rmb - total_cost_rmb
    
    premium_paid_rmb = entry_price * multiplier
    net_ret_premium = net_pnl_rmb / premium_paid_rmb if premium_paid_rmb > 0 else 0.0
    
    return {
        "gross_pnl_rmb": gross_pnl_rmb,
        "net_pnl_rmb": net_pnl_rmb,
        "net_ret_premium": net_ret_premium,
        "total_cost_rmb": total_cost_rmb,
        "premium_paid_rmb": premium_paid_rmb,
    }

def calc_vertical_spread_pnl(
    leg1_entry: float,
    leg1_exit: float,
    leg2_entry: float,
    leg2_exit: float,
    multiplier: float = 10000.0,
) -> dict:
    """Calculate P&L for a vertical debit spread (Long Leg 1 OTM1, Short Leg 2 OTM2).
    
    Leg 1: Buy open, sell close (NAKED_LONG_COST = 8 RMB)
    Leg 2: Sell open, buy close (NAKED_SHORT_COST = 6 RMB)
    Total spread fees = 14 RMB per spread pair.
    """
    leg1_res = calc_naked_option_pnl(leg1_entry, leg1_exit, multiplier, NAKED_LONG_COST)
    leg2_res = calc_naked_option_pnl(leg2_entry, leg2_exit, multiplier, NAKED_SHORT_COST)
    
    # For leg 2 (short option), gross profit is (entry - exit)
    leg2_gross_pnl_rmb = (leg2_entry - leg2_exit) * multiplier
    leg2_net_pnl_rmb = leg2_gross_pnl_rmb - NAKED_SHORT_COST.total_round_trip
    
    net_pnl_rmb = leg1_res["net_pnl_rmb"] + leg2_net_pnl_rmb
    net_debit_rmb = (leg1_entry - leg2_entry) * multiplier
    
    net_ret_capital = net_pnl_rmb / net_debit_rmb if net_debit_rmb > 0 else 0.0
    
    return {
        "net_pnl_rmb": net_pnl_rmb,
        "net_debit_rmb": net_debit_rmb,
        "net_ret_capital": net_ret_capital,
        "total_cost_rmb": NAKED_LONG_COST.total_round_trip + NAKED_SHORT_COST.total_round_trip,
    }
