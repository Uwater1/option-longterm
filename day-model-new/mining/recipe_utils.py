import numpy as np
import pandas as pd

def compute_recipe(df: pd.DataFrame, recipe: dict, train_means: dict = None, train_stds: dict = None, train_medians: dict = None) -> np.ndarray:
    """
    Dynamically compute feature values from a recipe dictionary.
    Aligns scale by standardizing inputs for min/max/diff/ifelse using train_means/train_stds if provided.
    """
    op = recipe["op"]
    
    # Helper to get standardized column
    def get_std_col(col_name):
        val = df[col_name].values.astype(np.float64)
        if train_means is not None and col_name in train_means:
            mean = train_means[col_name]
            std = train_stds[col_name]
        else:
            mean = np.nanmean(val)
            std = np.nanstd(val)
        if std < 1e-12:
            std = 1.0
        return (val - mean) / std

    if op == "min":
        a_std = get_std_col(recipe["feature_a"])
        b_std = get_std_col(recipe["feature_b"])
        return np.minimum(a_std, b_std)
        
    elif op == "max":
        a_std = get_std_col(recipe["feature_a"])
        b_std = get_std_col(recipe["feature_b"])
        return np.maximum(a_std, b_std)
        
    elif op == "diff":
        a_std = get_std_col(recipe["feature_a"])
        b_std = get_std_col(recipe["feature_b"])
        return a_std - b_std
        
    elif op == "ratio":
        # Ratio uses raw values because B is assumed to be a positive-only scaling feature (vol/volume)
        a_val = df[recipe["feature_a"]].values.astype(np.float64)
        b_val = df[recipe["feature_b"]].values.astype(np.float64)
        return a_val / (np.abs(b_val) + 1e-5)
        
    elif op == "ifelse":
        cond_col = recipe["feature_cond"]
        cond_val = df[cond_col].values.astype(np.float64)
        
        # Get threshold (median of condition column)
        if train_medians is not None and cond_col in train_medians:
            thresh = train_medians[cond_col]
        else:
            thresh = np.nanmedian(cond_val)
            
        a_std = get_std_col(recipe["feature_a"])
        b_std = get_std_col(recipe["feature_b"])
        return np.where(cond_val > thresh, a_std, b_std)
        
    else:
        raise ValueError(f"Unknown operation in recipe: {op}")
