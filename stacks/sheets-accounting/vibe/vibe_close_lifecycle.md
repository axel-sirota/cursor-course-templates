# Vibe: The Close Lifecycle (spreadsheet stack)

## Close calendar, mapped to sessions

Business day 0 (BD0) is the last day of the period.

| Day | Close activity | Course phase | Command | Paper |
|---|---|---|---|---|
| BD-3 to BD0 | Agree scope, materiality, owners. Request extracts | Phase 0 Skeleton | `/architect accountant` | `docs/close-plan.md`, empty papers |
| BD+1 | Extracts land in `data/raw/`. Count and total them | Phase 1 Sources | `/start-session accountant` | `working/sources-<period>.csv` |
| BD+1 to BD+2 | Bank and sub-ledger reconciliations | Phase 2 Reconciliations | `/acct-reconcile` | `working/recon-<account>-<period>.csv` |
| BD+2 to BD+3 | Flux: budget vs actual, month over month | Phase 3 Flux | `/acct-variance` | `working/flux-<period>.csv` |
| BD+3 | JE testing for SOX evidence | Phase 4 JE testing | `/acct-je-test` | `working/je-test-<period>.csv` |
| BD+4 to BD+5 | Close memo, open items, review | Phase 5 Close memo | `/acct-close-handoff` | `output/close-memo-<period>.md` |

Each session ends with `/next-session`. It runs the quality gate (tie-out checker, controls checker, raw folder unchanged) and writes the handoff.

## One working paper, start to finish

```
1. Plan       docs/close-plan.md: period, accounts, materiality
2. Receive    extract copied to data/raw/ (never edited after this)
3. Count      rows and control total written to working/sources-<period>.csv
4. Build      the agent writes the paper from its template, every row cited
5. Tie out    filter section = TIE-OUT; every difference is 0.00
6. Check      follow three amounts to their source rows; run tie-out-checker
7. Ask        question anything odd in plain language; the agent answers from rows
8. Carry      open items go to the memo with owner role and due date
```

## Materiality comes first

Two numbers, in the plan, before any analysis:

- **Overall**: items above this go to the memo one by one.
- **Flux threshold**: an amount AND a percent. An account needs an explanation when it crosses both. Accounts that cross only one are classed and noted.

Picking a threshold after seeing the results is how bias gets in.

## Explanations come from people

The agent can compute a flux and match it to a department note. It cannot know why spend moved if nobody said so. Every explanation either cites a source (a note, a contract, a JE description) or reads `OWNER TO EXPLAIN` with the owner's role. A plausible story with no source is worse than a blank.

## Late data

When a late extract arrives:
1. Copy the new file into `data/raw/` with a date suffix. Keep the old one.
2. Ask the agent to rebuild the paper from the new file.
3. Compare the two `TIE-OUT` sections. Ask the agent to list every row that moved.

Never fix a number on a paper by hand. The reviewer cannot see why it changed.

## What "done" means for the period

- Every paper in the plan exists and every `TIE-OUT` row is 0.00
- Every unmatched item and exception is cleared with evidence or on the open items list
- Proposed entries balance and are marked `PROPOSED - NOT POSTED`
- `data/raw/` is unchanged since it was received
- The close memo is ready for a person to sign
