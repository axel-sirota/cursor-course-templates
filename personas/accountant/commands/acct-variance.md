---
description: Flux analysis. Budget vs actual and month over month by account, flag lines over the materiality threshold, collect explanations with sources.
---

# /acct-variance

Budget vs actual and month over month flux, with explanations that cite a source or name an owner.

```
/acct-variance <period>
/acct-variance 2026-10
```

## Inputs

| Input | Where | Required |
|---|---|---|
| Trial balance, current period | `data/raw/` | yes |
| Trial balance, prior period | `data/raw/` | for month over month |
| Budget by account for the period | `data/raw/` | for budget vs actual |
| Flux threshold: an amount AND a percent, plus "both" or "either" | plan | yes. Stop and ask if missing |
| Supporting detail (GL lines, sub-ledger) for drill-down | `data/raw/` | no |

## Steps

1. **Read the plan.** Confirm period and thresholds. If the flux threshold is missing, stop and ask.
2. **Validate each trial balance.** Debits = credits. Row counts and totals recorded as control totals. Account numbers read as strings.
3. **Align accounts.** Outer join current, prior and budget on account number. List accounts that appear on one side only. Never drop them.
4. **Compute flux in cents.** For each account: change = current - comparison; change % = change / |comparison| (show `n/a` when comparison is 0). Keep both comparisons in separate columns.
5. **Flag lines** that cross the threshold rule from the plan.
6. **Drill down** on each flagged line, if GL detail exists: top 5 lines by absolute amount driving the change, each with file and row.
7. **Explanations.** For each flagged line, write an explanation only if a source supports it (a JE description, a detail row, a contract in `docs/`). Otherwise write `OWNER TO EXPLAIN` and the owner role. Never invent a business reason.
8. **Write tie-out tests** in `tests/test_flux.py`: each TB balances, sum of account lines = TB total for each column, flagged set equals the threshold rule applied to the data. Run `pytest -q tests/`.
9. **Call the `tie-out-checker` agent** on the flux outputs.

## Outputs (in `output/`)

| File | Contents |
|---|---|
| `flux-<period>.md` | Threshold rule, summary, flagged lines with change, change %, drivers, explanation or `OWNER TO EXPLAIN`, source |
| `flux-<period>.csv` | Every account: current, prior, budget, both changes in cents, flags, source rows |
| `flux-questions-<period>.md` | One question per unexplained flagged line, addressed to the owner role |

## Agent

`tie-out-checker` (required before done).

## Done when

- Column totals in the CSV equal the TB totals
- Every flagged line has a sourced explanation or an `OWNER TO EXPLAIN` flag
- `pytest -q tests/` passes and `tie-out-checker` reports PASS
