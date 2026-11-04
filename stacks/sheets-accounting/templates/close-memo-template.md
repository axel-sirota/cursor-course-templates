# Close memo: <entity>, period <YYYY-MM>

> Synthetic data for training. Prepared with AI assistance. Every number below traces to a working paper in `working/`.

| Field | Value |
|---|---|
| Entity | <entity> |
| Period | <YYYY-MM-01> to <YYYY-MM-DD> |
| Materiality | <amount> overall; flux threshold more than <amount> AND more than <percent> |
| Prepared by (role) | <Staff Accountant> |
| Reviewed by (role) | <Accounting Manager> |
| Status | Draft / Ready for review / Reviewed |

## 1. Summary

<Three to five sentences. What closed, what ties, what is still open. Facts and amounts only.>

## 2. Reconciliations

| Account | Balance per GL | Balance per source | Adjusted difference | Reconciling items | Status | Working paper |
|---|---:|---:|---:|---:|---|---|
| <1010 Operating Cash> | | | 0.00 | <count> | Tied | working/recon-1010-<period>.csv |

## 3. Accrual tie-outs

| Account | Expected (from sub-ledger) | GL balance | Gap | Explained by | Unexplained | Working paper |
|---|---:|---:|---:|---|---:|---|

## 4. Flux

Threshold: more than <amount> AND more than <percent>, vs budget and vs prior month.

| Account | Actual | Budget | Change vs budget | % | Explanation | Source |
|---|---:|---:|---:|---:|---|---|

Accounts over threshold with no explanation: <count>. Listed in open items as `OWNER TO EXPLAIN`.

## 5. JE testing

Population: <entries> entries, <lines> lines, total debits <amount> (working/je-test-<period>.csv tie-out rows).

| Test | Basis | Exceptions | Cleared | Open |
|---|---|---:|---:|---:|
| Weekend or holiday posting | <policy> | | | |
| Preparer outside Finance | <policy> | | | |
| Entered after close | <policy> | | | |
| Round amounts | <rule> | | | |
| Just under approval limit | <policy> | | | |
| Seldom-used accounts | <rule> | | | |
| Self-approved | <policy> | | | |
| Duplicates | <rule> | | | |
| Intercompany without offset | <policy> | | | |

## 6. Proposed adjusting entries (PROPOSED - NOT POSTED)

| Proposed JE | Account | Debit | Credit | Reason | Working paper row |
|---|---|---:|---:|---|---|

Total debits = total credits: <amount> = <amount>.

## 7. Open items

| # | Item | Amount | Owner (role) | Due | Working paper |
|---|---|---:|---|---|---|

## 8. Tie-out evidence

| Check | Result | Evidence |
|---|---|---|
| Every `TIE-OUT` row in `working/` is 0.00 | PASS / FAIL | <papers and rows checked> |
| tie-out-checker agent | PASS / FAIL | <summary line> |
| controls-checker agent (JE testing) | PASS / FAIL | <summary line> |
| `data/raw/` unchanged | PASS / FAIL | <how checked> |
| pii-redactor agent | PASS / FAIL | <files scanned> |

## 9. Sign-off

Left blank on purpose. A person signs, not the assistant.

| Role | Name | Date |
|---|---|---|
| Preparer | | |
| Reviewer | | |
