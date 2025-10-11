import pandas as pd

df = pd.read_parquet("data/silver/pima.parquet")
print(df.head())