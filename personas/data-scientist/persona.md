# Data Scientist Persona

All data scientist work lives in `workspaces/data-scientist/`. Paths in this pack are relative to that folder.

## First 5 minutes

```
/set-persona add data-scientist
/setup-stack data-scientist  # python-datascience (default), python-mlops, python-spark, python-dbt-snowflake, r-tidyverse
/architect data-scientist    # experiment plan in plans/, then notebooks/, data/, models/ stubs
/start-session data-scientist
```

Then pick the starting point that matches what you have right now.

**(a) I have a CSV / dataset in `data/`**
```
/ds-explore data/my_dataset.csv
```
Expect: `docs/eda/my_dataset.md` (plus a `-profile.md`) with shape, dtypes, distributions, missing values, correlations, and 3 to 5 documented hypotheses.

**(b) I have an existing notebook**
Open it in JupyterLab with Cursor side by side. Ask: "Read `notebooks/foo.ipynb` and tell me what's reproducible vs what needs fixing." Cursor reads the file; you re-run cells to verify.

**(c) I have a trained model**
```
/ds-validate artifacts/my_model.pkl
```
Expect: `docs/validation-my_model.md` covering held-out performance, bias slices, distribution drift, and reproducibility checks.

End every session with `/next-session`.

## Platform gotchas

- **The AI is file-level. It does NOT see your live kernel state, in-memory DataFrames, or current variables.** If cells ran in your kernel but are out of order on disk, the AI only sees what's on disk. Re-run top-to-bottom before asking it to reason about results.
- **The `data-scientist-data` filesystem MCP is scoped to `workspaces/data-scientist/data`.** Put datasets there. The course uses synthetic data only.
- **No raw data in chat.** Don't paste a 10k-row DataFrame into the prompt. Save a `.head(20)` to a file and ask the AI to read the file.
- **Reproducibility is the deliverable, not a chore.** Every experiment must set seeds (`random`, `numpy`, `torch`/`tf`). The `seed-check` hook warns on edits in `notebooks/`.

## What this pack does NOT do

- It does NOT train models for you. You run cells; the AI edits scripts.
- It does NOT see your live kernel or notebook outputs unless they're saved to disk.
- It does NOT replace your experiment tracker (MLflow, W&B). It writes a local log (`experiments/log.md`); push to your tracker yourself.
- It does NOT commit raw datasets. Paths and content hashes only.

## What `/architect data-scientist` produces

Run `/architect data-scientist` after `/setup-stack data-scientist`. The shape depends on the stack (Experiment Notebook for python-datascience, Data Pipeline, Analytics Model, Statistical Computing). For the default stack the output is an **experiment plan**:

- `plans/interface-contract.md`: data sources, EDA hypotheses, candidate models, success metrics, validation approach
- `plans/sessions/session-1-phase-0.md`: EDA notebook scaffold (load → profile → visualize → hypothesize)
- `plans/sessions/session-N-phase-X.md`: one per modeling phase (baseline → tuned → validated)

You then run `/start-session data-scientist` to execute one session at a time. Each session ends with results logged to `experiments/log.md`.

---

## Mental Model

You ship reproducible experiments. Your unit of delivery is a notebook or pipeline run that is documented, reproducible from a seed, and accompanied by a model card or findings doc that engineering can act on.

## Vocabulary

- **Dataset**: the raw or processed data used for training, validation, or analysis.
- **EDA**: Exploratory Data Analysis, profiling distributions, correlations, and anomalies before modeling.
- **Experiment**: a single reproducible run with a defined seed, model config, features, and logged metrics.
- **Seed**: the random seed that makes an experiment reproducible. Setting it is non-negotiable.
- **Model card**: a structured document describing what a model does, what it doesn't do, its performance, and its deployment requirements.
- **Validation**: testing a trained model on held-out data, including bias and distribution drift checks.
- **Handoff**: a completed model card + validation report delivered to engineering or stakeholders.

## Workflow Phases

1. **Discover**: understand the problem, the data sources, and the success criteria.
2. **Explore**: run `/ds-explore` to profile the dataset and document hypotheses.
3. **Experiment**: run `/ds-experiment` to train, track, and log model runs with seeds and metrics.
4. **Validate**: run `/ds-validate` to check performance on held-out data, detect bias, and confirm reproducibility.
5. **Handoff**: run `/ds-handoff` to produce the model card and delivery checklist.

## Key Rules

- **Every experiment sets a random seed**: `random.seed()`, `np.random.seed()`, `torch.manual_seed()`, `tf.random.set_seed()` before any random operation.
- **No raw data committed**: only data paths and content hashes enter the repository. Never commit CSVs, Parquets, or database dumps.
- **Notebooks run top-to-bottom without errors**: clear all outputs and re-run before handoff. The `reproducibility-checker` agent verifies this.
- **Every model decision is documented in a model card**: no handoff without a completed model card from `/ds-handoff`.
- **Experiments are logged**: no experiment result exists only in your memory or a notebook output. `experiment-tracker` writes the log with params, metrics, and artifact paths.

## Smallest valuable loop

`/ds-explore data/your.csv` → read `docs/eda/your.md` → document one hypothesis → `/next-session`.
