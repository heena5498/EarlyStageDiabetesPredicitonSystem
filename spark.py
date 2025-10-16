import pandas as pd
from pathlib import Path

silver_dir = Path("data/silver")

for file in silver_dir.glob("*.parquet"):
    print(f"\n📄 {file.name}")
    df = pd.read_parquet(file)
    print(df.head(), "\nShape:", df.shape)