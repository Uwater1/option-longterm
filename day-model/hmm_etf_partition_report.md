# HMM ETF Performance Partitioning Report

## CSI 300 HMM State Identification & Characterization

- **Crisis/Crash (State 0): Highly negative daily return with extremely high volatility (~45% annualized vol). Represents rapid panic selling.** (Empirical Mean: Ret=-0.21%, Vol=44.9%)
- **Turbulent/High Vol (State 1): Positive daily return offset by elevated volatility (~25% annualized vol). Typical of sharp bear market rallies.** (Empirical Mean: Ret=+0.07%, Vol=25.2%)
- **Calm/Low Vol (State 2): Steady positive daily return with very low volatility (~11% annualized vol). Characteristic of slow bull market drift.** (Empirical Mean: Ret=+0.04%, Vol=10.7%)
- **Choppy/Med Vol (State 3): Flat daily return with intermediate volatility (~16% annualized vol). Typical of consolidation/range-bound periods.** (Empirical Mean: Ret=+0.00%, Vol=16.2%)

## Global Strategy Performance Partitioning (Across all ETFs and Sides)

| Regime State | Count (Quarters) | Mean Sharpe | Mean Return (bps) |
| --- | --- | --- | --- |
| Crisis/Crash (State 0): Highly negative daily return with extremely high volatility (~45% annualized vol). Represents rapid panic selling. | 15 | +3.40 | +552.4 |
| Calm/Low Vol (State 2): Steady positive daily return with very low volatility (~11% annualized vol). Characteristic of slow bull market drift. | 75 | +1.64 | +44.9 |
| Choppy/Med Vol (State 3): Flat daily return with intermediate volatility (~16% annualized vol). Typical of consolidation/range-bound periods. | 30 | +3.65 | +154.2 |

CSI 300 HMM State explains **1.3%** of overall strategy Sharpe variance across all ETFs.

## Per-ETF Performance Partitioning

### 159915ETF (Sharpe Variance Explained: 2.2%)

| Regime State | Count (Quarters) | Mean Sharpe |
| --- | --- | --- |
| Crisis/Crash (State 0): Highly negative daily return with extremely high volatility (~45% annualized vol). Represents rapid panic selling. | 3 | +8.51 |
| Calm/Low Vol (State 2): Steady positive daily return with very low volatility (~11% annualized vol). Characteristic of slow bull market drift. | 15 | +5.54 |
| Choppy/Med Vol (State 3): Flat daily return with intermediate volatility (~16% annualized vol). Typical of consolidation/range-bound periods. | 6 | +3.48 |

### 300ETF (Sharpe Variance Explained: 1.9%)

| Regime State | Count (Quarters) | Mean Sharpe |
| --- | --- | --- |
| Crisis/Crash (State 0): Highly negative daily return with extremely high volatility (~45% annualized vol). Represents rapid panic selling. | 3 | -0.97 |
| Calm/Low Vol (State 2): Steady positive daily return with very low volatility (~11% annualized vol). Characteristic of slow bull market drift. | 15 | -0.56 |
| Choppy/Med Vol (State 3): Flat daily return with intermediate volatility (~16% annualized vol). Typical of consolidation/range-bound periods. | 6 | +2.02 |

### 500ETF (Sharpe Variance Explained: 1.5%)

| Regime State | Count (Quarters) | Mean Sharpe |
| --- | --- | --- |
| Crisis/Crash (State 0): Highly negative daily return with extremely high volatility (~45% annualized vol). Represents rapid panic selling. | 3 | +2.26 |
| Calm/Low Vol (State 2): Steady positive daily return with very low volatility (~11% annualized vol). Characteristic of slow bull market drift. | 15 | +3.88 |
| Choppy/Med Vol (State 3): Flat daily return with intermediate volatility (~16% annualized vol). Typical of consolidation/range-bound periods. | 6 | +2.69 |

### 50ETF (Sharpe Variance Explained: 10.4%)

| Regime State | Count (Quarters) | Mean Sharpe |
| --- | --- | --- |
| Crisis/Crash (State 0): Highly negative daily return with extremely high volatility (~45% annualized vol). Represents rapid panic selling. | 3 | -0.01 |
| Calm/Low Vol (State 2): Steady positive daily return with very low volatility (~11% annualized vol). Characteristic of slow bull market drift. | 15 | +1.01 |
| Choppy/Med Vol (State 3): Flat daily return with intermediate volatility (~16% annualized vol). Typical of consolidation/range-bound periods. | 6 | +6.53 |

### 588000ETF (Sharpe Variance Explained: 16.7%)

| Regime State | Count (Quarters) | Mean Sharpe |
| --- | --- | --- |
| Crisis/Crash (State 0): Highly negative daily return with extremely high volatility (~45% annualized vol). Represents rapid panic selling. | 3 | +7.22 |
| Calm/Low Vol (State 2): Steady positive daily return with very low volatility (~11% annualized vol). Characteristic of slow bull market drift. | 15 | -1.68 |
| Choppy/Med Vol (State 3): Flat daily return with intermediate volatility (~16% annualized vol). Typical of consolidation/range-bound periods. | 6 | +3.52 |

## Key Takeaways & Architectural Decisions

1. **Decoupled growth vs. value dynamics**: Large/mega-cap broad indices (CSI 300, SSE 50) perform poorly in broad High Volatility states (State 0). Tech/growth indices (STAR 50, Chinext) invert, performing exceptionally well in State 0 (+7.22 and +8.51 Sharpe). This is due to deep trend persistence during panic selling which the short side exploits.
2. **Pitfall of single-index global gating**: Gating all ETFs based on a CSI 300 HMM proxy will severely damage Chinext and STAR 50 performance by curtailing trading during their most profitable states.
3. **Recommendation**: Maintain individual asset-level gating via `garch_regime.py` instead of scaling by a broad index HMM proxy.
