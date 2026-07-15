import argparse
import sys
import warnings
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from hmmlearn.hmm import GaussianHMM

warnings.filterwarnings("ignore")

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT))

DATA_DIR = HERE / "data"

def generate_hmm_regimes(etf="300ETF", force=False):
    """Generate and cache look-ahead free 3D HMM regime states."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    cache_path = DATA_DIR / f"hmm_regimes_{etf}.parquet"
    
    if cache_path.exists() and not force:
        return pd.read_parquet(cache_path)
        
    print(f"[INFO] Generating 3D HMM regimes for {etf}...")
    
    feat_path = DATA_DIR / f"features_{etf}.parquet"
    if not feat_path.exists():
        raise FileNotFoundError(f"Feature parquet file not found at: {feat_path}")
        
    df_feat = pd.read_parquet(feat_path)
    if "date" not in df_feat.columns:
        df_feat = df_feat.reset_index()
    df_feat["date"] = pd.to_datetime(df_feat["date"])
    df_feat = df_feat.sort_values("date").reset_index(drop=True)
    
    req_cols = ["yesterday_return", "vol20", "yesterday_illiquidity_amihud"]
    missing = [c for c in req_cols if c not in df_feat.columns]
    if missing:
        raise ValueError(f"Missing columns for HMM fitting on {etf}: {missing}")
        
    df_clean = df_feat.dropna(subset=req_cols).copy()
    X = df_clean[req_cols].values
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    M, D = X_scaled.shape
    
    # 1. AIC/BIC Tuning for K in {3, 4}
    best_bic = np.inf
    opt_k = 3
    bic_scores = {}
    
    for k in range(3, 5):
        best_ll = -np.inf
        best_m = None
        for seed in range(10):
            model = GaussianHMM(n_components=k, covariance_type="diag", random_state=seed, n_iter=100)
            try:
                model.fit(X_scaled)
                ll = model.score(X_scaled)
                if ll > best_ll:
                    best_ll = ll
                    best_m = model
            except Exception:
                pass
        
        if best_m is None:
            continue
            
        p = k * (k - 1) + (k - 1) + 2 * k * D
        bic = -2 * best_ll + p * np.log(M)
        bic_scores[k] = bic
        
        if bic < best_bic:
            best_bic = bic
            opt_k = k
            
    print(f"  Optimal K selected for {etf}: {opt_k} (BIC={best_bic:+.1f})")
    
    # Refit optimal K model
    best_ll = -np.inf
    opt_model = None
    for seed in range(10):
        model = GaussianHMM(n_components=opt_k, covariance_type="diag", random_state=seed, n_iter=100)
        try:
            model.fit(X_scaled)
            ll = model.score(X_scaled)
            if ll > best_ll:
                best_ll = ll
                opt_model = model
        except Exception:
            pass
            
    df_clean["state_raw"] = opt_model.predict(X_scaled)
    
    # 2. Sort states dynamically by volatility mean (vol20)
    state_vol_means = df_clean.groupby("state_raw")["vol20"].mean().sort_values()
    state_mapping = {old_label: new_label for new_label, old_label in enumerate(state_vol_means.index)}
    df_clean["state"] = df_clean["state_raw"].map(state_mapping)
    
    # 3. Create look-ahead free signal (yesterday's state applies to today)
    df_clean["state_signal"] = df_clean["state"].shift(1)
    df_clean = df_clean.dropna(subset=["state_signal"]).copy()
    
    df_clean["state"] = df_clean["state"].astype(int)
    df_clean["state_signal"] = df_clean["state_signal"].astype(int)
    
    # Build output df
    df_out = df_clean[["date", "state", "state_signal", "yesterday_return", "vol20", "yesterday_illiquidity_amihud"]].copy()
    
    # Save cache
    df_out.to_parquet(cache_path, index=False)
    print(f"[SUCCESS] Saved HMM regimes to {cache_path}")
    
    return df_out

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="3D HMM Regime Generator")
    parser.add_argument("-e", "--etf", type=str, default="300ETF", choices=["50ETF", "300ETF", "500ETF", "588000ETF", "159915ETF", "all"])
    parser.add_argument("-f", "--force", action="store_true", help="Force recalculation")
    args = parser.parse_args()
    
    if args.etf == "all":
        for e in ["50ETF", "300ETF", "500ETF", "588000ETF", "159915ETF"]:
            try:
                generate_hmm_regimes(e, force=args.force)
            except Exception as ex:
                print(f"[ERROR] Failed for {e}: {ex}")
    else:
        generate_hmm_regimes(args.etf, force=args.force)
