# Data Scientist Persona Pack

Runs reproducible experiments in `workspaces/data-scientist/` with seeds, baselines and tracked metrics, on synthetic data.

Install with `/set-persona add data-scientist`, then `/setup-stack data-scientist` → `/architect data-scientist` → `/start-session data-scientist`. All paths below are relative to `workspaces/data-scientist/`.

## What this pack adds

**Commands:**
- `/ds-explore`: EDA loop (profile dataset, summarize distributions, document hypotheses) into `docs/eda/`
- `/ds-experiment`: run a model experiment with tracked params, metrics, and seed
- `/ds-validate`: validate a model on held-out data, check for bias and distribution drift
- `/ds-handoff`: generate model card + handoff notes for engineering or stakeholders

**Subagents:**
- `data-profiler`: statistical profile of a dataset (shape, dtypes, distributions, correlations, outliers)
- `experiment-tracker`: logs experiment params, metrics, and artifacts to `experiments/log.md`
- `reproducibility-checker`: verifies experiment reproducibility (seed, pinned deps, relative paths, execution order)

**Hooks** (installed to `.cursor/scripts/data-scientist/`, scoped to `workspaces/data-scientist/`):
- `afterFileEdit`: `seed-check.sh` (`.py` / `.ipynb` in `notebooks/`) and `notebook-lint.sh` (`.ipynb`)
- `stop`: `log-experiment.sh` reminds you to log results before ending the session

**MCP servers** (no credentials required):
- `data-scientist-data` (filesystem server): read access to `workspaces/data-scientist/data`
- `context7`: up-to-date pandas, scikit-learn, and PyTorch documentation

## How this pack pairs with `/setup-stack`

After `/set-persona add data-scientist`, run `/setup-stack data-scientist` and pick one of: python-datascience (default), python-mlops, python-spark, python-dbt-snowflake, r-tidyverse. Stack rules install into `.cursor/rules/data-scientist/` next to this pack's rules. Both apply only to files in `workspaces/data-scientist/`.

## Prerequisites

See `SETUP.md` for the pre-class checklist.
