# Project Context: Python Accounting (Close Workbook)

## Architecture Shape
Close Workbook (Sources → Validate → Reconcile / Analyse → Tie-out → Report)
Not an HTTP service and not a notebook. The deliverable is a set of reports in `output/` where every number ties back to a source file and row, plus pytest tie-out tests that prove it.
Each step is a plain Python function that takes and returns DataFrames. Steps run in order from one entry script per workpaper (`src/<workpaper>.py`).

## Tech Stack
- **Language**: Python 3.11+
- **Data**: pandas 2.x (2.3.3 pinned in the example), numpy 2.x
- **Excel in/out**: openpyxl 3.1.x (read `.xlsx` sources, write `.xlsx` workpapers when a reviewer wants Excel)
- **Testing**: pytest 8.x (tie-out tests)
- **Schema checks (optional)**: pandera 0.2x for column and dtype contracts on source files
- **Environment**: `uv` or `python -m venv`; dependencies pinned in `requirements.txt`
- **No database, no web framework, no ERP connection.** Sources are CSV or XLSX extracts placed in `data/raw/`.

## Vibe & Style
- **Coding style**: snake_case, PEP 8, type hints on every step function
- **Money**: integer cents (`int64`) or `decimal.Decimal`. Never float for amounts. Never compare floats for equality
- **Dates**: ISO 8601 (`2026-10-31`). Parse with an explicit format string
- **Dtypes**: read every source with `dtype=str`, then convert column by column. Account numbers stay strings (leading zeros matter)
- **Traceability**: every row loaded carries `source_file` and `source_row`. Every row written keeps them
- **Settings**: period, materiality threshold, account numbers and tolerances live in one config block or `config.yaml`. No amounts hardcoded in logic
- **Proposed entries are proposals**: output files mark them `PROPOSED - NOT POSTED`

## Key Rules
- `data/raw/` is read-only. Work copies go to `data/interim/`, results to `output/`
- Every number in a report cites its source file and row, or shows the formula that produced it
- Debits equal credits in every JE you read and every JE you propose
- Control totals (row count + amount) are recorded at load time and re-checked at the end
- Every unmatched or excepted item is listed. Nothing is netted away silently
- The materiality threshold is stated in the plan before analysis starts
- No personal data (employee names, emails, bank account numbers) in prompts, logs or reports. Use IDs
- Synthetic data only in this course (Northwind Co.)

## Workspace Layout
Paths are relative to the persona workspace (`workspaces/accountant/`).
```
data/raw/          ← source extracts, read-only (GL, bank, TB, JE detail, approval limits)
data/interim/      ← cleaned or reshaped copies (gitignored)
src/               ← one module per workpaper: load, validate, reconcile / analyse, tie-out, report
tests/             ← pytest tie-out tests, one file per workpaper
output/            ← reports, exception lists, proposed JEs, close memo
docs/              ← close plan, materiality memo, vibe docs, review notes
plans/             ← /architect session plans and transitions
```
- **Entry point**: `python src/<workpaper>.py` (for example `src/bank_rec.py`, `src/flux.py`, `src/je_test.py`)
- **Test command**: `pytest -q tests/`
- **Example**: `examples/bank-rec/` is a complete, passing workpaper to copy from

## Active Phase
- Current: Phase 0 (Skeleton)
- Phases: 0 Skeleton → 1 Sources & validation → 2 Reconciliations → 3 Flux analysis → 4 JE testing → 5 Close memo

## Active Persona
- (set by /set-persona)
