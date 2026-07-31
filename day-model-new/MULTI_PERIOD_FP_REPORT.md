# Multi-Period FP Rate Comparison Report

Cross-period comparison of filter gate false positive/negative rates.
Ground truth: OOS (post-training) performance. No lockbox used.

---

## 300ETF — `single`

| Period | Pool Size | Clusters | Cluster Sizes | FP Rate | Mean OOS IC | Mean OOS Sharpe |
| :--- | ---: | ---: | :--- | ---: | ---: | ---: |
| 2015-2022 (Original) | 44 | 20 | `[4, 4, 3, 3, 3, 3, 2, 2, 2, 2, 2, 2, ... (20 clusters)]` | 43.2% | +0.0150 | +0.0146 |
| 2018-2026 | 123 | 26 | `[17, 10, 9, 8, 7, 4, 3, 3, 3, 3, 3, 2, ... (26 clusters)]` | 98.4% | -0.0952 | -1.5824 |

### Per-Gate False Negative Rate Comparison

| Gate | 2015-2022 (Original) | 2018-2026 |
| :--- | ---: | ---: |
| 7-Year Jackknife Sign Stability | 30.0% | 0.0% |
| B2 Rolling Guard | 23.3% | 6.7% |
| B3 Composite Floor | 63.3% | 0.0% |
| B4 Correlation Gate | 73.3% | 6.7% |
| BH-FDR Gate | 0.0% | 0.0% |

---

## 50ETF — `single`

| Period | Pool Size | Clusters | Cluster Sizes | FP Rate | Mean OOS IC | Mean OOS Sharpe |
| :--- | ---: | ---: | :--- | ---: | ---: | ---: |
| 2015-2022 (Original) | 0 | - | `-` | 0.0% | +0.0000 | +0.0000 |
| 2018-2026 | 0 | - | `-` | 0.0% | +0.0000 | +0.0000 |

### Per-Gate False Negative Rate Comparison

| Gate | 2015-2022 (Original) | 2018-2026 |
| :--- | ---: | ---: |
| 7-Year Jackknife Sign Stability | 33.3% | 46.7% |
| B2 Rolling Guard | 43.3% | 33.3% |
| B3 Composite Floor | 0.0% | 0.0% |
| B4 Correlation Gate | 0.0% | 0.0% |
| BH-FDR Gate | 0.0% | 60.0% |

---

## 500ETF — `single`

| Period | Pool Size | Clusters | Cluster Sizes | FP Rate | Mean OOS IC | Mean OOS Sharpe |
| :--- | ---: | ---: | :--- | ---: | ---: | ---: |
| 2015-2022 (Original) | 248 | 55 | `[13, 12, 11, 9, 8, 7, 7, 6, 6, 6, 6, 6, ... (55 clusters)]` | 19.8% | +0.0903 | +0.3577 |
| 2018-2026 | 148 | 50 | `[9, 8, 7, 6, 5, 5, 4, 3, 3, 3, 3, 3, ... (50 clusters)]` | 77.7% | +0.0053 | -0.9438 |

### Per-Gate False Negative Rate Comparison

| Gate | 2015-2022 (Original) | 2018-2026 |
| :--- | ---: | ---: |
| 7-Year Jackknife Sign Stability | 93.3% | 33.3% |
| B2 Rolling Guard | 76.7% | 16.7% |
| B3 Composite Floor | 93.3% | 6.7% |
| B4 Correlation Gate | 90.0% | 6.7% |
| BH-FDR Gate | 0.0% | 0.0% |

---

## 159915ETF — `single`

| Period | Pool Size | Clusters | Cluster Sizes | FP Rate | Mean OOS IC | Mean OOS Sharpe |
| :--- | ---: | ---: | :--- | ---: | ---: | ---: |
| 2015-2022 (Original) | 29 | 16 | `[2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, ... (16 clusters)]` | 6.9% | +0.1181 | +0.9856 |
| 2018-2026 | 178 | 53 | `[12, 10, 8, 8, 7, 7, 6, 6, 5, 4, 3, 2, ... (53 clusters)]` | 68.0% | +0.0215 | -0.8474 |

### Per-Gate False Negative Rate Comparison

| Gate | 2015-2022 (Original) | 2018-2026 |
| :--- | ---: | ---: |
| 7-Year Jackknife Sign Stability | 66.7% | 30.0% |
| B2 Rolling Guard | 96.7% | 60.0% |
| B3 Composite Floor | 100.0% | 10.0% |
| B4 Correlation Gate | 93.3% | 70.0% |
| BH-FDR Gate | 80.0% | 100.0% |

---

