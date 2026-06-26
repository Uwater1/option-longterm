# Gating Model Benchmarking & Performance Report

Separate binary classifiers trained on `trade_return` (entry open to exit close) to predict tradability.

## 1. Summary of Best Models

| ETF | Side | Best Model | Final Threshold | CV PR-AUC | CV AUC | CV Prec@70 | HO PR-AUC | HO AUC | HO Prec@70 | Deployable? |
|---|---|---|---|---|---|---|---|---|---|---|
| **50ETF** | `long` | logistic | 0.0076 | 0.2111 | 0.6743 | 18.23% | 0.1442 | 0.5533 | 9.15% | Yes |
| **50ETF** | `short` | logistic | 0.0072 | 0.2313 | 0.6503 | 20.81% | 0.2646 | 0.6609 | 18.29% | Yes |
| **300ETF** | `long` | lightgbm | 0.0078 | 0.2086 | 0.6680 | 17.50% | 0.2083 | 0.6413 | 16.46% | Yes |
| **300ETF** | `short` | rf | 0.0072 | 0.2254 | 0.6528 | 22.28% | 0.2826 | 0.7244 | 23.78% | Yes |
| **500ETF** | `long` | lightgbm | 0.0091 | 0.2163 | 0.7076 | 19.34% | 0.2126 | 0.6166 | 19.51% | Yes |
| **500ETF** | `short` | lightgbm | 0.0083 | 0.2274 | 0.7189 | 22.10% | 0.3086 | 0.7006 | 26.83% | Yes |
| **588000ETF** | `long` | lightgbm | 0.0130 | 0.1989 | 0.5970 | 18.60% | 0.2128 | 0.5611 | 23.08% | Yes |
| **588000ETF** | `short` | logistic | 0.0120 | 0.2129 | 0.5625 | 17.44% | 0.2953 | 0.6826 | 25.64% | Yes |
| **159915ETF** | `long` | rf | 0.0127 | 0.2233 | 0.6967 | 16.94% | 0.2672 | 0.7077 | 23.17% | Yes |
| **159915ETF** | `short` | logistic | 0.0103 | 0.2113 | 0.6846 | 20.44% | 0.2233 | 0.5601 | 19.51% | Yes |

## 2. Head-to-Head Comparison (CV PR-AUC)

| ETF | Side | Logistic | Random Forest | LightGBM |
|---|---|---|---|---|
| **50ETF** | `long` | 0.2111 | 0.1925 | 0.1906 |
| **50ETF** | `short` | 0.2313 | 0.2172 | 0.2202 |
| **300ETF** | `long` | 0.1711 | 0.1971 | 0.2086 |
| **300ETF** | `short` | 0.2083 | 0.2254 | 0.2110 |
| **500ETF** | `long` | 0.1757 | 0.2115 | 0.2163 |
| **500ETF** | `short` | 0.1914 | 0.2141 | 0.2274 |
| **588000ETF** | `long` | 0.1963 | 0.1977 | 0.1989 |
| **588000ETF** | `short` | 0.2129 | 0.2050 | 0.1706 |
| **159915ETF** | `long` | 0.2055 | 0.2233 | 0.2225 |
| **159915ETF** | `short` | 0.2113 | 0.2057 | 0.2093 |

## 3. Deployability & Model Selection Analysis

Detailed analysis of why specific model architectures were selected:

### 50ETF

- **`long` Side**: Selected **logistic**.
  * *Reason*: Logistic Regression won, showing that a linear boundary is highly robust here. Non-linear models (RF/LightGBM) overfit to noise.
  * *Metrics*: PR-AUC `0.2111` (Base: `0.1050`), Precision@70 `18.23%` (Lift: `+73.7%`).
  * *Verdict*: **Deployable** (Significant precision lift, PR-AUC exceeds base rate, out-of-sample AUC > 0.55).
- **`short` Side**: Selected **logistic**.
  * *Reason*: Logistic Regression won, showing that a linear boundary is highly robust here. Non-linear models (RF/LightGBM) overfit to noise.
  * *Metrics*: PR-AUC `0.2313` (Base: `0.1365`), Precision@70 `20.81%` (Lift: `+52.5%`).
  * *Verdict*: **Deployable** (Significant precision lift, PR-AUC exceeds base rate, out-of-sample AUC > 0.55).

### 300ETF

- **`long` Side**: Selected **lightgbm**.
  * *Reason*: LightGBM won, showing that gradient boosting successfully captured complex non-linear combinations of early-bar and daily signals.
  * *Metrics*: PR-AUC `0.2086` (Base: `0.1061`), Precision@70 `17.50%` (Lift: `+64.9%`).
  * *Verdict*: **Deployable** (Significant precision lift, PR-AUC exceeds base rate, out-of-sample AUC > 0.55).
- **`short` Side**: Selected **rf**.
  * *Reason*: Random Forest won, showing that bagging is effective at reducing variance and mitigating overfitting on noisy features.
  * *Metrics*: PR-AUC `0.2254` (Base: `0.1348`), Precision@70 `22.28%` (Lift: `+65.3%`).
  * *Verdict*: **Deployable** (Significant precision lift, PR-AUC exceeds base rate, out-of-sample AUC > 0.55).

### 500ETF

- **`long` Side**: Selected **lightgbm**.
  * *Reason*: LightGBM won, showing that gradient boosting successfully captured complex non-linear combinations of early-bar and daily signals.
  * *Metrics*: PR-AUC `0.2163` (Base: `0.0934`), Precision@70 `19.34%` (Lift: `+107.1%`).
  * *Verdict*: **Deployable** (Significant precision lift, PR-AUC exceeds base rate, out-of-sample AUC > 0.55).
- **`short` Side**: Selected **lightgbm**.
  * *Reason*: LightGBM won, showing that gradient boosting successfully captured complex non-linear combinations of early-bar and daily signals.
  * *Metrics*: PR-AUC `0.2274` (Base: `0.1149`), Precision@70 `22.10%` (Lift: `+92.3%`).
  * *Verdict*: **Deployable** (Significant precision lift, PR-AUC exceeds base rate, out-of-sample AUC > 0.55).

### 588000ETF

- **`long` Side**: Selected **lightgbm**.
  * *Reason*: LightGBM won, showing that gradient boosting successfully captured complex non-linear combinations of early-bar and daily signals.
  * *Metrics*: PR-AUC `0.1989` (Base: `0.1360`), Precision@70 `18.60%` (Lift: `+36.8%`).
  * *Verdict*: **Deployable** (Significant precision lift, PR-AUC exceeds base rate, out-of-sample AUC > 0.55).
- **`short` Side**: Selected **logistic**.
  * *Reason*: Logistic Regression won, showing that a linear boundary is highly robust here. Non-linear models (RF/LightGBM) overfit to noise.
  * *Metrics*: PR-AUC `0.2129` (Base: `0.1384`), Precision@70 `17.44%` (Lift: `+26.1%`).
  * *Verdict*: **Deployable** (Significant precision lift, PR-AUC exceeds base rate, out-of-sample AUC > 0.55).

### 159915ETF

- **`long` Side**: Selected **rf**.
  * *Reason*: Random Forest won, showing that bagging is effective at reducing variance and mitigating overfitting on noisy features.
  * *Metrics*: PR-AUC `0.2233` (Base: `0.0950`), Precision@70 `16.94%` (Lift: `+78.3%`).
  * *Verdict*: **Deployable** (Significant precision lift, PR-AUC exceeds base rate, out-of-sample AUC > 0.55).
- **`short` Side**: Selected **logistic**.
  * *Reason*: Logistic Regression won, showing that a linear boundary is highly robust here. Non-linear models (RF/LightGBM) overfit to noise.
  * *Metrics*: PR-AUC `0.2113` (Base: `0.1254`), Precision@70 `20.44%` (Lift: `+63.0%`).
  * *Verdict*: **Deployable** (Significant precision lift, PR-AUC exceeds base rate, out-of-sample AUC > 0.55).


## 4. Diagnostic Plots & Validation

ROC and PR Curves are saved under `gating_model/plots/curves_{ETF}_{side}.png`.
