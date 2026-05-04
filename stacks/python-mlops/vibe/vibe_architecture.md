# Architecture Vibe: Python MLOps

This document answers the "which tool?" and "which pattern?" questions that come up repeatedly in ML engineering. Use it to make technology decisions confidently and explain them to stakeholders.

---

## When MLOps over a Datascience Notebook

**Notebook rule**: "You're done when it works once."
**MLOps rule**: "You're done when it ships, stays shipped, and can be fixed when it breaks."

Use a notebook (python-datascience stack) when:
- You are exploring data or testing a hypothesis
- The output is a report, a chart, or a one-time analysis
- You need to move fast and the model will not be used in production
- The audience is a stakeholder, not a system

Use an MLOps pipeline (this stack) when:
- The model will make predictions in a product or automated workflow
- You need to retrain the model on a schedule or in response to drift
- Multiple people will work on the model over time
- You need to roll back to a previous version if something breaks
- You need an audit trail: who trained what, on what data, with what results

**The trap**: teams build a notebook that "works", copy it into a script, and call it production. This skips the registry, skips validation, skips serving isolation, and skips reproducibility. Two months later, nobody can reproduce the model or explain why predictions changed. MLOps is the discipline that prevents this.

---

## The Three Failure Modes of ML in Production

Understanding these failure modes is why the three-layer architecture exists.

### 1. Model Rot (Data Drift)
The world changes. Customer behavior shifts, upstream data pipelines change schema, a new product feature changes the distribution of inputs. The model was trained on historical data that no longer represents current reality. Predictions silently degrade.

**Prevention**: input schema validation on every request (Pandera on the serving layer). Drift detection on feature distributions. Scheduled retraining. Monitoring on prediction distribution, not just latency/errors.

### 2. Silent Failures (Bad Predictions With No Error)
The model runs. It returns a response. But the prediction is wrong — not because of a bug, but because the model is confidently wrong on out-of-distribution input. No exception is raised. No alert fires. The product just makes bad decisions.

**Prevention**: confidence/probability thresholds (if `prob < 0.6`, return "uncertain" not a hard prediction). Hold-out evaluation tests that fail if model regresses below baseline. Serving smoke tests after every model promotion.

### 3. Reproducibility Failures (Can't Retrain the Same Model)
Six months later, you need to retrain. The data is gone, the environment has changed, the hyperparameters were never written down. The "production" model lives in a pickle file on someone's laptop. You cannot reproduce it, you cannot understand it, and you cannot improve it without starting from scratch.

**Prevention**: log everything to MLflow — params, data hash, metrics, artifacts, git commit, environment. The MLflow run is the single source of truth. A model must be reproducible from its run metadata alone.

---

## MLflow vs Alternatives

| | MLflow | Weights & Biases | Neptune | Comet ML |
|---|---|---|---|---|
| Open-source | Yes (Apache 2.0) | No (SaaS-first) | No (SaaS-first) | No (SaaS-first) |
| Self-hosted | Yes | Limited | Limited | Limited |
| Databricks native | Yes (managed) | No | No | No |
| Model registry | Yes | Yes | Yes | Yes |
| Cost (team of 5) | Free (self-hosted) | ~$500/mo | ~$400/mo | ~$300/mo |
| Serving integration | pyfunc (flexible) | Partial | Partial | Partial |

**When MLflow wins**:
- You are on Databricks (MLflow is native, Unity Catalog as registry)
- You need self-hosted for security/compliance (no data leaves your VPC)
- Cost sensitivity (open-source, no per-seat pricing)
- You want a vendor-neutral format (MLflow model format is the closest thing to a standard)

**When W&B wins**:
- Deep learning teams with heavy experiment visualization needs (W&B's UI is excellent for comparing dozens of runs visually)
- Teams already paying for W&B enterprise

**The rule for this stack**: default to MLflow. It is the only tracking tool with first-class Databricks integration, the most flexible pyfunc serving interface, and zero cost on self-hosted.

---

## Training/Serving Split: Why You Never Import Training Code in Serving

This is the most violated rule in ML engineering. Here is why it matters.

**The temptation**: the serving code and the training code both need the feature engineering logic. It seems DRY to import `features.py` in both places.

**The problem**:
1. Training deps (scikit-learn, xgboost, pandas with training extras) bloat the serving image by hundreds of MB.
2. A change to `features.py` for a new training experiment breaks the currently-deployed serving layer — they are coupled.
3. The serving layer should be frozen at "what the registered model expects" — not at "what the latest training code produces".

**The solution**: the MLflow model artifact contains everything the serving layer needs. The model was logged with `input_example` and a `ModelSignature` — the registry knows what input schema is expected. The serving layer validates against that schema, not against training-time Pandera schemas.

Feature engineering for serving lives in the model artifact (as a pipeline step or preprocessing wrapper), not in a shared `features.py`. If you use `sklearn.Pipeline`, the whole pipeline is the artifact.

---

## Model Registry as the Contract

The MLflow model registry is the handoff point between two roles that may be different people:

- **Data Scientist**: trains the model, evaluates it, registers it as `Staging`
- **ML Platform Engineer / MLOps**: promotes `Staging` → `Production` after smoke tests pass, manages the serving infrastructure

The registry enforces this contract:
- The data scientist does not need access to the serving infrastructure
- The platform engineer does not need to understand the training code
- If a model is in `Production`, it passed all gates — there is a documented audit trail

**Model stages**:
- `None`: just registered, not yet evaluated
- `Staging`: passed eval gate, available for smoke testing
- `Production`: promoted by ML engineer after smoke tests pass
- `Archived`: previous production version, kept for rollback

Never skip stages. Never manually set `Production` from a notebook. The registry is a quality gate, not a file store.

---

## Databricks-Managed MLflow vs Local MLflow

### Use Local MLflow (SQLite or PostgreSQL tracking server) when:
- Solo data scientist or team of 1–2
- Startup, cost-sensitive, or no Databricks contract
- Data stays on-prem and you cannot use cloud storage for artifacts
- Prototype phase — you will revisit infrastructure when the model proves its value

Setup: `MLFLOW_TRACKING_URI=sqlite:///mlruns.db` or run `mlflow server --host 0.0.0.0 --port 5000`

### Use Databricks-Managed MLflow when:
- Team of 3+ data scientists sharing experiments
- Already paying for Databricks (MLflow tracking is included)
- You want Unity Catalog as the model registry (governance, access control, lineage)
- Budget > $5k/month on Databricks compute (the incremental cost of managed tracking is zero)

Setup: `MLFLOW_TRACKING_URI=databricks`, set `DATABRICKS_HOST` and `DATABRICKS_TOKEN` env vars.

**The cost trap**: Databricks-managed MLflow has no per-seat cost, but storing large model artifacts in Databricks-managed object storage adds to your cloud bill. For teams training large models frequently, audit artifact storage costs quarterly.
