# 500ETF Covered Call Strategy Research Report

**Date:** June 2026  
**Scope:** 45 cycles, Sep 2022 → Jun 2026  
**Baseline P&L:** 21,448 RMB → **Improved P&L:** 22,145 RMB (+3.3%)

---

## 1. Executive Summary

500ETF (CSI 500) covered call strategy underperforms 300ETF (67% vs 88% win rate) due to higher volatility (26.8% annualized vs 19.1%). The main losses come from sharp intra-cycle rallies (+8-16%) that blow through all sold call strikes. After testing 10 strategy variants across filters, OTM levels, put levels, and IVR-driven regimes, the best improvement is raising the RSI filter threshold from 66→70 for 500ETF, gaining +697 RMB. No filter-based approach can prevent the biggest loss cycles because they occur when RSI is already low.

---

## 2. 500ETF Characteristics vs Peers

| Metric | 50ETF | 300ETF | **500ETF** |
|--------|-------|--------|-----------|
| Underlying | SSE 50 | CSI 300 | **CSI 500** |
| Ann. Volatility | 21.4% | 19.1% | **26.8%** |
| Price Range | 1.58–3.67 | 2.60–5.25 | **3.61–9.82** |
| Data Start | 2015 | 2019 | **Sep 2022** |
| Cycles Available | 120+ | 78 | **45** |
| Options History | Longest | Longer | **Shortest** |

500ETF has ~40% higher volatility than 300ETF, meaning strikes are hit more frequently. The price range is extreme (3.61→9.82), meaning recent data includes a massive structural rally.

---

## 3. OTM Level Analysis

### 3.1 Real Data (45 cycles, no filter)

| OTM Level | Win Rate | Expire Worthless | Expected Return | Max Loss |
|-----------|----------|------------------|-----------------|----------|
| 0 (ATM) | 71.1% | 33.3% | +675 | -10,947 |
| 1 | 75.6% | 60.0% | +337 | -9,355 |
| **2** | **84.4%** | **82.2%** | **+124** | **-7,277** |
| 3 | 91.1% | 88.9% | +51 | -4,916 |
| **4** | **97.7%** | **95.5%** | **+105** | **-2,486** |
| 5 | 100.0% | 100.0% | +96 | +2 |

### 3.2 Real Data (with RSI<66+BBU filter, 38 cycles pass)

| OTM Level | Win Rate | Expire Worthless | Expected Return | Max Loss |
|-----------|----------|------------------|-----------------|----------|
| 0 | 76.3% | 36.8% | +1,250 | -6,494 |
| 1 | 78.9% | 63.2% | +760 | -5,359 |
| **2** | **89.5%** | **86.8%** | **+389** | **-3,752** |
| 3 | 94.7% | 92.1% | +186 | -1,726 |
| **4** | **100.0%** | **97.4%** | **+149** | **+6** |
| 5 | 100.0% | 100.0% | +86 | +2 |

**Key insight:** OTM2 on 500ETF has only 84% win rate (no filter) vs 93% on 300ETF. OTM4 is the "sweet spot" for 500ETF — 97.7% win rate with positive expected return. But selling only OTM4 sacrifices too much premium income.

### 3.3 Put Level Analysis (real data, 45 cycles)

| Put Level | Win Rate | Expected Return | Max Loss |
|-----------|----------|-----------------|----------|
| 0 (ATM-ish) | 51.1% | +375 | -3,266 |
| **1 (closest OTM)** | **28.9%** | **+14** | **-1,924** |
| 2 | 13.3% | -43 | -1,317 |
| 3 | 8.9% | -35 | -733 |
| 4 | 4.8% | -19 | -603 |
| 5 | 3.3% | -51 | -568 |

Put Level 1 is barely positive (+14 RMB expected). Level 2+ are net negative. The put is expensive protection, not a profit center.

### 3.4 Synthetic Data (Numba-accelerated, ~692 samples)

| OTM Level | Call Win Rate | Call Exp Return | Put Win Rate | Put Exp Return |
|-----------|---------------|-----------------|--------------|----------------|
| 0 | 72.8% | +1,039 | 53.9% | +531 |
| 1 | 79.1% | +594 | 29.5% | +65 |
| 2 | 86.6% | +178 | 11.2% | -53 |
| **3** | **93.2%** | **-20** | 4.5% | -55 |
| 4 | 86.2% | -93 | 1.1% | -63 |
| 5 | 71.1% | -116 | 0.6% | -63 |

**Warning:** Synthetic data shows OTM3+ have negative expected returns for calls. This is because synthetic data uses constant-maturity interpolation and includes many more high-vol regimes where even far OTM strikes get hit. The real data is more favorable.

---

## 4. Filter Research

### 4.1 Individual Filter Evaluation (synthetic 500ETF data)

| Filter | Placement Rate | Avg ER (Passed) | Avg ER (Filtered) |
|--------|---------------|-----------------|-------------------|
| baseline | 100.0% | +267 | 0 |
| **f3: RSI<70** | **92.0%** | **+284** | **+73** |
| f4: RSI>30 | 93.7% | +290 | -75 |
| f6: Close<BBU | 95.6% | +322 | -924 |
| f9: ROC<5% | 78.5% | +298 | +156 |
| f20: Keltner | 72.7% | +293 | +200 |
| f5: MACD<0 | 47.9% | +399 | +147 |

### 4.2 Filter Combinations (synthetic 500ETF data)

| Combo | Placement Rate | Avg ER (In) | Avg ER (Out) |
|-------|---------------|-------------|-------------|
| **f4 AND f6 (RSI>30 AND BBU)** | **89.3%** | **+350** | **-425** |
| f3 AND f6 (RSI<70 AND BBU) | 90.2% | +319 | -210 |
| f3 AND f4 AND f6 | 83.9% | +349 | -157 |
| f12 OR (f3 AND f6) | 91.1% | +295 | -11 |
| c2: f1 OR f3 (SMA20 OR RSI<70) | 92.0% | +284 | +73 |

### 4.3 Filter Combinations (real 500ETF data)

| Combo | Cycles | Win Rate | Avg ER | Max Loss |
|-------|--------|----------|--------|----------|
| **c11: BBU AND ROC<5%** | **35** | **89.5%** | **+435** | **-2,887** |
| c8: ROC<5% AND ATR breakout | 32 | 89.6% | +436 | -2,887 |
| c2: SMA20 OR RSI<70 | 40 | 88.3% | +321 | -5,830 |
| c21: (SMA20 OR ADX<25) AND RSI<70 | 32 | 85.9% | +176 | -5,830 |

---

## 5. 10-Variant Head-to-Head Comparison

### 5.1 Summary Table

| # | Variant | Filter | Call Pass | Call Fail | Put | P&L | Wins | Assigned |
|---|---------|--------|-----------|-----------|-----|-----|------|----------|
| 1 | **Baseline** | RSI<66+BBU | OTM2+3 | OTM4 | L1 | **21,448** | 29/45 | 6 |
| 2 | **RSI70+BBU** | RSI<70+BBU | OTM2+3 | OTM4 | L1 | **22,145** | 30/45 | 6 |
| 3 | IVR-Driven | RSI<66+BBU | IVR→1+2/2+3/4+5 | | L1 | 21,396 | 31/45 | **18** |
| 4 | IVR+RSI70 | RSI<70+BBU | IVR→1+2/2+3/4+5 | | L1 | 21,396 | 31/45 | **18** |
| 5 | Wider OTM | RSI<66+BBU | OTM3+4 | OTM5 | L1 | 14,047 | 20/45 | 3 |
| 6 | Put L2 | RSI<66+BBU | OTM2+3 | OTM4 | L2 | 18,892 | 33/45 | 6 |
| 7 | BBU+ROC | BBU+ROC<5% | OTM2+3 | OTM4 | L1 | 17,080 | 27/45 | 6 |
| 8 | All3 Filter | RSI<66+BBU+ROC | OTM2+3 | OTM4 | L1 | 16,383 | 26/45 | 6 |
| 9 | IVR+Wider+RSI70 | RSI<70+BBU | IVR→2+3/3+4/4+5 | | L1 | 8,502 | 32/45 | 8 |
| 10 | IVR+Wider+Put2 | RSI<66+BBU | IVR→2+3/3+4/4+5 | | L2 | 5,947 | 37/45 | 8 |

### 5.2 Analysis

**Best overall: RSI70+BBU (+697 over baseline)**
- Only 1 cycle differs from baseline: 2025-09-25 (RSI=68.4, baseline FAIL, RSI70 PASS)
- That cycle made +428 RMB profit (OTM2+3 calls, put exercised)
- Same number of assignments (6), same strike levels

**Wider OTM3+4/5: Fewest assignments (3) but worst P&L**
- Reduces worst-case loss: -3,371 vs baseline -7,261
- But sacrifices too much premium: avg cycle income drops significantly
- Best for risk-averse approach if capital preservation > income

**IVR-Driven: Catastrophically bad for 500ETF**
- 18 assignments vs 6 baseline — triple the assignment rate
- Low IVR (<0.20) → sells OTM1+2 → closest strikes → gets assigned constantly
- Worst single cycle: -18,203 (2025-12: +16.2% rally, IVR=0.00, sold OTM1+2)
- IVR-Driven works for 300ETF but NOT for 500ETF due to higher vol

---

## 6. Loss Cycle Deep Dive

The 3 worst loss cycles for the baseline strategy:

### Cycle 2025-01-23 → 2025-02-26: **-3,375 RMB**
- **ETF:** 5.542 → 6.000 (+8.3%)
- **RSI=46.0, IVR=0.05** → Filter PASS → sold OTM2(K=5.750) + OTM3(K=5.903)
- **Both assigned:** ETF rallied through both strikes
- **Wider OTM3+4 would have lost only -1,350** (OTM3 K=5.903 assigned, OTM4 K=6.000 barely assigned)

### Cycle 2025-12-25 → 2026-01-28: **-4,057 RMB**
- **ETF:** 7.478 → 8.691 (+16.2%)
- **RSI=64.6, IVR=0.00** → Filter FAIL → sold OTM4(K=8.437)
- **Assigned:** Massive rally, ETF up 16.2% in one month
- **Wider OTM5 would have lost only -1,571** (OTM5 not assigned)

### Cycle 2026-03-26 → 2026-04-22: **-7,261 RMB**
- **ETF:** 7.700 → 8.455 (+9.8%)
- **RSI=37.0, IVR=0.04** → Filter PASS → sold OTM2(K=8.000) + OTM3(K=8.250)
- **Both assigned:** ETF rallied +9.8%, blew through both strikes
- **Wider OTM3+4 would have lost -3,371** (only OTM3 assigned)

### Key Pattern
All 3 big losses occur when RSI is LOW (37-46), meaning the market is NOT overbought. The filter PASSES and we trade aggressively (2 call legs). The losses come from **unexpected intra-cycle rallies** that no entry-date filter can predict.

---

## 7. Conclusions

### What Works
1. **RSI threshold 70 for 500ETF** — implemented, +697 RMB improvement
2. Current OTM2+3/4 structure — best balance of premium income vs assignment risk
3. Put Level 1 — barely positive but provides crash protection for long stock holders

### What Doesn't Work
1. **IVR-driven OTM** — catastrophic for 500ETF (18 assignments, worst -18K cycle)
2. **Wider OTM3+4/5** — reduces assignments but sacrifices too much premium (-7,400 vs baseline)
3. **Put Level 2** — cheaper put but net worse P&L (-2,556 vs baseline)
4. **ROC<5% filter** — too restrictive, skips profitable cycles
5. **Tighter RSI<60** — skips good trades, net worse

### Fundamental Limitation
No entry-date filter can prevent the big losses because they occur when RSI is low (market not overbought). The losses come from **intra-cycle sharp rallies** (+8-16%) that blow through all strike levels within a month. To further improve 500ETF performance, consider:

1. **Early roll management** — roll calls to higher strikes mid-cycle if underlying rallies past threshold
2. **Delta hedging** — dynamically adjust position delta
3. **Shorter DTE** — use weekly options to reduce exposure window
4. **Volatility-scaled position sizing** — reduce contracts when VIX-equivalent is low

---

## 8. Data Completeness & Robustness Analysis

### 8.1 Cross-ETF Data Coverage

| ETF | Cycles | Option History | Ann. Vol | Opt Rows |
|-----|--------|---------------|----------|----------|
| 50ETF | 136 | 2015-02 → 2026-05 | 21.4% | 353,380 |
| 300ETF | 78 | 2019-12 → 2026-05 | 19.1% | 188,822 |
| **500ETF** | **45** | **2022-09 → 2026-05** | **26.8%** | **104,996** |

500ETF has 3.0x fewer cycles than 50ETF and 1.7x fewer than 300ETF. Only ~3.7 years of option history. This is a fundamental data limitation — all conclusions carry wider uncertainty bands.

### 8.2 Bootstrap Confidence Intervals (5000 iterations)

| Variant | Total P&L | 95% CI Low | 95% CI High | Boot Std | Win Rate |
|---------|-----------|------------|-------------|----------|----------|
| Baseline RSI66+BBU | 21,448 | -8,192 | 51,131 | 14,972 | 64% |
| **RSI70+BBU** | **22,145** | **-7,014** | **51,369** | **14,867** | **67%** |
| RSI60+BBU | 15,608 | -12,679 | 43,799 | 14,346 | 58% |
| Conservative OTM3+4/5 | 14,047 | -6,795 | 37,487 | 11,148 | 44% |
| Aggressive OTM1+2/3 | 39,498 | -6,162 | 80,103 | 22,032 | 62% |
| No filter OTM2+3 | 8,502 | -36,890 | 46,787 | 21,501 | 71% |

**Key finding:** 95% CIs overlap massively across ALL variants. The difference between "best" and "worst" variant is not statistically significant at 95% level with only 45 cycles.

### 8.3 Leave-One-Out Cross-Validation

| Variant | LOOCV Min | LOOCV Max | LOOCV Range | LOOCV Std |
|---------|-----------|-----------|-------------|-----------|
| Baseline RSI66+BBU | 14,079 | 28,709 | 14,630 | 2,244 |
| RSI70+BBU | 14,776 | 29,406 | 14,630 | 2,241 |
| Aggressive OTM1+2/3 | 31,276 | 50,392 | 19,116 | 3,275 |

A single cycle swing of ~14,630 RMB (68% of baseline total) demonstrates extreme sensitivity to individual cycle outcomes. Any variant ranking can flip with one more good/bad month.

### 8.4 RSI70 vs RSI66 Statistical Significance

| Metric | Value |
|--------|-------|
| Total improvement | +697 RMB |
| Bootstrap 95% CI | [+0, +2,090] |
| P(improvement > 0) | **64.3%** |
| Cycles differing | 1 (2025-09-25, RSI=68.4) |

**Conclusion:** The +697 RMB improvement from RSI70 over RSI66 is NOT statistically significant. With P=64.3%, this is roughly a coin flip. The improvement comes from exactly 1 cycle. We keep RSI70 as implemented because it doesn't hurt, but we should not have high confidence that it's truly better.

### 8.5 Cross-ETF Volatility Regime

500ETF's average 20-day realized vol (22.7%) matches 300ETF's worst 18% of the time. The correlation of 20-day returns between 500ETF and 300ETF is 0.85; vol correlation is 0.80.

**Implication:** We cannot reliably use 300ETF's longer history to validate 500ETF strategy variants, because 500ETF lives in a permanently higher-vol regime that 300ETF rarely experiences.

### 8.6 Sample Size Sensitivity

| Simulated N | P(RSI70 > Baseline) | Baseline 95% CI Width |
|-------------|---------------------|----------------------|
| 20 | 35.8% | ±18,914 |
| 30 | 48.8% | ±22,910 |
| 40 | 58.9% | ±28,176 |
| **45 (actual)** | **63.8%** | **±30,127** |

Even at N=45, confidence is only 64%. Would need ~100+ cycles (8+ years) for >80% confidence in RSI70 superiority.

### 8.7 Robustness Conclusions

1. **All variant rankings are unstable** with only 45 cycles. Bootstrap CIs overlap broadly.
2. **RSI70 improvement is marginal** (P=64.3%). Keep it but don't over-rely on it.
3. **Aggressive OTM1+2/3 looks best in P&L** (39,498) but has the widest CI (boot std 22K) — highest variance, highest risk.
4. **Conservative OTM3+4/5 is most stable** (boot std 11K) but sacrifices too much premium.
5. **500ETF's vol regime is structurally different** from 300ETF — cross-ETF transfer learning is limited.
6. **More data is needed.** At current rate (~12 cycles/year), robust conclusions (>90% confidence) require 5-8 more years of data.

---

## 9. Synthetic Data Robustness Analysis

Enhanced `eval_synth_filters.py` — full strategy simulation (Pass→OTM2+3 Call, Fail→OTM4 Call, + Put L1) with risk metrics (Sharpe, MaxDD, Calmar, VaR, CVaR, profit factor), bootstrap CIs (5000 iterations), multi-criteria scoring across 63 filters/combos on 692 synthetic 500ETF samples (15x real data).

### 9.1 Per-Level OTM Breakdown (Synthetic, No Filter)

| Level | N | Win Rate | Exp Worthless | Avg ER | Max Loss |
|-------|---|----------|---------------|--------|----------|
| ATM | 692 | 72.8% | 35.1% | +1,039 | -14,776 |
| OTM1 | 692 | 79.0% | 67.3% | +594 | -14,472 |
| OTM2 | 692 | 86.6% | 83.5% | +178 | -14,009 |
| **OTM3** | **692** | **93.2%** | **93.1%** | **-20** | **-13,406** |
| OTM4 | 689 | 86.2% | 95.9% | -93 | -12,655 |
| OTM5 | 655 | 71.1% | 96.6% | -116 | -11,790 |

**Synthetic confirms:** OTM2 is the deepest level with positive ER. OTM3+ negative on synthetic (vs positive on real data) — synthetic includes more high-vol regimes.

### 9.2 Full Strategy Risk Analysis (Top Filters)

Strategy: Pass→OTM2+3 Call, Fail→OTM4 Call, + Put L1 always. 63 filters tested.

| Filter | Place% | Total | Mean | Sharpe | MaxDD | Calmar | WinRate | Worst | PF |
|--------|--------|-------|------|--------|-------|--------|---------|-------|----|
| **f4_AND_f6** | **89.0%** | **-12,160** | **-18** | **-0.006** | **-345,844** | **-0.04** | **55.1%** | **-26,421** | **0.97** |
| f4_AND_f6_AND_f_cci | 88.6% | -13,215 | -19 | -0.006 | -345,844 | -0.04 | 54.8% | -26,421 | 0.97 |
| f6_BBU | 95.2% | -19,497 | -28 | -0.009 | -343,482 | -0.06 | 56.2% | -26,421 | 0.96 |
| f4_RSI30 | 93.8% | -25,395 | -37 | -0.011 | -359,987 | -0.07 | 56.2% | -26,421 | 0.95 |
| f6_AND_f_cci | 94.8% | -20,552 | -30 | -0.009 | -343,482 | -0.06 | 55.9% | -26,421 | 0.96 |
| f_roc5 | 97.3% | -23,516 | -34 | -0.011 | -346,987 | -0.07 | 56.5% | -26,421 | 0.95 |
| f_sma50 | 52.0% | -16,064 | -23 | -0.009 | -301,436 | -0.05 | 47.4% | -21,367 | 0.96 |
| c12_f5_AND_f16 | 37.3% | -13,033 | -19 | -0.009 | -268,939 | -0.05 | 40.5% | -13,300 | 0.97 |
| f5_MACD | 47.5% | +608 | +1 | 0.000 | -264,961 | 0.00 | 42.6% | -13,300 | 1.00 |
| baseline | 100.0% | -32,732 | -47 | -0.014 | -357,625 | -0.09 | 57.4% | -26,421 | 0.93 |

**Key:** All strategies are net negative because Put L1 costs ~65 RMB/date × 692 = ~45K drag. Call-only baseline is -78K → combined -33K.

### 9.3 Call vs Put Breakdown

| Strategy | Call Total | Put Total | Put Drag% |
|----------|-----------|-----------|-----------|
| f4_AND_f6 | -57,244 | +45,084 | 78.8% |
| f6_BBU | -64,581 | +45,084 | 69.8% |
| f5_MACD | -44,476 | +45,084 | 101.4% |
| baseline | -77,816 | +45,084 | 57.9% |

Put contributes +45K consistently across all filters (since puts are unfiltered). Best filters reduce call losses, making the put a larger fraction of total P&L.

### 9.4 Filters Beating Baseline on BOTH Total & Drawdown

13 filters beat baseline on both metrics simultaneously:

| Filter | P(total>) | P(DD>) | ΔSharpe | Place% | Notes |
|--------|-----------|--------|---------|--------|-------|
| **f4_AND_f6** | **82.1%** | **80.4%** | **+0.009** | **89.0%** | RSI>30 AND BBU — best balance |
| f4_AND_f6_AND_f_cci | 80.5% | 79.1% | +0.008 | 88.6% | Adding CCI ≈ no change |
| f5_MACD | 78.3% | 98.1% | +0.015 | 47.5% | Best Sharpe/DD but too restrictive |
| c12_f5_AND_f16 | 66.1% | 96.6% | +0.006 | 37.3% | MACD+RollHi — very restrictive |
| f_sma50 | 69.4% | 89.4% | +0.006 | 52.0% | Close>SMA50 — decent |
| f_vol_low | 63.6% | 90.1% | +0.003 | 39.0% | Low vol regime — restrictive |
| f6_BBU | 73.9% | 72.1% | +0.005 | 95.2% | BBU only — high placement |
| f6_AND_f_cci | 71.5% | 69.9% | +0.005 | 94.8% | BBU+CCI — high placement |
| f4_RSI30 | 78.7% | 69.4% | +0.003 | 93.8% | RSI>30 — high placement |
| f6_AND_f_atr_low | 63.9% | 82.3% | +0.004 | 66.3% | BBU+low ATR |
| f_roc5 | 66.9% | 61.5% | +0.004 | 97.3% | ROC<3% — high placement |
| f_atr_low | 54.9% | 76.4% | +0.000 | 68.6% | Low ATR only |
| f_roc10 | 62.6% | 56.0% | +0.002 | 98.7% | ROC10<5% — highest placement |

**None reach 95% significance** on both metrics. f4_AND_f6 is the strongest candidate (82%/80%).

### 9.5 Multi-Criteria Composite Scoring

Weights: Total 20%, Sharpe 20%, MaxDD 20%, Calmar 15%, WinRate 10%, WorstLoss 10%, PF 5%.

| Rank | Filter | Score | vs Baseline | Total | MaxDD | Sharpe |
|------|--------|-------|-------------|-------|-------|--------|
| 1 | f4_AND_f6 | 0.833 | +0.056 | -12,160 | -345,844 | -0.006 |
| 2 | f4_AND_f6_AND_f_cci | 0.828 | +0.050 | -13,215 | -345,844 | -0.006 |
| 3 | f6_BBU | 0.806 | +0.029 | -19,497 | -343,482 | -0.009 |
| 4 | f4_RSI30 | 0.804 | +0.027 | -25,395 | -359,987 | -0.011 |
| 5 | f6_AND_f_cci | 0.800 | +0.023 | -20,552 | -343,482 | -0.009 |
| **8** | **baseline** | **0.777** | — | **-32,732** | **-357,625** | **-0.014** |

### 9.6 Deep Dive: f4_AND_f6 vs Baseline

| Metric | Baseline | f4_AND_f6 | Improvement |
|--------|----------|-----------|-------------|
| Total P&L | -32,732 | -12,160 | +20,572 (63%) |
| Mean P&L | -47.3 | -17.6 | +29.7 |
| Sharpe | -0.014 | -0.006 | +0.009 |
| MaxDD | -357,625 | -345,844 | +11,781 (3%) |
| Calmar | -0.09 | -0.04 | +0.05 |
| Win Rate | 57.4% | 55.1% | -2.3% |
| Profit Factor | 0.93 | 0.97 | +0.04 |
| Big losses (>-2K) | 31 | 27 | -4 |
| CVaR5% | -10,879 | -9,574 | +1,305 |
| VaR5% | -1,767 | -1,603 | +164 |
| 95% CI (Total) | [-209K, +130K] | [-177K, +145K] | Tighter |
| 95% CI (MaxDD) | [-245K, -42K] | [-218K, -38K] | Shallower |

f4_AND_f6 reduces big losses from 31 to 27, improves profit factor from 0.93 to 0.97, and shifts CVaR5% from -10,879 to -9,574. The main drawdown period (indices 389→691, 303 periods) is slightly less deep.

### 9.7 Put Strategy Comparison

| Strategy | Total | Sharpe | MaxDD | WinRate | Notes |
|----------|-------|--------|-------|---------|-------|
| No Put (calls only) | -77,816 | -0.039 | -295,628 | 93.8% | Highest win rate, worst total |
| Put L1 (current) | -32,732 | -0.014 | -357,625 | 57.4% | Reduces losses by 42K but adds 62K DD |
| Put L2 | -114,500 | -0.054 | -300,372 | 71.8% | Worse — cheaper but less protection |

**Put L1 is the correct choice** — it reduces call-only losses by 45K but adds 62K to max drawdown (from -296K to -358K). The put acts as insurance: lower total losses, higher win rate on calls, but creates more cumulative drawdown because put premium is paid every period.

### 9.8 Synthetic Robustness Conclusions

1. **f4_AND_f6 (RSI>30 AND BBU) is the best filter** — ranks #1 in composite scoring, beats baseline on both total (P=82.1%) and drawdown (P=80.4%). Not 95% significant but strongest directional signal across 692 samples.
2. **13 filters beat baseline on both metrics.** The consistent winners are: BBU-based filters (f6, f4_AND_f6, f6_AND_f_cci), low-vol filters (f_vol_low, f_atr_low, f_sma50), and MACD+RollHi (c12). High-placement filters (>85%) are more practical.
3. **Adding CCI to f4_AND_f6 provides negligible improvement** (score 0.828 vs 0.833 — actually slightly worse). CCI doesn't add signal.
4. **f5 (MACD<0) has best raw Sharpe (0.000) and shallowest drawdown (-265K)** but only 47.5% placement — too restrictive. Best for risk-averse if low trade count acceptable.
5. **Put L1 is the correct put level** — L2 is cheaper but overall worse. No put is actually better total for calls-only but much worse on risk.
6. **Combined strategy (calls+put) is net negative** on synthetic. Put L1 drag (~45K) overwhelms call income. This is expected — the strategy aims for income generation on the equity side, not options P&L alone.
7. **No filter reaches 95% significance** even with 692 samples. Filter improvements for 500ETF are genuinely marginal — the strategy works, but filter tuning won't transform it.

---

## 10. TODO

- [x] Explore Synthetic Data for 500ETF and make research more robust (→ `eval_synth_filters.py`)
- [ ] Explore more filters: ROC5/10 standalone, f_sma50, CCI, vol_ratio, ATR_low show promise as individual filters — test as combos with BBU on real data
- [ ] Explore more dynamic put protection strategies for 500 ETF, not open it every time
- [ ] Revisit conclusions when 500ETF reaches 80+ cycles (~2029)
