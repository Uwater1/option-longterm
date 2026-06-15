# Filter Indicator Statistical Validation Report

Generated on: `2026-06-15 14:29:12`  
Primary Horizon: `30` calendar days  
Horizons: `['7d', '14d', '30d']`  

> [!NOTE]
> Validates technical indicators used in both the **Call Strategy** (`backtest_covered_call.py`) and the **Put Strategy** (`backtest_put.py`) (RSI, BBU, ROC, SMA50, MACD Hist, Vol20 regime) against forward ETF returns. Determines if filter conditions have statistical edge.

## Visualizations

### Figure 1: Indicator Value vs 30-Calendar-Day Forward Return Scatter & Bin Plots
![Scatter & Bin Plots](filter_validation_report.png)

### Figure 2: Filter Pass/Fail Bar Chart, Significance Heatmap, and Summary Table
![Bar Chart + Heatmap + Table](filter_validation_report_2.png)

## Interpretation Guide

- **Cohen's d (Effect Size)**: Standard deviation difference between Pass and Fail returns.
  - Positive: Filter-pass has higher forward returns (good for trend entry checks).
  - Negative: Filter-pass has lower forward returns (supports RSI/BBU cap to avoid overbought assignments).
  - Size: 0.1 = small, 0.3 = medium, 0.5 = large.
- **p-value**: Welch's t-test / Mann-Whitney U test significance. p < 0.05 is statistically reliable.
- **Verdict**:
  - `SIGNIFICANT`: p < 0.05 and |Cohen's d| >= 0.1
  - `MARGINAL`: p < 0.10
  - `NOT SIGNIFICANT`: p >= 0.10

## Individual Filter Analysis (Call + Put Indicators)

### 7-Calendar-Day Forward Return Horizon

| ETF | Filter | Placement % | Pass Avg | Fail Avg | Diff | p(t-test) | p(M-W) | Cohen's d | Verdict |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| 300ETF | RSI < 66 | 89.6% | +0.083% | +0.734% | -0.650% | 0.0464 | 0.5332 | -0.226 | **SIGNIFICANT** |
| 300ETF | RSI < 72 | 95.5% | +0.095% | +1.348% | -1.253% | 0.0179 | 0.0453 | -0.436 | **SIGNIFICANT** |
| 300ETF | RSI > 25 | 99.1% | +0.134% | +1.922% | -1.789% | 0.0759 | 0.0165 | -0.621 | *MARGINAL* |
| 300ETF | RSI > 30 | 96.8% | +0.121% | +1.030% | -0.908% | 0.0279 | 0.0282 | -0.315 | **SIGNIFICANT** |
| 300ETF | RSI > 35 | 91.6% | +0.105% | +0.649% | -0.543% | 0.0127 | 0.0077 | -0.189 | **SIGNIFICANT** |
| 300ETF | Close < BBU | 93.2% | +0.078% | +1.148% | -1.070% | 0.0077 | 0.0125 | -0.372 | **SIGNIFICANT** |
| 300ETF | Close < BBU+0.5*ATR | 97.0% | +0.082% | +2.369% | -2.287% | 0.0050 | 0.0004 | -0.800 | **SIGNIFICANT** |
| 300ETF | Close > SMA50 | 50.8% | +0.086% | +0.217% | -0.131% | 0.3353 | 0.1085 | -0.045 | NOT SIGNIFICANT |
| 300ETF | ROC10 < 3% | 80.4% | +0.058% | +0.531% | -0.473% | 0.0251 | 0.5432 | -0.164 | **SIGNIFICANT** |
| 300ETF | ROC10 < 7% | 95.8% | +0.109% | +1.105% | -0.996% | 0.0814 | 0.1061 | -0.346 | *MARGINAL* |
| 300ETF | ROC20 < 3% | 71.6% | +0.131% | +0.200% | -0.068% | 0.6691 | 0.7067 | -0.024 | NOT SIGNIFICANT |
| 300ETF | ROC20 < 4% | 78.7% | +0.085% | +0.393% | -0.308% | 0.0898 | 0.1364 | -0.107 | *MARGINAL* |
| 300ETF | MACD Hist < 0 | 50.6% | +0.191% | +0.110% | +0.081% | 0.5558 | 0.1220 | +0.028 | NOT SIGNIFICANT |
| 300ETF | Vol20 < Med | 43.8% | -0.004% | +0.271% | -0.276% | 0.0394 | 0.0079 | -0.096 | *MARGINAL* |
| 300ETF | RSI < 55 | 61.7% | +0.115% | +0.209% | -0.094% | 0.5226 | 0.3905 | -0.032 | NOT SIGNIFICANT |
| 300ETF | RSI < 60 | 75.4% | +0.113% | +0.267% | -0.154% | 0.4082 | 0.4405 | -0.053 | NOT SIGNIFICANT |
| 300ETF | Vol20 > Med | 41.2% | +0.209% | +0.110% | +0.100% | 0.4825 | 0.6721 | +0.035 | NOT SIGNIFICANT |
| 300ETF | Close < SMA50 | 46.6% | +0.115% | +0.182% | -0.066% | 0.6249 | 0.9497 | -0.023 | NOT SIGNIFICANT |
| 50ETF | RSI < 66 | 89.4% | +0.026% | +0.271% | -0.244% | 0.2311 | 0.9169 | -0.082 | NOT SIGNIFICANT |
| 50ETF | RSI < 72 | 96.0% | +0.038% | +0.388% | -0.350% | 0.3245 | 0.8636 | -0.118 | NOT SIGNIFICANT |
| 50ETF | RSI > 25 | 98.7% | +0.030% | +1.712% | -1.682% | 0.0533 | 0.0724 | -0.567 | *MARGINAL* |
| 50ETF | RSI > 30 | 96.5% | +0.021% | +0.926% | -0.905% | 0.0272 | 0.0341 | -0.305 | **SIGNIFICANT** |
| 50ETF | RSI > 35 | 92.2% | +0.034% | +0.264% | -0.230% | 0.3706 | 0.3842 | -0.077 | NOT SIGNIFICANT |
| 50ETF | Close < BBU | 92.9% | +0.047% | +0.116% | -0.069% | 0.7629 | 0.9738 | -0.023 | NOT SIGNIFICANT |
| 50ETF | Close < BBU+0.5*ATR | 97.6% | +0.060% | -0.253% | +0.313% | 0.5733 | 0.0232 | +0.105 | NOT SIGNIFICANT |
| 50ETF | Close > SMA50 | 51.5% | +0.058% | +0.047% | +0.011% | 0.9225 | 0.1350 | +0.004 | NOT SIGNIFICANT |
| 50ETF | ROC10 < 3% | 80.9% | +0.079% | -0.059% | +0.138% | 0.3718 | 0.0101 | +0.047 | NOT SIGNIFICANT |
| 50ETF | ROC10 < 7% | 96.1% | +0.057% | -0.053% | +0.109% | 0.7851 | 0.2687 | +0.037 | NOT SIGNIFICANT |
| 50ETF | ROC20 < 3% | 72.5% | +0.066% | +0.015% | +0.051% | 0.6923 | 0.1979 | +0.017 | NOT SIGNIFICANT |
| 50ETF | ROC20 < 4% | 78.9% | +0.033% | +0.124% | -0.091% | 0.5448 | 0.9567 | -0.031 | NOT SIGNIFICANT |
| 50ETF | MACD Hist < 0 | 48.5% | +0.076% | +0.030% | +0.047% | 0.6788 | 0.4690 | +0.016 | NOT SIGNIFICANT |
| 50ETF | Vol20 < Med | 48.9% | +0.198% | -0.087% | +0.285% | 0.0110 | 0.0260 | +0.096 | *MARGINAL* |
| 50ETF | RSI < 55 | 64.3% | +0.066% | +0.028% | +0.038% | 0.7452 | 0.0466 | +0.013 | NOT SIGNIFICANT |
| 50ETF | RSI < 60 | 77.1% | +0.022% | +0.155% | -0.133% | 0.3355 | 0.3831 | -0.045 | NOT SIGNIFICANT |
| 50ETF | Vol20 > Med | 41.4% | -0.020% | +0.103% | -0.123% | 0.2749 | 0.1600 | -0.042 | NOT SIGNIFICANT |
| 50ETF | Close < SMA50 | 46.8% | +0.038% | +0.065% | -0.027% | 0.8086 | 0.1394 | -0.009 | NOT SIGNIFICANT |
| 500ETF | RSI < 66 | 87.2% | -0.085% | +5.056% | -5.141% | 0.0016 | 0.0000 | -0.449 | **SIGNIFICANT** |
| 500ETF | RSI < 72 | 92.8% | -0.052% | +8.642% | -8.694% | 0.0025 | 0.0000 | -0.766 | **SIGNIFICANT** |
| 500ETF | RSI > 25 | 98.3% | +0.545% | +2.360% | -1.815% | 0.0115 | 0.0009 | -0.157 | **SIGNIFICANT** |
| 500ETF | RSI > 30 | 94.9% | +0.537% | +1.309% | -0.772% | 0.0625 | 0.0016 | -0.067 | *MARGINAL* |
| 500ETF | RSI > 35 | 90.3% | +0.584% | +0.496% | +0.088% | 0.8136 | 0.0142 | +0.008 | NOT SIGNIFICANT |
| 500ETF | Close < BBU | 94.6% | +0.485% | +2.147% | -1.662% | 0.0007 | 0.0000 | -0.144 | **SIGNIFICANT** |
| 500ETF | Close < BBU+0.5*ATR | 98.2% | +0.523% | +3.442% | -2.919% | 0.0032 | 0.0000 | -0.253 | **SIGNIFICANT** |
| 500ETF | Close > SMA50 | 50.5% | +1.073% | +0.068% | +1.005% | 0.0210 | 0.8460 | +0.087 | *MARGINAL* |
| 500ETF | ROC10 < 3% | 75.1% | -0.117% | +2.664% | -2.781% | 0.0011 | 0.0000 | -0.242 | **SIGNIFICANT** |
| 500ETF | ROC10 < 7% | 92.5% | +0.013% | +7.508% | -7.495% | 0.0069 | 0.0000 | -0.658 | **SIGNIFICANT** |
| 500ETF | ROC20 < 3% | 67.3% | -0.131% | +2.031% | -2.161% | 0.0009 | 0.0000 | -0.188 | **SIGNIFICANT** |
| 500ETF | ROC20 < 4% | 73.2% | -0.124% | +2.484% | -2.609% | 0.0010 | 0.0000 | -0.227 | **SIGNIFICANT** |
| 500ETF | MACD Hist < 0 | 47.2% | -0.148% | +1.224% | -1.371% | 0.0011 | 0.0236 | -0.119 | **SIGNIFICANT** |
| 500ETF | Vol20 < Med | 47.4% | +0.082% | +1.020% | -0.938% | 0.0252 | 0.3180 | -0.081 | *MARGINAL* |
| 500ETF | RSI < 55 | 60.4% | -0.076% | +1.570% | -1.646% | 0.0025 | 0.0543 | -0.143 | **SIGNIFICANT** |
| 500ETF | RSI < 60 | 74.4% | -0.085% | +2.497% | -2.582% | 0.0018 | 0.0010 | -0.224 | **SIGNIFICANT** |
| 500ETF | Vol20 > Med | 42.9% | +0.076% | +0.951% | -0.874% | 0.0252 | 0.0728 | -0.076 | *MARGINAL* |
| 500ETF | Close < SMA50 | 47.7% | -0.023% | +1.123% | -1.146% | 0.0067 | 0.1769 | -0.099 | *MARGINAL* |

### 14-Calendar-Day Forward Return Horizon

| ETF | Filter | Placement % | Pass Avg | Fail Avg | Diff | p(t-test) | p(M-W) | Cohen's d | Verdict |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| 300ETF | RSI < 66 | 89.6% | +0.178% | +0.979% | -0.801% | 0.0367 | 0.1979 | -0.204 | **SIGNIFICANT** |
| 300ETF | RSI < 72 | 95.5% | +0.197% | +1.634% | -1.437% | 0.0074 | 0.0286 | -0.366 | **SIGNIFICANT** |
| 300ETF | RSI > 25 | 99.1% | +0.247% | +1.767% | -1.520% | 0.1540 | 0.2204 | -0.386 | NOT SIGNIFICANT |
| 300ETF | RSI > 30 | 96.8% | +0.183% | +2.610% | -2.427% | 0.0045 | 0.0009 | -0.620 | **SIGNIFICANT** |
| 300ETF | RSI > 35 | 91.6% | +0.189% | +1.057% | -0.868% | 0.0249 | 0.0709 | -0.221 | **SIGNIFICANT** |
| 300ETF | Close < BBU | 93.2% | +0.215% | +0.904% | -0.689% | 0.0627 | 0.1691 | -0.175 | *MARGINAL* |
| 300ETF | Close < BBU+0.5*ATR | 97.0% | +0.218% | +1.671% | -1.453% | 0.0328 | 0.0291 | -0.370 | **SIGNIFICANT** |
| 300ETF | Close > SMA50 | 50.6% | +0.079% | +0.448% | -0.369% | 0.0474 | 0.2409 | -0.094 | *MARGINAL* |
| 300ETF | ROC10 < 3% | 80.3% | +0.206% | +0.489% | -0.283% | 0.2505 | 0.8345 | -0.072 | NOT SIGNIFICANT |
| 300ETF | ROC10 < 7% | 95.8% | +0.235% | +0.866% | -0.630% | 0.2138 | 0.2486 | -0.160 | NOT SIGNIFICANT |
| 300ETF | ROC20 < 3% | 71.6% | +0.255% | +0.277% | -0.022% | 0.9195 | 0.5111 | -0.006 | NOT SIGNIFICANT |
| 300ETF | ROC20 < 4% | 78.6% | +0.225% | +0.395% | -0.170% | 0.4912 | 0.2182 | -0.043 | NOT SIGNIFICANT |
| 300ETF | MACD Hist < 0 | 50.4% | +0.405% | +0.116% | +0.290% | 0.1198 | 0.1392 | +0.074 | NOT SIGNIFICANT |
| 300ETF | Vol20 < Med | 43.9% | +0.131% | +0.364% | -0.233% | 0.2162 | 0.0000 | -0.059 | NOT SIGNIFICANT |
| 300ETF | RSI < 55 | 61.8% | +0.198% | +0.364% | -0.166% | 0.3937 | 0.3856 | -0.042 | NOT SIGNIFICANT |
| 300ETF | RSI < 60 | 75.3% | +0.226% | +0.371% | -0.145% | 0.5352 | 0.9212 | -0.037 | NOT SIGNIFICANT |
| 300ETF | Vol20 > Med | 41.1% | +0.217% | +0.293% | -0.076% | 0.6800 | 0.1282 | -0.019 | NOT SIGNIFICANT |
| 300ETF | Close < SMA50 | 46.8% | +0.261% | +0.263% | -0.002% | 0.9907 | 0.4141 | -0.001 | NOT SIGNIFICANT |
| 50ETF | RSI < 66 | 89.4% | +0.079% | +0.227% | -0.148% | 0.5656 | 0.3163 | -0.037 | NOT SIGNIFICANT |
| 50ETF | RSI < 72 | 96.0% | +0.105% | -0.166% | +0.271% | 0.4961 | 0.0354 | +0.068 | NOT SIGNIFICANT |
| 50ETF | RSI > 25 | 98.7% | +0.061% | +2.578% | -2.517% | 0.0155 | 0.0104 | -0.631 | **SIGNIFICANT** |
| 50ETF | RSI > 30 | 96.5% | +0.031% | +1.843% | -1.811% | 0.0019 | 0.0002 | -0.455 | **SIGNIFICANT** |
| 50ETF | RSI > 35 | 92.2% | +0.036% | +0.782% | -0.746% | 0.0346 | 0.0333 | -0.187 | **SIGNIFICANT** |
| 50ETF | Close < BBU | 92.9% | +0.121% | -0.249% | +0.370% | 0.1774 | 0.1688 | +0.093 | NOT SIGNIFICANT |
| 50ETF | Close < BBU+0.5*ATR | 97.6% | +0.134% | -1.510% | +1.644% | 0.0010 | 0.0001 | +0.412 | **SIGNIFICANT** |
| 50ETF | Close > SMA50 | 51.6% | +0.109% | +0.079% | +0.030% | 0.8446 | 0.2558 | +0.007 | NOT SIGNIFICANT |
| 50ETF | ROC10 < 3% | 80.9% | +0.186% | -0.291% | +0.477% | 0.0266 | 0.0005 | +0.119 | **SIGNIFICANT** |
| 50ETF | ROC10 < 7% | 96.1% | +0.120% | -0.534% | +0.655% | 0.2053 | 0.0190 | +0.164 | NOT SIGNIFICANT |
| 50ETF | ROC20 < 3% | 72.5% | +0.125% | +0.014% | +0.111% | 0.5346 | 0.0698 | +0.028 | NOT SIGNIFICANT |
| 50ETF | ROC20 < 4% | 78.9% | +0.092% | +0.106% | -0.014% | 0.9464 | 0.2185 | -0.003 | NOT SIGNIFICANT |
| 50ETF | MACD Hist < 0 | 48.4% | +0.197% | -0.002% | +0.199% | 0.1898 | 0.3613 | +0.050 | NOT SIGNIFICANT |
| 50ETF | Vol20 < Med | 49.0% | +0.367% | -0.167% | +0.534% | 0.0004 | 0.0194 | +0.134 | **SIGNIFICANT** |
| 50ETF | RSI < 55 | 64.2% | +0.067% | +0.144% | -0.076% | 0.6265 | 0.2854 | -0.019 | NOT SIGNIFICANT |
| 50ETF | RSI < 60 | 77.1% | +0.052% | +0.237% | -0.185% | 0.3170 | 0.2835 | -0.046 | NOT SIGNIFICANT |
| 50ETF | Vol20 > Med | 41.3% | -0.040% | +0.189% | -0.229% | 0.1203 | 0.0842 | -0.057 | NOT SIGNIFICANT |
| 50ETF | Close < SMA50 | 46.7% | +0.027% | +0.154% | -0.126% | 0.4097 | 0.5109 | -0.032 | NOT SIGNIFICANT |
| 500ETF | RSI < 66 | 87.1% | -0.100% | +9.366% | -9.466% | 0.0000 | 0.0000 | -0.583 | **SIGNIFICANT** |
| 500ETF | RSI < 72 | 92.8% | -0.013% | +15.629% | -15.642% | 0.0001 | 0.0000 | -0.976 | **SIGNIFICANT** |
| 500ETF | RSI > 25 | 98.3% | +1.102% | +2.039% | -0.937% | 0.3725 | 0.1592 | -0.057 | NOT SIGNIFICANT |
| 500ETF | RSI > 30 | 94.9% | +1.135% | +0.799% | +0.336% | 0.5590 | 0.7525 | +0.020 | NOT SIGNIFICANT |
| 500ETF | RSI > 35 | 90.3% | +1.179% | +0.546% | +0.633% | 0.1958 | 0.6406 | +0.038 | NOT SIGNIFICANT |
| 500ETF | Close < BBU | 94.5% | +1.007% | +3.045% | -2.039% | 0.0004 | 0.0000 | -0.123 | **SIGNIFICANT** |
| 500ETF | Close < BBU+0.5*ATR | 98.2% | +1.062% | +4.168% | -3.106% | 0.0010 | 0.0000 | -0.188 | **SIGNIFICANT** |
| 500ETF | Close > SMA50 | 50.4% | +1.875% | +0.348% | +1.527% | 0.0144 | 0.7634 | +0.092 | *MARGINAL* |
| 500ETF | ROC10 < 3% | 75.1% | -0.077% | +4.713% | -4.790% | 0.0001 | 0.0000 | -0.292 | **SIGNIFICANT** |
| 500ETF | ROC10 < 7% | 92.5% | +0.095% | +13.695% | -13.599% | 0.0006 | 0.0000 | -0.842 | **SIGNIFICANT** |
| 500ETF | ROC20 < 3% | 67.3% | -0.126% | +3.675% | -3.801% | 0.0000 | 0.0000 | -0.231 | **SIGNIFICANT** |
| 500ETF | ROC20 < 4% | 73.1% | -0.104% | +4.440% | -4.544% | 0.0001 | 0.0000 | -0.277 | **SIGNIFICANT** |
| 500ETF | MACD Hist < 0 | 47.1% | -0.173% | +2.269% | -2.442% | 0.0000 | 0.0000 | -0.148 | **SIGNIFICANT** |
| 500ETF | Vol20 < Med | 47.5% | +0.283% | +1.873% | -1.590% | 0.0081 | 0.3166 | -0.096 | *MARGINAL* |
| 500ETF | RSI < 55 | 60.3% | -0.033% | +2.869% | -2.902% | 0.0002 | 0.0021 | -0.176 | **SIGNIFICANT** |
| 500ETF | RSI < 60 | 74.4% | -0.116% | +4.699% | -4.815% | 0.0000 | 0.0000 | -0.294 | **SIGNIFICANT** |
| 500ETF | Vol20 > Med | 42.8% | +0.046% | +1.920% | -1.874% | 0.0007 | 0.0161 | -0.114 | **SIGNIFICANT** |
| 500ETF | Close < SMA50 | 47.8% | +0.155% | +2.001% | -1.846% | 0.0023 | 0.1040 | -0.112 | **SIGNIFICANT** |

### 30-Calendar-Day Forward Return Horizon

| ETF | Filter | Placement % | Pass Avg | Fail Avg | Diff | p(t-test) | p(M-W) | Cohen's d | Verdict |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| 300ETF | RSI < 66 | 89.7% | +0.515% | +1.716% | -1.200% | 0.0226 | 0.0091 | -0.215 | **SIGNIFICANT** |
| 300ETF | RSI < 72 | 95.6% | +0.489% | +3.932% | -3.444% | 0.0000 | 0.0000 | -0.620 | **SIGNIFICANT** |
| 300ETF | RSI > 25 | 99.0% | +0.630% | +1.682% | -1.052% | 0.4041 | 0.4874 | -0.188 | NOT SIGNIFICANT |
| 300ETF | RSI > 30 | 96.7% | +0.555% | +3.152% | -2.597% | 0.0243 | 0.0820 | -0.465 | **SIGNIFICANT** |
| 300ETF | RSI > 35 | 91.6% | +0.549% | +1.622% | -1.073% | 0.0778 | 0.4261 | -0.192 | *MARGINAL* |
| 300ETF | Close < BBU | 93.2% | +0.568% | +1.614% | -1.046% | 0.0825 | 0.0757 | -0.187 | *MARGINAL* |
| 300ETF | Close < BBU+0.5*ATR | 97.0% | +0.538% | +3.877% | -3.339% | 0.0011 | 0.0001 | -0.599 | **SIGNIFICANT** |
| 300ETF | Close > SMA50 | 50.3% | +0.096% | +1.189% | -1.093% | 0.0000 | 0.0004 | -0.196 | **SIGNIFICANT** |
| 300ETF | ROC10 < 3% | 80.4% | +0.551% | +1.002% | -0.451% | 0.1988 | 0.0167 | -0.081 | NOT SIGNIFICANT |
| 300ETF | ROC10 < 7% | 95.8% | +0.566% | +2.302% | -1.736% | 0.0162 | 0.0001 | -0.310 | **SIGNIFICANT** |
| 300ETF | ROC20 < 3% | 71.8% | +0.585% | +0.779% | -0.194% | 0.5096 | 0.2614 | -0.035 | NOT SIGNIFICANT |
| 300ETF | ROC20 < 4% | 78.6% | +0.515% | +1.097% | -0.582% | 0.0806 | 0.0128 | -0.104 | *MARGINAL* |
| 300ETF | MACD Hist < 0 | 50.3% | +0.658% | +0.621% | +0.036% | 0.8910 | 0.7707 | +0.007 | NOT SIGNIFICANT |
| 300ETF | Vol20 < Med | 43.8% | +0.455% | +0.783% | -0.328% | 0.2217 | 0.0010 | -0.059 | NOT SIGNIFICANT |
| 300ETF | RSI < 55 | 62.1% | +0.526% | +0.826% | -0.300% | 0.2791 | 0.2153 | -0.054 | NOT SIGNIFICANT |
| 300ETF | RSI < 60 | 75.4% | +0.468% | +1.167% | -0.699% | 0.0348 | 0.0642 | -0.125 | **SIGNIFICANT** |
| 300ETF | Vol20 > Med | 41.1% | +0.466% | +0.761% | -0.295% | 0.2656 | 0.7638 | -0.053 | NOT SIGNIFICANT |
| 300ETF | Close < SMA50 | 47.1% | +0.739% | +0.551% | +0.188% | 0.4809 | 0.6560 | +0.034 | NOT SIGNIFICANT |
| 50ETF | RSI < 66 | 89.4% | +0.300% | -0.114% | +0.414% | 0.2501 | 0.0649 | +0.072 | NOT SIGNIFICANT |
| 50ETF | RSI < 72 | 96.0% | +0.291% | -0.593% | +0.885% | 0.0481 | 0.0687 | +0.154 | **SIGNIFICANT** |
| 50ETF | RSI > 25 | 98.7% | +0.227% | +2.362% | -2.135% | 0.1195 | 0.1754 | -0.371 | NOT SIGNIFICANT |
| 50ETF | RSI > 30 | 96.5% | +0.163% | +2.806% | -2.644% | 0.0004 | 0.0003 | -0.461 | **SIGNIFICANT** |
| 50ETF | RSI > 35 | 92.1% | +0.151% | +1.479% | -1.328% | 0.0060 | 0.0126 | -0.231 | **SIGNIFICANT** |
| 50ETF | Close < BBU | 92.9% | +0.313% | -0.487% | +0.800% | 0.0627 | 0.0049 | +0.139 | *MARGINAL* |
| 50ETF | Close < BBU+0.5*ATR | 97.6% | +0.305% | -1.702% | +2.007% | 0.0031 | 0.0002 | +0.349 | **SIGNIFICANT** |
| 50ETF | Close > SMA50 | 51.4% | +0.203% | +0.311% | -0.108% | 0.6247 | 0.8826 | -0.019 | NOT SIGNIFICANT |
| 50ETF | ROC10 < 3% | 80.9% | +0.343% | -0.114% | +0.457% | 0.1519 | 0.0348 | +0.079 | NOT SIGNIFICANT |
| 50ETF | ROC10 < 7% | 96.0% | +0.244% | +0.532% | -0.287% | 0.7261 | 0.4449 | -0.050 | NOT SIGNIFICANT |
| 50ETF | ROC20 < 3% | 72.5% | +0.296% | +0.151% | +0.144% | 0.5711 | 0.1851 | +0.025 | NOT SIGNIFICANT |
| 50ETF | ROC20 < 4% | 78.8% | +0.221% | +0.386% | -0.166% | 0.5678 | 0.6900 | -0.029 | NOT SIGNIFICANT |
| 50ETF | MACD Hist < 0 | 48.3% | +0.244% | +0.267% | -0.023% | 0.9167 | 0.7545 | -0.004 | NOT SIGNIFICANT |
| 50ETF | Vol20 < Med | 49.1% | +0.567% | -0.044% | +0.611% | 0.0051 | 0.0404 | +0.106 | **SIGNIFICANT** |
| 50ETF | RSI < 55 | 64.2% | +0.203% | +0.351% | -0.149% | 0.5137 | 0.7559 | -0.026 | NOT SIGNIFICANT |
| 50ETF | RSI < 60 | 77.1% | +0.242% | +0.304% | -0.062% | 0.8180 | 0.2533 | -0.011 | NOT SIGNIFICANT |
| 50ETF | Vol20 > Med | 41.1% | +0.255% | +0.257% | -0.002% | 0.9927 | 0.9900 | -0.000 | NOT SIGNIFICANT |
| 50ETF | Close < SMA50 | 46.8% | +0.104% | +0.390% | -0.287% | 0.1927 | 0.4906 | -0.050 | NOT SIGNIFICANT |
| 500ETF | RSI < 66 | 87.1% | -0.012% | +21.777% | -21.789% | 0.0000 | 0.0000 | -0.808 | **SIGNIFICANT** |
| 500ETF | RSI < 72 | 92.8% | +0.083% | +37.524% | -37.440% | 0.0000 | 0.0000 | -1.428 | **SIGNIFICANT** |
| 500ETF | RSI > 25 | 98.3% | +2.757% | +4.621% | -1.864% | 0.1551 | 0.0003 | -0.067 | NOT SIGNIFICANT |
| 500ETF | RSI > 30 | 94.9% | +2.817% | +2.253% | +0.564% | 0.4866 | 0.0085 | +0.020 | NOT SIGNIFICANT |
| 500ETF | RSI > 35 | 90.3% | +2.942% | +1.370% | +1.572% | 0.0335 | 0.1336 | +0.056 | *MARGINAL* |
| 500ETF | Close < BBU | 94.5% | +2.364% | +10.104% | -7.740% | 0.0361 | 0.0000 | -0.277 | **SIGNIFICANT** |
| 500ETF | Close < BBU+0.5*ATR | 98.2% | +2.605% | +12.729% | -10.124% | 0.1146 | 0.0000 | -0.363 | NOT SIGNIFICANT |
| 500ETF | Close > SMA50 | 50.2% | +3.456% | +2.115% | +1.341% | 0.2071 | 0.0000 | +0.048 | NOT SIGNIFICANT |
| 500ETF | ROC10 < 3% | 75.1% | +0.087% | +10.950% | -10.863% | 0.0000 | 0.0000 | -0.394 | **SIGNIFICANT** |
| 500ETF | ROC10 < 7% | 92.5% | +0.442% | +31.663% | -31.221% | 0.0000 | 0.0000 | -1.169 | **SIGNIFICANT** |
| 500ETF | ROC20 < 3% | 67.5% | +0.083% | +8.419% | -8.336% | 0.0000 | 0.0000 | -0.301 | **SIGNIFICANT** |
| 500ETF | ROC20 < 4% | 73.3% | +0.084% | +10.205% | -10.121% | 0.0000 | 0.0000 | -0.367 | **SIGNIFICANT** |
| 500ETF | MACD Hist < 0 | 47.1% | -0.488% | +5.706% | -6.194% | 0.0000 | 0.0000 | -0.223 | **SIGNIFICANT** |
| 500ETF | Vol20 < Med | 47.6% | +0.909% | +4.496% | -3.587% | 0.0004 | 0.2968 | -0.129 | **SIGNIFICANT** |
| 500ETF | RSI < 55 | 60.5% | +0.204% | +6.747% | -6.543% | 0.0000 | 0.0028 | -0.236 | **SIGNIFICANT** |
| 500ETF | RSI < 60 | 74.4% | -0.065% | +11.066% | -11.131% | 0.0000 | 0.0000 | -0.404 | **SIGNIFICANT** |
| 500ETF | Vol20 > Med | 42.6% | -0.090% | +4.924% | -5.014% | 0.0000 | 0.0004 | -0.180 | **SIGNIFICANT** |
| 500ETF | Close < SMA50 | 48.0% | +0.793% | +4.633% | -3.840% | 0.0002 | 0.0983 | -0.138 | **SIGNIFICANT** |

## Put Strategy Combined Filter Analysis

> Per-ETF combined conditions as implemented in `PutStrategy.evaluate_filter()` (`backtest_strategies.py`).
> Optimized via `optimize_put_filters.py` (real data, 6-component composite score).
> For put timing, **negative** Cohen's d is desired — pass days should have *lower* forward returns (i.e. the market drops after the signal, validating hedge timing).

| ETF | Combined Filter | Condition |
| :--- | :--- | :--- |
| 300ETF | `RSI<60 & Vol20>Med` | `RSI(14) < 60` AND `Vol20 > Vol20_252d_median` |
| 50ETF  | `RSI<55 & Close<SMA50` | `RSI(14) < 55` AND `Close < SMA(50)` |
| 500ETF | `RSI<55 & Vol20>Med` | `RSI(14) < 55` AND `Vol20 > Vol20_252d_median` |

### Put Combined Filter — 7-Calendar-Day Forward Return

| ETF | Filter | Placement % | Pass Avg | Fail Avg | Diff | p(t-test) | p(M-W) | Cohen's d | Verdict |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| 300ETF | RSI<60 & Vol20>Med | 31.3% | +0.153% | +0.150% | +0.004% | 0.9778 | 0.2303 | +0.001 | NOT SIGNIFICANT |
| 50ETF | RSI<55 & Close<SMA50 | 45.7% | +0.032% | +0.069% | -0.037% | 0.7423 | 0.1585 | -0.013 | NOT SIGNIFICANT |
| 500ETF | RSI<55 & Vol20>Med | 30.8% | -0.033% | +0.847% | -0.880% | 0.0084 | 0.0942 | -0.076 | *MARGINAL* |

### Put Combined Filter — 14-Calendar-Day Forward Return

| ETF | Filter | Placement % | Pass Avg | Fail Avg | Diff | p(t-test) | p(M-W) | Cohen's d | Verdict |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| 300ETF | RSI<60 & Vol20>Med | 31.1% | +0.220% | +0.281% | -0.061% | 0.7426 | 0.0391 | -0.015 | NOT SIGNIFICANT |
| 50ETF | RSI<55 & Close<SMA50 | 45.6% | -0.005% | +0.179% | -0.184% | 0.2306 | 0.8184 | -0.046 | NOT SIGNIFICANT |
| 500ETF | RSI<55 & Vol20>Med | 30.7% | -0.044% | +1.632% | -1.675% | 0.0004 | 0.0099 | -0.101 | **SIGNIFICANT** |

### Put Combined Filter — 30-Calendar-Day Forward Return

| ETF | Filter | Placement % | Pass Avg | Fail Avg | Diff | p(t-test) | p(M-W) | Cohen's d | Verdict |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| 300ETF | RSI<60 & Vol20>Med | 31.2% | +0.256% | +0.813% | -0.557% | 0.0370 | 0.8600 | -0.100 | *MARGINAL* |
| 50ETF | RSI<55 & Close<SMA50 | 45.8% | +0.058% | +0.423% | -0.365% | 0.0977 | 0.2378 | -0.063 | *MARGINAL* |
| 500ETF | RSI<55 & Vol20>Med | 30.7% | +0.114% | +3.973% | -3.859% | 0.0000 | 0.0631 | -0.138 | **SIGNIFICANT** |

### Put Combined Filter Interpretation

For the protective put strategy, we buy puts when the filter passes and skip when it fails. A **negative** `Pass Avg - Fail Avg` (Diff) means the market tends to drop more on filter-pass days, which makes the put hedge more valuable — this validates the timing signal. Conversely, a positive Diff suggests the filter triggers before rallies, making the put a drag.

**Placement rate** is important: too low (<20%) means the hedge rarely activates, too high (>80%) means the filter provides little selectivity. The optimized filters target 30–50% placement.
