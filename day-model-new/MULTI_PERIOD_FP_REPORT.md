# Multi-Period FP Rate Comparison Report

Cross-period comparison of filter gate false positive/negative rates.
Ground truth: OOS (post-training) performance. No lockbox used.

---

## 300ETF — `single`

| Period | Pool Size | Clusters | Cluster Sizes | FP Rate | Mean OOS IC | Mean OOS Sharpe |
| :--- | ---: | ---: | :--- | ---: | ---: | ---: |
| 2015-2022 (Original) | 18 | 9 | `[3, 3, 2, 2, 2, 2, 2, 1, 1]` | 33.3% | +0.0196 | +0.1240 |
| 2015-2023 | 51 | 26 | `[5, 4, 3, 3, 3, 3, 2, 2, 2, 2, 2, 2, ... (26 clusters)]` | 33.3% | +0.0585 | +0.2198 |
| 2016-2024 | 62 | 28 | `[4, 4, 4, 4, 3, 3, 3, 3, 2, 2, 2, 2, ... (28 clusters)]` | 59.7% | +0.0154 | -0.0667 |
| 2017-2025 | 50 | 25 | `[6, 3, 3, 3, 2, 2, 2, 2, 2, 2, 2, 2, ... (25 clusters)]` | 92.0% | +0.0015 | -0.8620 |
| 2018-2026 | 63 | 19 | `[9, 9, 7, 7, 5, 3, 3, 2, 2, 2, 2, 2, ... (19 clusters)]` | 96.8% | -0.0938 | -1.5550 |

### Per-Gate False Negative Rate Comparison

| Gate | 2015-2022 (Original) | 2015-2023 | 2016-2024 | 2017-2025 | 2018-2026 |
| :--- | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 30.0% | 60.0% | 40.0% | 50.0% | 0.0% |
| B2 Rolling Guard | 26.7% | 86.7% | 30.0% | 33.3% | 6.7% |
| B3 Composite Floor | 30.8% | 61.5% | 0.0% | 0.0% | 0.0% |
| B4 Correlation Gate | 80.0% | 93.3% | 43.3% | 30.0% | 6.7% |
| BH-FDR Gate | 40.0% | 0.0% | 25.0% | 33.3% | 0.0% |

---

