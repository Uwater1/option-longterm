"""
Task 1: Extract dual features from 5m intraday data
- Raw intraday paths (48 bars): normalized price, volume, returns
- Engineered scalar features: gap, return, shape, volume, volatility
"""
import pandas as pd
import numpy as np
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# ETF configuration
ETF_CONFIG = {
    '300ETF': {'file_5m': '510300_5m.parquet', 'file_1d': '510300_1d.parquet'},
    '50ETF': {'file_5m': '50ETF_5m.parquet', 'file_1d': '50ETF_1d.parquet'},
    '500ETF': {'file_5m': '500ETF_5m.parquet', 'file_1d': '500ETF_1d.parquet'},
    '588000ETF': {'file_5m': '588000ETF_5m.parquet', 'file_1d': '588000ETF_1d.parquet'},
    '159915ETF': {'file_5m': '159915ETF_5m.parquet', 'file_1d': '159915ETF_1d.parquet'},
}

DATA_DIR = Path(__file__).resolve().parent.parent / 'data'
OUTPUT_DIR = Path(__file__).resolve().parent
OUT_DATA_DIR = OUTPUT_DIR / 'data'


def load_data(etf_name):
    """Load 5m and 1d data for an ETF"""
    cfg = ETF_CONFIG[etf_name]
    
    path_5m = DATA_DIR / cfg['file_5m']
    path_1d = DATA_DIR / cfg['file_1d']
    
    if not path_5m.exists():
        print(f"  [SKIP] {etf_name}: {path_5m} not found")
        return None, None
    
    df_5m = pd.read_parquet(path_5m)
    df_1d = pd.read_parquet(path_1d)
    
    # Prepare 5m data
    df_5m['datetime'] = pd.to_datetime(df_5m['datetime'])
    df_5m['date'] = df_5m['datetime'].dt.normalize()
    df_5m = df_5m.sort_values(['date', 'datetime'])
    
    # Prepare 1d data
    df_1d['date'] = pd.to_datetime(df_1d['date'])
    df_1d = df_1d.sort_values('date').reset_index(drop=True)
    
    print(f"  {etf_name}: {len(df_5m):,} 5m bars, {len(df_1d):,} days")
    return df_5m, df_1d


def extract_day_paths(df_day, prev_close):
    """Extract raw intraday paths for one day"""
    if len(df_day) < 10:  # Skip days with too few bars
        return None
    
    # Get 48 bars (or pad/truncate)
    n_bars = 48
    bars = df_day.head(n_bars).copy()
    
    if len(bars) < n_bars:
        # Pad with last value
        last_row = bars.iloc[-1]
        n_pad = n_bars - len(bars)
        pad_rows = pd.DataFrame([last_row] * n_pad)
        bars = pd.concat([bars, pad_rows], ignore_index=True)
    
    day_open = bars.iloc[0]['open']
    
    # Normalized price curve: (close - day_open) / prev_close
    norm_price = (bars['close'].values - day_open) / prev_close
    
    # Normalized volume curve: volume / day_avg_volume
    day_avg_vol = bars['volume'].mean()
    norm_volume = bars['volume'].values / (day_avg_vol + 1e-10)
    
    # Intraday returns: log(close / open)
    log_returns = np.log(bars['close'].values / (bars['open'].values + 1e-10))
    
    return {
        'norm_price': norm_price,
        'norm_volume': norm_volume,
        'log_returns': log_returns,
        'bars': bars
    }


def extract_scalar_features(bars, prev_close, prev_day_vol, prev_day_realized_vol):
    """Extract engineered scalar features from one day's bars"""
    
    day_open = bars.iloc[0]['open']
    day_close = bars.iloc[-1]['close']
    day_high = bars['high'].max()
    day_low = bars['low'].min()
    
    # Gap & Return features
    gap_pct = (day_open - prev_close) / prev_close
    intraday_return = (day_close - day_open) / day_open
    day_range = (day_high - day_low) / prev_close
    close_location = (day_close - day_low) / (day_high - day_low + 1e-10)
    
    # AM/PM split (first 24 bars = AM, last 24 = PM)
    am_bars = bars.iloc[:24]
    pm_bars = bars.iloc[24:]
    
    am_close = am_bars.iloc[-1]['close']
    pm_open = pm_bars.iloc[0]['open']
    pm_close = pm_bars.iloc[-1]['close']
    
    am_return = (am_close - day_open) / day_open
    pm_return = (pm_close - pm_open) / pm_open
    
    # Path / Shape features
    cummax = bars['close'].cummax()
    cummin = bars['close'].cummin()
    
    drawdowns = (bars['close'] - cummax) / cummax
    max_drawdown_intra = drawdowns.min()
    
    rallies = (bars['close'] - cummin) / (cummin + 1e-10)
    max_rally_intra = rallies.max()
    
    # Path efficiency: |net move| / sum(|bar moves|)
    bar_moves = bars['close'].diff().abs().sum()
    net_move = abs(day_close - day_open)
    path_efficiency = net_move / (bar_moves + 1e-10)
    
    # First/last 30min (6 bars)
    first_30min_return = (bars.iloc[5]['close'] - day_open) / day_open
    last_30min_return = (day_close - bars.iloc[-7]['close']) / bars.iloc[-7]['close']
    
    # High/low timing
    high_time_idx = bars['high'].idxmax()
    low_time_idx = bars['low'].idxmin()
    
    # AM-PM correlation
    am_returns = am_bars['close'].pct_change().dropna()
    pm_returns = pm_bars['close'].pct_change().dropna()
    if len(am_returns) == len(pm_returns) and len(am_returns) > 0:
        am_pm_corr = am_returns.corr(pm_returns)
    else:
        am_pm_corr = 0.0
    
    # Volume features
    am_vol = am_bars['volume'].sum()
    pm_vol = pm_bars['volume'].sum()
    volume_ratio_am_pm = am_vol / (pm_vol + 1e-10)
    
    volume_spike_open = bars.iloc[0]['volume'] / (bars['volume'].mean() + 1e-10)
    
    # Volume trend (correlation with bar index)
    bar_idx = np.arange(len(bars))
    volume_trend = np.corrcoef(bar_idx, bars['volume'].values)[0, 1]
    
    # Volume skewness
    volume_skew = bars['volume'].skew()
    
    # Volatility features
    log_returns = np.log(bars['close'] / bars['open']).values
    realized_vol = log_returns.std() * np.sqrt(48)
    
    range_vol_ratio = (day_high - day_low) / (realized_vol + 1e-10)
    
    # Volatility of volatility (rolling 6-bar vol)
    rolling_vol = pd.Series(log_returns).rolling(6).std().dropna() * np.sqrt(48)
    vol_of_vol = rolling_vol.std() if len(rolling_vol) > 0 else 0.0
    
    return {
        'gap_pct': gap_pct,
        'intraday_return': intraday_return,
        'day_range': day_range,
        'am_return': am_return,
        'pm_return': pm_return,
        'close_location': close_location,
        'max_drawdown_intra': max_drawdown_intra,
        'max_rally_intra': max_rally_intra,
        'path_efficiency': path_efficiency,
        'first_30min_return': first_30min_return,
        'last_30min_return': last_30min_return,
        'high_time_idx': high_time_idx,
        'low_time_idx': low_time_idx,
        'am_pm_corr': am_pm_corr,
        'volume_ratio_am_pm': volume_ratio_am_pm,
        'volume_spike_open': volume_spike_open,
        'volume_trend': volume_trend,
        'volume_skew': volume_skew,
        'realized_vol': realized_vol,
        'range_vol_ratio': range_vol_ratio,
        'prev_day_vol': prev_day_vol,
        'vol_of_vol': vol_of_vol,
    }


def process_etf(etf_name):
    """Process one ETF: extract features and paths"""
    print(f"\n{'='*60}")
    print(f"Processing {etf_name}")
    print('='*60)
    
    df_5m, df_1d = load_data(etf_name)
    if df_5m is None:
        return
    
    # Build prev_close lookup from 1d data
    prev_close_map = dict(zip(df_1d['date'], df_1d['prev_close']))
    close_map = dict(zip(df_1d['date'], df_1d['close']))
    
    # Get trading days
    trading_days = sorted(df_5m['date'].unique())
    print(f"  Trading days: {len(trading_days)}")
    
    # Extract features day by day
    all_features = []
    all_paths_price = []
    all_paths_volume = []
    all_paths_returns = []
    all_dates = []
    
    for i, date in enumerate(trading_days):
        if i % 100 == 0:
            print(f"  Processing day {i+1}/{len(trading_days)}...")
        
        # Get prev_close
        if date not in prev_close_map:
            continue
        prev_close = prev_close_map[date]
        
        if pd.isna(prev_close) or prev_close <= 0:
            continue
        
        # Get day's bars
        df_day = df_5m[df_5m['date'] == date].copy()
        if len(df_day) < 10:
            continue
        
        # Extract paths
        paths = extract_day_paths(df_day, prev_close)
        if paths is None:
            continue
        
        # Get previous day's features for lagged variables
        if i > 0:
            prev_date = trading_days[i-1]
            prev_day_vol = close_map.get(prev_date, np.nan)
            # Approximate prev day realized vol from previous iteration
            prev_day_realized_vol = all_features[-1].get('realized_vol', 0.0) if all_features else 0.0
        else:
            prev_day_vol = np.nan
            prev_day_realized_vol = 0.0
        
        # Extract scalar features
        scalar_feats = extract_scalar_features(
            paths['bars'], prev_close, prev_day_vol, prev_day_realized_vol
        )
        scalar_feats['date'] = date
        
        all_features.append(scalar_feats)
        all_paths_price.append(paths['norm_price'])
        all_paths_volume.append(paths['norm_volume'])
        all_paths_returns.append(paths['log_returns'])
        all_dates.append(date)
    
    print(f"  Extracted {len(all_features)} days")
    
    # Save features CSV
    df_features = pd.DataFrame(all_features)
    df_features = df_features.set_index('date')
    
    out_csv = OUT_DATA_DIR / f'features_{etf_name}.csv'
    df_features.to_csv(out_csv)
    print(f"  Saved: {out_csv} ({len(df_features)} rows, {len(df_features.columns)} features)")
    
    # Save paths NPZ
    out_npz = OUT_DATA_DIR / f'paths_{etf_name}.npz'
    np.savez(
        out_npz,
        price=np.array(all_paths_price),
        volume=np.array(all_paths_volume),
        returns=np.array(all_paths_returns),
        dates=np.array(all_dates)
    )
    print(f"  Saved: {out_npz}")
    
    # Quick stats
    print(f"\n  Feature stats:")
    print(f"    gap_pct: {df_features['gap_pct'].mean():.4f} ± {df_features['gap_pct'].std():.4f}")
    print(f"    intraday_return: {df_features['intraday_return'].mean():.4f} ± {df_features['intraday_return'].std():.4f}")
    print(f"    realized_vol: {df_features['realized_vol'].mean():.4f} ± {df_features['realized_vol'].std():.4f}")


def main():
    OUT_DATA_DIR.mkdir(exist_ok=True)
    
    print("Day-Type Discovery: Feature Extraction")
    print("=" * 60)
    
    for etf_name in ETF_CONFIG.keys():
        try:
            process_etf(etf_name)
        except Exception as e:
            print(f"  [ERROR] {etf_name}: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*60)
    print("Feature extraction complete!")
    print("="*60)


if __name__ == '__main__':
    main()
