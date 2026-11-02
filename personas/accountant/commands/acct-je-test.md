---
description: Journal entry testing for SOX evidence. Duplicates, weekend and after-hours postings, round amounts, self-approval, approval limits. Lists every exception with JE ID and source row.
---

# /acct-je-test

Test journal entries for duplicates, weekend postings, round amounts and self-approval, then hand the results to the controls checker.

```
/acct-je-test <period>
/acct-je-test 2026-10
```

## Inputs

| Input | Where | Required |
|---|---|---|
| JE detail: JE ID, line, account, debit, credit, posting timestamp, preparer ID, approver ID, description | `data/raw/` | yes |
| Approval limits by user ID or role | `data/raw/approval_limits.csv` | for the limit test |
| Business hours and time zone | plan, else default 07:00 to 19:00 local | no |
| Round-amount rule | plan, else default: multiple of 1,000.00 and at least 10,000.00 | no |
| Holiday calendar | `data/raw/` | no |

User fields must be IDs (`USR-014`), not names. If the extract has names or emails, stop and run the `pii-redactor` agent first.

## Steps

1. **Define the population.** Count JEs and lines, total debits and total credits. Record as control totals. The population must tie to the extract.
2. **Validate.** Every JE balances. List any that do not as exceptions; keep going.
3. **Run each test** as its own function, each producing rows with JE ID, test name, detail, `source_file`, `source_row`:

| Test | Rule |
|---|---|
| Duplicates | Same account, amount and date, or same reference and amount, on different JE IDs |
| Weekend postings | Posting date is Saturday or Sunday (or a listed holiday) |
| After-hours postings | Posting time outside business hours |
| Round amounts | Line amount matches the round-amount rule |
| Self-approval | Preparer ID = approver ID |
| Missing approval | Approver ID blank |
| Over approval limit | JE total debits above the approver's limit |
| Unbalanced | Debits not equal to credits for the JE |
| Missing description | Description blank or a placeholder (`adj`, `misc`, `.`) |

4. **Summarise** per test: population, exceptions, percent.
5. **Call the `controls-checker` agent** on the JE detail and the exception list. Add its findings and control references to the report.
6. **Write tie-out tests** in `tests/test_je_test.py`: population totals tie to the extract, each test finds its seeded case, every exception row cites a source row. Run `pytest -q tests/`.
7. **Call the `tie-out-checker` agent**, then the `pii-redactor` agent on every output file that lists user IDs alongside other detail.

## Outputs (in `output/`)

| File | Contents |
|---|---|
| `je-test-<period>.md` | Population, rules used, summary per test, controls-checker findings, exceptions above materiality |
| `je-exceptions-<period>.csv` | Every exception: JE ID, test, detail, amount, preparer ID, approver ID, `source_file`, `source_row` |

## Agents

`controls-checker`, then `tie-out-checker`, then `pii-redactor`.

## Done when

- Population ties to the extract (count, debits, credits)
- Every test ran and its count is in the summary, including zeros
- No names or emails in any output
- `pytest -q tests/` passes
