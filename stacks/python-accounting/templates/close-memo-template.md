# Close memo: Northwind Co., period <YYYY-MM>

> Synthetic data for training. Prepared with AI assistance; every number below traces to a workpaper in `output/`.

| Field | Value |
|---|---|
| Entity | Northwind Co. |
| Period | <YYYY-MM-01> to <YYYY-MM-DD> |
| Materiality | <amount> overall; flux threshold <amount> and <percent> |
| Prepared by (role) | <Staff Accountant> |
| Reviewed by (role) | <Accounting Manager> |
| Status | Draft / Ready for review / Reviewed |

## 1. Summary

<Three to five sentences. What closed, what ties, what is still open. No adjectives, only facts and amounts.>

## 2. Reconciliations

| Account | Balance per GL | Balance per source | Difference | Reconciling items | Status | Workpaper |
|---|---:|---:|---:|---:|---|---|
| 1010 Cash - Operating | | | 0.00 | | Tied | output/recon-1010-<period>.md |

## 3. Flux

| Line | Current | Comparison | Change | Change % | Explanation | Source |
|---|---:|---:|---:|---:|---|---|

Lines over threshold without an explanation: <count>. Listed in open items.

## 4. JE testing

| Test | Population | Exceptions | Cleared | Open | Workpaper |
|---|---:|---:|---:|---:|---|
| Duplicates | | | | | output/je-test-<period>.md |
| Weekend / after-hours | | | | | |
| Round amounts | | | | | |
| Self-approval | | | | | |
| Over approval limit | | | | | |

## 5. Proposed adjusting entries (not posted)

| Proposed JE | Account | Debit | Credit | Reason | Source |
|---|---|---:|---:|---|---|

Total debits = total credits: <amount> = <amount>.

## 6. Open items

| # | Item | Amount | Owner (role) | Due | Workpaper |
|---|---|---:|---|---|---|

## 7. Tie-out evidence

| Check | Result | Evidence |
|---|---|---|
| `pytest -q tests/` | PASS / FAIL | <n passed> |
| tie-out-checker | PASS / FAIL | <summary line> |
| controls-checker | PASS / FAIL | <summary line> |
| `data/raw/` unchanged | PASS / FAIL | `git status data/raw/` clean |
| pii-redactor | PASS / FAIL | <files scanned, redactions made> |

## 8. Sign-off

Left blank on purpose. A person signs, not the assistant.

| Role | Name | Date |
|---|---|---|
| Preparer | | |
| Reviewer | | |
