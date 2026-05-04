# Model Card: Iris Random Forest Classifier

## Model Details
- **Model type**: RandomForestClassifier (scikit-learn)
- **Training date**: 2024-01-15
- **Framework**: scikit-learn 1.3.2
- **MLflow run ID**: abc123def456 (example — replace with actual run ID)
- **Git commit**: a1b2c3d4e5f6 (example — replace with actual SHA)
- **Random seed**: 42

## Intended Use
- **Primary use**: Multi-class classification of iris flowers into three species (setosa, versicolor, virginica) based on four morphological measurements (sepal length, sepal width, petal length, petal width).
- **Out-of-scope uses**: This model should NOT be used for identifying iris species in the wild from photographs, for any plant biology research requiring statistical rigor, or as a component in any production system making consequential decisions. It is a teaching/demonstration model only.
- **Users**: Data science students and instructors using this as a reference implementation of the EDA → experiment → model card workflow.

## Data
- **Training dataset**: Iris dataset (sklearn built-in), 120 samples (80% stratified split), 4 features: sepal length (cm), sepal width (cm), petal length (cm), petal width (cm)
- **Validation dataset**: 5-fold cross-validation on training set (24 samples per fold held out)
- **Test dataset**: 30 samples held out via stratified 80/20 split before any training. Never used for any tuning decisions — evaluated exactly once.
- **Known biases**: Dataset is perfectly balanced (50 samples per class) — real-world iris classification would rarely have such balance. Versicolor and virginica classes overlap in sepal width, which may cause misclassifications in boundary cases.

## Performance
| Metric | Train | Validation (CV mean ± std) | Test |
|---|---|---|---|
| Accuracy | 1.000 | 0.958 ± 0.022 | 0.967 |
| F1 (macro) | 1.000 | 0.958 ± 0.022 | 0.967 |

**Per-class test performance:**
| Class | Precision | Recall | F1 |
|---|---|---|---|
| setosa | 1.00 | 1.00 | 1.00 |
| versicolor | 0.91 | 1.00 | 0.95 |
| virginica | 1.00 | 0.90 | 0.95 |

## Limitations
- **Data size**: 150 samples is tiny. Performance metrics have high variance — the 0.967 test accuracy is from a single 30-sample test set and should not be over-interpreted.
- **Distribution shift**: Model trained on Anderson (1936) measurements. Any change in measurement instrument or protocol would invalidate the model.
- **Versicolor/virginica boundary**: 1 virginica sample misclassified as versicolor (see confusion matrix artifact in MLflow). This is a fundamental data limitation — the two species overlap morphologically.
- **No uncertainty estimates**: The model produces hard class predictions without calibrated probabilities. Do not use for any application where knowing prediction confidence matters.

## Ethical Considerations
- No meaningful ethical concerns for this toy dataset.
- As a teaching model, care should be taken not to present the near-perfect accuracy as representative of real-world ML performance. Real datasets are messier and performance is lower.

## Reproducibility
- [x] Seed set: `SEED = 42` in all notebooks — set before any random operation
- [x] Requirements pinned: `requirements.txt` committed with exact versions
- [x] Data hash logged in MLflow (tag: `data_source = sklearn_builtin_v1.3.2`)
- [x] Notebook `02_experiment.ipynb` runs top-to-bottom from clean kernel without errors
- [x] `nbval` confirms clean re-run: `pytest --nbval 02_experiment.ipynb`

**To reproduce this result:**
```bash
git clone <repo>
git checkout a1b2c3d4e5f6
pip install -r requirements.txt
jupyter nbconvert --to notebook --execute 02_experiment.ipynb
```
