# Model Card: {Model Name}

## Model Details
- **Model type**: {e.g., RandomForestClassifier, XGBRegressor}
- **Training date**: {YYYY-MM-DD}
- **Framework**: {scikit-learn 1.x / pytorch 2.x}
- **MLflow run ID**: {run-id}
- **Git commit**: {sha}
- **Random seed**: {seed value}

## Intended Use
- **Primary use**: {what task this model solves}
- **Out-of-scope uses**: {what it should NOT be used for}
- **Users**: {who will use this}

## Data
- **Training dataset**: {name, source, date, rows, features}
- **Validation dataset**: {name, split strategy}
- **Test dataset**: {name, held-out, never touched until final evaluation}
- **Known biases**: {any known biases in the data}

## Performance
| Metric | Train | Validation | Test |
|---|---|---|---|
| {metric 1} | | | |
| {metric 2} | | | |

## Limitations
- {List known limitations}

## Ethical Considerations
- {Any fairness, privacy, or misuse concerns}

## Reproducibility
- [ ] Seed set: `SEED = {value}` in all notebooks
- [ ] Requirements pinned: `requirements.txt` or `environment.yml` committed
- [ ] Data hash logged in MLflow
- [ ] Notebook runs top-to-bottom from clean kernel
- [ ] `nbval` or equivalent confirms clean re-run
