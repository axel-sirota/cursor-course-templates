# DS Notebook Starter Template

Use this as a structural guide when creating a new Jupyter notebook. Paste each section in order, then fill in the content for your specific dataset and problem.

---

## Section 1: Setup

**Purpose**: Import libraries, set the global seed, define paths and constants.

```python
# --- Imports ---
import random
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Optional ML imports (uncomment as needed):
# from sklearn.model_selection import train_test_split
# from sklearn.preprocessing import StandardScaler
# from sklearn.metrics import classification_report, mean_squared_error

# --- Seed ---
SEED = 42
random.seed(SEED)
np.random.seed(SEED)

# --- Paths ---
DATA_DIR = Path.cwd().parent / "data"
RAW_PATH = DATA_DIR / "raw" / "your_dataset.csv"   # update filename
PROCESSED_PATH = DATA_DIR / "processed"
MODELS_DIR = Path.cwd().parent / "models"

# --- Display settings ---
pd.set_option("display.max_columns", 50)
pd.set_option("display.float_format", "{:.4f}".format)
%matplotlib inline
```

---

## Section 2: Data Loading

**Purpose**: Load raw data, print shape and dtypes, confirm the file was read correctly.

```python
df = pd.read_csv(RAW_PATH)

print(f"Shape: {df.shape}")
print(f"\nDtypes:\n{df.dtypes}")
print(f"\nNull counts:\n{df.isnull().sum()}")
df.head()
```

Add a markdown cell noting:
- Data source and date range
- Row count and column count
- Any known quality issues

---

## Section 3: EDA

**Purpose**: Understand distributions, detect anomalies, and surface patterns before modeling.

```python
# Summary statistics
df.describe()
```

```python
# Null heatmap
import seaborn as sns
sns.heatmap(df.isnull(), cbar=False, yticklabels=False)
plt.title("Missing Values")
plt.show()
```

```python
# Distribution of target variable (replace 'target' with your column name)
sns.histplot(df["target"], kde=True)
plt.title("Target Distribution")
plt.show()
```

```python
# Correlation matrix (numeric columns only)
corr = df.select_dtypes(include="number").corr()
sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm")
plt.title("Correlation Matrix")
plt.show()
```

Document findings in markdown cells. Note which features look predictive, which look noisy, and any obvious data quality problems.

---

## Section 4: Hypothesis

**Purpose**: Articulate what you expect to find and why, before running any model.

Write a markdown cell answering:

1. **Problem statement**: What are you predicting or clustering?
2. **Key features**: Which columns do you expect to be most predictive, and why?
3. **Baseline**: What does a naive baseline (majority class, mean prediction) score?
4. **Success metric**: What metric will you optimize, and what threshold counts as good?
5. **Risks**: What could go wrong? (leakage, class imbalance, distribution shift)

```python
# Compute baseline
from sklearn.dummy import DummyClassifier  # or DummyRegressor
# baseline = DummyClassifier(strategy="most_frequent").fit(X_train, y_train)
# print("Baseline accuracy:", baseline.score(X_val, y_val))
```

---

## Section 5: Experiment

**Purpose**: Define, train, and log one model. Keep each experiment in its own versioned notebook or clearly marked section.

```python
from sklearn.model_selection import train_test_split

# Feature and target split
FEATURES = ["col1", "col2", "col3"]   # update list
TARGET = "target"

X = df[FEATURES]
y = df[TARGET]

X_train, X_val, y_train, y_val = train_test_split(
    X, y, test_size=0.2, random_state=SEED
)
```

```python
# Model definition — update as needed
from sklearn.ensemble import RandomForestClassifier

model = RandomForestClassifier(n_estimators=100, random_state=SEED)
model.fit(X_train, y_train)
```

```python
# Experiment logging — fill in all fields
import json, datetime

experiment_log = {
    "timestamp": datetime.datetime.utcnow().isoformat(),
    "seed": SEED,
    "model": type(model).__name__,
    "params": model.get_params(),
    "features": FEATURES,
    "train_rows": len(X_train),
    "val_rows": len(X_val),
}
print(json.dumps(experiment_log, indent=2))
```

---

## Section 6: Evaluation

**Purpose**: Measure model performance, visualize errors, and decide whether to iterate.

```python
from sklearn.metrics import classification_report, ConfusionMatrixDisplay

y_pred = model.predict(X_val)

print(classification_report(y_val, y_pred))
```

```python
ConfusionMatrixDisplay.from_estimator(model, X_val, y_val)
plt.title("Confusion Matrix — Validation Set")
plt.show()
```

```python
# Feature importance (tree-based models)
importances = pd.Series(model.feature_importances_, index=FEATURES).sort_values()
importances.plot(kind="barh")
plt.title("Feature Importances")
plt.show()
```

Update the experiment log with metrics:

```python
from sklearn.metrics import accuracy_score

experiment_log["val_accuracy"] = accuracy_score(y_val, y_pred)
print(json.dumps(experiment_log, indent=2))
```

---

## Section 7: Next Steps

Write a markdown cell summarizing:

1. **Key findings**: What did the model learn? What features mattered?
2. **Performance vs. baseline**: Did the model beat the naive baseline?
3. **Outstanding questions**: What data or features are missing?
4. **Decision**: Should you validate this model or iterate back to EDA/Experiment?
5. **Handoff status**: Is a model card ready? Has the notebook passed a clean run?

```python
# Save model artifact (uncomment when ready to hand off)
# import joblib
# MODELS_DIR.mkdir(exist_ok=True)
# joblib.dump(model, MODELS_DIR / "model_v1.pkl")
# print("Model saved.")
```
