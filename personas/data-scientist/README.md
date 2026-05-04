# Data Scientist Persona Pack

This pack adds data-scientist-specific commands, subagents, hooks, MCP integrations, and rules to the Adaptive SDLC. It is installed by running `/set-persona data-scientist`.

## What this pack adds

**Commands:**
- `/ds-explore` — EDA loop: profile dataset, visualize distributions, document hypotheses
- `/ds-experiment` — Run a model experiment with tracked params, metrics, and seed
- `/ds-validate` — Validate model on held-out data, check for bias and distribution drift
- `/ds-handoff` — Generate model card + handoff notes for engineering or stakeholders

**Subagents:**
- `data-profiler` — Statistical profile of a dataset (shape, dtypes, distributions, correlations, outliers)
- `experiment-tracker` — Logs experiment params, metrics, and artifacts to `docs/experiments/log.md`
- `reproducibility-checker` — Verifies experiment reproducibility (seed, pinned deps, relative paths, execution order)

**Hooks:**
- `afterFileEdit` — Runs `seed-check.sh` and `notebook-lint.sh` on every `.ipynb` or `.py` file edited in `notebooks/`
- `stop` — Runs `log-experiment.sh` to remind you to log results before ending the session

**MCP servers:**
- `filesystem` — Local `data/` directory access. **No credentials required.**
- `context7` — Up-to-date pandas, scikit-learn, and PyTorch documentation. **No credentials required.**

## How this pack pairs with `setup-stack`

After running `/set-persona data-scientist`, run `/setup-stack python-datascience` to activate the notebook-first context and DS-specific rules. Unlike the designer and PM personas, the data scientist persona requires this step because students choose different Python toolchains (sklearn vs pytorch vs statsmodels).

## Default MCPs require NO external credentials

The default configuration works out of the box. The `filesystem` MCP is scoped to the local `./data` directory and needs no authentication. `context7` also requires no credentials for its free tier.

## Client overlay

Your instructor may provide a `client-config/` directory that adds data platform MCPs for internal systems. Common additions include:

- Snowflake (enterprise data warehouse)
- BigQuery (GCP analytics)
- Internal MLflow (experiment tracking server)
- Internal data catalog

These require credentials provided by your instructor. See `.env.example` for where to add them.

## Prerequisites

See `SETUP.md` for the full pre-class checklist.
