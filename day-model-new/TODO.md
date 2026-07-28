
## TODO: Tighten B4 Correlation Gate (from newtrade downstream evidence)

**Date**: 2026-07-28
**Source**: `newtrade/test_feature_count.py` + `newtrade/diagnose_correlation.py`

### Problem
500ETF admitted pool has 32 features. Downstream EW trading shows:
- Top-5 features → OOS Sharpe = 0.614
- All-32 features → OOS Sharpe = 0.238 (2.6× worse)

The bottom 22 features aren't bad individually (all passed B3), but equal-weighting them dilutes the top-5 signal into noise.

### Correlation evidence (500ETF, signed standardized)
- Mean pairwise |r| = **0.47** (very high)
- 192/496 pairs (39%) have |r| ≥ 0.60
- 10 pairs have |r| ≥ 0.85
- Max |r| = 0.89

Compare 159915ETF (11 features): mean |r| = 0.62 but works great (OOS SR=1.085). Fewer features + high corr = strong consensus. Many features + moderate corr = noise accumulation.

### Code discrepancy
- `plan.md` line 163 says θ=0.70 was set
- `select_features.py` line 39: `DEFAULT_THETA = 0.85` ← **still 0.85 in code**
- B6b adaptive gate (TIGHT_THETA=0.75) only fires when pool > 35. 500ETF has 32 → never triggers.

### Recommended fix
1. **Set `DEFAULT_THETA = 0.70` in code** (match what plan says was done)
3. Do NOT force diversity — low-corr features can be the weak ones (see Q2 below)

### Impact
Re-running `select_features.py` with θ=0.70 on 500ETF should cut pool from 32 → ~10-12 features. Downstream EW should improve from OOS 0.238 → ~0.6-0.7.

---

### Downstream Feature Selection Research (newtrade/research_feature_selection.py)

#### Q1: Feature Count Sweet Spot

| ETF | Best N | OOS SR | Cliff |
|-----|--------|--------|-------|
| 500ETF | **7-9** | 0.717-0.723 | Sharp drop at N=12 (0.328) |
| 159915ETF | **5-11** | 1.085-1.260 | No cliff; all work |
| 300ETF | **9-10** | 0.440-0.698 | Needs nearly all; top-5 dead (0.057) |

500ETF granular: top-3=0.690, top-5=0.614, top-7=**0.717**, top-9=**0.723**, top-10=0.613, top-12=0.328, top-32=0.238.

**Takeaway**: Target pool size **10-12** for 500ETF. 159915ETF is fine at 11. 300ETF needs all 10.

#### Q2: Low-Correlation ≠ Better

| ETF | Low-corr top-5 | High-corr top-5 | IC top-5 |
|-----|---------------|----------------|----------|
| 500ETF | 0.057 (dead, 44 trades) | 0.582 | **0.614** |
| 159915ETF | **1.249** | 1.037 | 1.260 |
| 300ETF | **0.493** | 0.062 | 0.057 |

**Insight**: For 500ETF, the low-corr features are the WEAK ones (low IC, barely generate trades). The high-corr features are strong — correlated because they capture the same real signal. For 300ETF, diversity genuinely helps.

**Rule for B4 gate**: The corr gate should remove redundant copies of the SAME signal (e.g., tri_min vs rank_min of same primitives, |r|=0.88). It should NOT force artificial diversity by keeping weak independent features. IC-quality first, then prune redundancy.

#### Q3: Regime-Adaptive Feature Selection = BAD

| ETF | Adaptive top-5 | Adaptive top-10 | Fixed top-5 | Fixed top-10 |
|-----|---------------|----------------|-------------|--------------|
| 500ETF | 0.120 | 0.100 | **0.614** | **0.613** |
| 159915ETF | 0.398 | 0.854 | **1.260** | 0.994 |

Feature ranking stability (500ETF top-5 year-over-year overlap): **0-3/5**. Rankings completely reshuffle annually. Adaptive selection chases yesterday's winners.

159915ETF: 2-4/5 overlap — more stable, but adaptive still loses to fixed.

**Verdict**: Do NOT implement rolling/adaptive feature selection downstream. Fixed pool + EW is superior. This validates the current design: select features once at admission, never re-rank.

#### Q4: Smart Weighting Can't Fix Large Pools

500ETF all-32:
- EW: 0.238 | IC-weighted: 0.108 (worse!) | Sqrt-IC: 0.224 | Inv-corr: 0.290 | IC×InvCorr: **0.362**

300ETF all-10:
- EW: 0.440 | IC-weighted: **0.671** | Inv-corr: **0.662** | Sqrt-IC: 0.656

159915ETF all-11:
- EW: 1.085 | IC-weighted: 1.101 | Inv-corr: **1.151** | IC×InvCorr: 0.977

**Verdict**: For large pools (32), no weighting fixes dilution — cut features. For small pools (10-11), IC-weighting gives +0.2 boost. After corr gate fix, downstream should use ICW for 300ETF and EW for 159915ETF.

#### Summary of Recommendations for day-model-new

1. **θ=0.70, MAX_POOL_SIZE=15** — hits the 7-12 sweet spot
2. **Quality-first, then prune redundancy** — don't sacrifice IC for diversity
3. **No adaptive/rolling selection downstream** — rankings are unstable
4. **Small pools (≤12) are ideal** — 159915ETF (11 features) is the gold standard
5. **GLM/Ridge: low priority** — if pool is already 10-12, EW or ICW suffices
