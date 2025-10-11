from .base import Adapter
import pandas as pd


class HTTPCSVAdapter(Adapter):
    """Generic adapter for CSV datasets available over HTTP/S."""

    name = "http_csv"

    def fetch(self) -> pd.DataFrame:
        url = self.config.get("url")
        if not url:
            raise ValueError("HTTPCSVAdapter requires a `url` in config")
        return pd.read_csv(url)
