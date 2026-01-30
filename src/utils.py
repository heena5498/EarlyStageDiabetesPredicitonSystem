import yaml, pandas as pd, numpy as np
from pathlib import Path

def load_yaml(path):
    with open(path, "r") as f:
        return yaml.safe_load(f)

def ensure_dir(p):
    Path(p).mkdir(parents=True, exist_ok=True)

def mgdl_to_mmol_glucose(x):
    # 1 mmol/L glucose ≈ 18 mg/dL
    return x / 18.0

def clean_zero_as_nan(df, cols):
    df = df.copy()
    for c in cols:
        mask = df[c].astype(float) == 0 
        df.loc[mask, c] = np.nan 
    return df

