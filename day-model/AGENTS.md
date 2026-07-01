# Day-Model Feature Expansion & Return Prediction Workflow

Workflow for day-model feature generation and multi-metric linear return predictor optimization.

## Target Definition

* **Target**: `trade_return = log(close[EXIT_BAR] / open[decision_bar+1])`
* **Entry**: 10:00 (bar 5 closes at 10:00, entry at open of bar 6)
* **Exit**: 14:35 (close of bar 42)
* **Underlying**: Log return from 10:00 to 14:35 across all 5 ETFs.

## Workflow

```bash
# 1. Re-generate parquet feature datasets
python3 day-model/build_features.py -e all

# 2. Run first-principles Stability Selection + Optuna training
python3 day-model/train_model.py -e all --trials 50

# 3. Generate summary REPORT.md and tables
python3 day-model/generate_report.py
```

## Remade Predictor Architecture (First Principles)

`train_model.py` implements the following robust modeling chain:

1. **Lockbox Split (Step 0)**: Hold out days from 2024-03-01 to last day.
2. **BH-FDR Screening (Step 1)**: Robust Spearman rank correlation on 2200 training days. Keep features surviving FDR = 0.40. Fallback to top 80 by p-value if fewer pass.
3. **Stability Selection (Step 2)**: ElasticNet path selection (l1_ratio = 0.5) across $B=100$ subsamples of size $\lfloor N/2 \rfloor$ of Step 1 survivors. Keep features with selection probability $\ge 0.60$ (fallback to top 5 if count < 3). Handles collinearity grouping naturally via ElasticNet grouping effect.
4. **Loss Weighting (Step 3)**: Power weights $w(y_i) = |y_i|^k$ (exponent $k$ tuned by Optuna) to focus model on tail days.
5. **LOYO CV with Embargo (Step 4)**: 9 Yearly blocks (2015-2023) with a 10-day embargo at test block boundaries.
6. **Pilot Normalization (Step 4.1)**: Runs 50 pilot trials, computes median and MAD for each of the 8 metrics to calculate robust z-scores.
7. **Objective Function**: Maximizes weighted sum of normalized metrics ($w_i$):
   - $M_1$ (Tail IC IR): 20%
   - $M_2$ (Tail IC Mean): 20%
   - $M_3$ (Yearly Hit Rate): 15%
   - $M_4$ (Overall Rank IC): 15%
   - $M_5$ (Decile Monotonicity): 10%
   - $M_6$ (Top-Bottom Spread): 5%
   - $M_7$ (Feature Parsimony): 10%
   - $M_8$ (Coefficient Bloat): 5%
8. **Kill Switches**: Trial pruned (returns `-1e9`) if:
   - Overall IC <= 0
   - Hit Rate < 60%
   - Decile Monotonicity <= 0.4
   - Top-Bottom Spread <= 0
9. **One-Shot Evaluation (Step 6)**: Fits final model on all 2200 training rows and evaluates on the 500-day lockbox.
