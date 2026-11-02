# Vibe: The Close Lifecycle

## Close calendar, mapped to sessions

Month-end close runs on a calendar. The course pipeline follows it. Business day 0 (BD0) is the last day of the period.

| Day | Close activity | Course phase | Command |
|---|---|---|---|
| BD-3 to BD0 | Agree scope, materiality, owners. Request extracts | Phase 0 Skeleton | `/architect accountant` |
| BD+1 | Extracts land in `data/raw/`. Load and validate | Phase 1 Sources & validation | `/start-session accountant` |
| BD+1 to BD+2 | Bank and sub-ledger reconciliations | Phase 2 Reconciliations | `/acct-reconcile` |
| BD+2 to BD+3 | Flux: budget vs actual, month over month | Phase 3 Flux | `/acct-variance` |
| BD+3 | JE testing for SOX evidence | Phase 4 JE testing | `/acct-je-test` |
| BD+4 to BD+5 | Close memo, open items, review | Phase 5 Close memo | `/acct-close-handoff` |

Each session ends with `/next-session`. It runs the quality gate (tie-out checker, controls checker, raw folder unchanged) and writes the handoff for the next person.

## One workpaper, start to finish

```
1. Plan       docs/close-plan.md: period, accounts, materiality, sources expected
2. Receive    extract saved to data/raw/ (never edited after this)
3. Profile    row count + control total recorded in the plan
4. Build      src/<workpaper>.py, step by step, tests first
5. Run        output/<workpaper>-<period>.md + exception CSVs
6. Tie out    pytest + tie-out-checker agent
7. Review     reviewer reads the report, follows file + row to the source
8. Carry      open items go to the close memo with owner and date
```

## Materiality comes first

State materiality in the plan before any analysis. Two numbers:

- **Overall**: items above this go to the memo individually.
- **Flux threshold**: an amount AND a percent. A line needs an explanation when it crosses both (or either; the plan says which).

If the plan has no materiality, the commands stop and ask. Picking a threshold after seeing the results is how bias gets in.

## Explanations come from people

The assistant can compute a flux, rank lines and draft questions. It cannot know why marketing spend jumped. Flux explanations either:
- cite a source (a contract, a JE description, a sub-ledger detail row), or
- say `OWNER TO EXPLAIN` with the owner role and go to open items.

A plausible story with no source is worse than a blank.

## Rerun beats patch

When a late extract arrives or a JE is reversed:
1. Replace the file in `data/raw/` with the new extract (keep the old one with a date suffix).
2. Rerun the workpaper.
3. Let the tests tell you what moved.

Never fix a number in `output/` by hand. The next rerun would undo it, and the reviewer cannot see why it changed.

## What "done" means for the period

- Every workpaper in the plan has a report in `output/` and passing tie-out tests
- Every unmatched item and exception is either cleared with evidence or on the open items list
- Proposed JEs balance and are marked `PROPOSED - NOT POSTED`
- `data/raw/` is unchanged since it was received
- The close memo is ready for a person to sign
