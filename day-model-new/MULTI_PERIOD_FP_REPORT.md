# Multi-Period FP Rate Comparison Report

Cross-period comparison of filter gate false positive/negative rates.
Ground truth: OOS (post-training) performance. No lockbox used.

---

## 300ETF — `single`

| Period | Pool Size | FP Rate | Mean OOS IC | Mean OOS Sharpe |
| :--- | ---: | ---: | ---: | ---: |
| 2015-2022 (Original) | 11 | 54.5% | +0.0258 | -0.2203 |
| 2015-2023 | 3 | 33.3% | +0.0606 | +0.1155 |
| 2016-2024 | 2 | 100.0% | -0.0053 | -0.2462 |
| 2017-2025 | 4 | 100.0% | -0.0176 | -0.7587 |

### Per-Gate False Negative Rate Comparison

| Gate | 2015-2022 (Original) | 2015-2023 | 2016-2024 | 2017-2025 |
| :--- | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 10.0% | 56.7% | 43.3% | 50.0% |
| B2 Rolling Guard | 33.3% | 93.3% | 26.7% | 33.3% |
| B3 Composite Floor | 26.7% | 73.9% | 0.0% | 0.0% |
| B4 Correlation Gate | 40.0% | 83.3% | 36.7% | 0.0% |
| BH-FDR Gate | 37.5% | 0.0% | 9.1% | 33.3% |

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
| 7-Year Jackknife Sign Stability | 46.7% | 46.7% | 60.0% | 53.3% |
| B2 Rolling Guard | 23.3% | 6.7% | 10.0% | 53.3% |
| B3 Composite Floor | 0.0% | 0.0% | 0.0% | 0.0% |
| B4 Correlation Gate | 0.0% | 0.0% | 0.0% | 0.0% |
| BH-FDR Gate | 100.0% | 100.0% | 0.0% | 0.0% |

---

## 500ETF — `single`

| Period | Pool Size | FP Rate | Mean OOS IC | Mean OOS Sharpe |
| :--- | ---: | ---: | ---: | ---: |
| 2015-2022 (Original) | 37 | 40.5% | +0.0967 | +0.1342 |
| 2015-2023 | 13 | 7.7% | +0.0872 | +0.4491 |
| 2016-2024 | 12 | 8.3% | +0.0997 | +0.4884 |
| 2017-2025 | 12 | 66.7% | +0.0586 | -0.1476 |

### Per-Gate False Negative Rate Comparison

| Gate | 2015-2022 (Original) | 2015-2023 | 2016-2024 | 2017-2025 |
| :--- | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 63.3% | 96.7% | 96.7% | 60.0% |
| B2 Rolling Guard | 30.0% | 73.3% | 96.7% | 6.7% |
| B3 Composite Floor | 80.0% | 100.0% | 100.0% | 26.7% |
| B4 Correlation Gate | 60.0% | 100.0% | 96.7% | 0.0% |
| BH-FDR Gate | 10.3% | 0.0% | 0.0% | 0.0% |

---

## 159915ETF — `single`

| Period | Pool Size | FP Rate | Mean OOS IC | Mean OOS Sharpe |
| :--- | ---: | ---: | ---: | ---: |
| 2015-2022 (Original) | 15 | 13.3% | +0.1151 | +0.6320 |
| 2015-2023 | 10 | 10.0% | +0.1059 | +0.6683 |
| 2016-2024 | 12 | 25.0% | +0.0764 | +0.4086 |
| 2017-2025 | 11 | 27.3% | +0.1066 | +0.4474 |

### Per-Gate False Negative Rate Comparison

| Gate | 2015-2022 (Original) | 2015-2023 | 2016-2024 | 2017-2025 |
| :--- | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 63.3% | 93.3% | 83.3% | 73.3% |
| B2 Rolling Guard | 90.0% | 96.7% | 100.0% | 83.3% |
| B3 Composite Floor | 100.0% | 100.0% | 100.0% | 90.0% |
| B4 Correlation Gate | 96.7% | 100.0% | 100.0% | 100.0% |
| BH-FDR Gate | 83.3% | 0.0% | 0.0% | 25.0% |

---

