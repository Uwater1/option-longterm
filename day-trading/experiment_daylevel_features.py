"""
Experiment: Compare early-only vs early+day-level features for day-type prediction.

Tests whether adding 8 day-level technical indicators (RSI14, MACD, SMA20/50 dist,
ATR14, ROC10, BB%B, vol20) improves macro cluster prediction accuracy.

Outputs comparison table to stdout and saves results to data/daylevel_experiment.json.
"""
import json
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import pandas_ta as ta
import lightgbm as lgb
import xgboost as xgb
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import accuracy_score, f1_score
from sklearn.preprocessing import StandardScaler

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset

warnings.filterwarnings('ignore')

ETF_NAMES = ['300ETF', '50ETF', '500ETF', '588000ETF', '159915ETF']
ETF_1D_FILES = {
    '300ETF': '510300_1d.parquet',
    '50ETF': '50ETF_1d.parquet',
    '500ETF': '500ETF_1d.parquet',
    '588000ETF': '588000ETF_1d.parquet',
    '159915ETF': '159915ETF_1d.parquet',
}

OUTPUT_DIR = Path(__file__).resolve().parent
DATA_DIR = OUTPUT_DIR / 'data'
PARENT_DATA_DIR = OUTPUT_DIR.parent / 'data'

DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')


# ============================================================
# Day-level indicators (same logic as day-model/build_features.py)
# ============================================================
def compute_daylevel_indicators(etf_name):
    """Compute 8 day-level indicators from 1d data, shifted by 1 (no look-ahead)."""
    path_1d = PARENT_DATA_DIR / ETF_1D_FILES[etf_name]
    if not path_1d.exists():
        return None

    df = pd.read_parquet(path_1d)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date').reset_index(drop=True)
    px = df['close_adj']

    df['rsi14'] = ta.rsi(px, length=14)

    macd = ta.macd(px, fast=12, slow=26, signal=9)
    df['macd_hist'] = macd['MACDh_12_26_9'] if macd is not None else np.nan

    sma20 = ta.sma(px, length=20)
    sma50 = ta.sma(px, length=50)
    df['sma20_dist'] = (px - sma20) / sma20
    df['sma50_dist'] = (px - sma50) / sma50

    hlcv = pd.DataFrame({
        'high': df['high_adj'], 'low': df['low_adj'], 'close': df['close_adj'],
    })
    atr14 = ta.atr(hlcv['high'], hlcv['low'], hlcv['close'], length=14)
    df['atr14_norm'] = atr14 / px

    df['roc10'] = ta.roc(px, length=10) / 100.0

    bbands = ta.bbands(px, length=20, std=2)
    if bbands is not None:
        upper = bbands.iloc[:, 0]
        lower = bbands.iloc[:, 2]
        df['bb_pctb'] = (px - lower) / (upper - lower)
    else:
        df['bb_pctb'] = np.nan

    log_ret = np.log(px / px.shift(1))
    df['vol20'] = log_ret.rolling(20).std() * np.sqrt(252)

    day_cols = ['rsi14', 'macd_hist', 'sma20_dist', 'sma50_dist',
                'atr14_norm', 'roc10', 'bb_pctb', 'vol20']
    for col in day_cols:
        df[col] = df[col].shift(1)

    result = df[['date'] + day_cols].dropna(subset=day_cols)
    return result.set_index('date')


# ============================================================
# Neural Network (same architecture as predict_early.py)
# ============================================================
class EarlyPredictor(nn.Module):
    def __init__(self, input_dim, n_classes):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, 64),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(32, n_classes)
        )

    def forward(self, x):
        return self.net(x)


def train_neural_net(X, y, n_folds=5, epochs=50, batch_size=64):
    n_classes = len(np.unique(y))
    input_dim = X.shape[1]
    X_tensor = torch.FloatTensor(X).to(DEVICE)
    y_tensor = torch.LongTensor(y).to(DEVICE)
    skf = StratifiedKFold(n_splits=n_folds, shuffle=True, random_state=42)
    all_preds = np.zeros(len(y))
    fold_accs = []

    for fold, (train_idx, val_idx) in enumerate(skf.split(X, y)):
        X_train, X_val = X_tensor[train_idx], X_tensor[val_idx]
        y_train, y_val = y_tensor[train_idx], y_tensor[val_idx]

        model = EarlyPredictor(input_dim, n_classes).to(DEVICE)
        optimizer = torch.optim.Adam(model.parameters(), lr=1e-3, weight_decay=1e-4)
        criterion = nn.CrossEntropyLoss()

        train_dataset = TensorDataset(X_train, y_train)
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)

        model.train()
        for epoch in range(epochs):
            for batch_X, batch_y in train_loader:
                optimizer.zero_grad()
                output = model(batch_X)
                loss = criterion(output, batch_y)
                loss.backward()
                optimizer.step()

        model.eval()
        with torch.no_grad():
            val_output = model(X_val)
            val_preds = val_output.argmax(dim=1).cpu().numpy()

        all_preds[val_idx] = val_preds
        fold_accs.append(accuracy_score(y[val_idx], val_preds))

    return all_preds, np.mean(fold_accs), np.std(fold_accs)


# ============================================================
# Feature loading
# ============================================================
def load_early_features(etf_name):
    """Load existing early features + labels from day-trading/data."""
    paths_npz = np.load(DATA_DIR / f'paths_{etf_name}.npz', allow_pickle=True)
    dates = pd.to_datetime(paths_npz['dates'])

    features_df = pd.read_csv(DATA_DIR / f'features_{etf_name}.csv',
                              index_col='date', parse_dates=True)

    cluster_file = DATA_DIR / f'clusters_{etf_name}_kmeans_pca.csv'
    if not cluster_file.exists():
        return None, None, None

    cluster_df = pd.read_csv(cluster_file, parse_dates=['date'])
    cluster_df = cluster_df.set_index('date')['cluster']

    # Align dates
    common = sorted(set(dates) & set(features_df.index) & set(cluster_df.index))
    if len(common) == 0:
        return None, None, None

    path_idx_map = {d: i for i, d in enumerate(dates)}

    early_features = []
    y_list = []
    valid_dates = []

    for d in common:
        pi = path_idx_map.get(d)
        if pi is None:
            continue
        cluster_label = cluster_df.loc[d]
        if pd.isna(cluster_label):
            continue

        feat_row = features_df.loc[d]
        price_curves = paths_npz['price']
        return_curves = paths_npz['returns']

        early_price = price_curves[pi, :6]
        early_returns = return_curves[pi, :6]

        feat_dict = {
            'gap_pct': feat_row['gap_pct'],
            'first_30min_return': early_price[-1],
            'first_30min_vol': feat_row.get('prev_day_vol', np.nan),
            'volume_spike_open': feat_row.get('volume_spike_open', np.nan),
            'early_realized_vol': np.nanstd(early_returns) * np.sqrt(48),
            'prev_day_vol': feat_row['prev_day_vol'],
            'am_return': feat_row['am_return'],
        }
        for j, val in enumerate(early_returns):
            feat_dict[f'early_bar_{j}'] = val

        early_features.append(feat_dict)
        y_list.append(int(cluster_label))
        valid_dates.append(d)

    X = pd.DataFrame(early_features, index=valid_dates)
    y = np.array(y_list)
    return X, y, valid_dates


# ============================================================
# Run models for one feature set
# ============================================================
def run_models(X_scaled, y, label=""):
    """Run LightGBM, XGBoost, Neural Net. Return dict of acc/f1."""
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    results = {}

    # LightGBM
    lgb_preds = np.zeros(len(y))
    for train_idx, val_idx in skf.split(X_scaled, y):
        model = lgb.LGBMClassifier(
            n_estimators=200, max_depth=6, learning_rate=0.05,
            num_leaves=31, random_state=42, verbose=-1
        )
        model.fit(X_scaled[train_idx], y[train_idx])
        lgb_preds[val_idx] = model.predict(X_scaled[val_idx])
    acc_lgb = accuracy_score(y, lgb_preds)
    f1_lgb = f1_score(y, lgb_preds, average='macro')
    results['LightGBM'] = {'acc': acc_lgb, 'f1': f1_lgb}

    # XGBoost
    xgb_preds = np.zeros(len(y))
    for train_idx, val_idx in skf.split(X_scaled, y):
        model = xgb.XGBClassifier(
            n_estimators=200, max_depth=6, learning_rate=0.05,
            random_state=42, verbosity=0
        )
        model.fit(X_scaled[train_idx], y[train_idx])
        xgb_preds[val_idx] = model.predict(X_scaled[val_idx])
    acc_xgb = accuracy_score(y, xgb_preds)
    f1_xgb = f1_score(y, xgb_preds, average='macro')
    results['XGBoost'] = {'acc': acc_xgb, 'f1': f1_xgb}

    # Neural Net
    nn_preds, acc_nn, std_nn = train_neural_net(X_scaled, y, n_folds=5, epochs=50)
    f1_nn = f1_score(y, nn_preds, average='macro')
    results['NeuralNet'] = {'acc': acc_nn, 'f1': f1_nn}

    return results


# ============================================================
# Main experiment
# ============================================================
def main():
    print("Day-Level Indicator Experiment")
    print("=" * 70)
    print(f"Device: {DEVICE}")
    print("Comparing: Early-only (13 features) vs Early+Day-level (21 features)")
    print("=" * 70)

    all_results = {}

    for etf_name in ETF_NAMES:
        print(f"\n{'='*60}")
        print(f"  {etf_name}")
        print('='*60)

        # Load early features
        X_early, y, valid_dates = load_early_features(etf_name)
        if X_early is None:
            print(f"  [SKIP] No data for {etf_name}")
            continue

        # Load day-level indicators
        daylevel = compute_daylevel_indicators(etf_name)
        if daylevel is None:
            print(f"  [SKIP] No 1d data for {etf_name}")
            continue

        # Align day-level to valid dates
        day_cols = ['rsi14', 'macd_hist', 'sma20_dist', 'sma50_dist',
                    'atr14_norm', 'roc10', 'bb_pctb', 'vol20']

        day_aligned = daylevel.reindex(valid_dates)[day_cols]

        # Drop rows where day-level is NaN
        valid_mask = ~day_aligned.isna().any(axis=1).values & ~X_early.isna().any(axis=1).values
        X_early_clean = X_early[valid_mask].values
        day_clean = day_aligned[valid_mask].values
        y_clean = y[valid_mask]

        # Combined features
        X_combined = np.hstack([X_early_clean, day_clean])

        print(f"  Samples: {len(y_clean)}")
        print(f"  Early-only features: {X_early_clean.shape[1]}")
        print(f"  Combined features: {X_combined.shape[1]} (+{day_clean.shape[1]} day-level)")

        # Standardize
        scaler_early = StandardScaler()
        X_early_scaled = scaler_early.fit_transform(X_early_clean)

        scaler_combined = StandardScaler()
        X_combined_scaled = scaler_combined.fit_transform(X_combined)

        # Run models
        print("\n  Early-only models:")
        res_early = run_models(X_early_scaled, y_clean, "early")
        for name, m in res_early.items():
            print(f"    {name}: Acc={m['acc']:.4f}, F1={m['f1']:.4f}")

        print("\n  Early+Day-level models:")
        res_combined = run_models(X_combined_scaled, y_clean, "combined")
        for name, m in res_combined.items():
            print(f"    {name}: Acc={m['acc']:.4f}, F1={m['f1']:.4f}")

        # Compute deltas
        deltas = {}
        for name in res_early:
            delta_acc = res_combined[name]['acc'] - res_early[name]['acc']
            delta_f1 = res_combined[name]['f1'] - res_early[name]['f1']
            deltas[name] = {'delta_acc': delta_acc, 'delta_f1': delta_f1}
            sign = "+" if delta_acc >= 0 else ""
            print(f"    {name} delta: Acc={sign}{delta_acc:.4f}, F1={sign}{delta_f1:.4f}")

        all_results[etf_name] = {
            'n_samples': int(len(y_clean)),
            'n_early_features': int(X_early_clean.shape[1]),
            'n_combined_features': int(X_combined.shape[1]),
            'early': {k: {kk: round(vv, 4) for kk, vv in v.items()} for k, v in res_early.items()},
            'combined': {k: {kk: round(vv, 4) for kk, vv in v.items()} for k, v in res_combined.items()},
            'deltas': {k: {kk: round(vv, 4) for kk, vv in v.items()} for k, v in deltas.items()},
        }

    # Summary table
    print("\n" + "=" * 70)
    print("SUMMARY: Best Model (Neural Net) Accuracy Comparison")
    print("=" * 70)
    print(f"{'ETF':<12} {'Early-only':>12} {'Early+Day':>12} {'Delta':>10} {'Verdict':>10}")
    print("-" * 56)

    nn_deltas = []
    for etf_name, res in all_results.items():
        early_acc = res['early']['NeuralNet']['acc']
        combined_acc = res['combined']['NeuralNet']['acc']
        delta = combined_acc - early_acc
        nn_deltas.append(delta)
        verdict = "IMPROVED" if delta >= 0.005 else ("MARGINAL" if delta >= 0.001 else "NO CHANGE")
        print(f"{etf_name:<12} {early_acc:>12.4f} {combined_acc:>12.4f} {delta:>+10.4f} {verdict:>10}")

    mean_delta = np.mean(nn_deltas)
    print(f"\nMean delta across ETFs: {mean_delta:+.4f}")
    print(f"Threshold for significance: +0.005 (0.5%)")

    if mean_delta >= 0.005:
        print("\n>>> RESULT: Day-level indicators SIGNIFICANTLY improve prediction.")
        print(">>> RECOMMENDATION: Incorporate day-level features into predict_early.py")
    else:
        print("\n>>> RESULT: Day-level indicators do NOT significantly improve prediction.")
        print(">>> RECOMMENDATION: Keep early-only features, add note to REPORT.md")

    # Save results
    out_file = DATA_DIR / 'daylevel_experiment.json'
    with open(out_file, 'w') as f:
        json.dump(all_results, f, indent=2)
    print(f"\nResults saved to {out_file}")


if __name__ == '__main__':
    main()
