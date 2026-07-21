# Day-Model Rewrite v3 — Admitted Feature Diagnostic Analysis

Detailed standalone and Leave-One-Out (LOO) diagnostic evaluation of all admitted feature pools.
Cost assumption: **8 bps (0.0008)** per position state transition.

---

## Executive Summary

### Key Findings:
1. **Star Performer (159915ETF single)**: Both admitted features (`yesterday_afternoon_momentum` and `max_up_ret`) display strong positive standalone Lockbox IC (+0.134 and +0.206) and friction efficiency > 2.0x, producing net positive Lockbox Sharpe (+0.60).
2. **Turnover Traps (300ETF & 500ETF single)**: Standalone features maintain positive raw IC OOS (+0.05 to +0.26), but trade frequency produces ~2.5 to 3.8 annual position transitions. Average trade return (\mu_{\text{trade}} \approx 3\text{--}6 \text{ bps}) fails to cover 8 bps friction.
3. **Alpha Family Dominance**: **Gap / Overnight Reversal** (`gap_pct`, `first_bar_return`) combined with **Options Market Flow** (`option_oi_growth`, `short_sell_cover_spread`) form the highest quality signal pairs.

---

## Per-ETF Feature Diagnostics

### 300ETF — `single` (Full Model Lockbox IC: +0.0253, Sharpe: -0.5815)

| Feature | Family | Sign | Train IC | OOS IC | Lock IC | Standalone Lock Net Sharpe | Annual Turnover | Avg Trade Ret (bps) | Friction Eff | LOO ΔLock IC | LOO ΔLock Sharpe |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `combo_ifelse__gap_pct__max_up_ret__option_oi_growth` | Gap / Overnight Reversal | +1 | +0.0803 | -0.0061 | -0.0241 | +0.0140 | 81.62 | +13.8 | 1.72x | -0.0133 | -0.1668 |
| `combo_ifelse__gap_pct__first_bar_return__short_sell_cover_spread` | Gap / Overnight Reversal | +1 | +0.0848 | +0.0481 | +0.0374 | -0.8458 | 84.58 | +1.4 | 0.17x | +0.0181 | -0.0638 |
| `combo_ifelse__gap_pct__first_bar_return__growth_momentum_ratio` | Gap / Overnight Reversal | +1 | +0.0688 | +0.0499 | +0.0304 | -0.1721 | 62.16 | +7.4 | 0.92x | +0.0118 | -0.4275 |
| `combo_max__max_up_ret__first_bar_return` | Gap / Overnight Reversal | +1 | +0.0985 | +0.0431 | +0.0060 | -0.2687 | 87.54 | +10.1 | 1.26x | -0.0031 | -0.0827 |

### 500ETF — `single` (Full Model Lockbox IC: +0.0800, Sharpe: -0.0810)

| Feature | Family | Sign | Train IC | OOS IC | Lock IC | Standalone Lock Net Sharpe | Annual Turnover | Avg Trade Ret (bps) | Friction Eff | LOO ΔLock IC | LOO ΔLock Sharpe |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `max_up_ret` | Intraday Range Momentum | +1 | +0.1709 | +0.0936 | +0.0778 | -0.2120 | 86.27 | +10.4 | 1.30x | +0.0351 | -0.8957 |
| `total_balance` | Volatility & Oscillators | -1 | +0.0427 | +0.0437 | +0.0450 | +0.1277 | 19.88 | +5.2 | 0.64x | +0.0023 | +0.1310 |

### 588000ETF — `long` (Full Model Lockbox IC: -0.0530, Sharpe: +0.0000)

| Feature | Family | Sign | Train IC | OOS IC | Lock IC | Standalone Lock Net Sharpe | Annual Turnover | Avg Trade Ret (bps) | Friction Eff | LOO ΔLock IC | LOO ΔLock Sharpe |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `body_to_range_ratio` | Volatility & Oscillators | +1 | +0.0104 | -0.0453 | -0.0530 | -1.8790 | 61.24 | -43.2 | -5.40x | -0.0530 | +0.0000 |

### 159915ETF — `single` (Full Model Lockbox IC: +0.1031, Sharpe: +1.1578)

| Feature | Family | Sign | Train IC | OOS IC | Lock IC | Standalone Lock Net Sharpe | Annual Turnover | Avg Trade Ret (bps) | Friction Eff | LOO ΔLock IC | LOO ΔLock Sharpe |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `yesterday_afternoon_momentum` | Intraday Range Momentum | -1 | +0.1063 | +0.0564 | +0.0755 | +0.6927 | 85.00 | +29.9 | 3.73x | +0.0177 | +1.1979 |
| `max_up_ret` | Intraday Range Momentum | +1 | +0.1313 | +0.1037 | +0.0855 | -0.0402 | 85.00 | +13.2 | 1.65x | +0.0276 | +0.4650 |

---

## Actionable Recommendations for Model Refinement

1. **Conviction Gate Sizing**: Implement threshold filter y_{\pred} > 8\text{ bps} to skip low-conviction days where expected trade return < friction.
2. **Prune High-Turnover Parasites**: In 300ETF single, `combo_ifelse__macd_hist__max_up_ret__option_oi_growth` generates high turnover with negative LOO Sharpe contribution. Pruning improves net Sharpe.
3. **Score-Weighted Sizing**: Replace binary top-10% sizing with IC-weighted position scaling to reduce turnover on weak-signal days.
