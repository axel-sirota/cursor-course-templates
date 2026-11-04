# Data Scientist exercises

Three exercises on one dataset: Northwind Co. expense claims. You profile the data, build a category classifier without falling into a leakage trap, and ship a duplicate and policy detector with measured precision and recall. Every exercise uses the data scientist persona commands, so by the end you have run the full loop: explore, experiment, validate, hand off.

All work happens in YOUR stack's language. The problems and the expected numbers are the same for every stack.

| # | Exercise | Time | You produce |
|---|---|---|---|
| 1 | [EDA and data quality](01-eda-data-quality/README.md) | 60 to 75 min | `docs/eda/data-quality-findings.md`: every seeded issue with its count and ids |
| 2 | [Category model](02-category-model/README.md) | 75 to 90 min | Two baselines, one model, a leakage finding, `docs/validation-category-model.md` |
| 3 | [Duplicate and policy detection](03-duplicate-and-policy-detection/README.md) | 75 to 90 min | A detector, a precision/recall table per rule, `docs/model-card-expense-detector.md` |

Total: about 4 hours. Exercise 1 feeds 2 and 3 (the EDA doc is the input `/ds-experiment` asks for), so do them in order.

## Setup (once, 10 minutes)

```
/set-persona add data-scientist
/setup-stack data-scientist        # pick one: python-datascience (default), python-mlops, python-spark, python-dbt-snowflake, r-tidyverse
```

Copy the data into your workspace. Do not run the generator; the files are already built (seed 2026).

```bash
mkdir -p workspaces/data-scientist/data
cp exercises/_data/northwind/expense_lines.csv \
   exercises/_data/northwind/expense_claims.csv \
   exercises/_data/northwind/employees.csv \
   exercises/_data/northwind/expense_policy.json \
   workspaces/data-scientist/data/
```

Do not commit anything under `data/`. The persona rule is "no raw data committed".

Each exercise then runs the same flow:

```
/architect data-scientist exercises/data-scientist/<exercise>/README.md
/start-session data-scientist
/ds-explore  ->  /ds-experiment  ->  /ds-validate  ->  /ds-handoff     (the ones the exercise asks for)
/next-session
```

`/architect` reads the exercise README as the plan (Plan Extraction Mode). Expect it to write an experiment plan in `plans/` and stub the folders your stack uses.

## The data in one table

| File | Rows | Key columns |
|---|---|---|
| `expense_lines.csv` | 9,176 | `line_id`, `claim_id`, `expense_date`, `merchant`, `merchant_category_text`, `category`, `amount_cents`, `currency`, `receipt_attached`, `description`, `attendees_count`, `gl_account_hint` |
| `expense_claims.csv` | 4,000 | `claim_id`, `employee_id`, `status`, `approver_id`, `total_cents`, `currency`, `fx_rate` |
| `employees.csv` | 120 | `employee_id`, `role`, `manager_id`, `approval_limit_cents` |
| `expense_policy.json` | | Category limits, receipt threshold (7500 cents), 60-day rule, alcohol, approval rules |

Money is integer cents. The USD value of a line is `amount_cents x fx_rate` of its claim, rounded half up to the cent. Every policy limit is on that USD value. Column reference: `exercises/_data/README.md`, section "Column reference". Do not read the answer key sections of that README until you finish.

## Per stack: how you work

| Stack | Where the analysis lives | Tests | Notes |
|---|---|---|---|
| python-datascience (default) | `notebooks/01_eda.ipynb` ... plus `src/data.py`, `src/features.py`, `src/evaluation.py` | `pytest tests/` and `pytest --nbval-lax notebooks/` | pandas + scikit-learn. MLflow local store optional, `experiments/log.md` required |
| python-mlops | `src/` pipeline steps with a CLI entry point, MLflow runs | pytest, mock the MLflow client | Same analysis as scripts, not notebooks. Every run logs dataset hash, params, metrics |
| python-spark | `src/transforms/` pure functions, Bronze (raw CSV) to Silver (typed, USD) to Gold (findings) | chispa + pytest on `data/fixtures/` | Local Spark is fine. Integer cents stay `LongType`; use `DecimalType` for fx math |
| python-dbt-snowflake | `models/staging/` (typed sources), `models/marts/` (findings), `tests/` (one SQL test per rule) | `dbt build` | No Snowflake account? Use the `dbt-duckdb` adapter with the CSVs as seeds or `read_csv_auto` sources. Exercise 2 trains in Python on the mart |
| r-tidyverse | Quarto `analysis/*.qmd`, functions in `R/` | testthat 3rd edition | readr + dplyr + lubridate; tidymodels for exercise 2. `set.seed()` before any random step |

## How it is checked

Each exercise has a `checks/expected_findings.md`. Open it only after you have written your own doc, then compare line by line.

| Exercise | Pass bar |
|---|---|
| 1 | Every issue listed with the right count. Ids match for at least the small sets (missing category, mixed currency, outlier, self-approval, approval above limit) |
| 2 | Split by `claim_id` with zero claims in both sets, fixed seed logged, both baselines logged, model accuracy in the expected band, `gl_account_hint` excluded and the 100% result explained as leakage |
| 3 | Precision and recall per rule against the answer key, every rule at 1.00 / 1.00 after fixes or the gap explained, model card complete |

Instructors: each folder has a `SOLUTION.md` with the exact expected values and the common wrong answers. Every number in them was recomputed from the CSVs.
