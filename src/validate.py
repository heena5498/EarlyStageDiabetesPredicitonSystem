import pandas as pd
import pandera.pandas as pa
from pandera import Column, Check

def silver_schema():
    return pa.DataFrameSchema({
        "age_years": Column(float, Check.ge(0), nullable=True),
        "sex": Column(object, nullable=True),
        "bmi_kgm2": Column(float, Check.ge(5), nullable=True),
        "sbp_mmHg": Column(float, Check.ge(40), nullable=True),
        "dbp_mmHg": Column(float, Check.ge(20), nullable=True),
        "fpg_mgdl": Column(float, Check.ge(20), nullable=True),
        "hba1c_pct": Column(float, Check.ge(3), nullable=True),
        "insulin_uIUml": Column(float, Check.ge(0), nullable=True),
        "skinfold_triceps_mm": Column(float, Check.ge(0), nullable=True),
        "family_history_dm": Column(pd.Int64Dtype, nullable=True),
        "outcome_dm": Column(int, Check.isin([0,1]), nullable=True),
        "country": Column(object),
        "year": Column(int),
        "source_id": Column(object),
    }, coerce=True, strict=False)

def validate_silver(df: pd.DataFrame):
    return silver_schema().validate(df)
