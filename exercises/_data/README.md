# Northwind Co. synthetic dataset (expense claims and reimbursement)

One dataset for every persona. Engineers, PMs, designers, data scientists and accountants all work on the same fictional company, Northwind Co., so a number one persona finds is the same number another persona sees. Northwind sells an expense app (Northwind Expense) and runs its own employee reimbursements on it.

Everything here is synthetic. Company, people, merchants, vendors and customers are invented. Merchant descriptor strings imitate card statement text but name made-up merchants. There are no real card numbers.

This README is the answer key for exercise authors. Every seeded anomaly is listed with its exact row identifiers. The same content is in `northwind/answer_key.json`.

## Regenerate

```bash
python3 exercises/_data/generate.py                 # default seed 2026, writes northwind/ and this README
python3 exercises/_data/generate.py --seed 7 --out /tmp/nw   # another seed, README goes into /tmp/nw
python3 exercises/_data/generate.py --only gl_journal        # write one dataset only
python3 exercises/_data/test_generate.py                     # self-check
```

Python 3.11 or newer, standard library only. The same seed gives byte-identical files. The pre-generated files in `northwind/` use seed 2026; students do not need to run anything. The answer key below is for seed 2026 only. Another seed moves every identifier.

Dataset names for `--only`: `employees`, `expense_policy`, `expense_claims`, `gl_accounts`, `gl_journal`, `bank`, `budget`, `pm`, `payouts`, `answer_key`.

## Conventions

- Money is integer cents in columns ending `_cents`. GL, bank, budget and payouts are USD. Claims and lines are in their `currency`.
- USD value of a claim line = `amount_cents x fx_rate` from its claim, rounded half up to the cent. A claim's USD total is the sum of its line USD values. Approval limits, policy limits, the GL and payouts all use this USD value.
- Dates are ISO 8601 (`2026-10-31`). Datetimes are local time without a zone (`2026-10-30T14:05:00`).
- Close month is October 2026 (`2026-10`). Prior month is September 2026 (`2026-09`).
- Claims snapshot: end of day 2026-10-31. Claims cover submissions from 2026-08-01 to 2026-10-31.
- GL covers postings from 2026-09-01 to 2026-10-31, extracted on 2026-11-12 (so it includes late entries).
- Close dates: September closes 2026-10-06, October closes 2026-11-05.
- Company holidays: 2026-09-07 (Labor Day) and 2026-10-12 (Indigenous Peoples' Day). Business days are Monday to Friday excluding these.
- Payout runs are every Thursday. An approved claim is paid in the first run at least 2 days after approval.
- Entities: NW-US (all claims, cash, payroll) and NW-CA (a small Canadian entity, reported in USD).

## Files

| file | rows | purpose |
|---|---|---|
| `answer_key.json` |  | Machine-readable answer key (same content as the tables below) |
| `bank_statement_2026-10.csv` | 1429 | Operating bank account statement, October 2026 |
| `budget_2026.csv` | 415 | Monthly expense budget Aug to Dec 2026 by cost center and account |
| `context_notes_2026-10.md` |  | Department head notes for the October flux review |
| `employees.csv` | 120 | People, org chart and approval limits |
| `expense_claims.csv` | 4000 | Claim headers, Aug to Oct 2026 |
| `expense_lines.csv` | 9176 | Claim lines (one row per expense) |
| `expense_policy.json` |  | Expense policy rules the claims are tested against |
| `gl_accounts.csv` | 48 | Chart of accounts |
| `gl_balance_1010_2026-10.csv` | 5 | GL 1010 and bank opening and closing balances |
| `gl_journal.csv` | 13014 | General ledger journal lines, Sep and Oct 2026 |
| `gl_opening_balances_2026-09-01.csv` | 12 | Balance sheet opening balances at Sep 1 2026 |
| `interview_notes.md` |  | Six synthetic user interviews |
| `je_policy.json` |  | Close calendar, holidays and manual JE approval rules |
| `payouts_2026-10.csv` | 1366 | Reimbursement payouts made in October 2026 |
| `support_tickets.csv` | 60 | Sample of October 2026 support tickets |
| `usage_metrics.csv` | 8 | Northwind Expense product metrics per candidate feature |

## Column reference

### employees.csv

| column | type | meaning |
|---|---|---|
| `employee_id` | string | E0001 to E0120 |
| `name` | string | Fictional first and last name |
| `department` | string | Sales, Engineering, Finance, Marketing, Support or Operations |
| `role` | string | IC, Manager, Director or VP |
| `title` | string | Job title. Finance titles identify the JE preparers and approvers |
| `manager_id` | string | employee_id of the direct manager; blank for VPs |
| `approval_limit_cents` | int | Max claim total in USD cents this person can approve: IC 0, Manager 250000, Director 1000000, VP 5000000 |
| `cost_center` | string | CC-SAL, CC-ENG, CC-FIN, CC-MKT, CC-SUP, CC-OPS (one per department) |
| `hire_date` | date | ISO date |

### expense_claims.csv

| column | type | meaning |
|---|---|---|
| `claim_id` | string | C-00001 onward, ordered by submitted_at (drafts by creation time) |
| `employee_id` | string | Submitter, joins employees.csv |
| `submitted_at` | datetime | ISO local datetime; blank for drafts |
| `status` | string | draft, submitted (pending approval), approved (not yet paid), rejected, paid |
| `approver_id` | string | Who approved or rejected; blank for draft and submitted |
| `approved_at` | datetime | Approval datetime for approved and paid; blank otherwise |
| `total_cents` | int | Sum of line amount_cents, in the claim currency |
| `currency` | string | USD, EUR, GBP or CAD |
| `fx_rate` | decimal string | USD per 1 unit of claim currency, 4 decimals; 1.0000 for USD; blank means missing (seeded anomaly) |
| `paid_at` | date | Payout run date for paid claims |

### expense_lines.csv

| column | type | meaning |
|---|---|---|
| `line_id` | string | L-000001 onward, grouped by claim |
| `claim_id` | string | Joins expense_claims.csv |
| `expense_date` | date | Date the expense happened |
| `merchant` | string | Clean merchant name |
| `merchant_category_text` | string | Raw card descriptor text (for example RIDEO *TRIP, SKYLARK AIR 0062, BOXMART MKTP US*2K4) |
| `category` | string | Policy category label; blank for a few seeded lines |
| `amount_cents` | int | Amount in currency |
| `currency` | string | Line currency; equals the claim currency except 3 seeded lines |
| `receipt_attached` | bool | true or false |
| `description` | string | Employee free text |
| `attendees_count` | int | People covered, Meals and Client entertainment only; blank otherwise |
| `gl_account_hint` | string | GL account for the category (LEAKAGE: a 1:1 copy of the label, see answer key) |

### gl_accounts.csv

| column | type | meaning |
|---|---|---|
| `account` | string | 4-digit account number |
| `name` | string | Account name |
| `type` | string | asset, liability, equity, revenue or expense |
| `normal_balance` | string | debit or credit |

### gl_journal.csv

| column | type | meaning |
|---|---|---|
| `je_id` | string | JE-000001 onward, ordered by posting_date then source |
| `line_no` | int | Line number within the entry |
| `entity` | string | NW-US or NW-CA |
| `posting_date` | date | Accounting date |
| `entry_date` | date | Date the entry was keyed |
| `period` | string | YYYY-MM of posting_date |
| `account` | string | Joins gl_accounts.csv |
| `cost_center` | string | Set on expense lines; blank on balance sheet and revenue lines |
| `debit_cents` | int | Debit amount, USD cents (0 when the line is a credit) |
| `credit_cents` | int | Credit amount, USD cents (0 when the line is a debit) |
| `description` | string | Entry description; carries the claim, payout, invoice or bank reference |
| `source` | string | AP, EXP, PAYROLL, MANUAL or SYSTEM |
| `preparer_id` | string | employee_id, or SVC-EXPENSE / SVC-GL for system postings |
| `approver_id` | string | employee_id; blank for EXP and SYSTEM postings |

### gl_opening_balances_2026-09-01.csv

| column | type | meaning |
|---|---|---|
| `entity` | string | NW-US or NW-CA |
| `account` | string | Balance sheet account |
| `name` | string | Account name |
| `balance_cents` | int | Signed balance, debit positive, credit negative. Sums to 0 per entity |

### bank_statement_2026-10.csv

| column | type | meaning |
|---|---|---|
| `date` | date | Bank posting date |
| `description` | string | Bank text |
| `amount_cents` | int | Signed: deposits positive, withdrawals negative |
| `reference` | string | Bank reference. Matches the token in the GL description (RCPT-, NWR, CHK, INV-, PR-, MSF-) |
| `balance_cents` | int | Running balance after the row |

### gl_balance_1010_2026-10.csv

| column | type | meaning |
|---|---|---|
| `metric` | string | Which balance |
| `amount_cents` | int | Balance, USD cents |

### budget_2026.csv

| column | type | meaning |
|---|---|---|
| `month` | string | YYYY-MM, 2026-08 to 2026-12 |
| `cost_center` | string | Cost center |
| `account` | string | Expense account (6000 to 6800) |
| `budget_cents` | int | Budget, USD cents |

### payouts_2026-10.csv

| column | type | meaning |
|---|---|---|
| `payout_id` | string | PO-000001 onward across Aug to Oct; this file holds October only |
| `claim_id` | string | Joins expense_claims.csv |
| `employee_id` | string | Payee |
| `amount_cents` | int | USD amount paid (claim total converted per line at the claim fx_rate) |
| `currency` | string | Always USD |
| `method` | string | ACH or CHECK |
| `paid_at` | date | Payout run date (Thursdays) |
| `status` | string | sent (the payout system does not know bank clearing) |
| `bank_reference` | string | ACH trace (NWR...) or check number (CHK ...) |

### usage_metrics.csv

| column | type | meaning |
|---|---|---|
| `feature` | string | Candidate feature for the Northwind Expense app |
| `area` | string | Pain area: receipts, approvals, mobile, currency, policy, other |
| `monthly_active_users` | int | Users who touch this workflow area in a month today |
| `support_tickets_per_month` | int | Tickets per month in this area today |
| `avg_minutes_to_submit_claim` | decimal | Average minutes to submit a claim that touches this area |

### support_tickets.csv

| column | type | meaning |
|---|---|---|
| `ticket_id` | string | T-1001 onward |
| `created_at` | datetime | ISO local datetime, October 2026 |
| `category` | string | receipts, approvals, mobile, currency, policy, other |
| `text` | string | Ticket text |

### expense_policy.json

Category limits (`limit_cents` and `per`), `receipt_required_over_cents` (7500), `max_age_days` (60), `weekend_expenses` (`flag_for_review`), `non_reimbursable` (includes alcohol), approval chain rules and limits, foreign currency rule, payout rule.

### je_policy.json

Entities, close calendar and close rule, company holidays, manual JE approval limit (1000000 cents: Controller needed at or above it), preparer rule, source codes, intercompany rule, GL extract date.

### Markdown files

- `context_notes_2026-10.md`: memo-style notes from department heads for the October flux review.
- `interview_notes.md`: six short user interviews (P1 to P6) about receipts, slow approvals, mobile, currency and policy confusion.

# Answer key (seed 2026)

## Summary

| anomaly | count | file | section |
|---|---|---|---|
| Exact duplicate lines across claims | 90 | expense_lines.csv | A1 |
| Near-duplicate lines (1 cent or 1 day) | 45 | expense_lines.csv | A2 |
| Split groups just under receipt threshold | 6 | expense_lines.csv | A3 |
| Weekend expense lines | 30 | expense_lines.csv | A4 |
| Lines with missing category | 8 | expense_lines.csv | A5 |
| Mixed currency lines, claim fx_rate blank | 3 | expense_lines.csv | A6 |
| Outlier ($9,800 office supplies) | 1 | expense_lines.csv | A7 |
| Alcohol lines in Meals | 25 | expense_lines.csv | A8 |
| Over policy limit lines | 10 | expense_lines.csv | A9 |
| Missing receipt over $75 | 10 | expense_lines.csv | A10 |
| Older than 60 days at submission | 4 | expense_lines.csv | A11 |
| Leakage column | 1 | expense_lines.csv | A12 |
| Self-approved claims | 5 | expense_claims.csv | B1 |
| Claims approved above approver limit | 5 | expense_claims.csv | B2 |
| JE weekend or holiday postings | 4 | gl_journal.csv | C1 |
| JE by people who never post | 3 | gl_journal.csv | C2 |
| JE entered after close | 3 | gl_journal.csv | C3 |
| Round-amount manual JEs | 3 | gl_journal.csv | C4 |
| Manual JEs just under $10,000 | 3 | gl_journal.csv | C5 |
| JEs to seldom-used accounts | 3 | gl_journal.csv | C6 |
| Self-approved manual JEs | 2 | gl_journal.csv | C7 |
| Duplicate JEs (pairs) | 2 | gl_journal.csv | C8 |
| Intercompany entry with no NW-CA offset | 1 | gl_journal.csv | C9 |
| Bank rec reconciling items | 9 | bank_statement_2026-10.csv | D |
| Reimbursement accrual tie-out | 1 | payouts, claims, GL 2150 | E |
| Budget accounts over both thresholds | 4 | budget_2026.csv | F |
| Budget accounts over % only | 3 | budget_2026.csv | F |
| Budget accounts over $ only | 2 | budget_2026.csv | F |

Every list below was produced by running the stated detection rule over the final files, and the generator asserts that the rule finds exactly the seeded rows and nothing else.

Claim status counts: draft 110, submitted 161, approved 174, rejected 140, paid 3415.

## A. Expense lines

### A1. Exact duplicates across different claims

Rule: same employee (via claim), `merchant`, `expense_date`, `amount_cents` and `currency`, on two different claims. The later line_id is the duplicate.

| original_line_id | duplicate_line_id | claim_id | employee_id | merchant | expense_date | amount_cents |
|---|---|---|---|---|---|---|
| L-000112 | L-000327 | C-00137 | E0015 | Stayline Hotels | 2026-07-29 | 15093 |
| L-000121 | L-002976 | C-01271 | E0086 | Deskworks | 2026-07-21 | 16062 |
| L-000174 | L-004340 | C-01892 | E0014 | Ballpark Suites | 2026-07-23 | 23070 |
| L-000354 | L-001489 | C-00656 | E0097 | Swift Cab Co | 2026-07-30 | 1632 |
| L-000360 | L-002605 | C-01108 | E0083 | Diagramly | 2026-07-31 | 19484 |
| L-000373 | L-001018 | C-00431 | E0027 | ParkRight Garage | 2026-07-28 | 3345 |
| L-000413 | L-001313 | C-00564 | E0023 | ParkRight Garage | 2026-07-28 | 1735 |
| L-000742 | L-004234 | C-01848 | E0099 | Riverside Grill | 2026-07-29 | 20307 |
| L-000818 | L-002251 | C-00961 | E0003 | Bluejet Airways | 2026-08-03 | 47079 |
| L-000943 | L-000965 | C-00406 | E0005 | Skylark Air | 2026-08-04 | 30277 |
| L-001035 | L-003877 | C-01679 | E0009 | Skylark Air | 2026-07-28 | 73162 |
| L-001049 | L-003100 | C-01323 | E0066 | Deskworks | 2026-08-05 | 18084 |
| L-001086 | L-005323 | C-02322 | E0063 | CodeCamp Academy | 2026-08-03 | 218153 |
| L-001101 | L-001804 | C-00787 | E0052 | Riverside Grill | 2026-08-07 | 19317 |
| L-001102 | L-002243 | C-00955 | E0052 | Riverside Grill | 2026-08-10 | 23244 |
| L-001318 | L-005181 | C-02252 | E0027 | Paper & Pine Supply | 2026-08-13 | 14519 |
| L-001400 | L-001604 | C-00698 | E0120 | Ballpark Suites | 2026-08-10 | 34521 |
| L-001428 | L-004223 | C-01846 | E0002 | Deskworks | 2026-08-10 | 20888 |
| L-001750 | L-004443 | C-01937 | E0105 | Riverside Grill | 2026-08-07 | 46544 |
| L-001897 | L-002961 | C-01267 | E0104 | Skyline Steakhouse | 2026-08-07 | 15813 |
| L-002036 | L-006310 | C-02752 | E0103 | Ballpark Suites | 2026-08-19 | 36140 |
| L-002047 | L-002953 | C-01263 | E0078 | Diagramly | 2026-08-07 | 18620 |
| L-002086 | L-003190 | C-01358 | E0058 | Meridian Suites | 2026-08-12 | 28498 |
| L-002200 | L-002674 | C-01138 | E0086 | Bluejet Airways | 2026-08-19 | 64158 |
| L-002226 | L-002897 | C-01240 | E0091 | Northstar Airlines | 2026-08-17 | 80122 |
| L-002382 | L-007251 | C-03148 | E0090 | Stayline Hotels | 2026-08-19 | 17102 |
| L-002436 | L-005367 | C-02347 | E0097 | Swift Cab Co | 2026-08-13 | 4622 |
| L-002650 | L-004325 | C-01886 | E0021 | Riverside Grill | 2026-08-17 | 9008 |
| L-002671 | L-005255 | C-02286 | E0086 | Metro Transit | 2026-08-17 | 881 |
| L-002701 | L-004028 | C-01753 | E0082 | Boxmart Marketplace | 2026-08-10 | 27856 |
| L-002751 | L-006614 | C-02872 | E0082 | Parkway Inn | 2026-08-26 | 16339 |
| L-002844 | L-006551 | C-02851 | E0001 | Stayline Hotels | 2026-08-18 | 18093 |
| L-002986 | L-003272 | C-01394 | E0078 | Parkway Inn | 2026-08-27 | 20259 |
| L-003035 | L-004284 | C-01866 | E0001 | ParkRight Garage | 2026-08-27 | 3412 |
| L-003158 | L-004421 | C-01927 | E0093 | Roadrunner Car Rental | 2026-08-25 | 9624 |
| L-003262 | L-006084 | C-02654 | E0055 | Diagramly | 2026-08-24 | 26595 |
| L-003263 | L-006838 | C-02984 | E0039 | Skylark Air | 2026-08-27 | 70004 |
| L-003414 | L-007324 | C-03183 | E0087 | Bluejet Airways | 2026-08-27 | 33570 |
| L-003518 | L-007100 | C-03092 | E0012 | Parkway Inn | 2026-08-27 | 18450 |
| L-003595 | L-004088 | C-01779 | E0030 | Roadrunner Car Rental | 2026-08-28 | 13757 |
| L-003632 | L-004723 | C-02055 | E0014 | Metro Transit | 2026-09-01 | 883 |
| L-003677 | L-007210 | C-03129 | E0035 | Parkway Inn | 2026-08-27 | 15927 |
| L-003706 | L-006694 | C-02906 | E0008 | Boxmart Marketplace | 2026-08-31 | 26755 |
| L-003746 | L-006630 | C-02881 | E0009 | Swift Cab Co | 2026-09-01 | 5112 |
| L-003751 | L-008911 | C-03882 | E0085 | Pixelforge | 2026-09-04 | 29459 |
| L-003769 | L-005523 | C-02422 | E0018 | Boxmart Marketplace | 2026-08-28 | 29074 |
| L-004180 | L-004863 | C-02121 | E0043 | Boxmart Marketplace | 2026-08-31 | 10809 |
| L-004193 | L-004344 | C-01894 | E0027 | Summit Learning | 2026-09-07 | 202808 |
| L-004196 | L-006170 | C-02690 | E0098 | Northstar Airlines | 2026-09-01 | 32357 |
| L-004631 | L-009083 | C-03958 | E0078 | Pixelforge | 2026-09-08 | 11677 |
| L-004646 | L-007151 | C-03113 | E0013 | Northstar Airlines | 2026-09-07 | 80782 |
| L-004739 | L-006733 | C-02926 | E0098 | Rideo | 2026-09-16 | 2470 |
| L-004740 | L-005946 | C-02593 | E0099 | Boxmart Marketplace | 2026-08-28 | 4386 |
| L-004743 | L-006439 | C-02807 | E0005 | Meridian Suites | 2026-09-08 | 24115 |
| L-004793 | L-008958 | C-03905 | E0030 | Parkway Inn | 2026-09-15 | 26811 |
| L-004817 | L-007810 | C-03401 | E0028 | Rideo | 2026-09-11 | 3266 |
| L-005034 | L-007083 | C-03087 | E0077 | Meridian Suites | 2026-09-15 | 15450 |
| L-005193 | L-007045 | C-03068 | E0102 | Roadrunner Car Rental | 2026-09-16 | 12678 |
| L-005232 | L-006749 | C-02932 | E0003 | Roadrunner Car Rental | 2026-09-14 | 11066 |
| L-005234 | L-006899 | C-03009 | E0011 | Summit Learning | 2026-09-02 | 98538 |
| L-005384 | L-007914 | C-03442 | E0040 | Riverside Grill | 2026-09-17 | 38286 |
| L-005459 | L-007379 | C-03206 | E0081 | Paper & Pine Supply | 2026-09-22 | 21381 |
| L-005493 | L-008872 | C-03865 | E0086 | Boxmart Marketplace | 2026-09-18 | 22605 |
| L-005694 | L-005763 | C-02517 | E0094 | Skylark Air | 2026-09-22 | 59864 |
| L-005716 | L-007830 | C-03409 | E0089 | Deskworks | 2026-09-17 | 2917 |
| L-005799 | L-006193 | C-02704 | E0085 | Bluejet Airways | 2026-09-21 | 86134 |
| L-005865 | L-007939 | C-03452 | E0004 | Swift Cab Co | 2026-09-21 | 2820 |
| L-005896 | L-007647 | C-03333 | E0118 | Boxmart Marketplace | 2026-09-29 | 8207 |
| L-005935 | L-008988 | C-03922 | E0025 | Summit Learning | 2026-09-10 | 146803 |
| L-006000 | L-007539 | C-03284 | E0008 | Rideo | 2026-09-25 | 4196 |
| L-006104 | L-006618 | C-02873 | E0043 | Swift Cab Co | 2026-09-29 | 1549 |
| L-006128 | L-008827 | C-03847 | E0075 | Meridian Suites | 2026-09-24 | 27548 |
| L-006145 | L-006701 | C-02910 | E0022 | Stayline Hotels | 2026-09-22 | 24417 |
| L-006187 | L-007705 | C-03358 | E0033 | Deskworks | 2026-09-25 | 19152 |
| L-006540 | L-007338 | C-03190 | E0020 | Notably | 2026-09-29 | 13357 |
| L-006545 | L-007752 | C-03381 | E0089 | Swift Cab Co | 2026-09-28 | 2159 |
| L-006611 | L-009003 | C-03928 | E0090 | Diagramly | 2026-10-05 | 5247 |
| L-006670 | L-008121 | C-03534 | E0001 | ParkRight Garage | 2026-09-29 | 3903 |
| L-006715 | L-007886 | C-03432 | E0008 | Deskworks | 2026-09-25 | 17442 |
| L-006782 | L-006916 | C-03015 | E0081 | Parkway Inn | 2026-10-05 | 15654 |
| L-007013 | L-008377 | C-03646 | E0057 | Skylark Air | 2026-10-05 | 27081 |
| L-007036 | L-007040 | C-03064 | E0008 | Ballpark Suites | 2026-10-02 | 12134 |
| L-007054 | L-008927 | C-03890 | E0003 | Rideo | 2026-10-05 | 2535 |
| L-008058 | L-008464 | C-03688 | E0026 | Deskworks | 2026-10-20 | 21639 |
| L-008140 | L-008870 | C-03864 | E0023 | Roadrunner Car Rental | 2026-10-06 | 11777 |
| L-008267 | L-008931 | C-03892 | E0018 | Bluejet Airways | 2026-10-13 | 68830 |
| L-008417 | L-008834 | C-03850 | E0016 | Paper & Pine Supply | 2026-10-13 | 3544 |
| L-008493 | L-008567 | C-03734 | E0033 | Roadrunner Car Rental | 2026-10-19 | 8135 |
| L-008531 | L-008618 | C-03755 | E0015 | Parkway Inn | 2026-10-21 | 28700 |
| L-008854 | L-009016 | C-03932 | E0006 | Ballpark Suites | 2026-10-16 | 16532 |

`claim_id` is the claim holding the duplicate line.

### A2. Near-duplicates

Rule: same employee, `merchant` and `currency`, and either the same date with amounts 1 cent apart (`amount_1_cent`) or the same amount with dates 1 day apart (`date_1_day`). Pairs are on different claims.

| line_id_a | line_id_b | kind | employee_id | merchant | date_a | date_b | amount_a | amount_b |
|---|---|---|---|---|---|---|---|---|
| L-000107 | L-002374 | date_1_day | E0074 | ParkRight Garage | 2026-07-17 | 2026-07-16 | 2747 | 2747 |
| L-000138 | L-001535 | amount_1_cent | E0056 | Rideo | 2026-07-27 | 2026-07-27 | 2088 | 2089 |
| L-000297 | L-000954 | date_1_day | E0086 | Swift Cab Co | 2026-07-27 | 2026-07-28 | 4520 | 4520 |
| L-000465 | L-004067 | amount_1_cent | E0047 | Riverside Grill | 2026-07-24 | 2026-07-24 | 16966 | 16965 |
| L-000722 | L-001596 | amount_1_cent | E0046 | Skyline Steakhouse | 2026-07-24 | 2026-07-24 | 51692 | 51691 |
| L-000783 | L-004572 | amount_1_cent | E0006 | Skyline Steakhouse | 2026-07-22 | 2026-07-22 | 39305 | 39304 |
| L-000809 | L-003536 | date_1_day | E0083 | Pixelforge | 2026-07-27 | 2026-07-28 | 19337 | 19337 |
| L-000888 | L-001869 | amount_1_cent | E0007 | Summit Learning | 2026-07-24 | 2026-07-24 | 66246 | 66247 |
| L-000937 | L-001181 | amount_1_cent | E0107 | Meridian Suites | 2026-08-04 | 2026-08-04 | 24489 | 24488 |
| L-001115 | L-005156 | amount_1_cent | E0029 | ProCert Institute | 2026-07-31 | 2026-07-31 | 85420 | 85421 |
| L-001603 | L-005879 | amount_1_cent | E0120 | Paper & Pine Supply | 2026-08-07 | 2026-08-07 | 16146 | 16147 |
| L-001829 | L-002768 | date_1_day | E0116 | Northstar Airlines | 2026-08-13 | 2026-08-14 | 24881 | 24881 |
| L-001837 | L-003742 | date_1_day | E0008 | Northstar Airlines | 2026-08-17 | 2026-08-18 | 68036 | 68036 |
| L-001854 | L-003863 | amount_1_cent | E0030 | Riverside Grill | 2026-07-31 | 2026-07-31 | 32961 | 32962 |
| L-001886 | L-003348 | date_1_day | E0055 | Northstar Airlines | 2026-08-10 | 2026-08-11 | 74403 | 74403 |
| L-002630 | L-003826 | date_1_day | E0051 | Deskworks | 2026-08-20 | 2026-08-21 | 4138 | 4138 |
| L-002665 | L-006251 | date_1_day | E0080 | Bluejet Airways | 2026-08-24 | 2026-08-25 | 87531 | 87531 |
| L-002699 | L-004319 | date_1_day | E0001 | Deskworks | 2026-08-11 | 2026-08-12 | 23656 | 23656 |
| L-002801 | L-005775 | date_1_day | E0017 | Deskworks | 2026-08-20 | 2026-08-21 | 5855 | 5855 |
| L-003261 | L-003352 | date_1_day | E0022 | Boxmart Marketplace | 2026-08-17 | 2026-08-18 | 24732 | 24732 |
| L-003578 | L-004292 | date_1_day | E0097 | CodeCamp Academy | 2026-08-20 | 2026-08-21 | 118837 | 118837 |
| L-003679 | L-005983 | amount_1_cent | E0020 | Stayline Hotels | 2026-08-26 | 2026-08-26 | 21523 | 21522 |
| L-004150 | L-007270 | amount_1_cent | E0117 | Meridian Suites | 2026-08-31 | 2026-08-31 | 17265 | 17266 |
| L-004179 | L-007842 | date_1_day | E0086 | Skyline Steakhouse | 2026-09-04 | 2026-09-03 | 10950 | 10950 |
| L-004200 | L-006732 | amount_1_cent | E0098 | Metro Transit | 2026-09-02 | 2026-09-02 | 275 | 276 |
| L-004320 | L-008844 | amount_1_cent | E0001 | Pixelforge | 2026-09-09 | 2026-09-09 | 18059 | 18060 |
| L-004328 | L-005754 | date_1_day | E0055 | Boxmart Marketplace | 2026-09-02 | 2026-09-03 | 24479 | 24479 |
| L-004562 | L-007033 | amount_1_cent | E0012 | Northstar Airlines | 2026-09-14 | 2026-09-14 | 41280 | 41281 |
| L-004776 | L-005248 | date_1_day | E0081 | Roadrunner Car Rental | 2026-09-07 | 2026-09-08 | 8543 | 8543 |
| L-004927 | L-008935 | amount_1_cent | E0053 | Paper & Pine Supply | 2026-09-11 | 2026-09-11 | 3244 | 3245 |
| L-005436 | L-007912 | amount_1_cent | E0006 | Riverside Grill | 2026-09-14 | 2026-09-14 | 61550 | 61549 |
| L-005610 | L-005890 | date_1_day | E0087 | Riverside Grill | 2026-09-21 | 2026-09-22 | 25425 | 25425 |
| L-005758 | L-006490 | date_1_day | E0094 | Bluejet Airways | 2026-09-21 | 2026-09-22 | 39651 | 39651 |
| L-005981 | L-008932 | date_1_day | E0053 | Diagramly | 2026-09-24 | 2026-09-25 | 5560 | 5560 |
| L-006259 | L-007057 | date_1_day | E0034 | Stayline Hotels | 2026-09-30 | 2026-10-01 | 15154 | 15154 |
| L-006447 | L-008540 | amount_1_cent | E0090 | Deskworks | 2026-09-21 | 2026-09-21 | 1469 | 1470 |
| L-006707 | L-009135 | date_1_day | E0102 | Northstar Airlines | 2026-10-01 | 2026-10-02 | 41373 | 41373 |
| L-006950 | L-008969 | amount_1_cent | E0096 | Pixelforge | 2026-10-08 | 2026-10-08 | 3743 | 3744 |
| L-007023 | L-007050 | amount_1_cent | E0030 | Bluejet Airways | 2026-10-07 | 2026-10-07 | 31233 | 31234 |
| L-007174 | L-008079 | amount_1_cent | E0067 | Skylark Air | 2026-10-06 | 2026-10-06 | 23756 | 23757 |
| L-007256 | L-008833 | amount_1_cent | E0016 | Stayline Hotels | 2026-09-28 | 2026-09-28 | 20277 | 20278 |
| L-007691 | L-007915 | amount_1_cent | E0040 | Skylark Air | 2026-10-05 | 2026-10-05 | 57136 | 57135 |
| L-008208 | L-008246 | date_1_day | E0007 | Metro Transit | 2026-10-13 | 2026-10-14 | 983 | 983 |
| L-008382 | L-008727 | amount_1_cent | E0026 | Stayline Hotels | 2026-10-19 | 2026-10-19 | 22958 | 22957 |
| L-008978 | L-009160 | date_1_day | E0091 | Riverside Grill | 2026-10-21 | 2026-10-22 | 25896 | 25896 |

### A3. Split claims just under the receipt threshold

Rule: same employee, `merchant` and `expense_date`, two or more lines each between 6000 and 7499 USD cents, summing to more than 7500. None has a receipt. Each group spans two claims.

| line_ids | employee_id | merchant | expense_date | claim_ids | amounts_cents | total_cents |
|---|---|---|---|---|---|---|
| L-000213, L-000553, L-000554 | E0013 | Paper & Pine Supply | 2026-07-31 | C-00091, C-00241 | 7033, 7314, 7215 | 21562 |
| L-000222, L-000512 | E0003 | Pixelforge | 2026-07-31 | C-00096, C-00224 | 7479, 7240 | 14719 |
| L-000580, L-002258 | E0088 | Paper & Pine Supply | 2026-08-04 | C-00251, C-00964 | 7318, 7083 | 14401 |
| L-000694, L-001099, L-001100 | E0052 | Riverside Grill | 2026-08-06 | C-00298, C-00466 | 7467, 7142, 7070 | 21679 |
| L-000914, L-001272 | E0062 | Riverside Grill | 2026-08-07 | C-00385, C-00546 | 7403, 7025 | 14428 |
| L-001748, L-003696, L-003697 | E0095 | Pixelforge | 2026-08-17 | C-00764, C-01599 | 7186, 7314, 7078 | 21578 |

### A4. Weekend expenses

Rule: `expense_date` is a Saturday or Sunday. Normal lines are all on weekdays, so every weekend line is seeded.

| line_id | claim_id | employee_id | expense_date | merchant | category | amount_cents |
|---|---|---|---|---|---|---|
| L-000022 | C-00009 | E0097 | 2026-07-04 | Pixelforge | Software | 7920 |
| L-000408 | C-00178 | E0101 | 2026-07-19 | Deskworks | Office supplies | 6028 |
| L-000696 | C-00300 | E0100 | 2026-07-26 | Deskworks | Office supplies | 3347 |
| L-001008 | C-00425 | E0077 | 2026-08-01 | Boxmart Marketplace | Software | 19645 |
| L-001203 | C-00514 | E0020 | 2026-08-01 | Ballpark Suites | Client entertainment | 12216 |
| L-001360 | C-00588 | E0015 | 2026-07-26 | Boxmart Marketplace | Software | 5767 |
| L-001542 | C-00674 | E0119 | 2026-08-09 | Notably | Software | 25148 |
| L-002064 | C-00893 | E0058 | 2026-08-09 | Northside Bistro | Meals | 4166 |
| L-002238 | C-00953 | E0114 | 2026-08-02 | Riverside Grill | Client entertainment | 24126 |
| L-002252 | C-00961 | E0003 | 2026-08-16 | Lumen Cafe | Meals | 2327 |
| L-003214 | C-01364 | E0085 | 2026-08-29 | Corner Deli Co | Meals | 4196 |
| L-003346 | C-01424 | E0010 | 2026-08-23 | Lumen Cafe | Meals | 4423 |
| L-003438 | C-01465 | E0013 | 2026-08-29 | Northside Bistro | Meals | 2405 |
| L-003666 | C-01586 | E0082 | 2026-08-23 | Northside Bistro | Meals | 20805 |
| L-003759 | C-01625 | E0005 | 2026-08-23 | Deskworks | Office supplies | 23977 |
| L-003944 | C-01715 | E0023 | 2026-08-22 | Skyline Steakhouse | Client entertainment | 28825 |
| L-004620 | C-02007 | E0080 | 2026-08-30 | Roadrunner Car Rental | Ground transport | 10035 |
| L-004737 | C-02063 | E0098 | 2026-08-29 | Greenfield Kitchen | Meals | 4591 |
| L-005254 | C-02285 | E0003 | 2026-09-19 | Boxmart Marketplace | Software | 12363 |
| L-005858 | C-02559 | E0100 | 2026-09-05 | Deskworks | Office supplies | 1548 |
| L-006468 | C-02820 | E0058 | 2026-09-19 | Northside Bistro | Meals | 7452 |
| L-006829 | C-02976 | E0093 | 2026-09-20 | Diagramly | Software | 28164 |
| L-007038 | C-03063 | E0022 | 2026-10-04 | Corner Deli Co | Meals | 4082 |
| L-007184 | C-03122 | E0017 | 2026-10-03 | Ballpark Suites | Client entertainment | 18930 |
| L-007419 | C-03231 | E0020 | 2026-10-03 | Metro Transit | Ground transport | 1036 |
| L-007592 | C-03303 | E0020 | 2026-10-11 | Pixelforge | Software | 16400 |
| L-007782 | C-03396 | E0029 | 2026-10-03 | Ballpark Suites | Client entertainment | 64905 |
| L-008157 | C-03558 | E0044 | 2026-10-04 | Boxmart Marketplace | Software | 21654 |
| L-008533 | C-03720 | E0015 | 2026-10-04 | Diagramly | Software | 7656 |
| L-008909 | C-03880 | E0015 | 2026-10-24 | Harbor Noodle House | Meals | 5066 |

### A5. Missing category

Rule: `category` is blank (and so is `gl_account_hint`). If approved, these post to 6190 Other Travel and Expense (Uncategorized).

| line_id | claim_id | employee_id | merchant | amount_cents |
|---|---|---|---|---|
| L-000092 | C-00037 | E0110 | Boxmart Marketplace | 2184 |
| L-000542 | C-00238 | E0028 | Swift Cab Co | 5156 |
| L-002881 | C-01233 | E0001 | Deskworks | 18348 |
| L-004343 | C-01894 | E0027 | Deskworks | 15097 |
| L-005471 | C-02397 | E0011 | Skyline Steakhouse | 48300 |
| L-005932 | C-02586 | E0095 | Rideo | 4410 |
| L-006886 | C-03002 | E0090 | Roadrunner Car Rental | 11506 |
| L-007780 | C-03394 | E0007 | Rideo | 3536 |

### A6. Mixed currency without fx_rate

Rule: line `currency` differs from its claim `currency`. Each of these claims has a blank `fx_rate` and a `total_cents` that naively adds amounts in two currencies. All three claims are still `submitted`, so they are not in the GL.

| line_id | claim_id | employee_id | currency | amount_cents |
|---|---|---|---|---|
| L-008749 | C-03817 | E0080 | GBP | 921 |
| L-009143 | C-03986 | E0039 | CAD | 1840 |
| L-009164 | C-03996 | E0023 | EUR | 402 |

Claims with blank fx_rate: C-03817, C-03986, C-03996.

### A7. Outlier

`L-007001` on claim `C-03048` (E0088): Office supplies at Deskworks, $9,800.00 on 2026-09-24. Normal office supplies lines are under $240. It was approved in October and posted to 6150, which is why 6150 is a %-only flux item. It also breaks the $500 per line Office supplies limit (A9).

### A8. Alcohol in Meals

Rule: `description` contains one of `wine`, `beer`, `cocktail`, `bar tab`, `brewery`, `whiskey` (case-insensitive). All are Meals lines; 6 are at the merchant Copper Kettle Taproom. Alcohol is not reimbursable.

| line_id | claim_id | employee_id | merchant | expense_date | amount_cents |
|---|---|---|---|---|---|
| L-000334 | C-00142 | E0057 | Harbor Noodle House | 2026-07-24 | 9005 |
| L-000400 | C-00172 | E0109 | Northside Bistro | 2026-07-24 | 10236 |
| L-000750 | C-00323 | E0015 | Copper Kettle Taproom | 2026-07-30 | 3529 |
| L-000964 | C-00405 | E0012 | Northside Bistro | 2026-08-06 | 5789 |
| L-001506 | C-00660 | E0103 | Corner Deli Co | 2026-08-06 | 25010 |
| L-001896 | C-00827 | E0016 | Harbor Noodle House | 2026-08-19 | 6444 |
| L-001937 | C-00842 | E0021 | Copper Kettle Taproom | 2026-08-19 | 7251 |
| L-002831 | C-01208 | E0010 | Lumen Cafe | 2026-08-18 | 5487 |
| L-003043 | C-01296 | E0102 | Corner Deli Co | 2026-08-27 | 25536 |
| L-004195 | C-01835 | E0011 | Corner Deli Co | 2026-08-28 | 5281 |
| L-004294 | C-01871 | E0097 | Lumen Cafe | 2026-09-07 | 6626 |
| L-004557 | C-01980 | E0086 | Northside Bistro | 2026-09-04 | 3970 |
| L-004752 | C-02068 | E0011 | Lumen Cafe | 2026-09-09 | 10290 |
| L-005189 | C-02257 | E0075 | Copper Kettle Taproom | 2026-09-11 | 5567 |
| L-005539 | C-02426 | E0109 | Copper Kettle Taproom | 2026-09-18 | 5149 |
| L-006401 | C-02795 | E0004 | Basil & Rye | 2026-10-01 | 11640 |
| L-006640 | C-02882 | E0009 | Northside Bistro | 2026-09-29 | 5224 |
| L-006863 | C-02993 | E0094 | Harbor Noodle House | 2026-10-06 | 6777 |
| L-006993 | C-03042 | E0068 | Corner Deli Co | 2026-09-23 | 2474 |
| L-007180 | C-03119 | E0067 | Northside Bistro | 2026-10-08 | 1639 |
| L-007650 | C-03333 | E0118 | Copper Kettle Taproom | 2026-10-12 | 4313 |
| L-007741 | C-03374 | E0038 | Corner Deli Co | 2026-10-05 | 4368 |
| L-007791 | C-03398 | E0063 | Northside Bistro | 2026-10-13 | 6324 |
| L-007885 | C-03431 | E0077 | Greenfield Kitchen | 2026-10-13 | 1686 |
| L-008253 | C-03597 | E0097 | Copper Kettle Taproom | 2026-10-15 | 11007 |

### A9. Over policy limit

Rule: per `expense_policy.json` on USD values. Meals: sum per employee per date above 7500 x attendees. Lodging above 30000 per line (one line per night). Office supplies above 50000 per line.

| line_id | claim_id | employee_id | rule | amount_cents |
|---|---|---|---|---|
| L-002106 | C-00904 | E0075 | Lodging | 36234 |
| L-004252 | C-01855 | E0089 | Lodging | 40225 |
| L-005412 | C-02365 | E0007 | Meals | 9157 |
| L-005737 | C-02508 | E0029 | Meals | 12939 |
| L-005866 | C-02561 | E0004 | Lodging | 36649 |
| L-006708 | C-02913 | E0102 | Lodging | 34282 |
| L-007001 | C-03048 | E0088 | Office supplies | 980000 |
| L-007409 | C-03224 | E0005 | Meals | 13916 |
| L-007822 | C-03405 | E0031 | Meals | 12293 |
| L-007838 | C-03412 | E0059 | Meals | 12820 |

### A10. Missing receipt over the threshold

Rule: USD value above 7500 and `receipt_attached` is false.

| line_id | claim_id | employee_id | category | amount_cents |
|---|---|---|---|---|
| L-000135 | C-00054 | E0023 | Client entertainment | 21184 |
| L-000355 | C-00151 | E0097 | Office supplies | 22205 |
| L-000538 | C-00238 | E0028 | Airfare | 71500 |
| L-001631 | C-00714 | E0024 | Software | 13672 |
| L-003713 | C-01606 | E0085 | Airfare | 63215 |
| L-004046 | C-01760 | E0026 | Client entertainment | 42845 |
| L-005302 | C-02311 | E0039 | Software | 13651 |
| L-005692 | C-02489 | E0061 | Client entertainment | 30750 |
| L-007242 | C-03146 | E0057 | Airfare | 88283 |
| L-008680 | C-03787 | E0093 | Airfare | 54571 |

### A11. Older than 60 days

Rule: claim `submitted_at` date minus `expense_date` is more than 60 days.

| line_id | claim_id | employee_id | expense_date | category |
|---|---|---|---|---|
| L-000225 | C-00098 | E0078 | 2026-05-18 | Ground transport |
| L-003177 | C-01353 | E0079 | 2026-06-24 | Software |
| L-005700 | C-02491 | E0026 | 2026-07-13 | Ground transport |
| L-006388 | C-02788 | E0034 | 2026-07-31 | Software |

### A12. Leakage column (data science trap)

`gl_account_hint` is filled from `category` after labeling (Meals 6100, Lodging 6110, Airfare 6120, Ground transport 6130, Software 6140, Office supplies 6150, Training 6160, Client entertainment 6170; blank when category is blank). A classifier that predicts `category` with this column as a feature scores close to 100% and is useless in production, where the hint does not exist yet. Drop it. Also note that Boxmart Marketplace appears under both Software and Office supplies, so merchant alone is not enough.

## B. Expense claims

### B1. Self-approved claims

Rule: `approver_id` equals `employee_id`.

| claim_id | employee_id | approver_id | total_usd_cents | status |
|---|---|---|---|---|
| C-01045 | E0075 | E0075 | 29706 | paid |
| C-01201 | E0075 | E0075 | 84647 | paid |
| C-01904 | E0031 | E0031 | 145795 | paid |
| C-02145 | E0065 | E0065 | 2803 | paid |
| C-02468 | E0002 | E0002 | 45255 | paid |

### B2. Approved above the approver's limit

Rule: claim USD total above the approver's `approval_limit_cents`. In each case an IC's own Manager (limit 250000) approved a claim that needed a Director.

| claim_id | employee_id | approver_id | approver_limit_cents | total_usd_cents | status |
|---|---|---|---|---|---|
| C-01395 | E0027 | E0003 | 250000 | 303714 | paid |
| C-02645 | E0019 | E0004 | 250000 | 306118 | paid |
| C-03040 | E0013 | E0004 | 250000 | 350923 | paid |
| C-03115 | E0020 | E0005 | 250000 | 259624 | paid |
| C-03439 | E0058 | E0034 | 250000 | 273139 | paid |

## C. Journal entry testing (gl_journal.csv)

5274 entries, 13014 lines. Every `je_id` balances (sum of debits equals sum of credits). Each seeded entry carries one flag only.

### C1. Weekend or holiday postings

Rule: `posting_date` is a Saturday, Sunday or company holiday.

| je_id | entity | posting_date | entry_date | source | preparer_id | approver_id | total_debit_cents | description |
|---|---|---|---|---|---|---|---|---|
| JE-000510 | NW-US | 2026-09-07 | 2026-09-07 | MANUAL | E0067 | E0065 | 220815 | Accrue client event deposit |
| JE-001774 | NW-US | 2026-09-19 | 2026-09-19 | MANUAL | E0068 | E0065 | 137422 | Accrue car service invoice |
| JE-003581 | NW-US | 2026-10-12 | 2026-10-12 | MANUAL | E0068 | E0065 | 447690 | Record prepaid maintenance contract |
| JE-004085 | NW-US | 2026-10-18 | 2026-10-18 | MANUAL | E0069 | E0065 | 381240 | Reclass accrued vendor bill to AP |

### C2. Entries by people who normally never post

Rule: `preparer_id` is not a Finance employee and not a service account. Each of these people appears as preparer exactly once.

| je_id | entity | posting_date | entry_date | source | preparer_id | approver_id | total_debit_cents | description | preparer_department |
|---|---|---|---|---|---|---|---|---|---|
| JE-001903 | NW-US | 2026-09-22 | 2026-09-22 | MANUAL | E0033 | E0065 | 268411 | Accrue tooling subscription | Engineering |
| JE-003131 | NW-US | 2026-10-06 | 2026-10-06 | MANUAL | E0001 | E0065 | 195037 | Reclass client dinner to entertainment | Sales |
| JE-004780 | NW-US | 2026-10-26 | 2026-10-26 | MANUAL | E0079 | E0065 | 412066 | Accrue sponsorship booth | Marketing |

### C3. Entered after period close

Rule: period 2026-10 with `entry_date` after 2026-11-05 (or period 2026-09 after 2026-10-06; there are none). All three are balance sheet or revenue entries, so they do not move the expense flux.

| je_id | entity | posting_date | entry_date | source | preparer_id | approver_id | total_debit_cents | description |
|---|---|---|---|---|---|---|---|---|
| JE-005272 | NW-US | 2026-10-30 | 2026-11-06 | MANUAL | E0067 | E0065 | 318544 | Record prepaid conference booth |
| JE-005273 | NW-US | 2026-10-30 | 2026-11-09 | MANUAL | E0068 | E0065 | 274903 | Reclass October accrual to AP |
| JE-005274 | NW-US | 2026-10-30 | 2026-11-12 | MANUAL | E0069 | E0065 | 586210 | Late invoice adjustment, October billing |

### C4. Round-amount manual entries

Rule: source MANUAL and a line amount that is a whole multiple of $1,000.00.

| je_id | entity | posting_date | entry_date | source | preparer_id | approver_id | total_debit_cents | description |
|---|---|---|---|---|---|---|---|---|
| JE-002404 | NW-US | 2026-09-25 | 2026-09-25 | MANUAL | E0069 | E0064 | 2500000 | Prepaid deposit, event venue |
| JE-004720 | NW-US | 2026-10-23 | 2026-10-23 | MANUAL | E0067 | E0064 | 5000000 | Reclass accrued liabilities to AP |
| JE-004833 | NW-US | 2026-10-27 | 2026-10-27 | MANUAL | E0068 | E0064 | 10000000 | Prepay annual conference sponsorship |

### C5. Just under the manual JE approval limit

Rule: source MANUAL with total debits from $9,500.00 to $9,999.99. All were approved by the Accounting Manager; at $10,000.00 they would have needed the Controller.

| je_id | entity | posting_date | entry_date | source | preparer_id | approver_id | total_debit_cents | description |
|---|---|---|---|---|---|---|---|---|
| JE-002464 | NW-US | 2026-09-28 | 2026-09-28 | MANUAL | E0068 | E0065 | 999900 | Accrue outside counsel fees |
| JE-003580 | NW-US | 2026-10-09 | 2026-10-09 | MANUAL | E0067 | E0065 | 999500 | Accrue advisory retainer |
| JE-004834 | NW-US | 2026-10-27 | 2026-10-27 | MANUAL | E0069 | E0065 | 998750 | Accrue software true-up |

### C6. Entries to seldom-used accounts

Rule: accounts used by 1 or 2 entries in the two months: 1900, 3900, 6950, 6990. Accounts in the chart with no activity at all: 1020, 1050, 1500, 2200, 2400, 2500, 3000, 3100, 4990, 6900.

| je_id | entity | posting_date | entry_date | source | preparer_id | approver_id | total_debit_cents | description | accounts |
|---|---|---|---|---|---|---|---|---|---|
| JE-001973 | NW-US | 2026-09-23 | 2026-09-23 | MANUAL | E0067 | E0065 | 61250 | State late filing penalty | ['2100', '6950'] |
| JE-003730 | NW-US | 2026-10-14 | 2026-10-14 | MANUAL | E0069 | E0065 | 742118 | Park unidentified customer receipt | ['1200', '1900'] |
| JE-004227 | NW-US | 2026-10-20 | 2026-10-20 | MANUAL | E0068 | E0065 | 383317 | Clean up opening balance difference | ['3900', '6990'] |

### C7. Self-approved manual entries

Rule: `preparer_id` equals `approver_id`.

| je_id | entity | posting_date | entry_date | source | preparer_id | approver_id | total_debit_cents | description |
|---|---|---|---|---|---|---|---|---|
| JE-001232 | NW-US | 2026-09-15 | 2026-09-15 | MANUAL | E0065 | E0065 | 431508 | Accrue tax advisory fees |
| JE-004287 | NW-US | 2026-10-21 | 2026-10-21 | MANUAL | E0064 | E0064 | 670294 | Release legal accrual |

### C8. Duplicate entries

Rule: same entity, `posting_date`, `description` and identical lines on two `je_id`s. The second is the duplicate. The AP one double-books a vendor invoice to Prepaid; the EXP one double-books a reimbursement payout and is also a bank rec item (D).

| original_je_id | duplicate_je_id | total_debit_cents | description |
|---|---|---|---|
| JE-000662 | JE-000663 | 342960 | Pixelforge Software INV-PF-20931 annual license |
| JE-003979 | JE-003980 | 82695 | Reimbursement PO-002803 C-02932 NWR2610150176 |

### C9. Intercompany entry with no offset

Rule: an IC reference (IC-YYMM-NN in the description) booked in NW-US with no NW-CA entry for the same reference. Five IC references are paired; this one is not. NW-US 1310 will not agree with NW-CA 2310 by this amount.

| je_id | entity | posting_date | entry_date | source | preparer_id | approver_id | total_debit_cents | description |
|---|---|---|---|---|---|---|---|---|
| JE-005211 | NW-US | 2026-10-29 | 2026-10-29 | MANUAL | E0067 | E0064 | 1812494 | IC shared services recharge IC-2610-06 to NW-CA |

## D. Bank reconciliation, October 2026 (account 1010, NW-US)

| item | amount |
|---|---|
| GL 1010 opening 2026-10-01 (equals bank opening; September reconciled with no open items) | $5,004,257.32 |
| GL 1010 closing 2026-10-31 | $5,360,650.74 |
| Bank closing 2026-10-31 | $5,334,876.08 |

Reconciling items:

| item | je_id | detail | amount |
|---|---|---|---|
| Deposit in transit (bank side, add) | JE-005212 | Customer receipt RCPT-260145 Customer 0944 | $7,203.07 |
| Deposit in transit (bank side, add) | JE-005213 | Customer receipt RCPT-260146 Customer 0596 | $20,983.67 |
| Outstanding check (bank side, subtract) | JE-004646 | PO-003146 C-03339 CHK 010246 issued 2026-10-22 | -$44.84 |
| Outstanding check (bank side, subtract) | JE-005001 | PO-003206 C-03322 CHK 010269 issued 2026-10-29 | -$394.72 |
| Outstanding check (bank side, subtract) | JE-005208 | PO-003413 C-03741 CHK 010281 issued 2026-10-29 | -$1,158.70 |
| Bank fee not booked (book side, subtract) |  | 2026-10-21 WIRE SVC CHARGE BKFEE-1021 | -$35.00 |
| Interest not booked (book side, add) |  | 2026-10-30 INTEREST CREDIT INT-1030 | $12.87 |
| GL duplicate payment (book side, add back) | JE-003980 | duplicate of JE-003979, PO-002803 | $826.95 |
| Transposition (book side, add back) | JE-004388 | PO-002888 C-02965: GL $1,243.56, bank $1,234.56 | $9.00 |

Adjusted bank = bank closing + deposits in transit - outstanding checks = $5,361,464.56.

Adjusted book = GL closing - fee + interest + duplicate + transposition = $5,361,464.56.

Unreconciled difference: $0.00.

Distractors: two other October checks cleared a few days after issue and are not reconciling items: PO-002357 CHK 010231 issued 2026-10-08, cleared 2026-10-13; PO-002729 CHK 010243 issued 2026-10-15, cleared 2026-10-20. Every other bank row matches one GL 1010 line by reference and amount.

## E. Reimbursement accrual (2150 Accrued Reimbursements) at 2026-10-31

| item | value |
|---|---|
| Approved but unpaid claims (status approved) | 174 |
| Expected accrual (sum of their USD totals) | $90,735.87 |
| GL 2150 credit balance at 2026-10-31 (opening + Sep and Oct activity) | $89,899.92 |
| Difference (expected minus GL) | $835.95 |
| Explained by GL duplicate payment (D) | $826.95 |
| Explained by transposition (D) | $9.00 |
| 2150 opening balance 2026-09-01 | $108,258.40 |

The approved-unpaid claim ids are listed in `answer_key.json` under `accrual_2150`. October payouts in `payouts_2026-10.csv` tie to the EXP payout entries in the GL except the duplicate and the transposition. All three outstanding checks are paid in the payout system, so they are not in the accrual.

## F. Budget variance, October 2026

Level: account, summing all cost centers and both entities. Actual = sum(debit - credit) in `gl_journal.csv` for the period. Thresholds: more than $10,000.00 AND more than 10%. The same classification holds for Oct actual vs Oct budget and for Oct actual vs Sep actual. Classes: `both` (over $ and %), `pct_only` (small accounts), `dollar_only` (large accounts), `under`. The classification is on the GL as given, before any correcting entries. Unbudgeted accounts with activity (6950, 6990, revenue and balance sheet) are outside the budget file.

| account | name | class | budget Oct | actual Sep | actual Oct | vs budget | % | vs Sep | % | explanation |
|---|---|---|---|---|---|---|---|---|---|---|
| 6000 | Salaries and Wages | dollar_only | $1,150,178.32 | $1,150,063.33 | $1,188,489.50 | $38,311.18 | 3.3% | $38,426.17 | 3.3% | explained |
| 6010 | Payroll Taxes | under | $87,729.63 | $88,073.76 | $86,201.57 | -$1,528.06 | -1.7% | -$1,872.19 | -2.1% | not_flagged |
| 6020 | Employee Benefits | under | $140,082.33 | $140,097.16 | $142,147.85 | $2,065.52 | 1.5% | $2,050.69 | 1.5% | not_flagged |
| 6100 | Meals | under | $45,003.93 | $45,250.16 | $44,436.20 | -$567.73 | -1.3% | -$813.96 | -1.8% | not_flagged |
| 6110 | Lodging | under | $144,484.36 | $145,019.32 | $148,197.89 | $3,713.53 | 2.6% | $3,178.57 | 2.2% | not_flagged |
| 6120 | Airfare | under | $228,908.34 | $229,041.56 | $227,781.77 | -$1,126.57 | -0.5% | -$1,259.79 | -0.6% | not_flagged |
| 6130 | Ground Transport | under | $44,561.68 | $44,446.20 | $44,570.06 | $8.38 | 0.0% | $123.86 | 0.3% | not_flagged |
| 6140 | Software Subscriptions | under | $128,260.51 | $127,441.72 | $124,869.28 | -$3,391.23 | -2.6% | -$2,572.44 | -2.0% | not_flagged |
| 6150 | Office Supplies | pct_only | $56,909.99 | $57,056.36 | $65,556.36 | $8,646.37 | 15.2% | $8,500.00 | 14.9% | no_note |
| 6160 | Training | both | $221,123.99 | $220,791.80 | $252,932.30 | $31,808.31 | 14.4% | $32,140.50 | 14.6% | explained |
| 6170 | Client Entertainment | under | $118,195.07 | $118,246.26 | $118,539.47 | $344.40 | 0.3% | $293.21 | 0.2% | not_flagged |
| 6180 | Conferences and Events | both | $25,044.22 | $25,052.50 | $73,677.61 | $48,633.39 | 194.2% | $48,625.11 | 194.1% | explained |
| 6190 | Other Travel and Expense (Uncategorized) | under | $2,080.30 | $2,086.27 | $2,105.68 | $25.38 | 1.2% | $19.41 | 0.9% | not_flagged |
| 6200 | Rent | under | $115,752.19 | $114,859.95 | $116,561.43 | $809.24 | 0.7% | $1,701.48 | 1.5% | not_flagged |
| 6210 | Utilities | pct_only | $7,409.50 | $7,410.02 | $9,060.45 | $1,650.95 | 22.3% | $1,650.43 | 22.3% | no_note |
| 6300 | Professional Fees | both | $94,023.51 | $94,145.03 | $121,595.36 | $27,571.85 | 29.3% | $27,450.33 | 29.2% | owner_to_explain |
| 6310 | Legal Fees | under | $28,323.59 | $28,046.02 | $27,220.43 | -$1,103.16 | -3.9% | -$825.59 | -2.9% | not_flagged |
| 6400 | Marketing Programs | both | $120,185.69 | $120,041.67 | $156,351.44 | $36,165.75 | 30.1% | $36,309.77 | 30.2% | explained |
| 6500 | Depreciation | under | $20,913.35 | $21,081.47 | $20,841.62 | -$71.73 | -0.3% | -$239.85 | -1.1% | not_flagged |
| 6600 | Bank and Merchant Fees | under | $47,681.86 | $48,018.96 | $47,322.48 | -$359.38 | -0.8% | -$696.48 | -1.5% | not_flagged |
| 6700 | Hosting and Cloud | dollar_only | $309,146.22 | $310,012.02 | $329,135.47 | $19,989.25 | 6.5% | $19,123.45 | 6.2% | no_note |
| 6800 | Insurance | pct_only | $9,782.72 | $9,790.63 | $11,931.51 | $2,148.79 | 22.0% | $2,140.88 | 21.9% | no_note |

Explanations using `context_notes_2026-10.md`:

- 6000 Salaries and Wages (dollar_only): People note: merit increases effective Oct 1.
- 6150 Office Supplies (pct_only): No note. Driven by the $9,800.00 office supplies outlier line.
- 6160 Training (both): Engineering note: fall training cohort ran in October, planned for Q1 2027.
- 6180 Conferences and Events (both): Sales note: Q4 offsite moved from November to October.
- 6210 Utilities (pct_only): No note. Under the $10,000 threshold.
- 6300 Professional Fees (both): No note covers it. Finance owns 6300 and its note says nothing unusual.
- 6400 Marketing Programs (both): Marketing note: Q4 campaign launched three weeks early.
- 6700 Hosting and Cloud (dollar_only): No note. Not required: under the 10% threshold.
- 6800 Insurance (pct_only): No note. Under the $10,000 threshold.

Expected student result: explain 6160, 6180 and 6400 from the notes; flag 6300 Professional Fees as "owner to explain". The Operations note (office move) and the Support note do not match any variance. The November budget carries the offsite (6180, CC-SAL, +$45,000.00) and the campaign (6400, CC-MKT, +$35,000.00) that moved into October.

## G. PM data

`support_tickets.csv` is a sample of about 1 in 11 October tickets. Counts by category: receipts 21, approvals 15, mobile 9, currency 7, policy 7, other 1. `usage_metrics.csv` totals per area roughly match the sample ratio. Interview themes map to the same areas: receipts (P1, P4), approvals (P2), mobile (P3), currency (P4, P5), policy confusion (P6). The claims data backs this up: duplicate submissions (A1, A2), missing fx (A6) and policy misses (A9, A10) are the problems the interviews describe.

