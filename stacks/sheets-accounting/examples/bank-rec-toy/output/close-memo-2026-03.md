# Close memo: Tidewater Tools Co., period 2026-03

> Toy data for training. Prepared with AI assistance. Every number below traces to `working/recon-1010-2026-03.csv`.

| Field | Value |
|---|---|
| Entity | Tidewater Tools Co. (toy) |
| Period | 2026-03-01 to 2026-03-31 |
| Materiality | $500.00 overall |
| Prepared by (role) | Staff Accountant |
| Reviewed by (role) | Accounting Manager |
| Status | Ready for review |

## 1. Summary

Cash 1010 reconciles to the bank statement with a difference of 0.00 after five reconciling items (rows B2, B3, K2, K3, K4). Three adjusting entries are proposed for $37.62 in total debits. Two timing items stay open until the April statement. No item is above materiality.

## 2. Reconciliations

| Account | Balance per GL | Balance per bank | Adjusted difference | Reconciling items | Status | Working paper |
|---|---:|---:|---:|---:|---|---|
| 1010 Operating Cash | $14,637.85 (K1) | $12,874.47 (B1) | 0.00 (T1) | 5 | Tied | working/recon-1010-2026-03.csv |

| Item | Amount | Row | Type |
|---|---:|---|---|
| Deposit in transit RCPT-304 | $2,050.00 | B2 | Timing, clears in April |
| Outstanding check CHK 1003 | (315.00) | B3 | Timing, clears in April |
| Bank fee not booked BKFEE-0327 | (15.00) | K2 | Book side, PJE-01 |
| Interest not booked INT-0331 | $4.62 | K3 | Book side, PJE-02 |
| Keying error INV-4410 (GL 1,257.40, bank 1,275.40) | (18.00) | K4 | Book side, PJE-03 |

## 3. Proposed adjusting entries (PROPOSED - NOT POSTED)

| Proposed JE | Account | Debit | Credit | Reason | Working paper row |
|---|---|---:|---:|---|---|
| PJE-01 | 6600 Bank Fees | 15.00 | | March service fee | P1 |
| PJE-01 | 1010 Operating Cash | | 15.00 | | P2 |
| PJE-02 | 1010 Operating Cash | 4.62 | | March interest | P3 |
| PJE-02 | 4910 Interest Income | | 4.62 | | P4 |
| PJE-03 | 2000 Accounts Payable | 18.00 | | INV-4410 keyed short | P5 |
| PJE-03 | 1010 Operating Cash | | 18.00 | | P6 |

Total debits = total credits: 37.62 = 37.62 (T8).

## 4. Open items

| # | Item | Amount | Owner (role) | Due | Working paper |
|---|---|---:|---|---|---|
| 1 | Confirm RCPT-304 clears on the April statement | $2,050.00 | Staff Accountant | 2026-04-07 | B2 |
| 2 | Confirm CHK 1003 clears; follow up if not cashed in 60 days | (315.00) | AP Specialist | 2026-05-29 | B3 |
| 3 | Book PJE-01 to PJE-03 after review | $37.62 | Accounting Manager | 2026-04-03 | P1 to P6 |

## 5. Tie-out evidence

| Check | Result | Evidence |
|---|---|---|
| Every `TIE-OUT` row is 0.00 | PASS | T1 to T8 |
| tie-out-checker agent | PASS | every amount cites a file and row or a formula |
| `data/raw/` unchanged | PASS | files match the extracts received |

## 6. Sign-off

Left blank on purpose. A person signs, not the assistant.

| Role | Name | Date |
|---|---|---|
| Preparer | | |
| Reviewer | | |
