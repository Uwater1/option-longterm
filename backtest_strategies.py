"""
Backtest Strategies — CallStrategy and PutStrategy
====================================================
Each strategy defines:
  - evaluate_filter(): when to trade
  - select_legs(): which option legs to execute
  - Limit order prediction functions (BS mapping)
  - Mode labels and formatting for logging
"""

import pandas as pd
import numpy as np
from backtest_engine import (
    ETF_NAME, RISK_FREE, NUM_CONTRACTS,
    get_otm_strikes, get_strike_by_level,
    compute_iv, _bs_price, _predict_model_offset,
)


# ═══════════════════════════════════════════════════════════════════════════════
#  Call Strategy — Short Call (Covered Call)
# ═══════════════════════════════════════════════════════════════════════════════

class CallStrategy:
    """
    Short call strategy for covered call backtest.
    Filter pass → sell OTM2+OTM3; filter fail → sell OTM4 (or skip).
    Supports dynamic alpha mode and model-offset limit orders.
    """

    def __init__(self, etf_choice="300", no_filter=False, model_offset=False,
                 alpha=False, skip_otm4=True):
        self.etf_choice = etf_choice
        self.no_filter = no_filter
        self.model_offset = model_offset
        self.alpha = alpha
        self.skip_otm4 = skip_otm4
        self.name = "Covered Call"

    def needs_5m(self):
        return self.model_offset

    def use_limit_order(self, side):
        return side == "sell" and self.model_offset

    def is_no_filter_mode(self):
        return self.no_filter

    def evaluate_filter(self, etf, idx, etf_close, indicators):
        """Returns (filter_passed, filter_would_pass)."""
        rsi = indicators["rsi"]
        bbu = indicators["bbu"]
        macd_hist = indicators["macd_hist"]
        roc10 = indicators["roc10"]
        vol20 = indicators["vol20"]
        vol20_median = indicators["vol20_median"]

        filter_would_pass = False
        if self.etf_choice == "50":
            if pd.notna(rsi) and pd.notna(roc10) and pd.notna(vol20) and pd.notna(vol20_median):
                filter_would_pass = (rsi < 60.0) and (rsi > 30.0) and (roc10 < 3.0) and (vol20 < vol20_median)
        elif self.etf_choice == "500":
            if pd.notna(rsi) and pd.notna(bbu) and pd.notna(indicators["sma50"]):
                filter_would_pass = (rsi > 30.0) and (etf_close < bbu) and (etf_close > indicators["sma50"])
        elif self.etf_choice in ["588000", "159915"]:
            if pd.notna(rsi) and pd.notna(macd_hist):
                filter_would_pass = (rsi < 72.0) and (rsi > 25.0) and (macd_hist < 0.0)
        else:  # 300ETF
            if pd.notna(rsi) and pd.notna(macd_hist):
                filter_would_pass = (rsi < 72.0) and (rsi > 25.0) and (macd_hist < 0.0)

        if self.no_filter:
            filter_passed = True
        elif self.alpha:
            filter_passed = True  # alpha mode always trades
        else:
            filter_passed = filter_would_pass

        return filter_passed, filter_would_pass

    def select_legs(self, opt, etf, entry, expiry, filter_passed, indicators, iv, ivr):
        """Return list of (leg_dict, side, label)."""
        legs = []

        if self.alpha:
            # Dynamic alpha: signal-based combo switching
            rsi = indicators["rsi"]
            roc20 = indicators["roc20"]
            bbu = indicators["bbu"]
            sma50 = indicators["sma50"]
            etf_close = float(etf.loc[entry.normalize(), "close_adj"]) if "close_adj" in etf.columns else float(etf.loc[entry.normalize(), "close"])

            if self.etf_choice == "50":
                signal_strong = pd.notna(rsi) and rsi > 30 and (pd.isna(roc20) or roc20 < 3.0)
            elif self.etf_choice == "500":
                signal_strong = (pd.notna(rsi) and pd.notna(bbu) and pd.notna(sma50)
                                 and rsi > 35 and etf_close < bbu and etf_close > sma50)
            elif self.etf_choice in ["588000", "159915"]:
                signal_strong = pd.notna(rsi) and 30 < rsi < 60 and (pd.isna(roc20) or roc20 < 4.0)
            else:  # 300ETF
                signal_strong = pd.notna(rsi) and 30 < rsi < 60 and (pd.isna(roc20) or roc20 < 4.0)

            if signal_strong:
                call_offsets = [2, 3]
                tag = "A"
            else:
                call_offsets = [4]
                tag = "B"

            call_legs = get_otm_strikes(opt, etf, entry, expiry, "C", call_offsets)
            for i, off in enumerate(call_offsets):
                if i < len(call_legs) and call_legs[i] is not None:
                    legs.append((call_legs[i], "sell", f"Call OTM{off} (Dyn-{tag})"))
        elif filter_passed:
            call_offsets = [2, 3]
            call_legs = get_otm_strikes(opt, etf, entry, expiry, "C", call_offsets)
            if len(call_offsets) > 0 and call_legs[0] is not None:
                legs.append((call_legs[0], "sell", f"Call Leg A (OTM{call_offsets[0]})"))
            if len(call_offsets) > 1 and call_legs[1] is not None:
                legs.append((call_legs[1], "sell", f"Call Leg B (OTM{call_offsets[1]})"))
        else:
            if not self.skip_otm4:
                call_legs = get_otm_strikes(opt, etf, entry, expiry, "C", [4])
                if call_legs[0] is not None:
                    legs.append((call_legs[0], "sell", "Call Leg C (OTM4)"))
        return legs

    def get_model_spread(self, etf, entry):
        """Return model-based spread for sell-side limit orders, or None."""
        if not self.model_offset:
            return None
        p10_frac = _predict_model_offset(etf, entry)
        if p10_frac is not None:
            return max(0.0, p10_frac)
        return None

    def get_predict_limit_fn(self, side):
        """Return the limit price prediction function for 5m simulation."""
        if side == "sell":
            return _predict_call_limit_price
        return None

    def format_cycle(self, res):
        """Format a single cycle for console output."""
        call_str = "+".join([f"OTM{o}" for o in res['call_offsets']])
        total_contracts = sum(res['num_contracts'] for _ in res['legs'])

        if self.no_filter and not res['filter_would_pass']:
            filter_tag = "[FILTER WOULD FAIL — overridden to OTM2+OTM3]"
        else:
            filter_tag = "[FILTER PASS]" if res['filter_would_pass'] else "[FILTER FAIL]"

        # Call limit fill status
        call_limit_str = ""
        if self.model_offset and res.get("call_limit_results"):
            clr = res["call_limit_results"]
            n_filled = sum(1 for c in clr if c["filled"] is True)
            n_total = sum(1 for c in clr if c["filled"] is not None)
            if n_total > 0:
                call_limit_str = f"  calls_limit={n_filled}/{n_total} filled"

        return (f"\nCycle  {res['entry_date'].date()} → {res['expiry_date'].date()}"
                f"   IV={res['iv']:.1%} (IVR={res['ivr']:.2f})  calls={call_str} puts=None"
                f"   ETF={res['etf_entry']:.4f} RSI={res['rsi']:.1f} BBU={res['bbu']:.3f} "
                f"(Total {total_contracts} contracts) {filter_tag}{call_limit_str}")

    def mode_label(self):
        parts = []
        if self.alpha:
            parts.append("DYNAMIC ALPHA")
        if self.model_offset:
            parts.append("MODEL OFFSET")
        if not parts:
            parts.append("NO-FILTER" if self.no_filter else "FILTERED")
        return " + ".join(parts)

    def file_suffix(self):
        parts = [f"cc_{self.etf_choice}ETF"]
        if self.no_filter:
            parts.append("nofilter")
        if self.alpha:
            parts.append("alpha")
        if self.model_offset:
            parts.append("modeloffset")
        if not self.skip_otm4:
            parts.append("noskipotm4")
        return "_".join(parts)


def _predict_call_limit_price(etf_df, entry_date, S_open, K, T, P_open):
    """Predict limit sell price for a call using BS mapping.
    When ETF rises to predicted P10 high, the call value increases.
    Returns limit price or None."""
    try:
        R_ETF_P10_frac = _predict_model_offset(etf_df, entry_date)
        if R_ETF_P10_frac is None:
            return None
        sigma_open = compute_iv(P_open, S_open, K, T, RISK_FREE, True)
        S_target = S_open * (1 + R_ETF_P10_frac)
        T_new = max(T - 1 / 365.0, 1 / 365.0)
        P_limit = _bs_price(S_target, K, T_new, RISK_FREE, sigma_open, True)
        P_limit *= (1 - 0.003)  # 0.3% cushion below BS theoretical
        return P_limit if P_limit > 0 else None
    except Exception:
        return None


# ═══════════════════════════════════════════════════════════════════════════════
#  Put Strategy — Long Put (Selective Hedge)
# ═══════════════════════════════════════════════════════════════════════════════

class PutStrategy:
    """
    Long put strategy for protective put backtest.
    Selective hedging: filter pass → buy put at configured OTM level; fail → skip.
    Supports BS-mapping limit entry.
    """

    def __init__(self, etf_choice="300", no_filter=False, limit_entry=False,
                 put_level=1):
        self.etf_choice = etf_choice
        self.no_filter = no_filter
        self.limit_entry = limit_entry
        self.put_level = put_level  # OTM level for put (1=closest OTM)
        self.name = "Protective Put"

    def needs_5m(self):
        return self.limit_entry

    def use_limit_order(self, side):
        return side == "buy" and self.limit_entry

    def is_no_filter_mode(self):
        return self.no_filter

    def evaluate_filter(self, etf, idx, etf_close, indicators):
        """
        Returns (filter_passed, filter_would_pass).
        Optimized via optimize_put_filters.py (real data) + research_put_filters.py (synthetic).
        Buy puts when indicators suggest vulnerability (low RSI, high vol, below trend).
        """
        rsi = indicators["rsi"]
        bbl = indicators["bbl"]
        sma50 = indicators["sma50"]
        vol20 = indicators["vol20"]
        vol20_median = indicators["vol20_median"]
        macd_hist = indicators["macd_hist"]
        roc10 = indicators["roc10"]

        filter_would_pass = False
        if self.etf_choice == "50":
            # 50ETF OTM2: RSI < 50 AND Close < SMA50
            # (Optimized: +4,019 RMB at OTM2 vs +2,306 at OTM1)
            if pd.notna(rsi) and pd.notna(sma50):
                filter_would_pass = (rsi < 50.0) and (etf_close < sma50)
        elif self.etf_choice == "500":
            # 500ETF OTM2: VolHigh AND MACD<0 (no RSI threshold)
            # (Optimized: +1,225 RMB at OTM2)
            if pd.notna(vol20) and pd.notna(vol20_median) and pd.notna(macd_hist):
                filter_would_pass = (vol20 > vol20_median) and (macd_hist < 0)
        elif self.etf_choice in ["588000", "159915"]:
            if pd.notna(rsi) and pd.notna(vol20) and pd.notna(vol20_median):
                filter_would_pass = (rsi < 60.0) and (vol20 > vol20_median)
        else:  # 300ETF
            # Optimized: RSI < 60 AND Vol20 > Vol20_median (net positive on real data)
            if pd.notna(rsi) and pd.notna(vol20) and pd.notna(vol20_median):
                filter_would_pass = (rsi < 60.0) and (vol20 > vol20_median)

        if self.no_filter:
            filter_passed = True
        else:
            filter_passed = filter_would_pass

        return filter_passed, filter_would_pass

    def select_legs(self, opt, etf, entry, expiry, filter_passed, indicators, iv, ivr):
        """Return list of (leg_dict, side, label). Buy put only if filter passes."""
        if not filter_passed:
            return []  # Skip this cycle — no hedge

        put_leg = get_strike_by_level(opt, etf, entry, expiry, "P", self.put_level)
        if put_leg is not None:
            return [(put_leg, "buy", f"Put Buy    (Level {self.put_level})")]
        return []

    def get_model_spread(self, etf, entry):
        """Puts don't use sell-side model spread."""
        return None

    def get_predict_limit_fn(self, side):
        """Return limit price prediction function for put buy limit orders."""
        if side == "buy":
            return _predict_put_limit_price
        return None

    def format_cycle(self, res):
        """Format a single cycle for console output."""
        total_contracts = sum(res['num_contracts'] for _ in res['legs'])

        if self.no_filter and not res['filter_would_pass']:
            filter_tag = "[FILTER WOULD FAIL — overridden]"
        else:
            filter_tag = "[FILTER PASS]" if res['filter_would_pass'] else "[FILTER FAIL — SKIP]"

        puts_str = "None" if not res["put_offsets"] else f"Level{self.put_level}"
        if self.limit_entry and res.get("put_filled") is not None:
            fill_tag = " [FILLED]" if res["put_filled"] else " [FORCE FILL]"
            puts_str += fill_tag

        return (f"\nCycle  {res['entry_date'].date()} → {res['expiry_date'].date()}"
                f"   IV={res['iv']:.1%} (IVR={res['ivr']:.2f})  calls=None puts={puts_str}"
                f"   ETF={res['etf_entry']:.4f} RSI={res['rsi']:.1f} BBU={res['bbu']:.3f} "
                f"(Total {total_contracts} contracts) {filter_tag}")

    def mode_label(self):
        parts = []
        if self.limit_entry:
            parts.append("PUT LIMIT")
        if not parts:
            parts.append("NO-FILTER" if self.no_filter else "FILTERED")
        return " + ".join(parts)

    def file_suffix(self):
        parts = [f"put_{self.etf_choice}ETF"]
        if self.put_level != 1:
            parts.append(f"level{self.put_level}")
        if self.no_filter:
            parts.append("nofilter")
        if self.limit_entry:
            parts.append("putlimit")
        return "_".join(parts)


def _predict_put_limit_price(etf_df, entry_date, S_open, K, T, P_open):
    """
    Predict the limit buy price for a put using BS mapping.
    Maps predicted ETF high to put price, applies OTM-dependent cushion.
    Returns the limit price (the max price we're willing to pay), or None.
    """
    try:
        R_ETF_P10_frac = _predict_model_offset(etf_df, entry_date)
        if R_ETF_P10_frac is None:
            return None

        # Solve for open IV
        sigma_open = compute_iv(P_open, S_open, K, T, RISK_FREE, False)

        # Map ETF target high to put price via BS
        S_target = S_open * (1 + R_ETF_P10_frac)
        T_new = max(T - 1 / 365.0, 1 / 365.0)
        P_limit_bs = _bs_price(S_target, K, T_new, RISK_FREE, sigma_open, False)

        # Apply OTM-dependent liquidity cushion
        # More OTM → wider cushion needed for execution
        otm_pct = max(0.0, (S_open - K) / S_open * 100.0)
        cushion = (0.5 + 0.5 * otm_pct) / 100.0

        # P_limit is between P_open and P_limit_bs — closer to P_open for more cushion
        if P_open <= 0:
            return None
        p90_offset = (P_limit_bs - P_open) / P_open
        p90_offset_cushioned = min(0.0, p90_offset + cushion)
        P_limit = P_open * (1 + p90_offset_cushioned)

        return P_limit if P_limit > 0 else None
    except Exception:
        return None
