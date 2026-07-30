# Multi-Period FP Rate Comparison Report

Cross-period comparison of filter gate false positive/negative rates.
Ground truth: OOS (post-training) performance. No lockbox used.

---

## 300ETF — `single`

| Period | Pool Size | FP Rate | Mean OOS IC | Mean OOS Sharpe |
| :--- | ---: | ---: | ---: | ---: |
| 2015-2022 (Original) | 17 | 47.1% | +0.0062 | -0.2161 |

### Per-Gate False Negative Rate Comparison

| Gate | 2015-2022 (Original) |
| :--- | ---: |
| 7-Year Jackknife Sign Stability | 30.0% |
| B2 Rolling Guard | 23.3% |
| B3 Composite Floor | 63.3% |
| B4 Correlation Gate | 83.3% |
| BH-FDR Gate | 0.0% |

---

