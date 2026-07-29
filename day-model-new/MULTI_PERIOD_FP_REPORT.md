# Multi-Period FP Rate Comparison Report

Cross-period comparison of filter gate false positive/negative rates.
Ground truth: OOS (post-training) performance. No lockbox used.

---

## 300ETF — `single`

| Period | Pool Size | FP Rate | Mean OOS IC | Mean OOS Sharpe |
| :--- | ---: | ---: | ---: | ---: |
| 2015-2022 (Original) | 12 | 58.3% | +0.0141 | -0.2852 |
| 2015-2023 | 20 | 15.0% | +0.0551 | +0.2959 |
| 2016-2024 | 19 | 42.1% | +0.0167 | +0.0140 |
| 2017-2025 | 25 | 92.0% | +0.0057 | -0.7793 |

### Per-Gate False Negative Rate Comparison

| Gate | 2015-2022 (Original) | 2015-2023 | 2016-2024 | 2017-2025 |
| :--- | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 50.0% | 63.3% | 26.7% | 36.7% |
| B2 Rolling Guard | 30.0% | 93.3% | 23.3% | 26.7% |
| B3 Composite Floor | 40.0% | 73.3% | 0.0% | 0.0% |
| B4 Correlation Gate | 86.7% | 96.7% | 43.3% | 30.0% |
| BH-FDR Gate | 0.0% | 0.0% | 8.3% | 25.0% |

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
| 2015-2023 | 43 | 14.0% | +0.0929 | +0.4113 |
| 2016-2024 | 29 | 13.8% | +0.0903 | +0.3550 |
| 2017-2025 | 29 | 55.2% | +0.0683 | -0.1822 |

### Per-Gate False Negative Rate Comparison

| Gate | 2015-2022 (Original) | 2015-2023 | 2016-2024 | 2017-2025 |
| :--- | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 80.0% | 96.7% | 96.7% | 60.0% |
| B2 Rolling Guard | 76.7% | 70.0% | 90.0% | 6.7% |
| B3 Composite Floor | 93.3% | 100.0% | 86.7% | 30.0% |
| B4 Correlation Gate | 86.7% | 100.0% | 100.0% | 10.0% |
| BH-FDR Gate | 0.0% | 0.0% | 12.5% | 0.0% |

---

## 159915ETF — `single`

| Period | Pool Size | FP Rate | Mean OOS IC | Mean OOS Sharpe |
| :--- | ---: | ---: | ---: | ---: |
| 2015-2022 (Original) | 8 | 0.0% | +0.1239 | +1.1303 |
| 2015-2023 | 22 | 4.5% | +0.1105 | +0.7971 |
| 2016-2024 | 17 | 17.6% | +0.0892 | +0.5931 |
| 2017-2025 | 30 | 26.7% | +0.1108 | +0.4436 |

### Per-Gate False Negative Rate Comparison

| Gate | 2015-2022 (Original) | 2015-2023 | 2016-2024 | 2017-2025 |
| :--- | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 63.3% | 93.3% | 76.7% | 63.3% |
| B2 Rolling Guard | 100.0% | 96.7% | 100.0% | 60.0% |
| B3 Composite Floor | 100.0% | 100.0% | 100.0% | 96.7% |
| B4 Correlation Gate | 100.0% | 100.0% | 100.0% | 100.0% |
| BH-FDR Gate | 80.0% | 0.0% | 50.0% | 33.3% |

---

