# Multi-Period FP Rate Comparison Report

Cross-period comparison of filter gate false positive/negative rates.
Ground truth: OOS (post-training) performance. No lockbox used.

---

## 300ETF — `single`

| Period | Pool Size | Clusters | Cluster Sizes | FP Rate | Mean OOS IC | Mean OOS Sharpe |
| :--- | ---: | ---: | :--- | ---: | ---: | ---: |
| 2015-2022 (Original) | 44 | 20 | `[4, 4, 3, 3, 3, 3, 2, 2, 2, 2, 2, 2, ... (20 clusters)]` | 43.2% | +0.0150 | +0.0146 |
| 2015-2023 | 86 | 25 | `[11, 7, 7, 5, 4, 3, 3, 3, 3, 3, 2, 2, ... (25 clusters)]` | 20.9% | +0.0581 | +0.2807 |
| 2016-2024 | 109 | 37 | `[7, 7, 4, 3, 3, 3, 3, 3, 2, 2, 2, 2, ... (37 clusters)]` | 50.5% | +0.0167 | -0.0039 |
| 2017-2025 | 122 | 42 | `[8, 7, 5, 5, 4, 3, 3, 3, 3, 3, 2, 2, ... (42 clusters)]` | 91.8% | +0.0046 | -0.7693 |

### Per-Gate False Negative Rate Comparison

| Gate | 2015-2022 (Original) | 2015-2023 | 2016-2024 | 2017-2025 |
| :--- | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 30.0% | 80.0% | 40.0% | 50.0% |
| B2 Rolling Guard | 23.3% | 93.3% | 26.7% | 26.7% |
| B3 Composite Floor | 63.3% | 76.7% | 0.0% | 0.0% |
| B4 Correlation Gate | 73.3% | 86.7% | 56.7% | 33.3% |
| BH-FDR Gate | 0.0% | 0.0% | 9.1% | 0.0% |

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
| 2015-2023 | 259 | 64 | `[12, 11, 11, 10, 8, 7, 7, 7, 6, 6, 6, 5, ... (64 clusters)]` | 9.7% | +0.0919 | +0.3988 |
| 2016-2024 | 181 | 60 | `[12, 11, 11, 5, 5, 4, 4, 4, 3, 3, 3, 3, ... (60 clusters)]` | 11.0% | +0.0903 | +0.4127 |
| 2017-2025 | 206 | 47 | `[12, 10, 9, 8, 8, 8, 7, 7, 6, 6, 5, 5, ... (47 clusters)]` | 72.3% | +0.0599 | -0.4090 |

### Per-Gate False Negative Rate Comparison

| Gate | 2015-2022 (Original) | 2015-2023 | 2016-2024 | 2017-2025 |
| :--- | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 93.3% | 96.7% | 93.3% | 56.7% |
| B2 Rolling Guard | 76.7% | 70.0% | 90.0% | 6.7% |
| B3 Composite Floor | 93.3% | 100.0% | 100.0% | 26.7% |
| B4 Correlation Gate | 90.0% | 100.0% | 96.7% | 10.0% |
| BH-FDR Gate | 0.0% | 0.0% | 0.0% | 0.0% |

---

## 159915ETF — `single`

| Period | Pool Size | Clusters | Cluster Sizes | FP Rate | Mean OOS IC | Mean OOS Sharpe |
| :--- | ---: | ---: | :--- | ---: | ---: | ---: |
| 2015-2022 (Original) | 29 | 16 | `[2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, ... (16 clusters)]` | 6.9% | +0.1181 | +0.9856 |
| 2015-2023 | 105 | 28 | `[13, 9, 5, 5, 4, 4, 4, 4, 3, 3, 3, 3, ... (28 clusters)]` | 1.0% | +0.1148 | +0.9718 |
| 2016-2024 | 146 | 36 | `[18, 12, 8, 8, 6, 5, 5, 4, 3, 3, 3, 3, ... (36 clusters)]` | 3.4% | +0.1021 | +0.8003 |
| 2017-2025 | 183 | 48 | `[12, 12, 10, 9, 7, 6, 5, 5, 5, 4, 4, 3, ... (48 clusters)]` | 29.0% | +0.1039 | +0.3447 |

### Per-Gate False Negative Rate Comparison

| Gate | 2015-2022 (Original) | 2015-2023 | 2016-2024 | 2017-2025 |
| :--- | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 66.7% | 86.7% | 80.0% | 70.0% |
| B2 Rolling Guard | 96.7% | 96.7% | 100.0% | 66.7% |
| B3 Composite Floor | 100.0% | 100.0% | 100.0% | 90.0% |
| B4 Correlation Gate | 93.3% | 100.0% | 100.0% | 100.0% |
| BH-FDR Gate | 80.0% | 0.0% | 71.4% | 25.0% |

---

