import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path

from src.utils import clean_zero_as_nan

def main():
    # 1. Setup Paths (Relative to root)
    pima_path = Path('data/bronze/pima.csv')
    figures_dir = Path('figures')
    
    figures_dir.mkdir(exist_ok=True)

    if not pima_path.exists():
        print(f"Error: Could not find {pima_path}")
        print("Make sure you are running this script from the project root: python generate_prelim_figures.py")
        return

    # 2. Load Data
    print(f"Loading data from {pima_path}...")
    raw = pd.read_csv(pima_path)

    # 3. Clean Data (zeros -> NaN)
    cols_to_clean = ['Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'BMI']
    
    if 'plas' in raw.columns:
        cols_to_clean = ['plas', 'pres', 'skin', 'insu', 'mass']
        
    cleaned = clean_zero_as_nan(raw, cols_to_clean)

    # 4. Plot 1: Correlation Heatmap
    print("Generating Correlation Heatmap...")
    plt.figure(figsize=(6, 5))
    cols_of_interest = cols_to_clean[:3] # e.g. Glucose, BP, Skin
    sns.heatmap(cleaned[cols_of_interest].corr(), annot=True, cmap='coolwarm', fmt=".2f")
    plt.title('Correlation Matrix (Cleaned Data)')
    plt.tight_layout()
    plt.savefig(figures_dir / 'corr_heatmap.png', dpi=100)
    plt.close()

    # 5. Plot 2: Histogram (Raw vs Cleaned)
    print("Generating Distribution Histogram...")
    target_col = cols_to_clean[-1] # BMI (or 'mass')
    
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    
    # Raw
    raw[target_col].hist(ax=axes[0], bins=20, color='skyblue', alpha=0.7)
    axes[0].set_title(f'{target_col} (Raw - with zeros)')
    axes[0].set_ylabel("Frequency")
    
    # Cleaned
    cleaned[target_col].hist(ax=axes[1], bins=20, color='salmon', alpha=0.7)
    axes[1].set_title(f'{target_col} (Cleaned - zeros removed)')
    
    plt.suptitle(f'Impact of Data Cleaning: {target_col}', fontsize=14)
    plt.tight_layout()
    plt.savefig(figures_dir / 'raw_vs_cleaned_hist.png', dpi=100)
    plt.close()

    print("Success! Figures saved to figures/")

if __name__ == "__main__":
    main()