import pandas as pd, numpy as np
from .base import BaseAdapter

class NHANES_Adapter(BaseAdapter):
    def load_raw(self) -> pd.DataFrame:
        # you’ll likely need to join multiple files (exam, lab, demo).
        # Load them here and merge on respondent ID.
        raise NotImplementedError

    def to_silver(self, df_raw: pd.DataFrame) -> pd.DataFrame:
        # map NHANES variable names -> canonical names
        # convert mmol/L -> mg/dL if needed (*18 for glucose)
        raise NotImplementedError
