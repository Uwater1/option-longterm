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

## 8. TODO

- [ ] Test early roll management for 500ETF — roll calls to higher strikes if underlying rallies >5% mid-cycle
- [ ] Explore weekly options for 500ETF if available — shorter DTE reduces rally exposure
