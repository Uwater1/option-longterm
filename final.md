# Final System Blueprint — Integrated Option & Day-Trading Hedging Engine

Master architectural design, roadmap, and technical specification for the complete JEPI-CN combined investment system.

---

## 1. System Vision & Core Objectives

A unified, multi-layered hedging and income-generation system across liquid ETF markets (300ETF, 500ETF, 50ETF, 159915ETF, 588000ETF):
- **Downside Protection**: Protective puts and intraday options eliminate tail risk ("no panic on crash days").
- **Consistent Cash Flow**: Monthly Covered Calls monetize volatility via IV rank dynamic offset and open-high limit entry.
- **Intraday Alpha**: Day-trading signals (`newtrade` / `day-model`) generate uncorrelated alpha and actively hedge short call positions.
- **Risk-Adjusted Performance**: Superior Sharpe and Sortino ratios with controlled max drawdowns.

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                             INTEGRATED SYSTEM ARCHITECTURE                       │
├──────────────────────────────────────────────────────────────────────────────────┤
│ PART 1: Monthly Covered Call & Put Strategy (Option Overlay Engine)               │
│ • Safe Call Selling (RSI 25-72, BBU filter, IVR scaling)                        │
│ • Stop-Loss & Leg Buyback Rules (protect against sharp rallies)                 │
├──────────────────────────────────────────────────────────────────────────────────┤
│ PART 2: Day-Trading & Intraday Option System (newtrade Alpha Engine)            │
│ • Flexible Entry Window (09:35 – 10:00) & Exit Window (14:20 – 14:55)             │
│ • Intraday Stop-Loss & Midday Reversal Check (13:05 – 13:30)                    │
│ • ETF-to-Option Mapping (convert ETF signals -> long call / put options)        │
│ • Synthetic Short Call Buyback (Part 2 long options hedge Part 1 short calls)    │
└──────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Part 1: Monthly Covered Call & Option Strategy

### Completed / In-Progress Components
1. **Safe Call Entry Filters**:
   - **300ETF**: `25 < RSI < 72` and `MACD < 0`.
   - **500ETF**: `RSI > 30`, `Close < BBU` (Bollinger Upper), `Close > SMA50`.
   - **50ETF**: `30 < RSI < 60`, `ROC10 < 3%`, `Vol20 < Vol20_median`.
2. **IV Rank Dynamic Offset**:
   - High 252d IVR -> wider OTM offset (OTM2/OTM3) to monetize elevated IV.
   - Low 252d IVR -> tighter OTM offset (OTM4) to preserve premium.
3. **Model Limit Order Entry (`--model-offset`)**:
   - Open-to-high P10 bagged LightGBM prediction sets sell limit orders at market open. Achieves **99.0% fill rate** on 300ETF.

### Part 1 TODO & Roadmap
1. **Option Stop-Loss & Assignment Guard**:
   - Dynamic stop-loss trigger when underlying ETF breaches target strike + delta threshold.
   - `roc20` protective exit: buys back short call when 20-day momentum accelerates rapidly.
2. **Leg Buyback Rules**:
   - Take-profit rule: buy back short call when contract retains $< 10\%$ of initial premium collected before cycle expiry.
   - Roll-forward logic: dynamically roll short call to next month when underlying approaches ITM status.

---

## 3. Part 2: Day-Trading & Intraday Option System (`newtrade`)

### Completed Components
1. **Fixed Benchmark Intraday Engine**:
   - Open position at 10:00 (bar 6 open), close position at 14:35 (bar 42 close).
   - Conviction-weighted position sizing ($z_{\text{conviction}} = 0.5$, smooth $\tanh$ scaling).
   - Cost accounting: 8 bps flat friction per position state change.

### Part 2 Roadmap & Execution Upgrades

#### 1. Flexible Execution Windows (Expansion Beyond 10:00–14:35)
- **Early Entry Window (09:35 – 10:00)**:
  - Scans early 5m bars for strong opening drive, microstructure imbalance, and R-Breaker setups.
  - Allows early entry when signal conviction $|z| > 1.0$ to capture early-morning momentum.
- **Late Exit Window (14:20 – 14:55)**:
  - Staggers position exits between 14:20 and 14:55 to minimize market impact slippage.
  - Prevents forced liquidation at 14:35 during favorable late-day trend continuations.

#### 2. Intraday Dynamic Stop-Loss System
- **Hard Price Stop**: Exit immediately if intraday trade drawdown exceeds $-0.8\%$ from entry price.
- **Volatility Trailing Stop**: Trailing stop set at $1.5 \times \text{ATR}_{5\text{m}}$ from peak intraday favorable price.
- **Time Stop**: Exit position if trade stays flat ($|r_{\text{trade}}| < 0.1\%$) after 12 consecutive 5m bars.

#### 3. Midday Reversal Decision Engine (13:05 – 13:30)
- **Rationale**: Market frequently undergoes trend reversal or momentum exhaustion post-lunch re-open (13:00–13:30).
- **Logic**:
  - Evaluate signal direction against 13:05–13:30 price action.
  - If signal is Long but 13:00–13:20 return $< -0.3\%$, trigger early exit at 13:30 to lock in early morning gains or limit losses.

#### 4. Intraday ETF-to-Option Mapping Engine
- Translates simulated ETF directional signals ($z > 0.5 \implies \text{Long}$, $z < -0.5 \implies \text{Short}$) into liquid option trades:
  - **Long ETF Signal** $\implies$ Buy OTM1 / ATM Call Option (capped risk, high intraday delta leverage).
  - **Short ETF Signal** $\implies$ Buy OTM1 / ATM Put Option (downside profit without shorting ETF shares).
- Option selection: Front-month liquid contracts with $\text{DTE} \ge 7$ days and tight bid-ask spreads.

#### 5. Integrated Master Intraday Execution Timeline
```
09:35 - 10:00 │ Signal Scanning & Early Entry Window
              │ • Microstructure & R-Breaker trigger check
              │ • Open Long Call / Long Put if |z| > 0.5
──────────────┼──────────────────────────────────────────────────
10:00 - 13:05 │ Core Trend Hold & Active Trailing Stop
              │ • Monitor 1.5x ATR 5m trailing stop
──────────────┼──────────────────────────────────────────────────
13:05 - 13:30 │ Midday Reversal Decision Check
              │ • Early exit if lunch session contradicts entry signal
──────────────┼──────────────────────────────────────────────────
14:20 - 14:55 │ Staggered Profit-Take & Market Close Exit
              │ • Fully close all intraday option / ETF positions
```

---

## 4. System Synergy: Cross-Module Call Buyback & Hedging

The core advantage of combining **Part 1** and **Part 2**:

1. **Short Call Protection via Intraday Long Calls**:
   - When Part 1 holds a short monthly call and Part 2 generates a strong bullish signal ($z > 1.0$), Part 2 buys intraday call options.
   - If the market rallies sharply, Part 2's long call gains offset Part 1's short call assignment loss.

2. **Capital & Margin Efficiency**:
   - Intraday option buying requires low cash outlay compared to underlying ETF positions.
   - Part 1 monthly call premium finances Part 2 intraday option trades.

---

## 5. Implementation Roadmap & Checklist

- [x] Part 1: Covered Call safe entry filters (RSI, BBU, MACD).
- [x] Part 1: Open-to-high P10 limit order model (`--model-offset`).
- [x] Part 2: Fixed 10:00–14:35 baseline day-trading engine (`day-model-new` / `newtrade`).
- [ ] **Part 1 Upgrade**: Implement short call stop-loss & premium take-profit buyback (<10% residual value).
- [ ] **Part 2 Upgrade 1**: Early entry window (09:35–10:00) & late exit window (14:20–14:55).
- [ ] **Part 2 Upgrade 2**: Intraday dynamic stop-loss & trailing ATR stop.
- [ ] **Part 2 Upgrade 3**: Midday reversal exit logic (13:05–13:30 check).
- [ ] **Part 2 Upgrade 4**: ETF-to-Option trade execution translator (Long Call / Long Put buying).
- [ ] **Integration**: Combined backtest engine linking Part 1 monthly short calls with Part 2 intraday long option hedges.