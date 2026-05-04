# Session 9 — Phase E: `stacks/python-datascience/` Stack Pack

**Phase:** E
**Goal:** Create the python-datascience stack pack so DS students have a stack to select after `set-persona data-scientist`.
**Depends on:** Session 8 complete
**Next session:** Session 10 (`set-persona` command)

---

## Files to Create

```
stacks/python-datascience/
├── context.md
├── rules/
│   ├── 000-ds-workflow.mdc
│   └── 100-notebook-standards.mdc
├── templates/
│   └── ds-starter.md
└── vibe/
    └── vibe_ds_workflow.md
```

---

## File Specifications

### `stacks/python-datascience/context.md`

Following the same structure as `stacks/python-fastapi/context.md`:

```markdown
# Project Context: Python Data Science

## Tech Stack
- Language: Python 3.11+
- Notebook: JupyterLab / Jupyter Notebook
- Data manipulation: pandas 2.x, numpy 1.x
- ML: scikit-learn (default), pytorch / tensorflow (optional)
- Visualization: matplotlib, seaborn
- Testing: pytest (pipeline tests), nbval (notebook tests)
- Linting: ruff, nbqa (applies ruff to notebooks)

## Vibe & Style
- Coding Style: snake_case, PEP 8
- Architecture: Notebook-first for exploration; .py modules for reusable pipelines
- Data flow: raw → processed → features → model → evaluation

## Key Rules
- Seed every experiment before any random operation
- No raw data committed — paths and hashes only
- Notebooks run top-to-bottom (clear + re-run before handoff)
- Log every experiment with params, metrics, seed, and artifact paths
- Model card required before handoff

## Active Phase
- Current: Explore (EDA)

## Active Persona
- (set by /set-persona)
```

### `stacks/python-datascience/rules/000-ds-workflow.mdc`

Same content as `personas/data-scientist/rules/000-ds-workflow.mdc`.
(Stack rules and persona rules are both loaded — they can overlap safely because `alwaysApply: true` is idempotent for duplicate content.)

### `stacks/python-datascience/rules/100-notebook-standards.mdc`

Frontmatter: `description: Notebook organization and quality standards`, `alwaysApply: true`

Rules:
- **Cell organization:** imports at top, then config/constants, then data loading, then EDA, then modeling, then evaluation. Use markdown cells as section headers.
- **No global mutable state between cells:** each cell should be independently re-runnable with fresh kernel (test by restarting and running all)
- **Markdown headers required:** every major section starts with a `## Section Name` markdown cell
- **Output discipline:** large outputs (DataFrames, plots) use `.head()` or explicit `display()` — never print 10,000 rows
- **No hardcoded file paths:** use `pathlib.Path` relative to repo root or an env var
- **Reproducibility check before commit:** run `nbval` or re-run from clean kernel to confirm

### `stacks/python-datascience/templates/ds-starter.md`

A notebook starter template in markdown form — explains the structure to paste into a new notebook:

Sections:
1. Setup (imports, seed, paths)
2. Data loading (load from `data/`, print shape + dtypes)
3. EDA (profile, distributions, correlations)
4. Hypothesis (what to test and why)
5. Experiment (model definition, training, logging)
6. Evaluation (metrics, plots)
7. Next steps

### `stacks/python-datascience/vibe/vibe_ds_workflow.md`

The EDA → Experiment → Validate → Handoff guide. Explains:
- Why EDA comes before modeling (avoid wasted experiments)
- How `ds-explore` → `ds-experiment` → `ds-validate` → `ds-handoff` pipelines together
- When to iterate (back to explore) vs when to validate
- What "done" looks like: model card + reproducibility check + engineering handoff doc

---

## Acceptance Criteria

- [ ] `ls stacks/python-datascience/` shows: `context.md`, `rules/`, `templates/`, `vibe/`
- [ ] `context.md` has `## Tech Stack`, `## Key Rules`, `## Active Phase`
- [ ] `cat context.md | grep "Active Phase"` → `Explore (EDA)` (not `Phase 0 (Skeleton)` — DS doesn't use the same phase naming)
- [ ] Running `setup-stack` in Claude Code lists `python-datascience` as an option alongside existing stacks
- [ ] Existing stacks (`python-fastapi`, `node-express`, etc.) unaffected
