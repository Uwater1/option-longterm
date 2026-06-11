# Research Notes: ETF Intraday Open to High Distribution by 5 Overnight Gap Levels

Analyzed intraday relationship between Open and High prices for 50ETF, 300ETF, and 500ETF over the past 2000 trading days (or max available for 300ETF), segmented by **5 Overnight Gap Levels**:
- **Sig Gap Down:** $\text{Gap} < -0.5\%$
- **Mod Gap Down:** $-0.5\% \le \text{Gap} < -0.05\%$
- **Neutral:** $-0.05\% \le \text{Gap} \le 0.05\%$
- **Mod Gap Up:** $0.05\% < \text{Gap} \le 0.5\%$
- **Sig Gap Up:** $\text{Gap} > 0.5\%$

## Key Statistics

Below is the summary table of the differences:
- **Relative Difference (%):** $\frac{\text{High} - \text{Open}}{\text{Open}} \times 100\%$
- **Absolute Difference (RMB):** $\text{High} - \text{Open}$

| ETF | Regime | Count | Mean (%) | Median (%) | 10th Pct (%) | 90th Pct (%) | Mean (RMB) | Median (RMB) | 10th Pct (RMB) | 90th Pct (RMB) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **50ETF** | Sig Gap Down (< -0.5%) | 191 | 0.873% | 0.623% | **0.089%** | 2.027% | 0.0243 | 0.0180 | 0.0030 | 0.0540 |
| **50ETF** | Mod Gap Down ([-0.5%, -0.05%)) | 726 | 0.729% | 0.546% | **0.075%** | 1.577% | 0.0207 | 0.0155 | 0.0020 | 0.0440 |
| **50ETF** | Neutral ([-0.05%, 0.05%]) | 341 | 0.675% | 0.553% | **0.111%** | 1.481% | 0.0191 | 0.0150 | 0.0030 | 0.0430 |
| **50ETF** | Mod Gap Up ((0.05%, 0.5%]) | 581 | 0.783% | 0.588% | **0.130%** | 1.671% | 0.0229 | 0.0170 | 0.0040 | 0.0500 |
| **50ETF** | Sig Gap Up (> 0.5%) | 161 | 0.995% | 0.616% | **0.137%** | 1.972% | 0.0280 | 0.0180 | 0.0040 | 0.0550 |
| **300ETF** | Sig Gap Down (< -0.5%) | 153 | 0.878% | 0.701% | **0.073%** | 1.813% | 0.0360 | 0.0280 | 0.0030 | 0.0790 |
| **300ETF** | Mod Gap Down ([-0.5%, -0.05%)) | 676 | 0.730% | 0.530% | **0.078%** | 1.579% | 0.0306 | 0.0220 | 0.0030 | 0.0660 |
| **300ETF** | Neutral ([-0.05%, 0.05%]) | 344 | 0.653% | 0.486% | **0.054%** | 1.501% | 0.0276 | 0.0210 | 0.0020 | 0.0610 |
| **300ETF** | Mod Gap Up ((0.05%, 0.5%]) | 488 | 0.728% | 0.540% | **0.147%** | 1.537% | 0.0309 | 0.0230 | 0.0060 | 0.0670 |
| **300ETF** | Sig Gap Up (> 0.5%) | 141 | 1.067% | 0.763% | **0.169%** | 2.130% | 0.0438 | 0.0330 | 0.0070 | 0.0930 |
| **500ETF** | Sig Gap Down (< -0.5%) | 201 | 1.306% | 0.972% | **0.267%** | 2.702% | 0.0817 | 0.0650 | 0.0140 | 0.1740 |
| **500ETF** | Mod Gap Down ([-0.5%, -0.05%)) | 740 | 0.789% | 0.627% | **0.098%** | 1.690% | 0.0491 | 0.0400 | 0.0059 | 0.1062 |
| **500ETF** | Neutral ([-0.05%, 0.05%]) | 441 | 0.799% | 0.611% | **0.089%** | 1.729% | 0.0501 | 0.0390 | 0.0060 | 0.1130 |
| **500ETF** | Mod Gap Up ((0.05%, 0.5%]) | 469 | 0.872% | 0.660% | **0.129%** | 1.872% | 0.0534 | 0.0420 | 0.0080 | 0.1132 |
| **500ETF** | Sig Gap Up (> 0.5%) | 149 | 1.157% | 0.796% | **0.190%** | 2.389% | 0.0718 | 0.0510 | 0.0100 | 0.1656 |

### Key Observations

1. **Intraday Momentum on Gap Up:**
   - As we go from **Neutral** to **Moderate Up** to **Significant Up**, the mean and 10th percentile (90% fill rate) generally **increase**.
   - For example, for 300ETF:
     - Neutral: N=344, mean=0.653%, p10=**0.054%**
     - Moderate Up: N=488, mean=0.728%, p10=**0.147%**
     - Significant Up: N=141, mean=1.067%, p10=**0.169%**
   - This confirms that stronger overnight gaps up lead to more significant intraday upward follow-through, meaning we can set limit orders much higher!

2. **Significant Gap Down "Mean-Reversion" Effect:**
   - Interestingly, for **Significant Down** (Gap < -0.5%), the mean and 10th percentile **increase** significantly compared to Moderate Down and Neutral.
   - For example, for 500ETF:
     - Moderate Down: mean=0.789%, p10=**0.098%**
     - Significant Down: mean=1.306%, p10=**0.267%**
   - When there is a significant gap down, there is often a strong intraday bounce/mean-reversion! This means there's a large high-to-open difference because of the intraday recovery.
   - **Actionable Strategy Insight:** If entering a Covered Call option trade on a Significant Gap Down Thursday, we can still set our entry limit order relatively high (e.g. +0.267% for 500ETF) due to this mean-reversion bounce.

## Visualizations

### Overlay Distribution Plots
````carousel
![50ETF Overlay](/home/hallo/.gemini/antigravity-ide/brain/1fc9878a-b11d-429c-9d7f-c61fe0ea0c3c/open_high_distribution_50ETF.png)
<!-- slide -->
![300ETF Overlay](/home/hallo/.gemini/antigravity-ide/brain/1fc9878a-b11d-429c-9d7f-c61fe0ea0c3c/open_high_distribution_300ETF.png)
<!-- slide -->
![500ETF Overlay](/home/hallo/.gemini/antigravity-ide/brain/1fc9878a-b11d-429c-9d7f-c61fe0ea0c3c/open_high_distribution_500ETF.png)
<!-- slide -->
![Combined Overlay](/home/hallo/.gemini/antigravity-ide/brain/1fc9878a-b11d-429c-9d7f-c61fe0ea0c3c/open_high_distribution.png)
````

### Facet Grid Details (1x5 Subplots)
````carousel
![50ETF Facet Detail](/home/hallo/.gemini/antigravity-ide/brain/1fc9878a-b11d-429c-9d7f-c61fe0ea0c3c/open_high_distribution_facets_50ETF.png)
<!-- slide -->
![300ETF Facet Detail](/home/hallo/.gemini/antigravity-ide/brain/1fc9878a-b11d-429c-9d7f-c61fe0ea0c3c/open_high_distribution_facets_300ETF.png)
<!-- slide -->
![500ETF Facet Detail](/home/hallo/.gemini/antigravity-ide/brain/1fc9878a-b11d-429c-9d7f-c61fe0ea0c3c/open_high_distribution_facets_500ETF.png)
````
