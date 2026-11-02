---
description: Write the close memo for the period. Pulls every workpaper in output/, runs the tie-out, controls and PII checks, and lists open items with owners.
---

# /acct-close-handoff

Write the close memo with tie-outs and open items, ready for a person to review and sign.

```
/acct-close-handoff <period>
/acct-close-handoff 2026-10
```

## Inputs

| Input | Where | Required |
|---|---|---|
| Workpapers: recon, flux, JE test reports and CSVs | `output/` | at least one |
| Close plan with materiality and workpaper list | `plans/interface-contract.md` or `docs/close-plan.md` | yes |
| Proposed JEs | `output/proposed_je_<period>.csv` | if any |
| Memo template | `templates/close-memo-template.md` | yes |

## Steps

1. **Inventory.** List every workpaper in the plan and whether its output exists. A missing workpaper becomes an open item. Do not skip it silently.
2. **Run the tests.** `pytest -q tests/`. Record pass/fail counts.
3. **Call the `tie-out-checker` agent** on all of `output/`. Any FAIL goes into the memo's tie-out evidence and open items.
4. **Call the `controls-checker` agent** if a JE test report exists. Carry its findings forward.
5. **Draft the memo** from the template. Copy numbers from the workpapers only, each with its source (`output/<file>`, line or row). No new arithmetic in the memo; if a total is needed, compute it in code and cite the file.
6. **Open items.** Every unmatched item above materiality, every `OWNER TO EXPLAIN` flux line, every uncleared JE exception, every failed check. Each gets an owner role and a due date (ask if unknown).
7. **Proposed entries.** Summarise from the CSV. Show total debits = total credits. Keep `PROPOSED - NOT POSTED`.
8. **Call the `pii-redactor` agent** on the memo. No names, emails or full account numbers.
9. **Check raw data.** `git status data/raw/` must be clean. Record the result.
10. Leave the sign-off block blank. A person signs.

## Outputs (in `output/`)

| File | Contents |
|---|---|
| `close-memo-<period>.md` | Summary, reconciliations, flux, JE testing, proposed entries, open items, tie-out evidence, blank sign-off |
| `open-items-<period>.csv` | Item, amount, owner role, due date, source workpaper |

## Agents

`tie-out-checker`, `controls-checker` (if JE testing ran), `pii-redactor`.

## Done when

- Every workpaper in the plan is in the memo or on the open items list
- Every number in the memo traces to a file in `output/`
- Tie-out evidence table is filled in with real results
- Sign-off block is blank
