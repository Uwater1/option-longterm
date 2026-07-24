# Multi-Period FP Rate Comparison Report

Cross-period comparison of filter gate false positive/negative rates.
Ground truth: OOS (post-training) performance. No lockbox used.

---

## 300ETF — `single`

| Period | Pool Size | FP Rate | Mean OOS IC | Mean OOS Sharpe |
| :--- | ---: | ---: | ---: | ---: |
| 2015-2022 (Original) | 11 | 54.5% | +0.0258 | -0.2203 |
| 2015-2023 | 2 | 100.0% | +0.0664 | -0.2353 |
| 2016-2024 | 3 | 100.0% | +0.0104 | -0.5633 |
| 2017-2025 | 3 | 100.0% | -0.0209 | -1.6911 |

### Per-Gate False Negative Rate Comparison

| Gate | 2015-2022 (Original) | 2015-2023 | 2016-2024 | 2017-2025 |
| :--- | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 10.0% | 10.0% | 26.7% | 6.7% |
| B2 Rolling Guard | 33.3% | 0.0% | 0.0% | 0.0% |
| B3 Composite Floor | 26.7% | 25.0% | 40.0% | 0.0% |
| B4 Correlation Gate | 40.0% | 0.0% | 0.0% | 0.0% |
| BH-FDR Gate | 37.5% | 0.0% | 0.0% | 0.0% |

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
| 7-Year Jackknife Sign Stability | 26.7% | 10.0% | 36.7% | 20.0% |
| B2 Rolling Guard | 0.0% | 3.4% | 3.7% | 0.0% |
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
| 7-Year Jackknife Sign Stability | 13.3% | 6.7% | 20.0% | 26.7% |
| B2 Rolling Guard | 10.0% | 6.7% | 0.0% | 13.3% |
| B3 Composite Floor | 13.3% | 0.0% | 0.0% | 0.0% |
| B4 Correlation Gate | 0.0% | 0.0% | 0.0% | 0.0% |
| BH-FDR Gate | 36.7% | 0.0% | 0.0% | 33.3% |

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
| 7-Year Jackknife Sign Stability | 46.7% | 13.3% | 26.7% | 16.7% |
| B2 Rolling Guard | 23.3% | 0.0% | 0.0% | 0.0% |
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
| 7-Year Jackknife Sign Stability | 36.7% | 13.3% | 3.3% | 0.0% |
| B2 Rolling Guard | 6.7% | 0.0% | 3.7% | 4.2% |
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
| 7-Year Jackknife Sign Stability | 40.0% | 16.7% | 33.3% | 46.7% |
| B2 Rolling Guard | 3.3% | 6.7% | 0.0% | 16.7% |
| B3 Composite Floor | 0.0% | 0.0% | 0.0% | 0.0% |
| B4 Correlation Gate | 0.0% | 0.0% | 0.0% | 0.0% |
| BH-FDR Gate | 14.3% | 0.0% | 0.0% | 50.0% |

---

## 500ETF — `single`

| Period | Pool Size | FP Rate | Mean OOS IC | Mean OOS Sharpe |
| :--- | ---: | ---: | ---: | ---: |
| 2015-2022 (Original) | 37 | 40.5% | +0.0967 | +0.1342 |
| 2015-2023 | 7 | 42.9% | +0.0869 | -0.0411 |
| 2016-2024 | 6 | 66.7% | +0.0804 | -0.1402 |
| 2017-2025 | 6 | 100.0% | +0.0336 | -1.5296 |

### Per-Gate False Negative Rate Comparison

| Gate | 2015-2022 (Original) | 2015-2023 | 2016-2024 | 2017-2025 |
| :--- | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 63.3% | 16.7% | 30.0% | 10.0% |
| B2 Rolling Guard | 30.0% | 13.8% | 24.1% | 14.3% |
| B3 Composite Floor | 80.0% | 15.4% | 23.1% | 0.0% |
| B4 Correlation Gate | 60.0% | 33.3% | 42.9% | 0.0% |
| BH-FDR Gate | 10.3% | 25.0% | 8.3% | 0.0% |

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
| 7-Year Jackknife Sign Stability | 26.7% | 16.7% | 26.7% | 16.7% |
| B2 Rolling Guard | 10.0% | 16.7% | 11.5% | 18.2% |
| B3 Composite Floor | 20.0% | 0.0% | 0.0% | 0.0% |
| B4 Correlation Gate | 0.0% | 0.0% | 0.0% | 0.0% |
| BH-FDR Gate | 26.7% | 42.9% | 66.7% | 20.0% |

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
| 7-Year Jackknife Sign Stability | 13.3% | 33.3% | 20.0% | 16.7% |
| B2 Rolling Guard | 13.3% | 13.3% | 16.7% | 33.3% |
| B3 Composite Floor | 0.0% | 0.0% | 0.0% | 0.0% |
| B4 Correlation Gate | 0.0% | 0.0% | 0.0% | 0.0% |
| BH-FDR Gate | 71.4% | 0.0% | 0.0% | 25.0% |

---

## 159915ETF — `single`

| Period | Pool Size | FP Rate | Mean OOS IC | Mean OOS Sharpe |
| :--- | ---: | ---: | ---: | ---: |
| 2015-2022 (Original) | 15 | 13.3% | +0.1151 | +0.6320 |
| 2015-2023 | 2 | 0.0% | +0.1161 | +0.4710 |
| 2016-2024 | 1 | 100.0% | +0.0765 | -0.0485 |
| 2017-2025 | 3 | 100.0% | +0.0817 | -0.4825 |

### Per-Gate False Negative Rate Comparison

| Gate | 2015-2022 (Original) | 2015-2023 | 2016-2024 | 2017-2025 |
| :--- | ---: | ---: | ---: | ---: |
| 7-Year Jackknife Sign Stability | 63.3% | 56.7% | 53.3% | 46.7% |
| B2 Rolling Guard | 90.0% | 30.0% | 4.5% | 19.0% |
| B3 Composite Floor | 100.0% | 90.0% | 35.7% | 16.7% |
| B4 Correlation Gate | 96.7% | 0.0% | 0.0% | 100.0% |
| BH-FDR Gate | 83.3% | 50.0% | 50.0% | 0.0% |

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
| 7-Year Jackknife Sign Stability | 60.0% | 40.0% | 36.7% | 23.3% |
| B2 Rolling Guard | 80.0% | 30.0% | 28.6% | 4.0% |
| B3 Composite Floor | 0.0% | 0.0% | 0.0% | 0.0% |
| B4 Correlation Gate | 0.0% | 0.0% | 0.0% | 0.0% |
| BH-FDR Gate | 76.7% | 0.0% | 53.8% | 40.0% |

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
| 7-Year Jackknife Sign Stability | 40.0% | 16.7% | 26.7% | 23.3% |
| B2 Rolling Guard | 23.3% | 26.7% | 33.3% | 26.7% |
| B3 Composite Floor | 0.0% | 0.0% | 0.0% | 0.0% |
| B4 Correlation Gate | 0.0% | 0.0% | 0.0% | 0.0% |
| BH-FDR Gate | 75.0% | 50.0% | 100.0% | 0.0% |

---

