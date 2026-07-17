# Day-Model Rewrite v3 — Commands

Simplified feature selection & IC-weighted return combination pipeline.

## Commands

```bash
# 1. Run Stage A feature selection (saves selected_pool & mining_attempts JSONs to data/)
python3 day-model-new/select_features.py -e 300ETF -s single
python3 day-model-new/select_features.py -e 300ETF -s long

# 2. Run Stage B evaluation (saves results JSONs to data/)
python3 day-model-new/evaluate_concept.py -e 300ETF -s single
python3 day-model-new/evaluate_concept.py -e 300ETF -s long

# 3. Run full baseline loop across all 5 ETFs and 3 sides (saves BASELINE_REPORT.md)
python3 day-model-new/run_baseline.py
```

## Structure
- `data/`: JSON artifacts (selected pools, attempts logs, evaluation results).
- `select_features.py`: Overall IC sign-flipping + rolling tail IC filter + correlation gate + deflation.
- `evaluate_concept.py`: Z-score standardization + IC-weighted combination + VIF safety pass + bootstrap CI.
- `run_baseline.py`: Automates execution across all asset/side combinations.
