---
description: Reconcile a GL account to a bank statement or sub-ledger. Match line by line, list every unmatched item, prove the difference is zero.
---

# /acct-reconcile

Match bank (or sub-ledger) lines to GL lines and list every unmatched item.

```
/acct-reconcile <account> <period>
/acct-reconcile 1010 2026-10
```

## Inputs

| Input | Where | Required |
|---|---|---|
| GL extract (journal lines or account detail) | `data/raw/` | yes |
| Bank statement or sub-ledger detail | `data/raw/` | yes |
| Opening and closing balances for both sides | `data/raw/` | yes |
| Materiality threshold | `plans/interface-contract.md` or `docs/close-plan.md` | yes. Stop and ask if missing |
| Match key and timing window | plan, else default: reference + amount; 3 days | no |

## Steps

1. **Read the plan.** Confirm account, period and materiality. If materiality is not stated, stop and ask.
2. **Profile the sources.** For each file: row count, total in cents, date range. Write them to the top of the report as control totals.
3. **Validate.** Every JE balances (debits = credits). Opening + activity = closing on each side. If either fails, stop and report the failing JE IDs or the gap. Do not reconcile bad data.
4. **Match, pass 1.** One-to-one on reference + amount in cents. The nth item on one side pairs with the nth on the other, so duplicates surface.
5. **Match, pass 2 (optional).** Amount + date within the timing window, for items with no reference. Suggest only; do not auto-clear many-to-one matches.
6. **Classify every unmatched item.** Deposit in transit, outstanding payment, bank item not booked, bank fee not booked, duplicate GL entry, or investigate. Flag items above materiality.
7. **Build the reconciliation.** Adjusted bank balance vs adjusted book balance. Each line cites a file and row or shows its formula.
8. **Propose entries** for book-side items only (unbooked fees, duplicate reversals). Debits = credits. Mark `PROPOSED - NOT POSTED`.
9. **Write tie-out tests** in `tests/test_recon_<account>.py`: matched + unmatched = source (count and cents), every unmatched row listed, difference is zero. Run `pytest -q tests/`.
10. **Call the `tie-out-checker` agent** on the new outputs. Fix every FAIL before you report done.

Use `templates/recon-template.md` for the report layout and `examples/bank-rec/` as the reference implementation.

## Outputs (in `output/`)

| File | Contents |
|---|---|
| `recon-<account>-<period>.md` | Reconciliation, tie-out table, unmatched list, proposed entries |
| `unmatched-<account>-<period>.csv` | Every unmatched item: side, category, ID, date, amount, above materiality, `source_file`, `source_row` |
| `matched-<account>-<period>.csv` | Each matched pair with both source rows |
| `proposed_je_<period>.csv` | Draft adjusting entries, not posted |

## Agent

`tie-out-checker` (required before done).

## Done when

- Difference is 0.00, or equals the listed reconciling items
- Every unmatched source row appears in the unmatched CSV
- `pytest -q tests/` passes and `tie-out-checker` reports PASS
- `git status data/raw/` is clean
