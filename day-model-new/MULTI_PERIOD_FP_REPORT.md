# Multi-Period FP Rate Comparison Report

Cross-period comparison of filter gate false positive/negative rates.
Ground truth: OOS (post-training) performance. No lockbox used.

---

## 300ETF — `single`

| Period | Pool Size | Clusters | Cluster Sizes | FP Rate | Mean OOS IC | Mean OOS Sharpe |
| :--- | ---: | ---: | :--- | ---: | ---: | ---: |
| 2015-2022 (Original) | 44 | 20 | `[4, 4, 3, 3, 3, 3, 2, 2, 2, 2, 2, 2, ... (20 clusters)]` | 43.2% | +0.0150 | +0.0146 |
| 2015-2023 | 93 | 25 | `[9, 7, 7, 7, 5, 4, 3, 3, 3, 3, 3, 3, ... (25 clusters)]` | 22.6% | +0.0577 | +0.2748 |
| 2016-2024 | 127 | 37 | `[11, 6, 5, 4, 4, 4, 4, 4, 4, 3, 3, 3, ... (37 clusters)]` | 50.4% | +0.0155 | -0.0059 |
| 2017-2025 | 139 | 39 | `[11, 9, 8, 8, 6, 6, 4, 3, 3, 3, 3, 3, ... (39 clusters)]` | 92.8% | +0.0026 | -0.7866 |

### Per-Gate False Negative Rate Comparison

| Gate | 2015-2022 (Original) | 2015-2023 | 2016-2024 | 2017-2025 |
| :--- | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 30.0% | 83.3% | 43.3% | 46.7% |
| B2 Rolling Guard | 23.3% | 90.0% | 26.7% | 23.3% |
| B3 Composite Floor | 63.3% | 76.7% | 0.0% | 0.0% |
| B4 Correlation Gate | 73.3% | 86.7% | 53.3% | 33.3% |
| BH-FDR Gate | 0.0% | 0.0% | 0.0% | 0.0% |

---

