# Solution: Exercise 3, JE Testing and Close Memo (instructor only)

Source: `exercises/_data/README.md` sections C, D and E, recomputed from the CSVs. Row = first line of the entry in `gl_journal.csv` (header = row 1).

## Population

| Item | Value |
|---|---:|
| Entries | 5,274 (2026-09: 2,585; 2026-10: 2,689) |
| Lines | 13,014 |
| Total debits | 23,888,850.50 |
| Total credits | 23,888,850.50 |
| Unbalanced entries | 0 |
| By source (entries) | EXP 5,037; AP 121; SYSTEM 70; MANUAL 42; PAYROLL 4 |
| MANUAL entries | 42 (2026-09: 18; 2026-10: 24) |

## Exceptions: 24 entries, 9 tests, no entry in more than one test

Total debits of the 24 exception entries: 282,671.24. 16 of them are in period 2026-10.

| Test | je_id | Row | Posting | Entered | Preparer | Approver | Total debits | Accounts | Description |
|---|---|---:|---|---|---|---|---:|---|---|
| Weekend or holiday | JE-000510 | 1265 | 2026-09-07 (Labor Day) | 2026-09-07 | E0067 | E0065 | 2,208.15 | 2100, 6170 | Accrue client event deposit |
| Weekend or holiday | JE-001774 | 4324 | 2026-09-19 (Sat) | 2026-09-19 | E0068 | E0065 | 1,374.22 | 2100, 6130 | Accrue car service invoice |
| Weekend or holiday | JE-003581 | 8767 | 2026-10-12 (holiday) | 2026-10-12 | E0068 | E0065 | 4,476.90 | 1400, 2010 | Record prepaid maintenance contract |
| Weekend or holiday | JE-004085 | 10056 | 2026-10-18 (Sun) | 2026-10-18 | E0069 | E0065 | 3,812.40 | 2010, 2100 | Reclass accrued vendor bill to AP |
| Preparer outside Finance | JE-001903 | 4706 | 2026-09-22 | 2026-09-22 | E0033 (Engineering) | E0065 | 2,684.11 | 2100, 6140 | Accrue tooling subscription |
| Preparer outside Finance | JE-003131 | 7735 | 2026-10-06 | 2026-10-06 | E0001 (Sales) | E0065 | 1,950.37 | 6100, 6170 | Reclass client dinner to entertainment |
| Preparer outside Finance | JE-004780 | 11773 | 2026-10-26 | 2026-10-26 | E0079 (Marketing) | E0065 | 4,120.66 | 2100, 6400 | Accrue sponsorship booth |
| Entered after close | JE-005272 | 13010 | 2026-10-30 | 2026-11-06 | E0067 | E0065 | 3,185.44 | 1400, 2010 | Record prepaid conference booth |
| Entered after close | JE-005273 | 13012 | 2026-10-30 | 2026-11-09 | E0068 | E0065 | 2,749.03 | 2010, 2100 | Reclass October accrual to AP |
| Entered after close | JE-005274 | 13014 | 2026-10-30 | 2026-11-12 | E0069 | E0065 | 5,862.10 | 1200, 4000 | Late invoice adjustment, October billing |
| Round amount | JE-002404 | 5864 | 2026-09-25 | 2026-09-25 | E0069 | E0064 | 25,000.00 | 1400, 2100 | Prepaid deposit, event venue |
| Round amount | JE-004720 | 11595 | 2026-10-23 | 2026-10-23 | E0067 | E0064 | 50,000.00 | 2010, 2100 | Reclass accrued liabilities to AP |
| Round amount | JE-004833 | 11937 | 2026-10-27 | 2026-10-27 | E0068 | E0064 | 100,000.00 | 1400, 2010 | Prepay annual conference sponsorship |
| Just under $10,000 | JE-002464 | 6049 | 2026-09-28 | 2026-09-28 | E0068 | E0065 | 9,999.00 | 2100, 6310 | Accrue outside counsel fees |
| Just under $10,000 | JE-003580 | 8765 | 2026-10-09 | 2026-10-09 | E0067 | E0065 | 9,995.00 | 2100, 6300 | Accrue advisory retainer |
| Just under $10,000 | JE-004834 | 11939 | 2026-10-27 | 2026-10-27 | E0069 | E0065 | 9,987.50 | 2100, 6140 | Accrue software true-up |
| Seldom-used account | JE-001973 | 4896 | 2026-09-23 | 2026-09-23 | E0067 | E0065 | 612.50 | 2100, **6950** | State late filing penalty |
| Seldom-used account | JE-003730 | 9218 | 2026-10-14 | 2026-10-14 | E0069 | E0065 | 7,421.18 | 1200, **1900** | Park unidentified customer receipt |
| Seldom-used account | JE-004227 | 10459 | 2026-10-20 | 2026-10-20 | E0068 | E0065 | 3,833.17 | **3900, 6990** | Clean up opening balance difference |
| Self-approved | JE-001232 | 3082 | 2026-09-15 | 2026-09-15 | E0065 | E0065 | 4,315.08 | 2100, 6300 | Accrue tax advisory fees |
| Self-approved | JE-004287 | 10648 | 2026-10-21 | 2026-10-21 | E0064 | E0064 | 6,702.94 | 2100, 6310 | Release legal accrual |
| Duplicate | JE-000663 | 1688 | 2026-09-10 | 2026-09-11 | E0071 | E0066 | 3,429.60 | 1400, 2010 | Duplicate of JE-000662 (row 1686), Pixelforge INV-PF-20931 |
| Duplicate | JE-003980 | 9794 | 2026-10-15 | 2026-10-16 | SVC-EXPENSE | | 826.95 | 1010, 2150 | Duplicate of JE-003979 (row 9792), PO-002803. Same item as bank rec item 8 |
| Intercompany without offset | JE-005211 | 12818 | 2026-10-29 | 2026-10-29 | E0067 | E0064 | 18,124.94 | 1310, 4100 | IC-2610-06 to NW-CA, no NW-CA entry |

Supporting facts:
- Seldom-used accounts (1 or 2 entries in two months): 1900, 3900, 6950, 6990. Accounts in the chart with no activity: 1020, 1050, 1500, 2200, 2400, 2500, 3000, 3100, 4990, 6900. Unused accounts are a note, not an exception.
- Controller is E0064, Accounting Manager is E0065 (`employees.csv`). The three just-under entries were approved by E0065; at $10,000.00 they would need E0064.
- IC references: IC-2609-01 to IC-2610-05 are paired (NW-US and NW-CA entries). IC-2610-06 is NW-US only.
- Tests that a student may add and that find nothing: MANUAL entries of $10,000.00 or more not approved by the Controller (0), MANUAL entries with no approver (0), unbalanced entries (0). Credit a student who runs these and reports zero.

## Accrual tie-out (2150 Accrued Reimbursements, 2026-10-31)

| Line | Amount | Source / formula |
|---|---:|---|
| Approved, unpaid claims | 174 claims | `expense_claims.csv` status = approved |
| Expected accrual | 90,735.87 | sum of line USD values for those claims (`expense_lines.csv`, amount x claim fx_rate, half up) |
| 2150 opening 2026-09-01 (credit) | 108,258.40 | `gl_opening_balances_2026-09-01.csv` row 9 (-10825840) |
| 2150 net activity Sep and Oct (debit) | 18,358.48 | sum of debit - credit on 2150 in `gl_journal.csv` |
| GL 2150 credit balance | 89,899.92 | opening credit - net debit activity |
| Gap (expected - GL) | 835.95 | |
| Explained: duplicate payment JE-003980 | 826.95 | exercise 1 item 8 |
| Explained: transposition JE-004388 | 9.00 | exercise 1 item 9 |
| **Unexplained** | **0.00** | gap - 826.95 - 9.00 |

The two GL errors debited 2150 by 835.95 too much, so 2150 is understated. PJE-03 and PJE-04 from exercise 1 credit 2150 by the same 835.95 and bring it to 90,735.87. None of the 174 approved claims has a blank fx_rate. The three outstanding checks from exercise 1 are paid in the payout system, so they are not in the accrual.

## Stretch answers

- Intercompany: NW-US 1310 debit balance 97,474.46; NW-CA 2310 credit balance 79,349.52. Out of balance by 18,124.94, which is JE-005211.
- Late entries: JE-005272 (1400/2010), JE-005273 (2010/2100), JE-005274 (1200/4000). None touches an expense account, so the flux paper does not change. JE-005274 does move October revenue and AR.
- Approval limit: every MANUAL entry of $10,000.00 or more was approved by E0064. Zero exceptions.

## What the memo should say

| Section | Must include |
|---|---|
| Summary | 1010 reconciles with 0.00 difference after 9 items; 4 proposed entries for 883.82; 2150 gap 835.95 fully explained; 4 flux accounts over threshold, 3 explained, 6300 open; 24 JE exceptions open for review |
| Reconciliations | GL 5,360,650.74, bank 5,334,876.08, difference 0.00, 9 items |
| Accrual tie-outs | 90,735.87 expected, 89,899.92 GL, 835.95 gap, 0.00 unexplained |
| Flux | 6160, 6180, 6400 explained; 6300 OWNER TO EXPLAIN |
| JE testing | the 9 tests with counts 4, 3, 3, 3, 3, 3, 2, 2, 1 |
| Proposed entries | PJE-01 to PJE-04, debits 883.82 = credits 883.82, PROPOSED - NOT POSTED |
| Open items | 6300 explanation (Finance / Controller), JE-005211 missing NW-CA side, 3 after-close entries (Controller approval of late posting), self-approved entries (re-approval), duplicate JE-000663 reversal (AP Manager), deposits in transit and outstanding checks to clear in November |
| Sign-off | blank |

## Traps

| Trap | Weak answer | Right answer |
|---|---|---|
| Scope | Tests October only and misses the 8 September exceptions | Ticket says full extract. 24 exceptions, 16 in October |
| Round amounts | Includes EXP or SYSTEM entries | MANUAL only, per the rule |
| Seldom-used | Lists JE-004227 twice (two seldom accounts) | One row per entry per test |
| Names | Paper shows employee names | Ids and roles only |
| Clearing exceptions | Marks exceptions cleared because "they look normal" | Leave OPEN until evidence; the memo lists them |
| Accrual sign | Treats 2150 debit activity as an increase | 2150 is a credit balance; debits (payouts) reduce it |
| Plug | Writes off 835.95 as "rounding" | Both items cited; unexplained 0.00 |

## Grading

| Points | For |
|---:|---|
| 1 | Population ties |
| 4 | 24 exceptions with right ids (minus one per 3 missing, floor 0) |
| 1 | Tests with zero findings reported as run |
| 2 | Accrual tie-out with 0.00 unexplained |
| 2 | Memo complete, every number cited, sign-off blank |
