from abc import ABC, abstractmethod
import pandas as pd

class BaseAdapter(ABC):
    def __init__(self, path: str, country: str, year: int, source_id: str):
        self.path = path
        self.country = country
        self.year = year
        self.source_id = source_id

    @abstractmethod
    def load_raw(self) -> pd.DataFrame:
        ...

    @abstractmethod
    def to_silver(self, df_raw: pd.DataFrame) -> pd.DataFrame:
        ...

