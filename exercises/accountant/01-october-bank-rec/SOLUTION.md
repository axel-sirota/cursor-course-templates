# Solution: Exercise 1, October Bank Rec (instructor only)

Source: `exercises/_data/README.md` section D, recomputed from the CSVs. Row numbers count the header as row 1.

## Balances

| Item | Amount | Source |
|---|---:|---|
| GL 1010 opening 2026-10-01 | 5,004,257.32 | `gl_balance_1010_2026-10.csv` row 3 |
| Bank opening 2026-10-01 | 5,004,257.32 | `gl_balance_1010_2026-10.csv` row 5 |
| GL 1010 closing 2026-10-31 | 5,360,650.74 | `gl_balance_1010_2026-10.csv` row 4 |
| Bank closing 2026-10-31 | 5,334,876.08 | `gl_balance_1010_2026-10.csv` row 6 (also last running balance, `bank_statement_2026-10.csv` row 1430) |
| GL minus bank, before reconciling | 25,774.66 | row 4 - row 6 |

Population: 1,429 bank lines; 1,433 GL lines (account 1010, NW-US, period 2026-10). Both roll forward: opening + activity = closing on each side.

Matching on reference + amount: 1,426 bank lines match 1,426 GL lines. Unmatched: 3 bank lines, 7 GL lines.

## Reconciling items (9)

| # | Side | Category | Reference | je_id | Date | Amount | Source |
|---|---|---|---|---|---|---:|---|
| 1 | Bank | Deposit in transit (add) | RCPT-260145 | JE-005212 | 2026-10-30 | 7,203.07 | `gl_journal.csv` row 12820 |
| 2 | Bank | Deposit in transit (add) | RCPT-260146 | JE-005213 | 2026-10-30 | 20,983.67 | `gl_journal.csv` row 12822 |
| 3 | Bank | Outstanding check (subtract) | CHK 010246 | JE-004646 | 2026-10-22 | -44.84 | `gl_journal.csv` row 11411 |
| 4 | Bank | Outstanding check (subtract) | CHK 010269 | JE-005001 | 2026-10-29 | -394.72 | `gl_journal.csv` row 12399 |
| 5 | Bank | Outstanding check (subtract) | CHK 010281 | JE-005208 | 2026-10-29 | -1,158.70 | `gl_journal.csv` row 12813 |
| 6 | Book | Bank fee not booked (subtract) | BKFEE-1021 | | 2026-10-21 | -35.00 | `bank_statement_2026-10.csv` row 838 |
| 7 | Book | Interest not booked (add) | INT-1030 | | 2026-10-30 | 12.87 | `bank_statement_2026-10.csv` row 1430 |
| 8 | Book | GL duplicate payment (add back) | NWR2610150176 | JE-003980 | 2026-10-15 | 826.95 | `gl_journal.csv` row 9795 (original JE-003979 row 9793 matches bank row 784) |
| 9 | Book | Keying error, transposition (add back) | NWR2610220046 | JE-004388 | 2026-10-22 | 9.00 | GL -1,243.56 `gl_journal.csv` row 10895; bank -1,234.56 `bank_statement_2026-10.csv` row 884; payout 1,234.56 `payouts_2026-10.csv` row 840 |

Deposits in transit total 28,186.74. Outstanding checks total -1,598.26.

## Reconciliation

| Line | Amount | Formula |
|---|---:|---|
| Bank closing | 5,334,876.08 | |
| + deposits in transit | 28,186.74 | items 1 + 2 |
| - outstanding checks | -1,598.26 | items 3 + 4 + 5 |
| **Adjusted bank** | **5,361,464.56** | |
| GL closing | 5,360,650.74 | |
| - bank fee | -35.00 | item 6 |
| + interest | 12.87 | item 7 |
| + duplicate | 826.95 | item 8 |
| + transposition | 9.00 | item 9 |
| **Adjusted book** | **5,361,464.56** | |
| **Difference** | **0.00** | adjusted bank - adjusted book |

## Proposed entries (PROPOSED - NOT POSTED)

| PJE | Account | Debit | Credit | Reason |
|---|---|---:|---:|---|
| PJE-01 | 6600 Bank and Merchant Fees | 35.00 | | Wire service charge BKFEE-1021 not booked |
| PJE-01 | 1010 Operating Cash | | 35.00 | |
| PJE-02 | 1010 Operating Cash | 12.87 | | Interest credit INT-1030 not booked |
| PJE-02 | 4910 Interest Income | | 12.87 | |
| PJE-03 | 1010 Operating Cash | 826.95 | | Reverse duplicate JE-003980 (PO-002803 paid once) |
| PJE-03 | 2150 Accrued Reimbursements | | 826.95 | |
| PJE-04 | 1010 Operating Cash | 9.00 | | Correct JE-004388: keyed 1,243.56, paid 1,234.56 |
| PJE-04 | 2150 Accrued Reimbursements | | 9.00 | |

Total debits 883.82 = total credits 883.82.

PJE-03 and PJE-04 reverse the debit side of the original EXP entries (Dr 2150 / Cr 1010), so they credit 2150. Accept a student who books both to 2150 with the reason stated. Do not accept a credit to an expense account.

## Traps

| Trap | What a weak answer does | Right answer |
|---|---|---|
| Distractor checks | Lists CHK 010231 or CHK 010243 as outstanding | Not reconciling. CHK 010231 issued 2026-10-08 (JE-003262) cleared 2026-10-13 (bank row 598). CHK 010243 issued 2026-10-15 (JE-003905) cleared 2026-10-20 (bank row 833) |
| Duplicate | Matches both JE-003979 and JE-003980 to the one bank line, or matches on reference only | One-to-one matching leaves JE-003980 unmatched. It is the second posting of the same payout (entry_date 2026-10-16, one day after the original) |
| Transposition | Clears NWR2610220046 because the reference matches | Amounts differ by 9.00. Difference divisible by 9 points at transposed digits. The payout file shows 1,234.56 was paid, so the GL is wrong |
| Plug | Types 25,774.66 or a smaller balancing figure | Every item cited. Adjusted difference is 0.00 with no plug |
| Side | Puts the fee or interest on the bank side | Bank already has them. The GL is missing them, so they adjust the book |

## Grading

| Points | For |
|---:|---|
| 3 | Difference 0.00 with no plug |
| 3 | All 9 items, correct ids and amounts (one point off per missing or wrong item, floor 0) |
| 1 | Distractor checks excluded with a reason |
| 2 | Proposed entries balance, right accounts, marked PROPOSED - NOT POSTED |
| 1 | `TIE-OUT` rows complete and every amount cited |
