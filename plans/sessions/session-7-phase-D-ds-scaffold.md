# Session 7 — Phase D: Data Scientist Persona Scaffold

**Phase:** D (Data Scientist persona pack)
**Goal:** Directory skeleton + persona.md + README + SETUP + .env.example for data-scientist.
**Depends on:** Session 6 complete
**Next session:** Session 8 (DS commands + agents + hooks)

---

## Files to Create

```
personas/data-scientist/
├── persona.md
├── README.md
├── SETUP.md
├── .env.example
├── commands/
├── agents/
├── scripts/
└── rules/
```

---

## File Specifications

### `personas/data-scientist/persona.md`

- **Mental model:** Ship reproducible experiments. Unit of delivery = a notebook or pipeline run that is documented, reproducible from a seed, and accompanied by a model card or findings doc that engineering can act on.
- **Vocabulary:** Dataset / EDA / Experiment / Seed / Model card / Validation / Handoff
- **Workflow phases:** Discover → Explore → Experiment → Validate → Handoff
- **Key rules:**
  - Every experiment sets a random seed — `random.seed()`, `np.random.seed()`, `torch.manual_seed()`
  - No raw data committed — only data paths and content hashes
  - Notebooks run top-to-bottom without errors before handoff
  - Every model decision is documented in a model card
  - Experiments are logged with params, metrics, and artifacts — never just "it worked"
- **Active Stack:** Set by `setup-stack python-datascience` after `set-persona data-scientist`

### `personas/data-scientist/README.md`

- **Commands:** `ds-explore`, `ds-experiment`, `ds-validate`, `ds-handoff`
- **Subagents:** `data-profiler`, `experiment-tracker`, `reproducibility-checker`
- **Hooks:** `afterFileEdit` (.ipynb/.py in notebooks/) → seed-check + notebook-lint; `stop` → log-experiment
- **MCPs:** `filesystem` (local data/ dir, no auth), `context7` (pandas/sklearn/pytorch docs)
- **Why stack needed:** DS students choose Python tools (sklearn vs pytorch vs statsmodels) — `setup-stack python-datascience` provides the notebook-first context and rules
- **Client overlay adds:** Snowflake, internal MLflow, BigQuery, internal data catalog (instructor provides)
- **Prerequisites:** see SETUP.md

### `personas/data-scientist/SETUP.md`

1. AI code assistant
2. Python 3.11+ with pip and venv
3. Jupyter: `pip install jupyterlab notebook`
4. Core DS libraries: `pip install pandas numpy scikit-learn matplotlib seaborn`
5. Optional deep learning: `pip install torch` or `pip install tensorflow`
6. `jq` CLI tool (for notebook-lint.sh hook): `brew install jq` / `apt install jq`
7. Repository access + smoke test: `/set-persona`, pick `data-scientist`, then `/setup-stack python-datascience`

### `personas/data-scientist/.env.example`

```
# Data Scientist Persona — Environment Variables

# filesystem MCP — scoped to local data/ directory (no external service needed)
# No credentials required for default setup.

# Optional: Context7 (no auth needed for free tier)

# Client overlay adds data platform credentials:
# _note: Your instructor provides credentials for internal data platforms
# (e.g., Snowflake, BigQuery, internal MLflow, internal data catalog)
# Add those variables here as instructed.
```

---

## Acceptance Criteria

- [ ] `ls personas/data-scientist/` shows correct structure
- [ ] `persona.md` explicitly states seed discipline and no raw data rules
- [ ] `README.md` clearly states default MCPs require NO external credentials
- [ ] `SETUP.md` includes `jq` installation (required by notebook-lint.sh)
- [ ] `.env.example` makes clear client overlay adds the data platform credentials
- [ ] All 3 existing personas unaffected
