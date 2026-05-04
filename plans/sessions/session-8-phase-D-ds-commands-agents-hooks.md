# Session 8 — Phase D: Data Scientist Commands, Agents, Scripts, Hooks, MCP, Rule

**Phase:** D (Data Scientist persona pack)
**Goal:** All functional files for data-scientist persona.
**Depends on:** Session 7 (directory scaffold)
**Next session:** Session 9 (python-datascience stack pack)

---

## Files to Create

```
personas/data-scientist/
├── commands/
│   ├── ds-explore.md
│   ├── ds-experiment.md
│   ├── ds-validate.md
│   └── ds-handoff.md
├── agents/
│   ├── data-profiler.md
│   ├── experiment-tracker.md
│   └── reproducibility-checker.md
├── scripts/
│   ├── seed-check.sh
│   ├── notebook-lint.sh
│   └── log-experiment.sh
├── hooks.json
├── mcp.json
└── rules/
    └── 000-ds-workflow.mdc
```

---

## File Specifications

### `commands/ds-explore.md`

**Purpose:** EDA loop — profile dataset, visualize distributions, document hypotheses.

Steps:
1. Ask for dataset path (default: files in `data/`)
2. Delegate to `data-profiler` subagent → statistical profile
3. Generate `docs/eda-{dataset-name}.md` containing:
   - Dataset shape, dtypes, null counts
   - Distribution summaries (mean/median/std for numeric; value counts for categorical)
   - Correlation matrix highlights
   - Outlier flags
   - 3–5 hypotheses to test in experiments
4. Ask user to confirm or revise hypotheses before proceeding to `ds-experiment`

Output: `docs/eda-{dataset}.md` — the experiment plan starts here.

### `commands/ds-experiment.md`

**Purpose:** Run a model experiment with tracked params, metrics, and seed.

Prerequisites: EDA doc exists; random seed defined in session context.

Steps:
1. Read `docs/eda-{dataset}.md` to identify hypothesis being tested
2. Set and log the experiment seed (`random.seed`, `np.random.seed`, `torch.manual_seed`)
3. Define experiment: model type, hyperparams, features, target, train/val split
4. Run experiment (in notebook or `.py` script)
5. Delegate to `experiment-tracker` subagent → log to `docs/experiments/log.md`
6. Output `docs/experiments/{date}-{experiment-name}.md`:
   - Hypothesis tested
   - Seed value
   - Model config (params)
   - Train/val metrics (accuracy, F1, RMSE, etc. — appropriate to task)
   - Artifact paths (saved model, feature importance plot)
   - Next experiment to try

### `commands/ds-validate.md`

**Purpose:** Validate model on held-out data, check for bias and distribution drift.

Prerequisites: A trained model artifact from `ds-experiment`.

Steps:
1. Load model artifact and held-out test set (NOT the validation set used during training)
2. Compute test metrics — compare against val metrics to check for overfitting
3. Run bias check: split metrics by key demographic or categorical columns if present
4. Run distribution check: compare training data distribution vs test data distribution (feature drift)
5. Delegate to `reproducibility-checker` → verify experiment is reproducible from seed
6. Output `docs/validation-{model-name}.md`:
   - Test metrics vs val metrics
   - Bias findings (by subgroup)
   - Drift findings (by feature)
   - Reproducibility: pass/fail
   - Risk summary for model card

### `commands/ds-handoff.md`

**Purpose:** Generate model card + handoff notes for engineering or stakeholders.

Steps:
1. Read `docs/eda-{dataset}.md`, relevant `docs/experiments/` files, `docs/validation-{model}.md`
2. Generate `docs/model-card-{name}.md`:
   - **What it does:** one paragraph, non-technical
   - **What it doesn't do:** explicit limitations
   - **Training data:** source, date range, size, known biases
   - **Performance:** test metrics on representative slice
   - **Fairness:** bias findings from validation
   - **Deployment requirements:** Python version, dependencies, expected input schema, output schema, latency estimate
   - **Retraining triggers:** when to retrain (data drift threshold, performance degradation threshold)
   - **Contacts:** who owns this model
3. Output handoff checklist: model card complete? validation passed? reproducibility confirmed? artifact saved?

### `agents/data-profiler.md`

Frontmatter: `name: data-profiler`, `description: Statistical profile of a dataset`, `model: inherit`, `readonly: true`

Steps: load dataset via filesystem MCP → compute shape + dtypes + null counts + distributions (describe()) + cardinality for categoricals + correlation matrix + outlier flags (IQR method) → save structured profile to `docs/profile-{dataset}.md` → report path + summary.
Does NOT modify dataset.

### `agents/experiment-tracker.md`

Frontmatter: `name: experiment-tracker`, `description: Logs experiment params, metrics, and artifacts`, `model: inherit`, `readonly: false`

Steps: read current experiment results from context → append a structured entry to `docs/experiments/log.md` with timestamp, seed, model config, metrics, artifact paths → report entry appended.
Log format: markdown table with one row per experiment run. Comparable across runs.

### `agents/reproducibility-checker.md`

Frontmatter: `name: reproducibility-checker`, `description: Verifies experiment reproducibility`, `model: inherit`, `readonly: true`

Checks:
- Random seed explicitly set before any random operation (`random.seed`, `np.random.seed`, `torch.manual_seed`, `tf.random.set_seed`)
- `requirements.txt` or `pyproject.toml` exists with pinned versions (no `>=` without upper bound on core libs)
- No absolute file paths (all paths relative or use `pathlib.Path`)
- Notebook: all cells executed in order (execution count sequential from 1)
- No mutable global state modified between cells

Output: pass/fail per check + file+line for each failure.

### `scripts/seed-check.sh`

Reads `file_path`. Fires on `.py` and `.ipynb` only, and only in `notebooks/` directory.
- `.py`: grep for `random.seed\|np.random.seed\|torch.manual_seed\|tf.random.set_seed` — warn if not found
- `.ipynb`: `jq` parse source cells, same grep
Non-blocking (warning to stderr).

### `scripts/notebook-lint.sh`

Reads `file_path`. Fires on `.ipynb` only.
Uses `jq` to:
1. Count total cells: `jq '.cells | length'`
2. Get max execution_count: `jq '[.cells[].execution_count // 0] | max'`
3. Warn if max execution_count < total cells (notebook not run to completion) or if any cell has `null` execution_count mid-notebook

Non-blocking.

### `scripts/log-experiment.sh`

Triggered by `stop`. No file_path.
Prints advisory: "Session ended. Run /ds-handoff or invoke experiment-tracker to log results before your next session."
Non-blocking.

### `hooks.json`

```json
{
  "version": 1,
  "hooks": {
    "afterFileEdit": [
      { "command": ".cursor/scripts/seed-check.sh" },
      { "command": ".cursor/scripts/notebook-lint.sh" }
    ],
    "stop": [
      { "command": ".cursor/scripts/log-experiment.sh" }
    ]
  }
}
```

### `mcp.json`

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "./data"],
      "env": {},
      "_note": "Scoped to local ./data directory. No credentials needed. Override in client-config to add internal data platform MCPs (Snowflake, BigQuery, MLflow, etc.)"
    },
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp@latest"],
      "env": {}
    }
  }
}
```

### `rules/000-ds-workflow.mdc`

Frontmatter: `description: Data scientist persona workflow rules`, `alwaysApply: true`

Sections:
- **Seed discipline is mandatory** — every experiment sets a seed before any random operation; hooks enforce this
- **No raw data in repo** — only paths and hashes; never commit CSVs, Parquets, or database dumps
- **Notebooks run top-to-bottom** — clear all outputs and re-run before handoff; `reproducibility-checker` verifies
- **Experiments are logged** — no experiment result exists only in your memory or a notebook output; `experiment-tracker` writes the log
- **Model card required** — no handoff without a completed model card from `ds-handoff`
- **Subagent delegation:** new dataset → `data-profiler`; experiment complete → `experiment-tracker`; before handoff → `reproducibility-checker`

---

## Acceptance Criteria

- [ ] 4 command files, 3 agent files, 3 script files, 1 rule file
- [ ] `hooks.json` and `mcp.json` parse cleanly
- [ ] `mcp.json` filesystem server scoped to `./data` and has `_note` for client overlay
- [ ] `seed-check.sh` exits 0 on a `.css` file (wrong type — no-op)
- [ ] `notebook-lint.sh` exits 0 on a `.py` file (wrong type — no-op)
- [ ] `notebook-lint.sh` requires `jq` — SETUP.md already lists `jq` as prerequisite (Session 7 ✓)
- [ ] All 4 personas install cleanly and switch cleanly via manifest
