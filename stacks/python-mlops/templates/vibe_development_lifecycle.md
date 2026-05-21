# Development Lifecycle Vibe: Python MLOps

For git workflow, session rituals, and branching conventions, see `stacks/shared/` (if present). This document adds MLOps-specific lifecycle practices layered on top of standard engineering workflow.

---

## Experiment Branching

ML development has a different branching pattern than standard software engineering. A feature branch in ML corresponds to an experiment hypothesis, not just a code change.

**Branch naming**:
```
experiment/{hypothesis}         # e.g., experiment/xgboost-depth-tuning
experiment/{model-family}-v{n}  # e.g., experiment/gbm-v2
fix/{what-broke}                # e.g., fix/feature-drift-jan2025
infra/{what-changed}            # e.g., infra/serving-latency-optimization
```

**One branch per hypothesis**: if you are testing "does adding tenure_months improve AUC?", that is one branch. If you are testing "does XGBoost beat GBM?", that is a different branch. Keep hypothesis scope narrow so MLflow run comparisons are meaningful.

**Branch lifetime**: experiment branches are short-lived. Once the hypothesis is confirmed or rejected and the MLflow runs are logged, merge to main (if promoting) or close the branch (if rejecting). Do not let experiment branches accumulate.

---

## Model Card as the PR Description

Any PR that promotes a model to `Production` must include the model card as the PR description body. This is not optional. It is the artifact that justifies the promotion.

**Model card template for PR description**:

```markdown
## Model Card: {model_name} v{version}

### Training Data
- Source: {data source, e.g., "churn_features table, 2024-01-01 to 2024-12-31"}
- Size: {N rows, M features}
- Data hash: {md5 hash from MLflow run tags}

### Evaluation Metrics
| Metric | Value | Threshold | Pass? |
|--------|-------|-----------|-------|
| val_auc | 0.83 | 0.75 | ✅ |
| val_f1 | 0.71 | 0.65 | ✅ |

### MLflow Run
- Experiment: {experiment name}
- Run ID: {run_id}
- Git commit: {sha}

### Known Limitations
- {e.g., "Underperforms on customers with tenure < 30 days (n=150 in validation set)"}
- {e.g., "Not validated on international customers"}

### Intended Use
- {e.g., "30-day churn probability score for the retention marketing campaign trigger"}
- Not intended for: {e.g., "Real-time in-product scoring; latency SLA is 500ms not met"}
```

Reviewers who approve a model promotion PR are signing off on the model card, not just the code diff.

---

## Retraining Cadence

Production models degrade. Retraining is not a one-time event — it is a maintenance rhythm.

**Default cadences**:
| Use case | Cadence | Trigger |
|----------|---------|---------|
| Batch scoring (weekly report) | Weekly | Scheduled Prefect flow |
| Real-time serving (product feature) | Monthly | Drift detection alert |
| High-stakes decision (fraud, credit) | Weekly | Scheduled + drift |
| Rapidly-changing domain (news, social) | Daily | Drift only |

**Drift-triggered retraining**:
1. Serving layer logs input feature distributions to MLflow (or a metrics store)
2. A monitoring job computes PSI (Population Stability Index) or KL divergence daily
3. If PSI > 0.2 on any key feature, a Prefect flow triggers a retraining run
4. If the new model passes all gates, it is promoted to `Staging` automatically
5. A human promotes `Staging` → `Production` (or CI does it if all smoke tests pass)

**Never retrain silently**: every retraining run must produce an MLflow run with a `triggered_by` tag (`"scheduled"`, `"drift_alert"`, `"manual"`). Silent retraining is a reproducibility failure.

---

## Rollback Procedure

When a production model causes a regression (predictions change, latency spikes, error rate increases):

**Step 1 — Identify the previous Production version**:
```python
from mlflow.tracking import MlflowClient
client = MlflowClient()
versions = client.search_model_versions(f"name='{MODEL_NAME}'")
# Find the version that was Production before the current one
```

**Step 2 — Archive the bad version, promote the previous one**:
```python
# Archive the broken current Production version
client.transition_model_version_stage(
    name=MODEL_NAME,
    version=bad_version,
    stage="Archived",
    archive_existing_versions=False,
)
# Promote the previous version back to Production
client.transition_model_version_stage(
    name=MODEL_NAME,
    version=previous_version,
    stage="Production",
    archive_existing_versions=False,
)
```

**Step 3 — Restart the serving layer** (it loads from registry at startup):
```bash
# Kubernetes: rolling restart picks up the new Production version
kubectl rollout restart deployment/{serving-deployment}
# Docker: restart the serving container
docker restart {serving-container}
```

**Step 4 — Verify**: hit `/health` to confirm the rollback version is loaded. Run the serving smoke test.

**Document the rollback**: create a GitHub issue or incident report with: what version was rolled back, why, what the regression was, what the investigation found.

---

## Data Versioning Strategy

Training data is as important as model code. Without data versioning, you cannot reproduce a training run even if you have the MLflow run metadata.

**Option A — DVC (Data Version Control)**:
- Store large CSVs/Parquet files in S3/GCS, track pointers in git
- `dvc pull` restores the exact data version for a given git commit
- Best for: teams already using git-centric workflows, small-to-medium datasets (< 10GB)

**Option B — Delta Lake Time Travel**:
- If training data lives in Delta Lake (Databricks or open-source), use `VERSION AS OF` or `TIMESTAMP AS OF`
- Log the Delta table version number as an MLflow tag: `mlflow.set_tag("delta_version", "42")`
- Replay: `spark.read.format("delta").option("versionAsOf", "42").load(table_path)`
- Best for: teams on Databricks, large datasets, feature tables managed by a data engineering team

**Option C — Data Hash Only (minimal)**:
- Log the MD5 hash of the training DataFrame as an MLflow tag
- Does not allow replay, but allows detection of data changes
- Best for: prototypes, cost-sensitive teams, when data is immutable (append-only logs)

**The rule**: at minimum, always log `data_hash`. Upgrade to DVC or Delta time-travel when you need replay capability (i.e., when you are in production and reproducibility is a compliance requirement).
