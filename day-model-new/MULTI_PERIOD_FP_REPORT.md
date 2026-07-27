# Multi-Period FP Rate Comparison Report

Cross-period comparison of filter gate false positive/negative rates.
Ground truth: OOS (post-training) performance. No lockbox used.

---

## 300ETF — `single`

| Period | Pool Size | FP Rate | Mean OOS IC | Mean OOS Sharpe |
| :--- | ---: | ---: | ---: | ---: |
| 2015-2022 (Original) | 11 | 54.5% | +0.0258 | -0.2203 |
| 2015-2023 | 13 | 30.8% | +0.0518 | +0.2344 |
| 2016-2024 | 19 | 73.7% | +0.0182 | -0.2093 |
| 2017-2025 | 19 | 94.7% | +0.0096 | -0.7343 |

### Per-Gate False Negative Rate Comparison

| Gate | 2015-2022 (Original) | 2015-2023 | 2016-2024 | 2017-2025 |
| :--- | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 10.0% | 83.3% | 43.3% | 30.0% |
| B2 Rolling Guard | 33.3% | 56.7% | 23.3% | 13.3% |
| B3 Composite Floor | 26.7% | 100.0% | 63.3% | 26.7% |
| B4 Correlation Gate | 40.0% | 96.3% | 46.7% | 33.3% |
| BH-FDR Gate | 37.5% | 16.7% | 10.0% | 0.0% |

---

## 50ETF — `single`

| Period | Pool Size | FP Rate | Mean OOS IC | Mean OOS Sharpe |
| :--- | ---: | ---: | ---: | ---: |
| 2015-2022 (Original) | 0 | 0.0% | +0.0000 | +0.0000 |
| 2015-2023 | 0 | 0.0% | +0.0000 | +0.0000 |
| 2016-2024 | 0 | 0.0% | +0.0000 | +0.0000 |
| 2017-2025 | 0 | 0.0% | +0.0000 | +0.0000 |

### Per-Gate False Negative Rate Comparison

| Gate | 2015-2022 (Original) | 2015-2023 | 2016-2024 | 2017-2025 |
| :--- | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 46.7% | 76.7% | 80.0% | 56.7% |
| B2 Rolling Guard | 23.3% | 6.7% | 4.8% | 33.3% |
| B3 Composite Floor | 0.0% | 0.0% | 0.0% | 0.0% |
| B4 Correlation Gate | 0.0% | 0.0% | 0.0% | 0.0% |
| BH-FDR Gate | 100.0% | 0.0% | 0.0% | 0.0% |

---

## 500ETF — `single`

| Period | Pool Size | FP Rate | Mean OOS IC | Mean OOS Sharpe |
| :--- | ---: | ---: | ---: | ---: |
| 2015-2022 (Original) | 37 | 40.5% | +0.0967 | +0.1342 |
| 2015-2023 | 32 | 3.1% | +0.0937 | +0.4900 |
| 2016-2024 | 32 | 15.6% | +0.0893 | +0.3979 |
| 2017-2025 | 30 | 70.0% | +0.0638 | -0.3960 |

### Per-Gate False Negative Rate Comparison

| Gate | 2015-2022 (Original) | 2015-2023 | 2016-2024 | 2017-2025 |
| :--- | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 63.3% | 100.0% | 93.3% | 60.0% |
| B2 Rolling Guard | 30.0% | 53.3% | 80.0% | 16.7% |
| B3 Composite Floor | 80.0% | 100.0% | 100.0% | 33.3% |
| B4 Correlation Gate | 60.0% | 100.0% | 90.0% | 0.0% |
| BH-FDR Gate | 10.3% | 0.0% | 22.2% | 11.1% |

---

## 159915ETF — `single`

| Period | Pool Size | FP Rate | Mean OOS IC | Mean OOS Sharpe |
| :--- | ---: | ---: | ---: | ---: |
| 2015-2022 (Original) | 15 | 13.3% | +0.1151 | +0.6320 |
| 2015-2023 | 25 | 4.0% | +0.1116 | +0.8087 |
| 2016-2024 | 29 | 0.0% | +0.1106 | +0.8200 |
| 2017-2025 | 33 | 21.2% | +0.1098 | +0.5217 |

### Per-Gate False Negative Rate Comparison

| Gate | 2015-2022 (Original) | 2015-2023 | 2016-2024 | 2017-2025 |
| :--- | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 63.3% | 83.3% | 83.3% | 63.3% |
| B2 Rolling Guard | 90.0% | 73.3% | 86.7% | 73.3% |
| B3 Composite Floor | 100.0% | 100.0% | 96.7% | 90.0% |
| B4 Correlation Gate | 96.7% | 100.0% | 100.0% | 100.0% |
| BH-FDR Gate | 83.3% | 0.0% | 71.4% | 45.5% |

---

