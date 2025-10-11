import numpy as np
import pandas as pd
from .base import BaseAdapter
from src.utils import clean_zero_as_nan

class PimaAdapter(BaseAdapter):
    def load_raw(self) -> pd.DataFrame:
        return pd.read_csv(self.path)

    def to_silver(self, df_raw: pd.DataFrame) -> pd.DataFrame:
        df = df_raw.copy()

        # Map short -> long names if present
        colmap = {
            "preg": "Pregnancies",
            "plas": "Glucose",
            "pres": "BloodPressure",            # Pima BP is diastolic
            "skin": "SkinThickness",
            "insu": "Insulin",
            "mass": "BMI",
            "pedi": "DiabetesPedigreeFunction",
            "age":  "Age",
            "class":"Outcome",
        }
        df = df.rename(columns={k: v for k, v in colmap.items() if k in df.columns})

        # Ensure Outcome is 0/1 if it's strings like "tested_positive"
        if "Outcome" in df and not pd.api.types.is_integer_dtype(df["Outcome"]):
            df["Outcome"] = (
                df["Outcome"].astype(str).str.contains("pos", case=False).astype(int)
            )

        # Zero-as-missing (only for columns that exist)
        zero_cols = [c for c in ["Glucose","BloodPressure","SkinThickness","Insulin","BMI"] if c in df.columns]
        df = clean_zero_as_nan(df, zero_cols)

        # Build canonical frame
        out = pd.DataFrame({
            "age_years": df["Age"].astype(float),
            "sex":       "unknown",
            "bmi_kgm2":  df["BMI"].astype(float),
            "sbp_mmHg":  np.nan,                                # no systolic in Pima
            "dbp_mmHg":  df["BloodPressure"].astype(float),
            "fpg_mgdl":  df["Glucose"].astype(float),
            "hba1c_pct": np.nan,
            "insulin_uIUml": df["Insulin"].astype(float) if "Insulin" in df else np.nan,
            "skinfold_triceps_mm": df["SkinThickness"].astype(float) if "SkinThickness" in df else np.nan,
            "outcome_dm": df["Outcome"].astype(int),
            "country":   self.country,
            "year":      self.year,
            "source_id": self.source_id,
        })

        # Add nullable fields AFTER out exists
        out["family_history_dm"] = pd.Series(pd.NA, index=out.index, dtype="Int64")
        out["dpf_raw"] = (
            df["DiabetesPedigreeFunction"].astype(float)
            if "DiabetesPedigreeFunction" in df
            else pd.Series(np.nan, index=out.index, dtype="float")
        )

        return out
