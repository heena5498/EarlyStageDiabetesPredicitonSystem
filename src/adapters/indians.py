import numpy as np
import pandas as pd
from .base import BaseAdapter
from src.utils import clean_zero_as_nan  # keep consistent with pima.py usage

class IndiansAdapter(BaseAdapter):
    """
    Adapter for `indians.csv`-style files.

    Expected raw columns (present in your indians.csv):
      - Age, Gender, BMI, Family_History, Fasting_Blood_Sugar, HBA1C, Diabetes_Status
      - plus many additional fields we treat as extras

    Output (canonical silver) columns per schema:
      age_years, sex, bmi_kgm2, sbp_mmHg, dbp_mmHg, fpg_mgdl, hba1c_pct,
      insulin_uIUml, skinfold_triceps_mm, family_history_dm, outcome_dm,
      country, year, source_id
    """

    def load_raw(self) -> pd.DataFrame:
        return pd.read_csv(self.path)

    # --- helpers -------------------------------------------------------------

    @staticmethod
    def _norm_sex(val) -> str:
        if pd.isna(val):
            return "unknown"
        v = str(val).strip().lower()
        if v in {"male", "m"}:
            return "male"
        if v in {"female", "f"}:
            return "female"
        if v in {"other", "non-binary", "nonbinary", "nb", "third"}:
            return "other"
        return "unknown"

    @staticmethod
    def _yesno_to_int(val):
        if pd.isna(val):
            return pd.NA
        v = str(val).strip().lower()
        if v in {"yes", "y", "true", "1"}:
            return 1
        if v in {"no", "n", "false", "0"}:
            return 0
        return pd.NA

    # --- main transform ------------------------------------------------------

    def to_silver(self, df_raw: pd.DataFrame) -> pd.DataFrame:
        df = df_raw.copy()

        # Map & coerce fields; if a field is missing, create a proper typed NA series
        age = (
            df["Age"].astype(float)
            if "Age" in df
            else pd.Series(np.nan, index=df.index, dtype="float")
        )

        sex = (
            df["Gender"].map(self._norm_sex)
            if "Gender" in df
            else pd.Series("unknown", index=df.index, dtype="object")
        )

        bmi = (
            df["BMI"].astype(float)
            if "BMI" in df
            else pd.Series(np.nan, index=df.index, dtype="float")
        )

        # SBP/DBP are not provided in this dataset; leave as NaN
        sbp = pd.Series(np.nan, index=df.index, dtype="float")
        dbp = pd.Series(np.nan, index=df.index, dtype="float")

        fpg = (
            df["Fasting_Blood_Sugar"].astype(float)
            if "Fasting_Blood_Sugar" in df
            else pd.Series(np.nan, index=df.index, dtype="float")
        )

        hba1c = (
            df["HBA1C"].astype(float)
            if "HBA1C" in df
            else pd.Series(np.nan, index=df.index, dtype="float")
        )

        # Not available in this dataset
        insulin = pd.Series(np.nan, index=df.index, dtype="float")
        skinfold = pd.Series(np.nan, index=df.index, dtype="float")

        # Family history (0/1/NA)
        family_hist = (
            df["Family_History"].map(self._yesno_to_int).astype("Int64")
            if "Family_History" in df
            else pd.Series(pd.NA, index=df.index, dtype="Int64")
        )

        # Outcome (0/1/NA) from Diabetes_Status
        outcome = (
            df["Diabetes_Status"].map(self._yesno_to_int).astype("Int64")
            if "Diabetes_Status" in df
            else pd.Series(pd.NA, index=df.index, dtype="Int64")
        )

        # Optional: treat biological-impossible zeros as missing on numeric fields we have
        zero_cols = [c for c, series in {
            "Fasting_Blood_Sugar": fpg,
            "HBA1C": hba1c,
            "BMI": bmi
        }.items() if c in df.columns]
        if zero_cols:
            df_tmp = pd.DataFrame({"Fasting_Blood_Sugar": fpg, "HBA1C": hba1c, "BMI": bmi})
            df_tmp = clean_zero_as_nan(df_tmp, [c for c in zero_cols if c in df_tmp.columns])
            fpg = df_tmp.get("Fasting_Blood_Sugar", fpg)
            hba1c = df_tmp.get("HBA1C", hba1c)
            bmi = df_tmp.get("BMI", bmi)

        # Build canonical frame
        out = pd.DataFrame({
            "age_years": age,
            "sex": sex,
            "bmi_kgm2": bmi,
            "sbp_mmHg": sbp,
            "dbp_mmHg": dbp,
            "fpg_mgdl": fpg,
            "hba1c_pct": hba1c,
            "insulin_uIUml": insulin,
            "skinfold_triceps_mm": skinfold,
            "family_history_dm": family_hist,
            "outcome_dm": outcome,
            "country":   getattr(self, "country", None),
            "year":      getattr(self, "year", None),
            "source_id": getattr(self, "source_id", None),
        })

        return out
