import argparse
import sys
import warnings
from pathlib import Path
import numpy as np
import pandas as pd
from arch import arch_model
from sklearn.preprocessing import StandardScaler
from hmmlearn.hmm import GaussianHMM
from scipy.stats import mode

warnings.filterwarnings("ignore")

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT))

DATA_DIR = HERE / "data"
ROOT_DATA_DIR = ROOT / "data"

ETF_5M_FILE = {
    "50ETF": "50ETF_5m.parquet",
    "300ETF": "510300_5m.parquet",
    "500ETF": "500ETF_5m.parquet",
    "588000ETF": "588000ETF_5m.parquet",
    "159915ETF": "159915ETF_5m.parquet",
}

def get_hour_block(t):
    """Map datetime.time to 1h trading blocks for A-shares."""
    # Morning: 9:30 - 11:30, Afternoon: 13:00 - 15:00
    if t >= pd.Timestamp("09:30:00").time() and t <= pd.Timestamp("10:30:00").time():
        return 0
    elif t > pd.Timestamp("10:30:00").time() and t <= pd.Timestamp("11:30:00").time():
        return 1
    elif t >= pd.Timestamp("13:00:00").time() and t <= pd.Timestamp("14:00:00").time():
        return 2
    elif t > pd.Timestamp("14:00:00").time() and t <= pd.Timestamp("15:00:00").time():
        return 3
    return -1

def generate_garch_regimes(etf="300ETF", force=False):
    """Generate and cache look-ahead free multi-scale GARCH volatility states."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    cache_path = DATA_DIR / f"garch_regimes_{etf}.parquet"
    
    if cache_path.exists() and not force:
        print(f"[INFO] GARCH regimes cache already exists at {cache_path.name}. Skipping generation.")
        return pd.read_parquet(cache_path)
        
    print(f"[INFO] Generating multi-scale GARCH regimes for {etf}...")
    
    # 1. Load index 5m data (we use index as the market indicator proxy)
    # Mapping ETF to its corresponding index 5m file
    index_5m_map = {
        "300ETF": "000300_5m.parquet",
        "50ETF": "000016_5m.parquet",
        "500ETF": "000905_5m.parquet",
        "588000ETF": "000688_5m.parquet",
        "159915ETF": "399006_5m.parquet",
    }
    
    idx_file = index_5m_map.get(etf, "000300_5m.parquet")
    path_5m = ROOT_DATA_DIR / idx_file
    
    if not path_5m.exists():
        raise FileNotFoundError(f"Index 5m parquet file not found at: {path_5m}")
        
    df = pd.read_parquet(path_5m)
    df["datetime"] = pd.to_datetime(df["datetime"])
    df = df.sort_values("datetime").reset_index(drop=True)
    
    df["date"] = df["datetime"].dt.date
    df["time"] = df["datetime"].dt.time
    
    df["hour_block"] = df["time"].apply(get_hour_block)
    df = df[df["hour_block"] != -1]
    df["session_block"] = df["hour_block"].apply(lambda h: 0 if h in [0, 1] else 1)
    
    # 2. Aggregations
    # Daily close
    df_daily = df.groupby("date").agg(
        close=("close", "last")
    ).reset_index()
    
    # 2h close
    df_2h = df.groupby(["date", "session_block"]).agg(
        close=("close", "last")
    ).reset_index()
    
    # 1h close
    df_1h = df.groupby(["date", "hour_block"]).agg(
        close=("close", "last")
    ).reset_index()
    
    # Log returns
    df_daily["log_ret"] = np.log(df_daily["close"] / df_daily["close"].shift(1))
    df_2h["log_ret"] = np.log(df_2h["close"] / df_2h["close"].shift(1))
    df_1h["log_ret"] = np.log(df_1h["close"] / df_1h["close"].shift(1))
    
    df_daily = df_daily.dropna().reset_index(drop=True)
    df_2h = df_2h.dropna().reset_index(drop=True)
    df_1h = df_1h.dropna().reset_index(drop=True)
    
    # 3. Fit GARCH(1,1) models to extract conditional volatilities
    print("  Fitting GARCH(1,1) daily model...")
    model_daily = arch_model(df_daily["log_ret"] * 100.0, vol="Garch", p=1, q=1, dist="Normal")
    res_daily = model_daily.fit(disp="off")
    df_daily["vol_daily"] = (res_daily.conditional_volatility / 100.0) * np.sqrt(252)
    
    print("  Fitting GARCH(1,1) 2h model...")
    model_2h = arch_model(df_2h["log_ret"] * 100.0, vol="Garch", p=1, q=1, dist="Normal")
    res_2h = model_2h.fit(disp="off")
    df_2h["vol_2h_raw"] = (res_2h.conditional_volatility / 100.0) * np.sqrt(252 * 2)
    df_2h_daily = df_2h.groupby("date").agg(vol_2h=("vol_2h_raw", "last")).reset_index()
    
    print("  Fitting GARCH(1,1) 1h model...")
    model_1h = arch_model(df_1h["log_ret"] * 100.0, vol="Garch", p=1, q=1, dist="Normal")
    res_1h = model_1h.fit(disp="off")
    df_1h["vol_1h_raw"] = (res_1h.conditional_volatility / 100.0) * np.sqrt(252 * 4)
    df_1h_daily = df_1h.groupby("date").agg(vol_1h=("vol_1h_raw", "last")).reset_index()
    
    # 4. Merge
    df_vol = df_daily[["date", "vol_daily"]].merge(df_2h_daily, on="date")
    df_vol = df_vol.merge(df_1h_daily, on="date")
    df_vol = df_vol.dropna().sort_values("date").reset_index(drop=True)
    
    # 5. Fit 3-state HMM on volatilities
    print("  Fitting 3-state GMM-HMM with 10 EM restarts...")
    X = df_vol[["vol_daily", "vol_2h", "vol_1h"]].values
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    best_score = -np.inf
    best_model = None
    for seed in range(10):
        model = GaussianHMM(n_components=3, covariance_type="diag", random_state=seed, n_iter=100)
        try:
            model.fit(X_scaled)
            score = model.score(X_scaled)
            if score > best_score:
                best_score = score
                best_model = model
        except Exception:
            pass
            
    if best_model is None:
        raise RuntimeError("HMM model fitting failed to converge across all seeds.")
        
    states = best_model.predict(X_scaled)
    df_vol["state_raw"] = states
    
    # 6. Sort states dynamically by the mean daily volatility
    # This guarantees that State 0 = Calm, State 1 = Turbulent, State 2 = Crisis
    state_means = df_vol.groupby("state_raw")["vol_daily"].mean().sort_values()
    state_mapping = {old_label: new_label for new_label, old_label in enumerate(state_means.index)}
    df_vol["state"] = df_vol["state_raw"].map(state_mapping)
    
    # 7. Create look-ahead free signal (yesterday's state applies to today)
    df_vol["state_signal"] = df_vol["state"].shift(1)
    df_vol = df_vol.dropna().reset_index(drop=True)
    
    # Cast variables to appropriate types
    df_vol["state"] = df_vol["state"].astype(int)
    df_vol["state_signal"] = df_vol["state_signal"].astype(int)
    df_vol["date"] = pd.to_datetime(df_vol["date"])
    
    # Save cache
    df_vol.to_parquet(cache_path, index=False)
    print(f"[SUCCESS] Saved GARCH regimes to {cache_path}")
    
    # Print diagnostics
    print("\n==========================================")
    print(f"Diagnostics for {etf} GARCH regimes:")
    print("==========================================")
    print("State Distribution:")
    print(df_vol["state"].value_counts(normalize=True))
    print("\nState Volatility Means (Annualized):")
    print(df_vol.groupby("state")[["vol_daily", "vol_2h", "vol_1h"]].mean())
    print("\nHMM Transition Matrix:")
    print(best_model.transmat_)
    print("==========================================\n")
    
    return df_vol

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Multi-scale GARCH Volatility Regime Generator")
    parser.add_argument("-e", "--etf", type=str, default="300ETF", choices=list(ETF_5M_FILE.keys()) + ["all"],
                        help="ETF key (default: 300ETF)")
    parser.add_argument("-f", "--force", action="store_true", help="Force recomputation of regimes cache")
    args = parser.parse_args()
    
    if args.etf == "all":
        for e in ETF_5M_FILE.keys():
            try:
                generate_garch_regimes(e, force=args.force)
            except Exception as ex:
                print(f"[ERROR] Failed for {e}: {ex}")
    else:
        generate_garch_regimes(args.etf, force=args.force)
