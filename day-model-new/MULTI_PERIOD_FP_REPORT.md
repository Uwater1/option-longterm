# Multi-Period FP Rate Comparison Report

Cross-period comparison of filter gate false positive/negative rates.
Ground truth: OOS (post-training) performance. No lockbox used.

---

## 300ETF — `single`

| Period | Pool Size | Clusters | Cluster Sizes | FP Rate | Mean OOS IC | Mean OOS Sharpe |
| :--- | ---: | ---: | :--- | ---: | ---: | ---: |
| 2015-2022 (Original) | 44 | 20 | `[4, 4, 3, 3, 3, 3, 2, 2, 2, 2, 2, 2, ... (20 clusters)]` | 43.2% | +0.0150 | +0.0146 |
| 2015-2023 | 92 | 29 | `[9, 7, 5, 4, 3, 3, 3, 3, 3, 3, 3, 3, ... (29 clusters)]` | 21.7% | +0.0584 | +0.2850 |
| 2016-2024 | 124 | 37 | `[10, 7, 7, 6, 6, 4, 4, 3, 2, 2, 2, 2, ... (37 clusters)]` | 50.0% | +0.0158 | +0.0023 |
| 2017-2025 | 136 | 38 | `[12, 9, 8, 6, 6, 4, 3, 3, 3, 3, 2, 2, ... (38 clusters)]` | 92.6% | +0.0038 | -0.7754 |

### Per-Gate False Negative Rate Comparison

| Gate | 2015-2022 (Original) | 2015-2023 | 2016-2024 | 2017-2025 |
| :--- | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 30.0% | 83.3% | 43.3% | 46.7% |
| B2 Rolling Guard | 23.3% | 90.0% | 26.7% | 23.3% |
| B3 Composite Floor | 63.3% | 76.7% | 0.0% | 0.0% |
| B4 Correlation Gate | 73.3% | 86.7% | 53.3% | 33.3% |
| BH-FDR Gate | 0.0% | 0.0% | 0.0% | 0.0% |

---

## 50ETF — `single`

| Period | Pool Size | Clusters | Cluster Sizes | FP Rate | Mean OOS IC | Mean OOS Sharpe |
| :--- | ---: | ---: | :--- | ---: | ---: | ---: |
| 2015-2022 (Original) | 0 | - | `-` | 0.0% | +0.0000 | +0.0000 |
| 2015-2023 | 0 | - | `-` | 0.0% | +0.0000 | +0.0000 |
| 2016-2024 | 0 | - | `-` | 0.0% | +0.0000 | +0.0000 |
| 2017-2025 | 0 | - | `-` | 0.0% | +0.0000 | +0.0000 |

### Per-Gate False Negative Rate Comparison

| Gate | 2015-2022 (Original) | 2015-2023 | 2016-2024 | 2017-2025 |
| :--- | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 33.3% | 50.0% | 60.0% | 50.0% |
| B2 Rolling Guard | 43.3% | 6.7% | 10.0% | 46.7% |
| B3 Composite Floor | 0.0% | 0.0% | 0.0% | 0.0% |
| B4 Correlation Gate | 0.0% | 0.0% | 0.0% | 0.0% |
| BH-FDR Gate | 0.0% | 100.0% | 0.0% | 0.0% |

---

## 500ETF — `single`

| Period | Pool Size | Clusters | Cluster Sizes | FP Rate | Mean OOS IC | Mean OOS Sharpe |
| :--- | ---: | ---: | :--- | ---: | ---: | ---: |
| 2015-2022 (Original) | 248 | 55 | `[13, 12, 11, 9, 8, 7, 7, 6, 6, 6, 6, 6, ... (55 clusters)]` | 19.8% | +0.0903 | +0.3577 |
| 2015-2023 | 260 | 51 | `[37, 36, 15, 5, 5, 5, 5, 4, 4, 4, 3, 3, ... (51 clusters)]` | 9.6% | +0.0919 | +0.3996 |
| 2016-2024 | 181 | 13 | `[98, 13, 10, 7, 3, 2, 2, 2, 2, 2, 1, 1, 1]` | 12.7% | +0.0903 | +0.4059 |
| 2017-2025 | 207 | 14 | `[117, 12, 6, 4, 3, 2, 2, 2, 2, 2, 2, 2, 2, 1]` | 72.5% | +0.0597 | -0.4095 |

### Per-Gate False Negative Rate Comparison

| Gate | 2015-2022 (Original) | 2015-2023 | 2016-2024 | 2017-2025 |
| :--- | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 93.3% | 100.0% | 93.3% | 56.7% |
| B2 Rolling Guard | 76.7% | 70.0% | 90.0% | 6.7% |
| B3 Composite Floor | 93.3% | 100.0% | 100.0% | 26.7% |
| B4 Correlation Gate | 90.0% | 100.0% | 93.3% | 10.0% |
| BH-FDR Gate | 0.0% | 0.0% | 0.0% | 0.0% |

---

## 159915ETF — `single`

| Period | Pool Size | Clusters | Cluster Sizes | FP Rate | Mean OOS IC | Mean OOS Sharpe |
| :--- | ---: | ---: | :--- | ---: | ---: | ---: |
| 2015-2022 (Original) | 29 | 16 | `[2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, ... (16 clusters)]` | 6.9% | +0.1181 | +0.9856 |
| 2015-2023 | 119 | 7 | `[85, 3, 3, 2, 1, 1, 1]` | 0.8% | +0.1153 | +0.9810 |
| 2016-2024 | 151 | 7 | `[105, 4, 3, 3, 2, 2, 2]` | 3.3% | +0.1013 | +0.7877 |
| 2017-2025 | 187 | 4 | `[136, 9, 2, 1]` | 29.4% | +0.1035 | +0.3233 |

### Per-Gate False Negative Rate Comparison

| Gate | 2015-2022 (Original) | 2015-2023 | 2016-2024 | 2017-2025 |
| :--- | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 66.7% | 86.7% | 76.7% | 70.0% |
| B2 Rolling Guard | 96.7% | 96.7% | 100.0% | 66.7% |
| B3 Composite Floor | 100.0% | 100.0% | 100.0% | 90.0% |
| B4 Correlation Gate | 93.3% | 100.0% | 100.0% | 100.0% |
| BH-FDR Gate | 80.0% | 0.0% | 60.0% | 20.0% |

---

