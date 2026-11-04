# Exercise 1: EDA and data quality

**Time:** 60 to 75 minutes
**You produce:** `workspaces/data-scientist/docs/eda/data-quality-findings.md`, one section per issue, each with a count and the row ids. Plus the two `/ds-explore` docs it is built from.

## Scenario

Northwind's finance team wants a model that pre-fills the expense category and flags risky claims. Before anyone trains anything, the Head of Data asks for a data quality report on three months of claims (August to October 2026). The data was exported from the expense app with no cleaning. Somebody has already told you it has duplicates and currency problems. Your job is to find out exactly how many, and which rows, so the next two exercises start from known facts.

## Inputs

Copied into `workspaces/data-scientist/data/` during setup (see the index README):

| File | Use |
|---|---|
| `expense_lines.csv` | 9,176 lines, the main table |
| `expense_claims.csv` | 4,000 claim headers: employee, status, currency, `fx_rate` |
| `employees.csv` | Only needed to join approvers in the stretch |
| `expense_policy.json` | Receipt threshold, category limits, 60-day rule, alcohol |

Column meanings: `exercises/_data/README.md`, section "Column reference". Stop reading that file at "Answer key".

## Task

1. **Profile both tables.** Run `/ds-explore data/expense_lines.csv` and `/ds-explore data/expense_claims.csv`. Approve 3 to 5 hypotheses per table. At least one hypothesis must be about the data, not a model ("some lines are submitted twice on two claims").
2. **Build a USD value per line.** Join each line to its claim and compute `usd_cents = round_half_up(amount_cents x fx_rate)`. Lines on a claim with a blank `fx_rate` get no USD value. Keep this as a tested function (`src/data.py`, an `R/` function, a Silver transform or a staging model), not a notebook cell.
3. **Find every issue in the table below.** Use exactly the definitions given. Write each one into `docs/eda/data-quality-findings.md` with: definition used, count, the ids (line_ids or claim_ids; for pairs list both ids), and one sentence on what it would do to a model or to the GL if nobody fixed it.
4. **Log what you ran.** One row in `experiments/log.md` for the profiling run (seed is not used, write `n/a`; record the data file hashes).

### What to look for

| # | Issue | Definition (use this exactly) |
|---|---|---|
| 1 | Exact duplicates | Same employee (via claim), `merchant`, `expense_date`, `amount_cents` and `currency`, on two different claims. The later `line_id` is the duplicate |
| 2 | Near-duplicates | Same employee, `merchant`, `currency`, on different claims, and either same date with amounts 1 cent apart, or same amount with dates 1 day apart. Report the two kinds separately |
| 3 | Split to dodge the receipt rule | Same employee, `merchant`, `expense_date`: 2 or more lines each between 6000 and 7499 USD cents, summing to more than 7500 |
| 4 | Weekend expenses | `expense_date` is a Saturday or Sunday |
| 5 | Missing category | `category` is blank |
| 6 | Mixed currency without fx | Line `currency` differs from its claim `currency`. Also list the claims whose `fx_rate` is blank |
| 7 | Outlier | Use IQR per category on USD value, then look at the top of each category. Report the extreme one |
| 8 | Alcohol | `description` mentions wine, beer, cocktail(s), bar tab, brewery or whiskey (case-insensitive) |
| 9 | Over policy limit | Meals: sum of USD per employee per date above 7500 x `attendees_count` (blank means 1). Lodging above 30000 per line. Office supplies above 50000 per line |
| 10 | Missing receipt over $75 | USD value above 7500 and `receipt_attached` is false |
| 11 | Older than 60 days | Claim `submitted_at` date minus `expense_date` is more than 60 days |
| 12 | Suspicious column | One column carries the same information as `category`. Find it and show why (a crosstab is enough) |

## Done when

- [ ] `docs/eda/expense_lines.md` and `docs/eda/expense_claims.md` exist (from `/ds-explore`) with approved hypotheses
- [ ] `docs/eda/data-quality-findings.md` has all 12 issues, each with a count and ids
- [ ] Every count matches `checks/expected_findings.md` (open it only after step 3)
- [ ] The USD conversion function has at least 3 tests: a USD line, a non-USD line with rounding half up, a blank `fx_rate`
- [ ] `experiments/log.md` has a row for this run
- [ ] Nothing under `data/` is staged in git

## Commands to use

```
/architect data-scientist exercises/data-scientist/01-eda-data-quality/README.md
/start-session data-scientist
/ds-explore data/expense_lines.csv
/ds-explore data/expense_claims.csv
/next-session
```

- `/architect` turns this README into an experiment plan. Check that the plan lists all 12 issues before you approve it.
- `/ds-explore` calls the `data-profiler` agent. Its outlier section uses 1.5 x IQR on raw columns; that flags 836 rows on `amount_cents` because categories have very different scales. Ask for IQR per category on USD value instead.
- Ask the agent to print the count for each issue before writing the doc, then read the ids yourself for the small sets.

## Stretch

- Claims level: how many claims carry at least one exact or near-duplicate line (count the later line of each pair)?
- Approvals: find claims where `approver_id` equals `employee_id`, and claims whose USD total is above the approver's `approval_limit_cents`. You will need these in exercise 3.
- What would the 8 missing-category lines most likely be? Write your guess per line from merchant and description. Exercise 2 checks your guess with a model.

## Per stack notes

| Stack | How to do this exercise |
|---|---|
| python-datascience | `notebooks/01_eda.ipynb` for profiling, `src/data.py` for `usd_cents()` and the issue finders, pytest for both. Read CSVs with `dtype=str, keep_default_na=False` so blank `fx_rate` and `category` stay blank, then cast. Use `decimal.Decimal` with `ROUND_HALF_UP`; plain `round()` rounds half to even. (No line in this dataset lands on exactly half a cent, so the counts do not change, but the policy says half up and your test should prove it) |
| python-mlops | Same finders in `src/quality.py`, a `quality` CLI step that writes the findings doc and logs file hashes to MLflow as params |
| python-spark | Bronze: read CSVs as strings. Silver: cast, join claims, compute `usd_cents` with `DecimalType(18,4)` and `F.round` (HALF_UP). Gold: one DataFrame per issue. Pairs need a self-join on employee + merchant + currency with `claim_id` different and `line_id` ordered, to avoid counting each pair twice |
| python-dbt-snowflake | `stg_expense_lines`, `stg_expense_claims`, `int_lines_usd` (cast `fx_rate` to `DECIMAL(10,4)`, not a float, then `round()`; on positive amounts that is half up). One `tests/assert_<issue>.sql` per issue returning the offending rows; `dbt test` failure counts are your counts. Local run: `dbt-duckdb` adapter |
| r-tidyverse | `analysis/01_eda.qmd`, functions in `R/quality.R`, tests in `tests/testthat/`. `read_csv(col_types = cols(.default = "c"))` then convert. `round()` in R is half to even, so write `floor(x + 0.5)` for positive cents. `lubridate::wday(date, week_start = 1) >= 6` for weekends |
