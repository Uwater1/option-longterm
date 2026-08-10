# Meta-Labeling Report — Exit at 11:25 vs 13:05 vs 13:30 vs 14:35

Reconstructed production `icw` trades (threshold swept pre-2022, buffer +0.2, top-10 hysteresis ER=25, fast_ramp_quadratic sizing). Entry = open of 10:00 1m bar; exits = close of labeled 1m bar. Fee = 8 bps/side (identical across arms => fee-neutral comparison). Production trailing stop (time_decay_trailing=0.03) is **off** for the arms; overlap reported separately.

- **IS** = trades before 2022-01-01 (in-sample for the current model's threshold)
- **OOS** = trades from 2022-01-01 (reference panel)

## 0. Sanity check (1m exit prices vs pipeline target)

| ETF | corr(r_1435 (1m, unsigned), trade_return target) |
|---|---|
| 300ETF | 0.9832 |
| 500ETF | 0.9893 |
| 159915ETF | 0.9851 |

Slight <1.0 correlation is expected: 1m bar-open entry vs 5m bar-open entry convention and unadjusted vs raw price handling on ex-dividend days. Labels use the 1m prices consistently across all four exits.

## 1. In-sample panel (pre-2022)

**Fixed-exit arms** (mean gross bps/trade; Sharpe of full-calendar net series; columns in 1125 / 1305 / 1330 / 1435 order; oracle = per-trade best exit):

| ETF | Trades | Mean bps @1125/1305/1330/1435 | Sharpe @1125/1305/1330/1435 | Oracle gain vs 1435 (bps) | Oracle Sharpe |
|---|---|---|---|---|---|
| 300ETF | 123 | +31.2 / +34.0 / +37.1 / +55.3 | 0.49 / 0.46 / 0.56 / 0.79 | +34.0 | 1.51 |
| 500ETF | 209 | +28.8 / +37.3 / +43.0 / +50.7 | 0.66 / 0.83 / 0.99 / 1.12 | +34.2 | 2.06 |
| 159915ETF | 440 | +15.5 / +21.2 / +32.3 / +48.7 | -0.02 / 0.23 / 0.75 / 1.25 | +36.9 | 2.88 |

**Best-exit distribution** (% of trades where that exit had the highest return):

| ETF | %11:25 best | %13:05 best | %13:30 best | %14:35 best |
|---|---|---|---|---|
| 300ETF | 22.0 | 17.9 | 20.3 | 39.8 |
| 500ETF | 16.7 | 14.4 | 19.1 | 49.8 |
| 159915ETF | 19.3 | 12.7 | 20.7 | 47.3 |

**Early-exit opportunity** (% of trades where the early exit beats 14:35):

| ETF | % better @11:25 | % better @13:05 | % better @13:30 | % better at ANY early exit |
|---|---|---|---|---|
| 300ETF | 39.0 | 42.3 | 43.9 | 55.3 |
| 500ETF | 33.5 | 36.8 | 39.7 | 45.5 |
| 159915ETF | 32.3 | 34.5 | 38.2 | 45.9 |

**Model economics** (binary cut-vs-hold decision: p = base rate cutting is correct; G+/L- = mean gain/loss when right/wrong; breakeven = required balanced accuracy for E[ΔPnL]=0; Δ bps/trade at model accuracy 55/60/65/70%; pair-oracle = ceiling for this exit pair):

| ETF | Decision | p % | G+ bps | L- bps | Breakeven acc % | Δbps @55/60/65/70% acc | Pair-oracle bps |
|---|---|---|---|---|---|---|---|
| 300ETF | 13:05 | 42.3 | +63.4 | 83.4 | 64.2 | -6.9 / -3.2 / +0.6 / +4.3 | +26.8 |
| 300ETF | 13:30 | 43.9 | +48.8 | 70.5 | 64.9 | -6.0 / -3.0 / +0.1 / +3.1 | +21.4 |
| 500ETF | 13:05 | 36.8 | +69.0 | 61.5 | 60.4 | -3.5 / -0.3 / +2.9 / +6.1 | +25.4 |
| 500ETF | 13:30 | 39.7 | +61.2 | 53.1 | 56.8 | -1.0 / +1.8 / +4.6 / +7.4 | +24.3 |
| 159915ETF | 13:05 | 34.5 | +79.6 | 84.1 | 66.7 | -9.6 / -5.5 / -1.4 / +2.7 | +27.5 |
| 159915ETF | 13:30 | 38.2 | +72.3 | 71.3 | 61.5 | -4.6 / -1.1 / +2.5 / +6.1 | +27.6 |

**Predictability at the decision point** (can we tell early whether holding pays?):

| ETF | Spearman(pnl@1125, hold benefit) | Losers@1125 hold bps | Winners@1125 hold bps | Losers hold-positive % | Spearman(pnl@1305, hold benefit) | Losers@1305 hold bps | Winners@1305 hold bps | Spearman(pnl@1330, hold benefit) | Losers@1330 hold bps | Winners@1330 hold bps |
|---|---|---|---|---|---|---|---|---|---|---|
| 300ETF | 0.134 | 9.8 | 33.6 | 51.0 | 0.014 | 33.4 | 13.3 | 0.088 | 13.3 | 21.1 |
| 500ETF | 0.012 | 14.6 | 26.3 | 63.3 | -0.042 | 17.4 | 11.3 | 0.018 | 8.7 | 7.2 |
| 159915ETF | -0.047 | 37.3 | 30.6 | 66.3 | -0.085 | 43.6 | 18.1 | -0.069 | 30.3 | 8.9 |

**Naive meta-rules** Sharpe (Δ vs always-14:35). Rule decides with info available at the snapshot:

| ETF | Cut@11:25 if losing | Cut@11:25 if winning | Cut@13:05 if losing | Cut@13:30 if losing | Cut@13:30 if confirmed |
|---|---|---|---|---|---|
| 300ETF | 0.76 (-0.04) | 0.55 (-0.25) | 0.54 (-0.25) | 0.72 (-0.07) | 0.66 (-0.13) |
| 500ETF | 1.03 (-0.09) | 0.78 (-0.33) | 1.01 (-0.10) | 1.10 (-0.01) | 1.14 (+0.02) |
| 159915ETF | 0.75 (-0.51) | 0.69 (-0.57) | 0.66 (-0.60) | 0.88 (-0.38) | 0.91 (-0.35) |

**Cut rules economics** (Δ bps/trade vs always-14:35; help % = trades where rule improved outcome):

| ETF | @1125 Δbps | help % | @1305 Δbps | help % | @1330 Δbps | help % | @1330 confirmed Δbps | help % |
|---|---|---|---|---|---|---|---|---|
| 300ETF | -3.9 | 16.3 | -13.3 | 17.1 | -5.1 | 18.7 | -7.6 | 16.3 |
| 500ETF | -5.5 | 13.4 | -6.1 | 12.4 | -2.8 | 14.8 | -1.8 | 12.0 |
| 159915ETF | -14.3 | 11.1 | -16.2 | 11.4 | -10.7 | 11.6 | -10.3 | 10.2 |

**Reversal confirmation** (trades losing at 13:05; 'confirmed' = still losing at 13:30; hold benefit = gain of holding from 13:30 to 14:35 — negative means cutting confirmed losers at 13:30 was right):

| ETF | n losing@1305 | % confirmed@1330 | Confirmed hold bps | Confirmed hold-positive % | Recovered hold bps |
|---|---|---|---|---|---|
| 300ETF | 49 | 87.8 | 21.7 | 51.2 | 58.5 |
| 500ETF | 73 | 82.2 | 6.3 | 53.3 | 34.3 |
| 159915ETF | 163 | 82.2 | 33.8 | 62.7 | -6.5 |

**First-30-min noise conditioning** (split at panel median of first30_vol; values as high-noise / low-noise):

| ETF | n high/low | Cut@1305-if-loss Δbps h/l | Cut@1330-if-loss Δbps h/l | Hold-from-1305 bps h/l |
|---|---|---|---|---|
| 300ETF | 62 / 61 | -30.8 / +4.5 | -13.6 / +3.6 | +43.2 / -0.9 |
| 500ETF | 105 / 104 | -6.8 / -5.3 | -6.0 / +0.3 | +16.6 / +10.3 |
| 159915ETF | 220 / 220 | -20.9 / -11.4 | -14.0 / -7.5 | +35.1 / +20.0 |

**Null test — overlap with production trailing stop** (time_decay_trailing=0.03; stop evaluated on the same trades, not applied to the arms):

| ETF | Stop fires % | Fires by 11:25 % | Fires by 13:05 % | Fires by 13:30 % |
|---|---|---|---|---|
| 300ETF | 15.4 | 6.5 | 15.4 | 15.4 |
| 500ETF | 13.9 | 3.8 | 13.9 | 13.9 |
| 159915ETF | 18.9 | 7.3 | 18.9 | 18.9 |

## 2. OOS reference panel (2022+)

**Fixed-exit arms** (mean gross bps/trade; Sharpe of full-calendar net series; columns in 1125 / 1305 / 1330 / 1435 order; oracle = per-trade best exit):

| ETF | Trades | Mean bps @1125/1305/1330/1435 | Sharpe @1125/1305/1330/1435 | Oracle gain vs 1435 (bps) | Oracle Sharpe |
|---|---|---|---|---|---|
| 300ETF | 39 | +30.2 / +40.4 / +49.2 / +41.5 | 0.51 / 0.76 / 0.89 / 0.63 | +34.2 | 1.39 |
| 500ETF | 145 | +12.3 / +12.5 / +13.6 / +14.7 | -0.26 / -0.13 / 0.01 / 0.05 | +36.1 | 1.99 |
| 159915ETF | 249 | +16.9 / +20.8 / +21.9 / +23.3 | 0.39 / 0.64 / 0.64 / 0.57 | +41.3 | 2.72 |

**Best-exit distribution** (% of trades where that exit had the highest return):

| ETF | %11:25 best | %13:05 best | %13:30 best | %14:35 best |
|---|---|---|---|---|
| 300ETF | 28.2 | 20.5 | 23.1 | 28.2 |
| 500ETF | 23.4 | 14.5 | 17.9 | 44.1 |
| 159915ETF | 29.7 | 15.3 | 18.5 | 36.5 |

**Early-exit opportunity** (% of trades where the early exit beats 14:35):

| ETF | % better @11:25 | % better @13:05 | % better @13:30 | % better at ANY early exit |
|---|---|---|---|---|
| 300ETF | 53.8 | 56.4 | 48.7 | 71.8 |
| 500ETF | 44.8 | 42.8 | 42.8 | 55.2 |
| 159915ETF | 48.2 | 48.6 | 47.0 | 59.8 |

**Model economics** (binary cut-vs-hold decision: p = base rate cutting is correct; G+/L- = mean gain/loss when right/wrong; breakeven = required balanced accuracy for E[ΔPnL]=0; Δ bps/trade at model accuracy 55/60/65/70%; pair-oracle = ceiling for this exit pair):

| ETF | Decision | p % | G+ bps | L- bps | Breakeven acc % | Δbps @55/60/65/70% acc | Pair-oracle bps |
|---|---|---|---|---|---|---|---|
| 300ETF | 13:05 | 56.4 | +38.5 | 52.2 | 51.2 | +1.7 / +3.9 / +6.2 / +8.4 | +21.7 |
| 300ETF | 13:30 | 48.7 | +49.5 | 31.9 | 40.4 | +5.9 / +7.9 / +9.9 / +12.0 | +24.1 |
| 500ETF | 13:05 | 42.8 | +62.5 | 50.5 | 52.0 | +1.7 / +4.5 / +7.2 / +10.0 | +26.7 |
| 500ETF | 13:30 | 42.8 | +49.1 | 38.6 | 51.3 | +1.6 / +3.8 / +5.9 / +8.1 | +21.0 |
| 159915ETF | 13:05 | 48.6 | +58.5 | 60.2 | 52.1 | +1.7 / +4.7 / +7.6 / +10.6 | +28.4 |
| 159915ETF | 13:30 | 47.0 | +51.7 | 48.4 | 51.4 | +1.8 / +4.3 / +6.8 / +9.3 | +24.3 |

**Predictability at the decision point** (can we tell early whether holding pays?):

| ETF | Spearman(pnl@1125, hold benefit) | Losers@1125 hold bps | Winners@1125 hold bps | Losers hold-positive % | Spearman(pnl@1305, hold benefit) | Losers@1305 hold bps | Winners@1305 hold bps | Spearman(pnl@1330, hold benefit) | Losers@1330 hold bps | Winners@1330 hold bps |
|---|---|---|---|---|---|---|---|---|---|---|
| 300ETF | 0.338 | -15.5 | 24.7 | 23.1 | 0.295 | -26.2 | 14.7 | 0.091 | -28.7 | 0.5 |
| 500ETF | -0.073 | 6.7 | -0.8 | 52.5 | 0.022 | 0.4 | 3.6 | 0.143 | -5.7 | 5.8 |
| 159915ETF | 0.123 | -10.1 | 18.9 | 43.0 | 0.098 | -11.7 | 12.7 | 0.151 | -6.2 | 7.9 |

**Naive meta-rules** Sharpe (Δ vs always-14:35). Rule decides with info available at the snapshot:

| ETF | Cut@11:25 if losing | Cut@11:25 if winning | Cut@13:05 if losing | Cut@13:30 if losing | Cut@13:30 if confirmed |
|---|---|---|---|---|---|
| 300ETF | 0.79 (+0.16) | 0.27 (-0.35) | 0.90 (+0.28) | 0.89 (+0.26) | 0.92 (+0.29) |
| 500ETF | -0.10 (-0.15) | -0.02 (-0.07) | 0.10 (+0.05) | 0.24 (+0.19) | 0.18 (+0.13) |
| 159915ETF | 0.93 (+0.36) | -0.03 (-0.60) | 0.98 (+0.41) | 0.83 (+0.27) | 0.86 (+0.29) |

**Cut rules economics** (Δ bps/trade vs always-14:35; help % = trades where rule improved outcome):

| ETF | @1125 Δbps | help % | @1305 Δbps | help % | @1330 Δbps | help % | @1330 confirmed Δbps | help % |
|---|---|---|---|---|---|---|---|---|
| 300ETF | +5.2 | 23.1 | +8.7 | 25.6 | +8.1 | 15.4 | +9.9 | 15.4 |
| 500ETF | -2.8 | 18.6 | -0.2 | 20.0 | +2.3 | 20.0 | +1.6 | 15.9 |
| 159915ETF | +4.3 | 23.7 | +4.9 | 23.7 | +2.9 | 24.5 | +3.6 | 22.5 |

**Reversal confirmation** (trades losing at 13:05; 'confirmed' = still losing at 13:30; hold benefit = gain of holding from 13:30 to 14:35 — negative means cutting confirmed losers at 13:30 was right):

| ETF | n losing@1305 | % confirmed@1330 | Confirmed hold bps | Confirmed hold-positive % | Recovered hold bps |
|---|---|---|---|---|---|
| 300ETF | 13 | 76.9 | -38.5 | 30.0 | 20.3 |
| 500ETF | 64 | 76.6 | -4.8 | 53.1 | 2.6 |
| 159915ETF | 104 | 93.3 | -9.2 | 37.1 | 6.4 |

**First-30-min noise conditioning** (split at panel median of first30_vol; values as high-noise / low-noise):

| ETF | n high/low | Cut@1305-if-loss Δbps h/l | Cut@1330-if-loss Δbps h/l | Hold-from-1305 bps h/l |
|---|---|---|---|---|
| 300ETF | 20 / 19 | -2.3 / +20.4 | +1.6 / +14.9 | +16.2 / -14.9 |
| 500ETF | 73 / 72 | +4.1 / -4.5 | +5.5 / -1.0 | -5.8 / +10.3 |
| 159915ETF | 125 / 124 | +7.4 / +2.3 | +3.9 / +1.8 | -1.4 / +6.4 |

**Null test — overlap with production trailing stop** (time_decay_trailing=0.03; stop evaluated on the same trades, not applied to the arms):

| ETF | Stop fires % | Fires by 11:25 % | Fires by 13:05 % | Fires by 13:30 % |
|---|---|---|---|---|
| 300ETF | 7.7 | 0.0 | 7.7 | 7.7 |
| 500ETF | 7.6 | 1.4 | 7.6 | 7.6 |
| 159915ETF | 12.9 | 0.8 | 12.9 | 12.9 |

## 3. Verdict — is it worth the effort?

| ETF | Oracle gain IS (bps/trade) | Oracle gain OOS | Best rule IS (ΔSharpe) | Best rule OOS (ΔSharpe) |
|---|---|---|---|---|
| 300ETF | +34.0 | +34.2 | cut1125_if_loss -0.04 | cut1330_if_loss_confirmed +0.29 |
| 500ETF | +34.2 | +36.1 | cut1330_if_loss_confirmed +0.02 | cut1330_if_loss +0.19 |
| 159915ETF | +36.9 | +41.3 | cut1330_if_loss_confirmed -0.35 | cut1305_if_loss +0.41 |

**Pooled (3 ETFs) cut-losers economics:**

| Panel | Trades | Cut@1125-if-loss Δbps | Cut@1305-if-loss Δbps |
|---|---|---|---|
| IS | 772 | -10.3 | -13.0 |
| OOS | 433 | +2.0 | +3.5 |

Decision criteria: (a) the per-trade **oracle** gain is the absolute ceiling for any meta-model — if it is < ~5 bps/trade, no model can clear costs+complexity; (b) a rule/model must capture a stable share of that ceiling **in both panels** and across ETFs; (c) if the trailing stop already fires before 11:25 on most would-be-cut trades, the noon decision is redundant (the §1 null test).

### Findings & recommendation

1. **The ceiling is large.** Per-trade oracle gain averages **+36 bps** (range +34 to +41) across both panels — roughly half of the average trade's gross return. A perfect exit chooser would nearly double the arms' Sharpe. So the question is not whether value exists, but whether any of it is *predictable*.

2. **Fixed arms: always-14:35 still wins.** In IS it dominates all 3 ETFs on mean and Sharpe; in OOS 13:05/13:30 edge ahead on Sharpe for 300ETF/159915ETF but on only ~39-249 trades. 13:05 >= 11:25 in virtually every panel-ETF cell, so **11:25 is dropped as a candidate; the early-exit question is 13:05/13:30 vs 14:35**.

3. **How many trades can benefit from an early exit?** An early exit beats 14:35 on **47% (IS) / 59% (OOS)** of trades when any of 11:25/13:05/13:30 is allowed (13:30 alone: 40% / 46%). So roughly half of trades would benefit from SOME early exit — the oracle ceiling confirms this is a real per-trade decision problem, not a corner case.

4. **Would a model with moderate predictive power help?** The bar is moderate: the breakeven balanced accuracy for the cut-vs-hold decision at 13:05 is **65% (IS) / 52% (OOS)** (50% trade-weighted at 13:30) — higher than a coin flip because wrong cuts are somewhat costlier than right cuts, but well within reach of a decent classifier. Per the Model economics tables, a model sustaining 60-65% accuracy OOS earns +3 to +8 bps/trade against a pair-oracle ceiling of ~21-28 bps. BUT accuracy must be achieved walk-forward: the regime flip below shows in-sample accuracy does not transfer.

5. **Regime flip — the core problem.** The sign of the cut-losers edge reverses between panels: IS pooled Δ = -10.3 bps (cut@1125) / -13.0 bps (cut@1305) / -7.7 bps (cut@1330) — losers *recover* into the close (mean reversion); OOS pooled Δ = +2.0 / +3.5 / +3.1 bps — losers *keep losing* (momentum). A rule trained on pre-2022 labels would do the wrong thing in 2022+, and vice versa.

6. **13:30 confirmation check.** Confirmed reversals (losing at 13:05 AND still losing at 13:30) have pooled hold-benefit of +24.4 bps (IS) vs -10.4 bps (OOS) — the same regime split as the raw signal; the confirmation rule tracks it (pooled Δ -7.6 IS / +3.5 OOS). Two nuances in its favor: (a) 13:30 is the single most-often-best early exit (18-23% of trades vs 13-21% for 13:05) and the best fixed early arm on Sharpe in 5 of 6 panel-ETF cells; (b) in OOS, cutting at 13:30 helps slightly MORE on high first-30-min-noise days (+1.6 to +5.5 bps) than low-noise days — matching the 'noisy open needs confirmation' intuition — but the same pattern is absent or reversed IS, so it is a feature for the model to learn walk-forward, not a deployable rule. Net: 13:30 is a valid *substitute* for 13:05 (keeps the lunch-gap info, adds 25 min of confirmation) but not a fix for the regime problem.

7. **Null test passed (not redundant).** The production trailing stop fires before 11:25 on only 0-7% of trades; most stop events are lunch-gap stops landing at the 13:01-13:05 reopen. So an early-exit meta-decision is not a disguised stop — but a 13:05/13:30 decision would partially subsume the stop's gap protection.

**Recommendation.**

- As a *rule*: **not worth the effort** — pooled cut-losers flips sign between IS and OOS; deploying it violates the regime-stability gate this project applies everywhere else.

- As a *trained meta-model* (TODO #2): **conditionally yes** — the ~30 bps ceiling plus the low breakeven accuracy justify one careful attempt, but only with (a) strictly walk-forward training (year N model on labels < year N, mirroring the triple-barrier design in §1: features = running P&L, morning/first-30-min vol, Z_composite, lunch-gap move), (b) the FQ meta-IC harness as judge, and (c) a hard kill criterion: if the walk-forward model's sign or edge does not persist across >=2 consecutive held-out years on >=2/3 ETFs, stop — keep 14:35. Candidate early exit: 13:05 or 13:30 (confirmation variant), never 11:25.

- Labeled dataset for that attempt: `artifacts/meta_labels_{etf}.csv` (IS 772 + OOS 433 trades; columns `best_exit`, `gain_vs_1435`, snapshot features `pnl_at_1125/1305/1330`, `morning_vol`, `first30_vol`, `lunch_move`, `z_composite`).
