# Accountant Persona

## First 5 minutes

You have three possible starting points. Pick the one that matches what you have right now. All paths are inside `workspaces/accountant/`.

**(a) I have a bank statement and a GL extract**
```
/acct-reconcile 1010 2026-10
```
Expect: `output/recon-1010-2026-10.md` with adjusted bank vs adjusted book, a difference of 0.00 or a list of reconciling items, and every unmatched item with its file and row.

**(b) I have trial balances and a budget**
```
/acct-variance 2026-10
```
Expect: `output/flux-2026-10.md` with every line over your threshold flagged, top drivers, and an explanation or an `OWNER TO EXPLAIN` flag.

**(c) I have a journal entry extract**
```
/acct-je-test 2026-10
```
Expect: `output/je-test-2026-10.md` and an exceptions CSV covering duplicates, weekend postings, round amounts and self-approval, reviewed by the `controls-checker` agent.

No data yet? Run `/setup-stack accountant`, then open `examples/bank-rec/`. It has a seeded generator for Northwind Co. data and a working reconciliation with passing tie-out tests.

## Platform gotchas

- **Cursor reads files, not your open Excel window.** Save the workbook, or export the sheet to CSV in `data/raw/`. Unsaved changes do not exist for the assistant.
- **pandas reads the last saved values, not formulas.** If a workbook was never recalculated before saving, the numbers can be stale. Recalculate, save, then load.
- **Account numbers lose leading zeros** if read as numbers. `0410` becomes `410`. The stack rules read everything as text first.
- **Dates like 10/11/2026 are ambiguous.** Use ISO dates (`2026-10-11`) or tell the assistant the format.
- **Do not trust arithmetic in a chat reply.** Ask for the number to be computed in code and written to `output/`. The tie-out tests check it.
- **The raw-data hook warns, it does not block.** It fires after the edit. Undo with `git checkout -- <file>`.

## What this pack does NOT do

- It does NOT post journal entries. It writes proposed entries marked `PROPOSED - NOT POSTED`. You book them in the ERP.
- It does NOT connect to an ERP, bank portal or accounting system. Sources are files you place in `data/raw/`.
- It does NOT pick your materiality threshold. You state it in the plan.
- It does NOT invent flux explanations. It drafts questions for the account owner.
- It does NOT sign off. The memo's sign-off block stays blank for a person.
- It does NOT use real data. This course uses synthetic Northwind Co. data only.

## What `/architect` produces for this persona

Run `/architect accountant` after `/set-persona accountant` and `/setup-stack accountant`. The output is a **close plan**, not an app:

- `plans/interface-contract.md`: source files and their columns, reconciliation and analysis steps, output reports, tie-out points, materiality threshold
- `plans/sessions/session-1-phase-0.md`: the skeleton. `src/` step functions returning empty DataFrames, an `output/` folder, pytest tie-out stubs
- `plans/sessions/session-N-phase-X.md`: one per workpaper (reconciliation, flux, JE testing, close memo)

Then `/start-session accountant` works one session at a time. Each session ends with `/next-session`, which runs the quality gate.

---

## Mental Model

You ship workpapers that tie. Your unit of delivery is a report in `output/` where every number traces to a source file and row, with pytest tie-out tests that prove the totals, the balance and the completeness. A reviewer should be able to pick any number and find its source in under a minute.

## Vocabulary

- **GL**: General ledger. The book of record for every account.
- **Sub-ledger**: Detail behind a GL control account (AR, AP, fixed assets).
- **JE**: Journal entry. Debits must equal credits.
- **Reconciliation**: Proving a GL balance agrees with an independent source (bank, sub-ledger), with every difference listed.
- **Tie-out**: Proving a number in a report equals its source, by count and amount.
- **Flux**: Change in a balance between periods, or between actual and budget.
- **Materiality**: The amount above which an item matters to the reader. Stated before analysis.
- **Control total**: Row count and amount total of a source file, recorded at load and re-checked at the end.
- **SOX control**: A documented check, such as approval before posting, tested for evidence.

## Workflow Phases

1. **Plan**: State period, accounts, materiality and expected sources (`/architect accountant`).
2. **Load and validate**: Sources in `data/raw/`, control totals recorded, JEs balance.
3. **Reconcile**: Run `/acct-reconcile` per account.
4. **Analyse**: Run `/acct-variance` for flux.
5. **Test**: Run `/acct-je-test` for SOX JE testing.
6. **Hand off**: Run `/acct-close-handoff` for the close memo and open items.

## Key Rules

- **`data/raw/` is read-only.** The `protect-raw` hook warns on any edit there.
- **Every number cites a source file and row, or shows its formula.** The `tie-out-checker` agent enforces this.
- **No hardcoded amounts.** Thresholds are named settings that cite the plan.
- **Money is integer cents or Decimal.** Never float.
- **No personal data in prompts or logs.** Use user IDs. Run `pii-redactor` before sharing.
- **Materiality is in the plan before any analysis.**

## Active Stack

Set by `/setup-stack accountant` (stack: `python-accounting`). It adds the Close Workbook rules, templates (recon, close memo, phase checklist) and the `examples/bank-rec/` reference.

## Smallest valuable loop

Open `examples/bank-rec/` → run `python src/reconcile.py` and `pytest -q` → read `output/bank_rec_2026-10.md` → find the 35.00 fee in `data/raw/bank_statement_2026-10.csv` row 26 → done.
