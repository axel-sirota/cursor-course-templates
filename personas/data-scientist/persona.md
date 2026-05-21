# Data Scientist Persona

## First 5 minutes

You have three possible starting points. Pick the one that matches what you have right now.

**(a) I have a CSV / dataset in `data/`**
```
/ds-explore data/my_dataset.csv
```
Expect: `docs/eda/{dataset}-profile.md` with shape, dtypes, distributions, missing values, correlations, and 2-3 documented hypotheses.

**(b) I have an existing notebook**
Open it in JupyterLab. Open Claude Code side-by-side. Ask: "Read `notebooks/foo.ipynb` and tell me what's reproducible vs what needs fixing." Claude reads the file; you re-run cells to verify.

**(c) I have a trained model**
```
/ds-validate models/my_model.pkl
```
Expect: validation report covering held-out performance, bias slices, distribution drift, and reproducibility checks.

If you are starting completely from scratch (no data yet), run `/setup-stack python-datascience` first to scaffold `notebooks/`, `data/`, `models/`, `docs/`.

## Platform gotchas

- **Claude Code is file-level. It does NOT see your live kernel state, in-memory DataFrames, or current variables.** If a notebook ran successfully in your kernel but the cells aren't ordered correctly on disk, Claude only sees what's on disk. Re-run top-to-bottom before asking Claude to reason about results.
- **Use Jupyter MCP for `.ipynb` edits when available.** The built-in `NotebookEdit` tool has formatting quirks. Our pack ships `filesystem` + `context7`; adding Jupyter MCP is a recommended follow-up.
- **No raw data in chat.** Don't paste a 10k-row DataFrame into the prompt. Save a `.head(20)` to a file, ask Claude to read the file.
- **Reproducibility is the deliverable, not a chore.** Every experiment must set seeds (`random`, `numpy`, `torch`/`tf`). The `seed-check` hook enforces this on file edit.

## What this pack does NOT do

- It does NOT train models for you. You run cells; Claude edits scripts.
- It does NOT see your live kernel or notebook outputs unless they're saved to disk.
- It does NOT replace your experiment tracker (MLflow, W&B). It writes a local log (`docs/experiments/log.md`); push to your tracker yourself.
- It does NOT commit raw datasets. Paths and content hashes only.

## What `/architect` produces for this persona

Run `/architect` after `/set-persona data-scientist` + `/setup-stack python-datascience`. Output is NOT a code skeleton — it's an **experiment plan**:

- `plans/interface-contract.md` — data sources, EDA hypotheses, candidate models, success metrics, validation approach
- `plans/sessions/session-1-phase-0.md` — EDA notebook scaffold (load → profile → visualize → hypothesize)
- `plans/sessions/session-N-phase-X.md` — one per modeling phase (baseline → tuned → validated)

You then run `/start-session` to execute one session at a time. Each session ends with results logged to `docs/experiments/log.md`.

---

## Mental Model

You ship reproducible experiments. Your unit of delivery is a notebook or pipeline run that is documented, reproducible from a seed, and accompanied by a model card or findings doc that engineering can act on.

## Vocabulary

- **Dataset** — The raw or processed data used for training, validation, or analysis.
- **EDA** — Exploratory Data Analysis: profiling distributions, correlations, and anomalies before modeling.
- **Experiment** — A single reproducible run: a defined seed, model config, features, and logged metrics.
- **Seed** — The random seed that makes an experiment reproducible. Setting it is non-negotiable.
- **Model card** — A structured document describing what a model does, what it doesn't do, its performance, and its deployment requirements.
- **Validation** — Testing a trained model on held-out data, including bias and distribution drift checks.
- **Handoff** — A completed model card + validation report delivered to engineering or stakeholders.

## Workflow Phases

1. **Discover** — Understand the problem, the data sources, and the success criteria.
2. **Explore** — Run `/ds-explore` to profile the dataset and document hypotheses.
3. **Experiment** — Run `/ds-experiment` to train, track, and log model runs with seeds and metrics.
4. **Validate** — Run `/ds-validate` to check performance on held-out data, detect bias, and confirm reproducibility.
5. **Handoff** — Run `/ds-handoff` to produce the model card and delivery checklist.

## Key Rules

- **Every experiment sets a random seed** — `random.seed()`, `np.random.seed()`, `torch.manual_seed()`, `tf.random.set_seed()` before any random operation. The `seed-check` hook enforces this.
- **No raw data committed** — Only data paths and content hashes enter the repository. Never commit CSVs, Parquets, or database dumps.
- **Notebooks run top-to-bottom without errors** — Clear all outputs and re-run before handoff. The `reproducibility-checker` agent verifies this.
- **Every model decision is documented in a model card** — No handoff without a completed model card from `/ds-handoff`.
- **Experiments are logged** — No experiment result exists only in your memory or a notebook output. `experiment-tracker` writes the log with params, metrics, and artifact paths.

## Active Stack

Set by `/setup-stack python-datascience` after `/set-persona data-scientist` completes. Until then, this persona is incomplete.
Run `/setup-stack python-datascience` to activate the notebook-first rules and DS-specific context.

## Smallest valuable loop

`/ds-explore data/your.csv` → read `docs/eda/your-profile.md` → document one hypothesis → done.
