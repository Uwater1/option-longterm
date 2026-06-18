"""
Task 5: Early prediction of day type from first 30 minutes
- Features available at 10:00 AM (first 6 bars)
- Models: LightGBM, XGBoost, Neural Net
- Baselines: majority class, previous-day, gap-only
- Profitability proxy: expected afternoon return per predicted cluster
"""
import pandas as pd
import numpy as np
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import accuracy_score, f1_score, classification_report, confusion_matrix
from sklearn.preprocessing import StandardScaler
import lightgbm as lgb
import xgboost as xgb

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset

import matplotlib.pyplot as plt
import seaborn as sns

ETF_NAMES = ['300ETF', '50ETF', '500ETF', '588000ETF', '159915ETF']

OUTPUT_DIR = Path(__file__).resolve().parent
DATA_DIR = OUTPUT_DIR / 'data'
PLOTS_DIR = OUTPUT_DIR / 'plots'
MODELS_DIR = OUTPUT_DIR / 'models'

BAR_LUNCH = 24  # index of first PM bar (13:00)

DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')


# ============================================================
# Early Features Extraction
# ============================================================
def extract_early_features(etf_name):
    """Extract features available at 10:00 AM (first 6 bars).

    Returns (X, y_macro, y_sub, pm_returns):
      - y_macro : int array (K=3 macro labels)
      - y_sub   : str array (composite 'macro.sub' labels), or None
    """
    
    # Load paths
    paths_npz = np.load(DATA_DIR / f'paths_{etf_name}.npz', allow_pickle=True)
    price_curves = paths_npz['price']
    volume_curves = paths_npz['volume']
    return_curves = paths_npz['returns']
    dates = pd.to_datetime(paths_npz['dates'])
    
    # Load features
    features_df = pd.read_csv(DATA_DIR / f'features_{etf_name}.csv',
                              index_col='date', parse_dates=True)
    
    # Load macro labels (K=3)
    cluster_file = DATA_DIR / f'clusters_{etf_name}_kmeans_pca.csv'
    if not cluster_file.exists():
        return None, None, None, None
    
    cluster_df = pd.read_csv(cluster_file, parse_dates=['date'])
    cluster_df = cluster_df.set_index('date')['cluster']

    # Load sub-cluster labels (optional, hierarchical)
    sub_file = DATA_DIR / f'clusters_{etf_name}_sub.csv'
    sub_df = None
    if sub_file.exists():
        sub_df = pd.read_csv(sub_file, parse_dates=['date'])
        sub_df = sub_df.set_index('date')['cluster'].astype(str)
    
    # Align: find dates present in all sources
    date_set_paths = set(dates)
    date_set_feat = set(features_df.index)
    date_set_clust = set(cluster_df.index)
    common = sorted(date_set_paths & date_set_feat & date_set_clust)
    
    if len(common) == 0:
        return None, None, None, None
    
    # Build aligned arrays using index lookups
    path_idx_map = {d: i for i, d in enumerate(dates)}
    
    early_features = []
    y_list = []
    y_sub_list = []
    pm_returns_list = []
    
    for d in common:
        pi = path_idx_map.get(d)
        if pi is None:
            continue
        
        # Cluster label
        cluster_label = cluster_df.loc[d]
        if pd.isna(cluster_label):
            continue
        
        # Feature row
        feat_row = features_df.loc[d]
        
        # First 6 bars
        early_price = price_curves[pi, :6]
        early_volume = volume_curves[pi, :6]
        early_returns = return_curves[pi, :6]
        
        gap_pct = feat_row['gap_pct']
        first_30min_return = early_price[-1]
        first_30min_vol = early_volume.mean()
        volume_spike_open = early_volume[0]
        early_realized_vol = np.nanstd(early_returns) * np.sqrt(48)
        prev_day_vol = feat_row['prev_day_vol']
        am_return = feat_row['am_return']
        pm_return = feat_row['pm_return']
        
        feat_dict = {
            'gap_pct': gap_pct,
            'first_30min_return': first_30min_return,
            'first_30min_vol': first_30min_vol,
            'volume_spike_open': volume_spike_open,
            'early_realized_vol': early_realized_vol,
            'prev_day_vol': prev_day_vol,
            'am_return': am_return,
        }
        
        for j, val in enumerate(early_returns):
            feat_dict[f'early_bar_{j}'] = val
        
        early_features.append(feat_dict)
        y_list.append(int(cluster_label))
        # Sub-cluster label (empty string if not available)
        if sub_df is not None and d in sub_df.index:
            y_sub_list.append(str(sub_df.loc[d]))
        else:
            y_sub_list.append('')
        pm_returns_list.append(pm_return)
    
    X = pd.DataFrame(early_features)
    y_macro = np.array(y_list)
    y_sub = np.array(y_sub_list, dtype=object)
    pm_returns = np.array(pm_returns_list)
    
    return X, y_macro, y_sub, pm_returns


# ============================================================
# Neural Network Model
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
    """Train neural network with cross-validation"""
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
        
        # Predict
        model.eval()
        with torch.no_grad():
            val_output = model(X_val)
            val_preds = val_output.argmax(dim=1).cpu().numpy()
        
        all_preds[val_idx] = val_preds
        acc = accuracy_score(y[val_idx], val_preds)
        fold_accs.append(acc)
    
    return all_preds, np.mean(fold_accs), np.std(fold_accs)


# ============================================================
# Lunch Break Prediction Analysis
# ============================================================
def lunch_break_prediction(etf_name, best_preds, pm_returns):
    """Lunch-aware profitability analysis.

    Returns dict with:
    - close_before_noon: AM-only return per predicted cluster
    - pm_continuation: PM-only return per predicted cluster (already in pm_returns)
    - pm_independent: PM-only clustering profitability
    - strategy_matrix: AM-pred -> optimal PM action
    """
    # Load price curves for AM return computation
    paths_npz = np.load(DATA_DIR / f'paths_{etf_name}.npz', allow_pickle=True)
    price_curves = paths_npz['price']
    return_curves = paths_npz['returns']
    dates = pd.to_datetime(paths_npz['dates'])

    features_df = pd.read_csv(DATA_DIR / f'features_{etf_name}.csv',
                              index_col='date', parse_dates=True)

    # Align dates
    date_set = set(features_df.index) & set(dates)
    common = sorted(date_set)
    path_idx_map = {d: i for i, d in enumerate(dates)}

    # AM return: sum of log returns bars 0..23 (AM session)
    am_returns_arr = []
    pm_returns_arr = []
    valid_preds = []
    for d in common:
        pi = path_idx_map.get(d)
        if pi is None:
            continue
        am_ret = float(return_curves[pi, :BAR_LUNCH].sum())  # log-return sum
        pm_ret = float(return_curves[pi, BAR_LUNCH:].sum())
        am_returns_arr.append(am_ret)
        pm_returns_arr.append(pm_ret)

    am_returns_arr = np.array(am_returns_arr)
    pm_returns_arr = np.array(pm_returns_arr)

    # Map predictions to aligned indices
    # best_preds is aligned to the predict_etf's filtered set; use pm_returns as proxy length
    n = min(len(best_preds), len(am_returns_arr), len(pm_returns_arr))
    best_preds = best_preds[:n]
    am_returns_arr = am_returns_arr[:n]
    pm_returns_arr = pm_returns_arr[:n]

    # --- Close-before-noon: AM return per predicted cluster ---
    close_before_noon = []
    for cluster_id in sorted(np.unique(best_preds)):
        mask = best_preds == cluster_id
        am_ret = am_returns_arr[mask]
        mean_am = am_ret.mean()
        wr_am = (am_ret > 0).mean()
        sharpe_am = mean_am / (am_ret.std() + 1e-10) * np.sqrt(252)
        close_before_noon.append({
            'cluster': int(cluster_id),
            'n_days': int(mask.sum()),
            'am_return': mean_am,
            'am_win_rate': wr_am,
            'am_sharpe': sharpe_am,
        })

    # --- PM continuation: PM return per predicted cluster ---
    pm_continuation = []
    for cluster_id in sorted(np.unique(best_preds)):
        mask = best_preds == cluster_id
        pm_ret = pm_returns_arr[mask]
        mean_pm = pm_ret.mean()
        wr_pm = (pm_ret > 0).mean()
        sharpe_pm = mean_pm / (pm_ret.std() + 1e-10) * np.sqrt(252)
        pm_continuation.append({
            'cluster': int(cluster_id),
            'n_days': int(mask.sum()),
            'pm_return': mean_pm,
            'pm_win_rate': wr_pm,
            'pm_sharpe': sharpe_pm,
        })

    # --- Strategy matrix: AM-pred -> optimal PM action ---
    # For each cluster: compare (a) hold through PM, (b) close AM + short PM, (c) skip PM
    strategy_matrix = []
    for cluster_id in sorted(np.unique(best_preds)):
        mask = best_preds == cluster_id
        am_ret = am_returns_arr[mask]
        pm_ret = pm_returns_arr[mask]

        # Option A: long full-day (AM + PM)
        full_day = am_ret + pm_ret
        sharpe_full = full_day.mean() / (full_day.std() + 1e-10) * np.sqrt(252)

        # Option B: AM only (close at 11:30)
        sharpe_am = am_ret.mean() / (am_ret.std() + 1e-10) * np.sqrt(252)

        # Option C: AM + short PM (close AM long, enter short at 13:00)
        short_pm = am_ret + (-pm_ret)
        sharpe_short = short_pm.mean() / (short_pm.std() + 1e-10) * np.sqrt(252)

        # Pick best
        options = {'full_day_long': sharpe_full, 'am_only': sharpe_am, 'am_long_pm_short': sharpe_short}
        best_action = max(options, key=options.get)

        strategy_matrix.append({
            'cluster': int(cluster_id),
            'full_day_sharpe': sharpe_full,
            'am_only_sharpe': sharpe_am,
            'am_long_pm_short_sharpe': sharpe_short,
            'best_action': best_action,
            'best_sharpe': options[best_action],
        })

    # --- Plot: strategy comparison ---
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    ax = axes[0]
    cluster_ids = [s['cluster'] for s in strategy_matrix]
    x = np.arange(len(cluster_ids))
    w = 0.25
    ax.bar(x - w, [s['full_day_sharpe'] for s in strategy_matrix], w, label='Full Day Long', color='steelblue')
    ax.bar(x,     [s['am_only_sharpe'] for s in strategy_matrix], w, label='AM Only', color='orange')
    ax.bar(x + w, [s['am_long_pm_short_sharpe'] for s in strategy_matrix], w, label='AM Long + PM Short', color='purple')
    ax.set_xticks(x)
    ax.set_xticklabels([f'C{c}' for c in cluster_ids])
    ax.axhline(0, color='black', linewidth=0.5)
    ax.set_ylabel('Annualized Sharpe')
    ax.set_title(f'{etf_name}: Lunch Strategy Comparison per Predicted Cluster')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3, axis='y')

    ax = axes[1]
    am_means = [c['am_return'] * 100 for c in close_before_noon]
    pm_means = [c['pm_return'] * 100 for c in pm_continuation]
    ax.bar(x - 0.15, am_means, 0.3, label='AM return (%)', color='orange')
    ax.bar(x + 0.15, pm_means, 0.3, label='PM return (%)', color='steelblue')
    ax.axhline(0, color='black', linewidth=0.5)
    ax.set_xticks(x)
    ax.set_xticklabels([f'C{c}' for c in cluster_ids])
    ax.set_ylabel('Return (%)')
    ax.set_title(f'{etf_name}: AM vs PM Return per Predicted Cluster')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    plt.savefig(PLOTS_DIR / f'lunch_strategy_{etf_name}.png', dpi=120)
    plt.close()

    return {
        'close_before_noon': close_before_noon,
        'pm_continuation': pm_continuation,
        'strategy_matrix': strategy_matrix,
    }


# ============================================================
# Main Prediction Pipeline
# ============================================================
def predict_etf(etf_name):
    """Run early prediction for one ETF (two-level: macro + sub)."""
    print(f"\n{'='*60}")
    print(f"Early Prediction: {etf_name}")
    print('='*60)
    
    # Extract features (macro + sub labels)
    X, y, y_sub, pm_returns = extract_early_features(etf_name)
    if X is None:
        print(f"  [SKIP] No data for {etf_name}")
        return None
    
    # Drop rows with NaN
    nan_mask = np.isnan(X.values).any(axis=1) | np.isnan(y) | np.isnan(pm_returns)
    X = X[~nan_mask].values
    y = y[~nan_mask]
    y_sub = y_sub[~nan_mask] if y_sub is not None else None
    pm_returns = pm_returns[~nan_mask]
    
    print(f"  Samples: {len(X)}, Features: {X.shape[1]}, "
          f"Macro classes: {len(np.unique(y))}, "
          f"Sub classes: {len(np.unique(y_sub)) if y_sub is not None else 'n/a'}")
    
    # Standardize
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # ---- BASELINES ----
    print("\n  Baselines:")
    
    # 1) Majority class
    majority_class = pd.Series(y).mode().iloc[0]
    baseline_majority = np.full(len(y), majority_class)
    acc_majority = accuracy_score(y, baseline_majority)
    print(f"    Majority class: {acc_majority:.4f}")
    
    # 2) Previous day cluster (shift by 1)
    baseline_prev = np.roll(y, 1)
    baseline_prev[0] = majority_class
    acc_prev = accuracy_score(y, baseline_prev)
    print(f"    Previous day: {acc_prev:.4f}")
    
    # 3) Gap-only (simple threshold)
    gap_col = 0  # gap_pct is first feature
    baseline_gap = np.where(X[:, gap_col] > 0.003, 1, 
                           np.where(X[:, gap_col] < -0.003, 2, 0))
    acc_gap = accuracy_score(y, baseline_gap)
    print(f"    Gap-only: {acc_gap:.4f}")
    
    # ---- MODELS ----
    print("\n  Models (5-fold CV):")
    
    results = {}
    
    # 1) LightGBM
    print("    [1/3] LightGBM...")
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    lgb_preds = np.zeros(len(y))
    
    for train_idx, val_idx in skf.split(X_scaled, y):
        X_train, X_val = X_scaled[train_idx], X_scaled[val_idx]
        y_train, y_val = y[train_idx], y[val_idx]
        
        model = lgb.LGBMClassifier(
            n_estimators=200, 
            max_depth=6,
            learning_rate=0.05,
            num_leaves=31,
            random_state=42,
            verbose=-1
        )
        model.fit(X_train, y_train)
        lgb_preds[val_idx] = model.predict(X_val)
    
    acc_lgb = accuracy_score(y, lgb_preds)
    f1_lgb = f1_score(y, lgb_preds, average='macro')
    print(f"      Accuracy: {acc_lgb:.4f}, Macro-F1: {f1_lgb:.4f}")
    results['LightGBM'] = {'preds': lgb_preds, 'acc': acc_lgb, 'f1': f1_lgb}
    
    # Save one model
    model.fit(X_scaled, y)
    import joblib
    joblib.dump(model, MODELS_DIR / f'early_lgb_{etf_name}.joblib')
    
    # 2) XGBoost
    print("    [2/3] XGBoost...")
    xgb_preds = np.zeros(len(y))
    
    for train_idx, val_idx in skf.split(X_scaled, y):
        X_train, X_val = X_scaled[train_idx], X_scaled[val_idx]
        y_train, y_val = y[train_idx], y[val_idx]
        
        model = xgb.XGBClassifier(
            n_estimators=200,
            max_depth=6,
            learning_rate=0.05,
            random_state=42,
            verbosity=0
        )
        model.fit(X_train, y_train)
        xgb_preds[val_idx] = model.predict(X_val)
    
    acc_xgb = accuracy_score(y, xgb_preds)
    f1_xgb = f1_score(y, xgb_preds, average='macro')
    print(f"      Accuracy: {acc_xgb:.4f}, Macro-F1: {f1_xgb:.4f}")
    results['XGBoost'] = {'preds': xgb_preds, 'acc': acc_xgb, 'f1': f1_xgb}
    
    # 3) Neural Net
    print("    [3/3] Neural Net...")
    nn_preds, acc_nn, std_nn = train_neural_net(X_scaled, y, n_folds=5, epochs=50)
    f1_nn = f1_score(y, nn_preds, average='macro')
    print(f"      Accuracy: {acc_nn:.4f} ± {std_nn:.4f}, Macro-F1: {f1_nn:.4f}")
    results['NeuralNet'] = {'preds': nn_preds, 'acc': acc_nn, 'f1': f1_nn}
    
    # ---- PROFITABILITY PROXY ----
    print("\n  Profitability Proxy (afternoon return per predicted cluster):")
    best_model = max(results.keys(), key=lambda k: results[k]['acc'])
    best_preds = results[best_model]['preds']

    profit_analysis = []
    for cluster_id in sorted(np.unique(best_preds)):
        mask = best_preds == cluster_id
        cluster_pm_returns = pm_returns[mask]

        mean_ret = cluster_pm_returns.mean()
        std_ret = cluster_pm_returns.std() + 1e-10

        # Long metrics
        long_win_rate = (cluster_pm_returns > 0).mean()
        long_sharpe = mean_ret / std_ret * np.sqrt(252)

        # Short metrics (negate returns)
        short_mean = -mean_ret
        short_win_rate = (cluster_pm_returns < 0).mean()
        short_sharpe = short_mean / std_ret * np.sqrt(252)

        # Optimal direction: pick direction with higher absolute Sharpe
        if abs(long_sharpe) >= abs(short_sharpe):
            opt_dir = 'long'
            opt_return = mean_ret
            opt_win_rate = long_win_rate
            opt_sharpe = long_sharpe
        else:
            opt_dir = 'short'
            opt_return = short_mean
            opt_win_rate = short_win_rate
            opt_sharpe = short_sharpe

        profit_analysis.append({
            'cluster': cluster_id,
            'n_days': mask.sum(),
            'mean_pm_return': mean_ret,
            'win_rate': long_win_rate,
            'sharpe_annual': long_sharpe,
            'optimal_direction': opt_dir,
            'optimal_return': opt_return,
            'optimal_win_rate': opt_win_rate,
            'optimal_sharpe': opt_sharpe,
        })

        print(f"    Cluster {cluster_id}: {mask.sum()} days, "
              f"PM Return: {mean_ret*100:.3f}%, Win Rate: {long_win_rate*100:.1f}%, "
              f"Sharpe: {long_sharpe:.2f} | Optimal: {opt_dir} Sharpe={opt_sharpe:.2f}")
    
    # ---- PLOTS ----
    # Confusion matrix
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    
    for i, (model_name, res) in enumerate(results.items()):
        ax = axes[i]
        cm = confusion_matrix(y, res['preds'])
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=ax)
        ax.set_title(f'{model_name}\nAcc={res["acc"]:.4f}')
        ax.set_xlabel('Predicted')
        ax.set_ylabel('Actual')
    
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / f'early_prediction_cm_{etf_name}.png', dpi=100)
    plt.close()
    
    # Profitability plot
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    
    clusters = [p['cluster'] for p in profit_analysis]
    returns = [p['mean_pm_return'] * 100 for p in profit_analysis]
    win_rates = [p['win_rate'] * 100 for p in profit_analysis]
    sharpes = [p['sharpe_annual'] for p in profit_analysis]
    
    axes[0].bar(clusters, returns, color=['green' if r > 0 else 'red' for r in returns])
    axes[0].set_title('Mean PM Return by Predicted Cluster')
    axes[0].set_ylabel('Return (%)')
    axes[0].axhline(0, color='black', linestyle='--')
    axes[0].grid(True, alpha=0.3)
    
    axes[1].bar(clusters, win_rates, color='steelblue')
    axes[1].set_title('Win Rate by Predicted Cluster')
    axes[1].set_ylabel('Win Rate (%)')
    axes[1].axhline(50, color='red', linestyle='--', alpha=0.5)
    axes[1].grid(True, alpha=0.3)
    
    axes[2].bar(clusters, sharpes, color=['green' if s > 0 else 'red' for s in sharpes])
    axes[2].set_title('Annualized Sharpe by Predicted Cluster')
    axes[2].set_ylabel('Sharpe Ratio')
    axes[2].axhline(0, color='black', linestyle='--')
    axes[2].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / f'early_prediction_profit_{etf_name}.png', dpi=100)
    plt.close()
    
    # ---- LUNCH BREAK ANALYSIS ----
    print("\n  Lunch Break Prediction Analysis...")
    lunch_results = lunch_break_prediction(etf_name, best_preds, pm_returns)
    for s in lunch_results['strategy_matrix']:
        print(f"    Cluster {s['cluster']}: best_action={s['best_action']} (Sharpe={s['best_sharpe']:.2f})")

    # ---- LEVEL-2: SUB-CLUSTER PREDICTION ----
    sub_results = None
    if y_sub is not None and len(np.unique(y_sub)) > 1:
        print("\n  Level-2: Sub-Cluster Prediction (within each macro type):")
        sub_results = {}
        for macro_id in sorted(np.unique(y)):
            macro_mask = y == macro_id
            X_macro = X_scaled[macro_mask]
            y_sub_macro = y_sub[macro_mask]
            pm_sub = pm_returns[macro_mask]

            unique_sub = np.unique(y_sub_macro)
            unique_sub = unique_sub[unique_sub != '']  # drop empty
            if len(unique_sub) < 2:
                print(f"    Macro {macro_id}: < 2 sub-types, skipping")
                continue

            # Filter out empty labels
            valid = y_sub_macro != ''
            X_macro = X_macro[valid]
            y_sub_macro = y_sub_macro[valid]
            pm_sub = pm_sub[valid]

            from sklearn.preprocessing import LabelEncoder
            le = LabelEncoder()
            y_sub_enc = le.fit_transform(y_sub_macro)

            # LightGBM sub-classifier (5-fold CV)
            skf_sub = StratifiedKFold(n_splits=min(5, min(np.bincount(y_sub_enc))),
                                       shuffle=True, random_state=42)
            sub_preds = np.zeros(len(y_sub_enc), dtype=int)
            for train_idx, val_idx in skf_sub.split(X_macro, y_sub_enc):
                sub_model = lgb.LGBMClassifier(
                    n_estimators=150, max_depth=5, learning_rate=0.05,
                    num_leaves=20, random_state=42, verbose=-1
                )
                sub_model.fit(X_macro[train_idx], y_sub_enc[train_idx])
                sub_preds[val_idx] = sub_model.predict(X_macro[val_idx])

            sub_acc = accuracy_score(y_sub_enc, sub_preds)
            sub_f1 = f1_score(y_sub_enc, sub_preds, average='macro')
            print(f"    Macro {macro_id}: {len(y_sub_enc)} days, "
                  f"{len(unique_sub)} sub-types, Acc={sub_acc:.4f}, F1={sub_f1:.4f}")

            # Profitability per sub-cluster
            sub_profit = []
            for sub_id_enc in sorted(np.unique(sub_preds)):
                sub_mask = sub_preds == sub_id_enc
                sub_label = le.inverse_transform([sub_id_enc])[0]
                sub_pm = pm_sub[sub_mask]
                mean_ret = sub_pm.mean()
                sharpe = mean_ret / (sub_pm.std() + 1e-10) * np.sqrt(252)
                sub_profit.append({
                    'sub_cluster': sub_label,
                    'n_days': int(sub_mask.sum()),
                    'pm_return': float(mean_ret),
                    'sharpe': float(sharpe),
                })

            sub_results[str(macro_id)] = {
                'accuracy': sub_acc,
                'f1': sub_f1,
                'n_sub_types': len(unique_sub),
                'profit': sub_profit,
            }

    return {
        'baselines': {'majority': acc_majority, 'prev_day': acc_prev, 'gap_only': acc_gap},
        'models': results,
        'profit': profit_analysis,
        'lunch': lunch_results,
        'sub_results': sub_results,
    }


def main():
    PLOTS_DIR.mkdir(exist_ok=True)
    MODELS_DIR.mkdir(exist_ok=True)
    
    print("Early Prediction: First 30 Minutes")
    print("=" * 60)
    print(f"Device: {DEVICE}")
    
    all_results = {}
    
    for etf_name in ETF_NAMES:
        try:
            results = predict_etf(etf_name)
            if results:
                all_results[etf_name] = results
        except Exception as e:
            print(f"  [ERROR] {etf_name}: {e}")
            import traceback
            traceback.print_exc()
    
    # Summary
    print("\n" + "="*60)
    print("Summary: Best Model Accuracy per ETF")
    print("="*60)
    for etf_name, results in all_results.items():
        best_model = max(results['models'].keys(), 
                        key=lambda k: results['models'][k]['acc'])
        best_acc = results['models'][best_model]['acc']
        baseline = results['baselines']['majority']
        print(f"  {etf_name}: {best_model} = {best_acc:.4f} (baseline: {baseline:.4f})")
    
    # Save detailed results
    with open(DATA_DIR / 'early_prediction_results.txt', 'w') as f:
        f.write("Early Prediction Results (First 30 Minutes)\n")
        f.write("="*60 + "\n\n")
        
        for etf_name, results in all_results.items():
            f.write(f"\n{etf_name}\n")
            f.write("-"*60 + "\n")
            
            f.write("\nBaselines:\n")
            for name, acc in results['baselines'].items():
                f.write(f"  {name}: {acc:.4f}\n")
            
            f.write("\nModels:\n")
            for name, res in results['models'].items():
                f.write(f"  {name}: Acc={res['acc']:.4f}, F1={res['f1']:.4f}\n")
            
            f.write("\nProfitability Proxy:\n")
            for p in results['profit']:
                f.write(f"  Cluster {p['cluster']}: {p['n_days']} days, "
                       f"PM Return={p['mean_pm_return']*100:.3f}%, "
                       f"Win Rate={p['win_rate']*100:.1f}%, "
                       f"Sharpe={p['sharpe_annual']:.2f}, "
                       f"Optimal Dir={p['optimal_direction']}, "
                       f"Opt Return={p['optimal_return']*100:.3f}%, "
                       f"Opt Sharpe={p['optimal_sharpe']:.2f}\n")

            if 'lunch' in results:
                lr = results['lunch']
                f.write("\nLunch Strategy:\n")
                for s in lr.get('strategy_matrix', []):
                    f.write(f"  Cluster {s['cluster']}: full_day={s['full_day_sharpe']:.2f} "
                           f"am_only={s['am_only_sharpe']:.2f} "
                           f"am_long_pm_short={s['am_long_pm_short_sharpe']:.2f} "
                           f"best={s['best_action']}({s['best_sharpe']:.2f})\n")

            if results.get('sub_results'):
                f.write("\nLevel-2 Sub-Cluster Prediction:\n")
                for macro_id, sr in results['sub_results'].items():
                    f.write(f"  Macro {macro_id}: Acc={sr['accuracy']:.4f}, "
                           f"F1={sr['f1']:.4f}, {sr['n_sub_types']} sub-types\n")
                    for p in sr['profit']:
                        f.write(f"    Sub {p['sub_cluster']}: {p['n_days']} days, "
                               f"PM Ret={p['pm_return']*100:.3f}%, Sharpe={p['sharpe']:.2f}\n")
    
    print("\nEarly prediction complete!")


if __name__ == '__main__':
    main()
