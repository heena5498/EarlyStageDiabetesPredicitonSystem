"""Simple ingestion CLI to fetch datasets defined in config/registry.yaml

Usage: python -m src.ingest
"""
import typer, pandas as pd
from pathlib import Path
from src.utils import load_yaml, ensure_dir
from src.validate import validate_silver
from src.labeling import apply_labels
from src.adapters.pima import PimaAdapter
# from src.adapters.nhanes import NHANES_Adapter
# from src.adapters.steps_bd import STEPS_BD_Adapter  # example

app = typer.Typer()

ADAPTERS = {
    "pima": PimaAdapter,
    # "nhanes": NHANES_Adapter,
    # "steps": STEPS_BD_Adapter,
}

def _instantiate(dkey, meta):
    adapter_cls = ADAPTERS[meta["adapter"]]
    return adapter_cls(
        path=meta["path"],
        country=meta["country"],
        year=meta["year"],
        source_id=dkey
    )

@app.command()
def silver(dataset: str):
    """Make silver parquet for a specific dataset key in registry.yaml."""
    reg = load_yaml("config/registry.yaml")["datasets"]
    meta = reg[dataset]
    adapter = _instantiate(dataset, meta)

    df_raw = adapter.load_raw()
    df_silver = adapter.to_silver(df_raw)
    df_silver = apply_labels(df_silver)  # only changes if label missing

    df_silver = validate_silver(df_silver)

    ensure_dir("data/silver")
    outp = f"data/silver/{dataset}.parquet"
    df_silver.to_parquet(outp, index=False)
    typer.echo(f"Saved silver → {outp} | rows={len(df_silver)}")

@app.command()
def gold():
    """Merge all available silver files into one model-ready parquet."""
    ensure_dir("data/gold")
    silver_dir = Path("data/silver")
    frames = []
    for fp in silver_dir.glob("*.parquet"):
        frames.append(pd.read_parquet(fp))
    if not frames:
        typer.echo("No silver files found.")
        raise typer.Exit(code=1)
    df = pd.concat(frames, ignore_index=True)
    # (Optional) drop columns you won’t model on, e.g., sbp_mmHg when missing
    df.to_parquet("data/gold/diabetes_ml.parquet", index=False)
    typer.echo(f"Merged gold → data/gold/diabetes_ml.parquet | rows={len(df)}")

if __name__ == "__main__":
    app()

