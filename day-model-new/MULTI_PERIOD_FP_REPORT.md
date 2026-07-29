# Multi-Period FP Rate Comparison Report

Cross-period comparison of filter gate false positive/negative rates.
Ground truth: OOS (post-training) performance. No lockbox used.

---

## 300ETF — `single`

| Period | Pool Size | FP Rate | Mean OOS IC | Mean OOS Sharpe |
| :--- | ---: | ---: | ---: | ---: |
| 2015-2022 (Original) | 12 | 58.3% | +0.0141 | -0.2852 |
| 2015-2023 | 12 | 16.7% | +0.0548 | +0.2163 |
| 2016-2024 | 2 | 100.0% | -0.0053 | -0.2462 |
| 2017-2025 | 4 | 100.0% | -0.0176 | -0.7587 |

### Per-Gate False Negative Rate Comparison

| Gate | 2015-2022 (Original) | 2015-2023 | 2016-2024 | 2017-2025 |
| :--- | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 50.0% | 63.3% | 43.3% | 50.0% |
| B2 Rolling Guard | 30.0% | 93.3% | 26.7% | 33.3% |
| B3 Composite Floor | 40.0% | 73.3% | 0.0% | 0.0% |
| B4 Correlation Gate | 86.7% | 96.7% | 36.7% | 0.0% |
| BH-FDR Gate | 0.0% | 0.0% | 9.1% | 33.3% |

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
| 7-Year Jackknife Sign Stability | 43.3% | 53.3% | 66.7% | 56.7% |
| B2 Rolling Guard | 43.3% | 6.7% | 10.0% | 46.7% |
| B3 Composite Floor | 0.0% | 0.0% | 0.0% | 0.0% |
| B4 Correlation Gate | 0.0% | 0.0% | 0.0% | 0.0% |
| BH-FDR Gate | 0.0% | 100.0% | 0.0% | 0.0% |

---

## 500ETF — `single`

| Period | Pool Size | FP Rate | Mean OOS IC | Mean OOS Sharpe |
| :--- | ---: | ---: | ---: | ---: |
| 2015-2022 (Original) | 20 | 15.0% | +0.0958 | +0.5162 |
| 2015-2023 | 13 | 7.7% | +0.0872 | +0.4356 |
| 2016-2024 | 12 | 0.0% | +0.0997 | +0.5074 |
| 2017-2025 | 12 | 66.7% | +0.0586 | -0.2186 |

### Per-Gate False Negative Rate Comparison

| Gate | 2015-2022 (Original) | 2015-2023 | 2016-2024 | 2017-2025 |
| :--- | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 80.0% | 86.7% | 96.7% | 60.0% |
| B2 Rolling Guard | 76.7% | 70.0% | 90.0% | 3.3% |
| B3 Composite Floor | 93.3% | 100.0% | 100.0% | 26.7% |
| B4 Correlation Gate | 86.7% | 100.0% | 100.0% | 0.0% |
| BH-FDR Gate | 0.0% | 0.0% | 0.0% | 0.0% |

---

## 159915ETF — `single`

| Period | Pool Size | FP Rate | Mean OOS IC | Mean OOS Sharpe |
| :--- | ---: | ---: | ---: | ---: |
| 2015-2022 (Original) | 8 | 0.0% | +0.1239 | +1.1303 |
| 2015-2023 | 10 | 10.0% | +0.1059 | +0.6937 |
| 2016-2024 | 12 | 25.0% | +0.0764 | +0.4515 |
| 2017-2025 | 11 | 27.3% | +0.1066 | +0.4120 |

### Per-Gate False Negative Rate Comparison

| Gate | 2015-2022 (Original) | 2015-2023 | 2016-2024 | 2017-2025 |
| :--- | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 63.3% | 93.3% | 83.3% | 73.3% |
| B2 Rolling Guard | 100.0% | 96.7% | 100.0% | 80.0% |
| B3 Composite Floor | 100.0% | 100.0% | 100.0% | 90.0% |
| B4 Correlation Gate | 100.0% | 100.0% | 100.0% | 100.0% |
| BH-FDR Gate | 80.0% | 0.0% | 0.0% | 25.0% |

---

