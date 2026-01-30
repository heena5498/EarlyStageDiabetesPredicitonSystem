import pandas as pd
from src.utils import load_yaml

def apply_labels(df: pd.DataFrame, criteria_path="config/criteria.yaml") -> pd.DataFrame:
    cfg = load_yaml(criteria_path)
    df = df.copy()
    if cfg.get("use_label_if_present", True) and "outcome_dm" in df.columns and df["outcome_dm"].notna().any():
        return df

    rules = cfg["derive_rules"]
    outcome = pd.Series(0, index=df.index, dtype=int)

    if rules.get("use_fpg", False) and "fpg_mgdl" in df:
        fpg_cut = float(rules["fpg_diabetes_mgdl"])
        outcome = outcome.where(~(df["fpg_mgdl"] >= fpg_cut), 1)

    if rules.get("use_hba1c", False) and "hba1c_pct" in df:
        a1c_cut = float(rules["hba1c_diabetes_pct"])
        outcome = outcome.where(~(df["hba1c_pct"] >= a1c_cut), 1)

    df["outcome_dm"] = outcome.fillna(0).astype(int)
    return df
