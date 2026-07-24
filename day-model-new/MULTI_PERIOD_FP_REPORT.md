# Multi-Period FP Rate Comparison Report

Cross-period comparison of filter gate false positive/negative rates.
Ground truth: OOS (post-training) performance. No lockbox used.

---

## 300ETF — `single`

| Period | Pool Size | FP Rate | Mean OOS IC | Mean OOS Sharpe |
| :--- | ---: | ---: | ---: | ---: |
| 2015-2022 (Original) | 11 | 54.5% | +0.0258 | -0.2203 |
| 2015-2023 | 13 | 76.9% | +0.0518 | -0.2580 |
| 2016-2024 | 19 | 89.5% | +0.0182 | -0.6829 |
| 2017-2025 | 17 | 100.0% | +0.0077 | -1.3675 |

### Per-Gate False Negative Rate Comparison

| Gate | 2015-2022 (Original) | 2015-2023 | 2016-2024 | 2017-2025 |
| :--- | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 10.0% | 20.0% | 23.3% | 23.3% |
| B2 Rolling Guard | 33.3% | 13.3% | 6.7% | 6.7% |
| B3 Composite Floor | 26.7% | 53.3% | 20.0% | 0.0% |
| B4 Correlation Gate | 40.0% | 29.6% | 10.0% | 0.0% |
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
| 7-Year Jackknife Sign Stability | 46.7% | 56.7% | 66.7% | 46.7% |
| B2 Rolling Guard | 23.3% | 0.0% | 0.0% | 33.3% |
| B3 Composite Floor | 0.0% | 0.0% | 0.0% | 0.0% |
| B4 Correlation Gate | 0.0% | 0.0% | 0.0% | 0.0% |
| BH-FDR Gate | 100.0% | 0.0% | 0.0% | 0.0% |

---

## 500ETF — `single`

| Period | Pool Size | FP Rate | Mean OOS IC | Mean OOS Sharpe |
| :--- | ---: | ---: | ---: | ---: |
| 2015-2022 (Original) | 37 | 40.5% | +0.0967 | +0.1342 |
| 2015-2023 | 32 | 28.1% | +0.0937 | +0.1465 |
| 2016-2024 | 32 | 50.0% | +0.0893 | +0.0712 |
| 2017-2025 | 31 | 77.4% | +0.0634 | -0.7865 |

### Per-Gate False Negative Rate Comparison

| Gate | 2015-2022 (Original) | 2015-2023 | 2016-2024 | 2017-2025 |
| :--- | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 63.3% | 80.0% | 80.0% | 13.3% |
| B2 Rolling Guard | 30.0% | 3.3% | 50.0% | 10.0% |
| B3 Composite Floor | 80.0% | 80.0% | 73.3% | 10.0% |
| B4 Correlation Gate | 60.0% | 93.3% | 56.7% | 0.0% |
| BH-FDR Gate | 10.3% | 0.0% | 22.2% | 22.2% |

---

## 159915ETF — `single`

| Period | Pool Size | FP Rate | Mean OOS IC | Mean OOS Sharpe |
| :--- | ---: | ---: | ---: | ---: |
| 2015-2022 (Original) | 15 | 13.3% | +0.1151 | +0.6320 |
| 2015-2023 | 25 | 4.0% | +0.1116 | +0.5641 |
| 2016-2024 | 29 | 10.3% | +0.1106 | +0.5716 |
| 2017-2025 | 28 | 35.7% | +0.1129 | +0.2816 |

### Per-Gate False Negative Rate Comparison

| Gate | 2015-2022 (Original) | 2015-2023 | 2016-2024 | 2017-2025 |
| :--- | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 63.3% | 80.0% | 63.3% | 66.7% |
| B2 Rolling Guard | 90.0% | 70.0% | 80.0% | 56.7% |
| B3 Composite Floor | 100.0% | 100.0% | 76.7% | 53.3% |
| B4 Correlation Gate | 96.7% | 100.0% | 100.0% | 100.0% |
| BH-FDR Gate | 83.3% | 0.0% | 42.9% | 18.2% |

---

