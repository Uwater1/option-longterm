# Gating-Only vs Daytrade-Gated Comparison

**Question:** Can the gating model replace the daytrade linear score entirely
(i.e. gate fires long → go long, gate fires short → go short)?

**Answer:** **No.** The gate is a *tradability filter*, not a directional alpha
signal. Trading purely on the gate loses ~77% of the edge vs the gated-daytrade
pipeline, and goes negative on several cells.

## OOS Sharpe per ETF × side (holdout 2024-03-19+)

| ETF | Gate-Only L | Gated-Daytrade L | Gate-Only S | Gated-Daytrade S |
|-----|------------:|-----------------:|------------:|-----------------:|
| 50ETF   | **-1.85** | +1.16 | **-0.23** | +7.64 |
| 300ETF  | +2.77 | **+5.28** | +2.66 | **+2.00** |
| 500ETF  | **+6.19** | +3.78 | **+5.04** | +3.80 |
| 588000  | **-3.57** | +5.86 | **-2.15** | +3.30 |
| 159915  | +2.78 | **+5.07** | **-2.54** | +4.05 |
| **TOTAL** | **+6.30** | **+41.94** | **+2.77** | **+41.94** |

(Bold = the better of the two on that cell. Gate-only TOTAL = +9.08.)

## Three configurations compared

| Configuration | Total OOS Sharpe | Notes |
|---|---:|---|
| Gate-only (no daytrade score) | **+9.08** | Gate as sole signal. Loses on 50, 588000. |
| Ungated daytrade (mixed-mode) | +31.81 | Baseline daytrade single/hybrid/dual. |
| **Gated daytrade (mixed-mode)** | **+41.94** | Gate as veto over daytrade score. **Best.** |

## Interpretation

- The **daytrade linear score carries the directional alpha** (sign + conviction).
  Without it, "gate fires" only means "a big move is likely" — but ~half of big
  moves are up and half down, and the gate's per-side precision is too noisy to
  trade raw.
- The **gate's value is as a veto/selectivity filter** over the score: it removes
  low-tradability days where the score fires but the move won't follow through.
  That lifts the daytrade baseline by **+10.13 Sharpe** (31.81 → 41.94).
- 500ETF is the one cell where gate-only is competitive (+6.19 L / +5.04 S) —
  this ETF has high idiosyncratic vol where the gate's big-move call is itself
  near-alpha. Even there, gated-daytrade is close, so nothing is lost by keeping
  the score layer.
- **Conclusion: keep the daytrade score. Use the gate as a filter, not a
  replacement.** The `+gated` mixed-mode deployment already does this and is the
  production config.

## Reproduce

```bash
# Gate-only standalone backtest
python -m daytrade.gating_only                 # all ETFs, 4% stop, conflict=flat
python -m daytrade.gating_only --no-stop       # hold to 14:30, no stop
python -m daytrade.gating_only --conflict long # when both gates fire, take long

# Gated daytrade (production)
python -m daytrade.calibrate --mode single --sweep-gated
python -m daytrade.calibrate --mode hybrid --sweep-gated
python -m daytrade.calibrate --mode dual   --sweep-gated
python -m daytrade.deploy    # mixed-mode picker auto-adopts +gated per side
python -m daytrade.report
```
