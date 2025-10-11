# Early Diabetes Risk Prediction (Multi‑Country) — Initial Approach

A lightweight, extensible pipeline and web app to estimate **diabetes risk** from routinely collected health metrics. Starts with the **Pima Indians Diabetes** dataset for fast prototyping, then scales to cross‑country microdata (e.g., **NHANES**, **WHO STEPS**, **ENSANUT**, **CHNS**) using a harmonized schema.

---

## 🎯 Goals
- Build a **clean baseline** model (Logistic Regression → RF/XGBoost later) that predicts diabetes risk.
- Create a **reproducible ETL** (bronze → silver → gold) to harmonize multiple countries’ datasets.
- Ship a **minimal Flask UI** + programmatic inference.
- Keep **thresholds and diagnostic criteria editable** (config‑driven).

> **Not medical advice.** This tool provides educational risk estimates and is **not a diagnostic device**. Consult a licensed clinician for medical decisions.

---

## 🗺️ Architecture at a glance
```
(raw) bronze  →  (harmonized per‑dataset) silver  →  (merged) gold  →  train  →  Flask app
```
- **bronze**: As‑downloaded CSV/Parquet (read‑only)
- **silver**: Canonical columns with units + derived labels if needed
- **gold**: Union of all silver datasets (model‑ready)

---

## 📁 Repository structure
```
diabetes-risk/
├─ data/
│  ├─ bronze/                  # raw files
│  ├─ silver/                  # cleaned per‑dataset
│  └─ gold/                    # merged for modeling
├─ config/
│  ├─ registry.yaml            # dataset registry (paths, years, adapters)
│  ├─ schema.yaml              # canonical variables + units
│  └─ criteria.yaml            # diagnostic cutoffs & rules
├─ src/
│  ├─ adapters/                # one adapter per dataset
│  │  ├─ base.py
│  │  ├─ pima.py               # working adapter (today)
│  │  └─ nhanes_skeleton.py    # skeleton to extend
│  ├─ ingest.py                # CLI: build silver/gold
│  ├─ labeling.py              # derive outcome via config
│  ├─ validate.py              # schema checks (pandera)
│  └─ utils.py
├─ app/
│  ├─ server.py                # Flask app (form UI)
│  └─ templates/index.html
├─ models/
│  ├─ model.joblib             # trained pipeline
│  └─ config.json              # thresholds, metrics, feature order
├─ notebooks/
│  └─ 01_eda_baseline.ipynb
├─ requirements.txt
└─ README.md
```

---

## 🧾 Canonical feature schema (silver)
| Column | Type | Unit | Notes |
|---|---|---|---|
| `age_years` | float | years | |
| `sex` | category | – | {male, female, other, unknown} (often unavailable in Pima) |
| `bmi_kgm2` | float | kg/m² | |
| `sbp_mmHg` | float | mmHg | Systolic BP (may be NA in some datasets) |
| `dbp_mmHg` | float | mmHg | Diastolic BP (Pima’s BloodPressure is **DBP**) |
| `fpg_mgdl` | float | mg/dL | Fasting Plasma Glucose (FPG) |
| `hba1c_pct` | float | % | Optional if available |
| `insulin_uIUml` | float | µIU/mL | Optional; available in NHANES/Pima |
| `skinfold_triceps_mm` | float | mm | Optional; proxy for adiposity (NHANES) |
| `family_history_dm` | int | 0/1 | If collected; else NA |
| `outcome_dm` | int | 0/1 | Diabetes label (from dataset or derived) |
| `country` | string | – | e.g., USA, Bangladesh |
| `year` | int | – | Survey/reference year |
| `source_id` | string | – | Dataset key, e.g., `pima` |

> **Zeros‑as‑missing**: In Pima, zeros in `Glucose`, `BloodPressure`, `SkinThickness`, `Insulin`, `BMI` are treated as **missing** and converted to `NaN` during ETL.

---

## ⚙️ Configs
**`config/registry.yaml`** — register datasets (path, country, year, adapter)
```yaml
datasets:
  pima:
    path: "data/bronze/pima.csv"
    country: "USA"
    year: 1990
    adapter: "pima"
```

**`config/schema.yaml`** — enforce canonical columns & types (see table above)

**`config/criteria.yaml`** — diagnostic rules (editable)
```yaml
use_label_if_present: true
derive_rules:
  use_fpg: true
  fpg_diabetes_mgdl: 126
  use_hba1c: true
  hba1c_diabetes_pct: 6.5
priority: ["existing_label", "fpg", "hba1c"]
```

---

## ⚡ Setup: create virtualenv & install requirements

**macOS / Linux**
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
# quick sanity check
python -c "import pandas, sklearn, flask; print('env OK')"
```

**Windows (PowerShell)**
```powershell
py -m venv .venv
# activate
& .venv/Scripts/Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
# quick sanity check
python -c "import pandas, sklearn, flask; print('env OK')"
```

> Tip: If you use conda, create `conda create -n diabetes-risk python=3.10` then `conda activate diabetes-risk` and install `requirements.txt`.

---

## 🗃️ Populate `config/registry.yaml` with real dataset paths/URLs
- Put local files under `data/bronze/` **or** point directly to a remote URL (pandas can read `http(s)` CSVs).
- Each entry needs: `path`, `country`, `year`, and the `adapter` name you’ll use in `src/adapters/`.

**Examples**
```yaml
datasets:
  # Local Pima CSV
  pima:
    path: "data/bronze/pima.csv"
    country: "USA"
    year: 1990
    adapter: "pima"


**Download helpers**

macOS/Linux
```bash
mkdir -p data/bronze
curl -L -o data/bronze/pima.csv https://www.kaggle.com/datasets/uciml/pima-indians-diabetes-database
# or
wget -O data/bronze/pima.csv https://www.kaggle.com/datasets/uciml/pima-indians-diabetes-database
```

Windows (PowerShell)
```powershell
New-Item -ItemType Directory -Force data/bronze | Out-Null
Invoke-WebRequest -Uri https://www.kaggle.com/datasets/uciml/pima-indians-diabetes-database -OutFile "data/bronze/pima.csv"
```

**Verify the path works**
```bash
python - <<'PY'
import pandas as pd
print(pd.read_csv('data/bronze/pima.csv').shape)
PY
```

Then build the first silver file:
```bash
python src/ingest.py silver pima
```

---

## 🚀 Quickstart (5 minutes)
**Prereqs**: Python 3.10+, macOS/Linux/WSL
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 1) Place Pima CSV
mkdir -p data/bronze && cp <your_pima.csv> data/bronze/pima.csv

# 2) Build silver for Pima
python src/ingest.py silver pima

# 3) Merge to gold (once you have multiple silver files)
python src/ingest.py gold

# 4) Train baseline model
python src/train.py

# 5) Run the Flask UI
python app/server.py
# open http://localhost:5000
```

---

## 🧪 Modeling (baseline → explainable)
- **Baseline**: Logistic Regression (class_weight="balanced") wrapped in `CalibratedClassifierCV` for probability calibration.
- **Risk tiers** (config saved in `models/config.json`):
  - `p < t_med` → **Low**
  - `t_med ≤ p < t_high` → **Medium**
  - `p ≥ t_high` → **High**
- **Metrics**: ROC‑AUC, PR‑AUC, **recall (sensitivity)**, specificity, F2 (recall‑weighted), Brier score (calibration).
- **Explainability**: permutation importance or SHAP (optional) in `notebooks/01_eda_baseline.ipynb`.

---

## 🌐 Flask UI & API
**Web UI**: simple form at `/` that posts to `/predict`.

**Programmatic inference (Python):**
```python
from src.infer import predict_risk
payload = {
  "Pregnancies": 2, "Glucose": 148, "BloodPressure": 70,
  "SkinThickness": 35, "Insulin": 0, "BMI": 33.6,
  "DiabetesPedigreeFunction": 0.627, "Age": 50
}
print(predict_risk(payload))
# → {"probability": 0.73, "tier": "High", "version": "logreg_calibrated_v1"}
```

**HTTP (form POST) example:**
```bash
curl -X POST http://localhost:5000/predict \
  -d pregnancies=2 -d glucose=148 -d bloodpressure=70 \
  -d skinthickness=35 -d insulin=0 -d bmi=33.6 -d dpf=0.627 -d age=50
```

---

## 🔍 Data quality & harmonization notes
- **Units**: glucose in mg/dL (convert mmol/L → mg/dL by ×18). BP in mmHg. BMI in kg/m².
- **Zeros → NaN**: apply to Pima fields (`Glucose`, `BloodPressure`, `SkinThickness`, `Insulin`, `BMI`).
- **Labeling**: if dataset lacks an explicit diabetes flag, derive via `criteria.yaml` (FPG ≥ 126 mg/dL or HbA1c ≥ 6.5%).
- **Ranges** (sanity checks): BMI 10–80, SBP 70–250, DBP 40–150, FPG 40–500.

---

## 🧱 Extending to multi‑country data
1) **Add adapter** `src/adapters/<dataset>.py` mapping original columns → canonical names (handle joins/units).
2) Register in `config/registry.yaml` and run:
```bash
python src/ingest.py silver <dataset>
```
3) After multiple silver files exist, build gold and retrain:
```bash
python src/ingest.py gold
python src/train.py
```
---

## 🙌 Acknowledgments
- **Pima Indians Diabetes Dataset** (UCI ML Repository) used for prototyping.
- Inspiration from public health survey designs (NHANES, WHO STEPS, ENSANUT, CHNS).

---

## 📜 License
MIT License

---




