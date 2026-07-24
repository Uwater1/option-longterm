# Multi-Period FP Rate Comparison Report

Cross-period comparison of filter gate false positive/negative rates.
Ground truth: OOS (post-training) performance. No lockbox used.

---

## 300ETF — `single`

| Period | Pool Size | FP Rate | Mean OOS IC | Mean OOS Sharpe |
| :--- | ---: | ---: | ---: | ---: |
| 2015-2022 (Original) | 11 | 54.5% | +0.0258 | -0.2203 |
| 2015-2023 | 14 | 78.6% | +0.0527 | -0.2220 |
| 2016-2024 | 21 | 90.5% | +0.0166 | -0.6626 |
| 2017-2025 | 19 | 100.0% | +0.0070 | -1.3176 |

### Per-Gate False Negative Rate Comparison

| Gate | 2015-2022 (Original) | 2015-2023 | 2016-2024 | 2017-2025 |
| :--- | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 10.0% | 23.3% | 20.0% | 23.3% |
| B2 Rolling Guard | 33.3% | 13.3% | 6.7% | 6.7% |
| B3 Composite Floor | 26.7% | 53.3% | 20.0% | 0.0% |
| B4 Correlation Gate | 40.0% | 26.7% | 10.0% | 0.0% |
| BH-FDR Gate | 37.5% | 16.7% | 10.0% | 0.0% |

---

## 300ETF — `long`

| Period | Pool Size | FP Rate | Mean OOS IC | Mean OOS Sharpe |
| :--- | ---: | ---: | ---: | ---: |
| 2015-2022 (Original) | 0 | 0.0% | +0.0000 | +0.0000 |
| 2015-2023 | 0 | 0.0% | +0.0000 | +0.0000 |
| 2016-2024 | 0 | 0.0% | +0.0000 | +0.0000 |
| 2017-2025 | 0 | 0.0% | +0.0000 | +0.0000 |

### Per-Gate False Negative Rate Comparison

| Gate | 2015-2022 (Original) | 2015-2023 | 2016-2024 | 2017-2025 |
| :--- | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 26.7% | 16.7% | 60.0% | 26.7% |
| B2 Rolling Guard | 0.0% | 6.7% | 10.0% | 10.0% |
| B3 Composite Floor | 0.0% | 0.0% | 0.0% | 0.0% |
| B4 Correlation Gate | 0.0% | 0.0% | 0.0% | 0.0% |
| BH-FDR Gate | 0.0% | 0.0% | 0.0% | 0.0% |

---

## 300ETF — `short`

| Period | Pool Size | FP Rate | Mean OOS IC | Mean OOS Sharpe |
| :--- | ---: | ---: | ---: | ---: |
| 2015-2022 (Original) | 0 | 0.0% | +0.0000 | +0.0000 |
| 2015-2023 | 0 | 0.0% | +0.0000 | +0.0000 |
| 2016-2024 | 0 | 0.0% | +0.0000 | +0.0000 |
| 2017-2025 | 0 | 0.0% | +0.0000 | +0.0000 |

### Per-Gate False Negative Rate Comparison

| Gate | 2015-2022 (Original) | 2015-2023 | 2016-2024 | 2017-2025 |
| :--- | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 13.3% | 6.7% | 10.0% | 40.0% |
| B2 Rolling Guard | 10.0% | 6.7% | 3.3% | 30.0% |
| B3 Composite Floor | 13.3% | 0.0% | 0.0% | 100.0% |
| B4 Correlation Gate | 0.0% | 0.0% | 0.0% | 0.0% |
| BH-FDR Gate | 36.7% | 28.6% | 14.3% | 25.0% |

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

## 50ETF — `long`

| Period | Pool Size | FP Rate | Mean OOS IC | Mean OOS Sharpe |
| :--- | ---: | ---: | ---: | ---: |
| 2015-2022 (Original) | 0 | 0.0% | +0.0000 | +0.0000 |
| 2015-2023 | 0 | 0.0% | +0.0000 | +0.0000 |
| 2016-2024 | 0 | 0.0% | +0.0000 | +0.0000 |
| 2017-2025 | 0 | 0.0% | +0.0000 | +0.0000 |

### Per-Gate False Negative Rate Comparison

| Gate | 2015-2022 (Original) | 2015-2023 | 2016-2024 | 2017-2025 |
| :--- | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 36.7% | 3.3% | 23.3% | 0.0% |
| B2 Rolling Guard | 6.7% | 6.7% | 3.3% | 10.0% |
| B3 Composite Floor | 0.0% | 0.0% | 0.0% | 0.0% |
| B4 Correlation Gate | 0.0% | 0.0% | 0.0% | 0.0% |
| BH-FDR Gate | 0.0% | 0.0% | 0.0% | 0.0% |

---

## 50ETF — `short`

| Period | Pool Size | FP Rate | Mean OOS IC | Mean OOS Sharpe |
| :--- | ---: | ---: | ---: | ---: |
| 2015-2022 (Original) | 0 | 0.0% | +0.0000 | +0.0000 |
| 2015-2023 | 0 | 0.0% | +0.0000 | +0.0000 |
| 2016-2024 | 0 | 0.0% | +0.0000 | +0.0000 |
| 2017-2025 | 0 | 0.0% | +0.0000 | +0.0000 |

### Per-Gate False Negative Rate Comparison

| Gate | 2015-2022 (Original) | 2015-2023 | 2016-2024 | 2017-2025 |
| :--- | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 40.0% | 36.7% | 43.3% | 63.3% |
| B2 Rolling Guard | 3.3% | 6.7% | 0.0% | 16.7% |
| B3 Composite Floor | 0.0% | 0.0% | 0.0% | 0.0% |
| B4 Correlation Gate | 0.0% | 0.0% | 0.0% | 0.0% |
| BH-FDR Gate | 14.3% | 0.0% | 0.0% | 50.0% |

---

## 500ETF — `single`

| Period | Pool Size | FP Rate | Mean OOS IC | Mean OOS Sharpe |
| :--- | ---: | ---: | ---: | ---: |
| 2015-2022 (Original) | 37 | 40.5% | +0.0967 | +0.1342 |
| 2015-2023 | 32 | 37.5% | +0.0944 | +0.0893 |
| 2016-2024 | 31 | 48.4% | +0.0896 | +0.0974 |
| 2017-2025 | 32 | 78.1% | +0.0605 | -0.8063 |

### Per-Gate False Negative Rate Comparison

| Gate | 2015-2022 (Original) | 2015-2023 | 2016-2024 | 2017-2025 |
| :--- | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 63.3% | 80.0% | 80.0% | 10.0% |
| B2 Rolling Guard | 30.0% | 3.3% | 50.0% | 10.0% |
| B3 Composite Floor | 80.0% | 80.0% | 73.3% | 10.0% |
| B4 Correlation Gate | 60.0% | 93.3% | 53.3% | 0.0% |
| BH-FDR Gate | 10.3% | 0.0% | 16.7% | 18.2% |

---

## 500ETF — `long`

| Period | Pool Size | FP Rate | Mean OOS IC | Mean OOS Sharpe |
| :--- | ---: | ---: | ---: | ---: |
| 2015-2022 (Original) | 0 | 0.0% | +0.0000 | +0.0000 |
| 2015-2023 | 0 | 0.0% | +0.0000 | +0.0000 |
| 2016-2024 | 0 | 0.0% | +0.0000 | +0.0000 |
| 2017-2025 | 0 | 0.0% | +0.0000 | +0.0000 |

### Per-Gate False Negative Rate Comparison

| Gate | 2015-2022 (Original) | 2015-2023 | 2016-2024 | 2017-2025 |
| :--- | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 26.7% | 0.0% | 20.0% | 63.3% |
| B2 Rolling Guard | 10.0% | 20.0% | 3.3% | 10.0% |
| B3 Composite Floor | 20.0% | 20.7% | 100.0% | 0.0% |
| B4 Correlation Gate | 0.0% | 0.0% | 0.0% | 0.0% |
| BH-FDR Gate | 26.7% | 16.7% | 10.0% | 65.2% |

---

## 500ETF — `short`

| Period | Pool Size | FP Rate | Mean OOS IC | Mean OOS Sharpe |
| :--- | ---: | ---: | ---: | ---: |
| 2015-2022 (Original) | 0 | 0.0% | +0.0000 | +0.0000 |
| 2015-2023 | 0 | 0.0% | +0.0000 | +0.0000 |
| 2016-2024 | 0 | 0.0% | +0.0000 | +0.0000 |
| 2017-2025 | 0 | 0.0% | +0.0000 | +0.0000 |

### Per-Gate False Negative Rate Comparison

| Gate | 2015-2022 (Original) | 2015-2023 | 2016-2024 | 2017-2025 |
| :--- | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 13.3% | 43.3% | 20.0% | 23.3% |
| B2 Rolling Guard | 13.3% | 13.3% | 16.7% | 30.0% |
| B3 Composite Floor | 0.0% | 0.0% | 0.0% | 0.0% |
| B4 Correlation Gate | 0.0% | 0.0% | 0.0% | 0.0% |
| BH-FDR Gate | 71.4% | 33.3% | 50.0% | 7.1% |

---

## 159915ETF — `single`

| Period | Pool Size | FP Rate | Mean OOS IC | Mean OOS Sharpe |
| :--- | ---: | ---: | ---: | ---: |
| 2015-2022 (Original) | 15 | 13.3% | +0.1151 | +0.6320 |
| 2015-2023 | 27 | 7.4% | +0.1114 | +0.5806 |
| 2016-2024 | 30 | 16.7% | +0.1076 | +0.4779 |
| 2017-2025 | 27 | 37.0% | +0.1135 | +0.2255 |

### Per-Gate False Negative Rate Comparison

| Gate | 2015-2022 (Original) | 2015-2023 | 2016-2024 | 2017-2025 |
| :--- | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 63.3% | 76.7% | 66.7% | 63.3% |
| B2 Rolling Guard | 90.0% | 70.0% | 76.7% | 56.7% |
| B3 Composite Floor | 100.0% | 100.0% | 70.0% | 53.3% |
| B4 Correlation Gate | 96.7% | 100.0% | 100.0% | 100.0% |
| BH-FDR Gate | 83.3% | 0.0% | 44.4% | 15.4% |

---

## 159915ETF — `long`

| Period | Pool Size | FP Rate | Mean OOS IC | Mean OOS Sharpe |
| :--- | ---: | ---: | ---: | ---: |
| 2015-2022 (Original) | 0 | 0.0% | +0.0000 | +0.0000 |
| 2015-2023 | 0 | 0.0% | +0.0000 | +0.0000 |
| 2016-2024 | 0 | 0.0% | +0.0000 | +0.0000 |
| 2017-2025 | 0 | 0.0% | +0.0000 | +0.0000 |

### Per-Gate False Negative Rate Comparison

| Gate | 2015-2022 (Original) | 2015-2023 | 2016-2024 | 2017-2025 |
| :--- | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 60.0% | 56.7% | 63.3% | 36.7% |
| B2 Rolling Guard | 80.0% | 66.7% | 76.7% | 50.0% |
| B3 Composite Floor | 0.0% | 0.0% | 90.9% | 0.0% |
| B4 Correlation Gate | 0.0% | 0.0% | 0.0% | 0.0% |
| BH-FDR Gate | 76.7% | 90.0% | 86.7% | 93.3% |

---

## 159915ETF — `short`

| Period | Pool Size | FP Rate | Mean OOS IC | Mean OOS Sharpe |
| :--- | ---: | ---: | ---: | ---: |
| 2015-2022 (Original) | 0 | 0.0% | +0.0000 | +0.0000 |
| 2015-2023 | 0 | 0.0% | +0.0000 | +0.0000 |
| 2016-2024 | 0 | 0.0% | +0.0000 | +0.0000 |
| 2017-2025 | 0 | 0.0% | +0.0000 | +0.0000 |

### Per-Gate False Negative Rate Comparison

| Gate | 2015-2022 (Original) | 2015-2023 | 2016-2024 | 2017-2025 |
| :--- | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 40.0% | 23.3% | 30.0% | 30.0% |
| B2 Rolling Guard | 23.3% | 26.7% | 43.3% | 33.3% |
| B3 Composite Floor | 0.0% | 0.0% | 0.0% | 0.0% |
| B4 Correlation Gate | 0.0% | 0.0% | 0.0% | 0.0% |
| BH-FDR Gate | 75.0% | 50.0% | 50.0% | 0.0% |

---

