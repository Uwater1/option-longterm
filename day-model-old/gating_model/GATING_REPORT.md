# Gating Model Report

Per-side big-move gating classifiers (long = big-up tail, short = big-down tail) used as a veto filter over the daytrade linear score. Three target variants (`two_sided`, `joint3`, `gated`) × three feature selectors (`none`/all-130, `stability`, `lgbm`) are benchmarked; the best per ETF × side is auto-selected by honest walk-forward OOS PR-AUC.

Metrics: **WF** = pooled purged walk-forward over the full dataset (deployed-model proxy, `forward_wf_estimate`); **HO** = dev-trained model evaluated on the 20% chronological holdout (`dev_only_oos`).

## 1. Winner per ETF × side (auto-selected)

| ETF | Side | Variant | Selector | Model | #Feat | FireThr | WF PR-AUC | WF AUC | WF Prec@70 | HO PR-AUC | Deployable |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **50ETF** | `long` | `joint3` | `none` | logistic | 130 | 0.153 | 0.180 | 0.631 | 14.71% | 0.154 | Yes |
| **50ETF** | `short` | `joint3` | `stability` | logistic | 18 | 0.161 | 0.234 | 0.627 | 21.18% | 0.242 | Yes |
| **300ETF** | `long` | `gated` | `lgbm` | lightgbm | 25 | 0.135 | 0.195 | 0.706 | 16.76% | 0.216 | Yes |
| **300ETF** | `short` | `joint3` | `stability` | logistic | 19 | 0.159 | 0.229 | 0.595 | 20.15% | 0.244 | Yes |
| **500ETF** | `long` | `two_sided` | `none` | lightgbm | 130 | 0.175 | 0.222 | 0.678 | 19.85% | 0.201 | Yes |
| **500ETF** | `short` | `joint3` | `none` | lightgbm | 130 | 0.171 | 0.260 | 0.680 | 20.00% | 0.331 | Yes |
| **588000ETF** | `long` | `gated` | `stability` | logistic | 19 | 0.112 | 0.245 | 0.682 | 22.60% | 0.256 | Yes |
| **588000ETF** | `short` | `joint3` | `stability` | logistic | 19 | 0.166 | 0.239 | 0.602 | 20.43% | 0.353 | Yes |
| **159915ETF** | `long` | `gated` | `stability` | logistic | 14 | 0.112 | 0.205 | 0.699 | 16.32% | 0.234 | Yes |
| **159915ETF** | `short` | `joint3` | `stability` | logistic | 14 | 0.171 | 0.230 | 0.652 | 21.18% | 0.283 | Yes |

## 2. Full grid — forward walk-forward PR-AUC

Each cell shows the WF PR-AUC for every (variant, selector) combination. `**` marks the chosen winner; `()`: not deployable.


### Side: `long`

| ETF | two_sided/none | two_sided/stability | two_sided/lgbm | joint3/none | joint3/stability | joint3/lgbm | gated/none | gated/stability | gated/lgbm |
|---|---|---|---|---|---|---|---|---|---|
| **50ETF** | 0.176 | 0.158 | 0.158 | **0.180** | 0.166 | 0.175 | 0.164 | 0.148 | 0.156 |
| **300ETF** | 0.174 | 0.167 | 0.180 | 0.177 | 0.177 | 0.185 | 0.183 | 0.157 | **0.195** |
| **500ETF** | **0.222** | 0.196 | 0.192 | 0.204 | 0.204 | 0.215 | 0.189 | 0.199 | 0.179 |
| **588000ETF** | 0.181 | 0.245 | 0.234 | 0.185 | 0.242 | 0.229 | 0.192 | **0.245** | 0.227 |
| **159915ETF** | 0.196 | 0.203 | 0.196 | 0.195 | 0.203 | 0.197 | 0.181 | **0.205** | 0.182 |

### Side: `short`

| ETF | two_sided/none | two_sided/stability | two_sided/lgbm | joint3/none | joint3/stability | joint3/lgbm | gated/none | gated/stability | gated/lgbm |
|---|---|---|---|---|---|---|---|---|---|
| **50ETF** | 0.216 | 0.228 | 0.212 | 0.220 | **0.234** | 0.224 | 0.197 | 0.199 | 0.203 |
| **300ETF** | 0.217 | 0.226 | 0.211 | 0.197 | **0.229** | 0.206 | 0.187 | 0.208 | 0.210 |
| **500ETF** | 0.251 | 0.218 | 0.201 | **0.260** | 0.224 | 0.215 | 0.188 | 0.171 | 0.180 |
| **588000ETF** | 0.215 | 0.224 | 0.235 | 0.216 | **0.239** | 0.237 | 0.218 | 0.230 | 0.219 |
| **159915ETF** | 0.193 | 0.229 | 0.218 | 0.203 | **0.230** | 0.213 | 0.165 | 0.166 | 0.168 |

## 3. Selection summary & deployability

- **Variant**: `two_sided` = per-side binary big-move; `joint3` = shared 3-class softmax {big_up, neutral, big_down}; `gated` = big-move AND tradability/regime mask.
- **Selector**: `none` = all 238 features; `stability` = regime-stratified block bootstrap + randomized ElasticNet + OOB IC; `lgbm` = walk-forward LightGBM gain + permutation importance.
- **Deployable**: WF AUC > 0.53 AND WF PR-AUC > base rate AND WF Prec@70 > 1.1× base rate.


**Deployable cells: 10/10.**


## 4. Diagnostic plots

ROC + Precision-Recall curves per (ETF × side × variant × selector) are written to `gating_model/plots/curves_{ETF}_{side}_{variant}_{selector}.png`.
