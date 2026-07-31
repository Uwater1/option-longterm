# Multi-Period FP Rate Comparison Report

Cross-period comparison of filter gate false positive/negative rates.
Ground truth: OOS (post-training) performance. No lockbox used.

---

## 300ETF — `single`

| Period | Pool Size | FP Rate | Mean OOS IC | Mean OOS Sharpe |
| :--- | ---: | ---: | ---: | ---: |
| 2015-2022 (Original) | 17 | 47.1% | +0.0062 | -0.2161 |
| 2015-2023 | 93 | 21.5% | +0.0577 | +0.2804 |
| 2016-2024 | 126 | 50.8% | +0.0152 | -0.0042 |
| 2017-2025 | 141 | 92.9% | +0.0024 | -0.7958 |

### Per-Gate False Negative Rate Comparison

| Gate | 2015-2022 (Original) | 2015-2023 | 2016-2024 | 2017-2025 |
| :--- | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 30.0% | 80.0% | 40.0% | 50.0% |
| B2 Rolling Guard | 23.3% | 93.3% | 26.7% | 26.7% |
| B3 Composite Floor | 63.3% | 76.7% | 0.0% | 0.0% |
| B4 Correlation Gate | 83.3% | 86.7% | 53.3% | 33.3% |
| BH-FDR Gate | 0.0% | 0.0% | 0.0% | 0.0% |

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
| 7-Year Jackknife Sign Stability | 30.0% | 50.0% | 60.0% | 50.0% |
| B2 Rolling Guard | 43.3% | 6.7% | 10.0% | 46.7% |
| B3 Composite Floor | 0.0% | 0.0% | 0.0% | 0.0% |
| B4 Correlation Gate | 0.0% | 0.0% | 0.0% | 0.0% |
| BH-FDR Gate | 0.0% | 100.0% | 0.0% | 0.0% |

---

## 500ETF — `single`

| Period | Pool Size | FP Rate | Mean OOS IC | Mean OOS Sharpe |
| :--- | ---: | ---: | ---: | ---: |
| 2015-2022 (Original) | 43 | 23.3% | +0.0905 | +0.4148 |
| 2015-2023 | 260 | 10.0% | +0.0919 | +0.3966 |
| 2016-2024 | 181 | 11.0% | +0.0903 | +0.4127 |
| 2017-2025 | 207 | 72.5% | +0.0597 | -0.4095 |

### Per-Gate False Negative Rate Comparison

| Gate | 2015-2022 (Original) | 2015-2023 | 2016-2024 | 2017-2025 |
| :--- | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 90.0% | 96.7% | 93.3% | 56.7% |
| B2 Rolling Guard | 76.7% | 70.0% | 90.0% | 6.7% |
| B3 Composite Floor | 93.3% | 100.0% | 100.0% | 26.7% |
| B4 Correlation Gate | 93.3% | 100.0% | 96.7% | 10.0% |
| BH-FDR Gate | 0.0% | 0.0% | 0.0% | 0.0% |

---

## 159915ETF — `single`

| Period | Pool Size | FP Rate | Mean OOS IC | Mean OOS Sharpe |
| :--- | ---: | ---: | ---: | ---: |
| 2015-2022 (Original) | 9 | 11.1% | +0.1249 | +1.0425 |
| 2015-2023 | 119 | 0.8% | +0.1153 | +0.9786 |
| 2016-2024 | 151 | 3.3% | +0.1013 | +0.7906 |
| 2017-2025 | 187 | 29.4% | +0.1035 | +0.3299 |

### Per-Gate False Negative Rate Comparison

| Gate | 2015-2022 (Original) | 2015-2023 | 2016-2024 | 2017-2025 |
| :--- | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 66.7% | 86.7% | 80.0% | 70.0% |
| B2 Rolling Guard | 96.7% | 96.7% | 100.0% | 66.7% |
| B3 Composite Floor | 100.0% | 100.0% | 100.0% | 90.0% |
| B4 Correlation Gate | 100.0% | 100.0% | 100.0% | 100.0% |
| BH-FDR Gate | 80.0% | 0.0% | 60.0% | 20.0% |

---

