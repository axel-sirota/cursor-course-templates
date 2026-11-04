# Solution: Exercise 2, October Flux Analysis (instructor only)

Source: `exercises/_data/README.md` section F, recomputed from `gl_journal.csv` and `budget_2026.csv`.

Rule: actual = sum of `debit_cents - credit_cents` per account and period, all cost centers and both entities. Flag = more than $10,000.00 AND more than 10%. The class is the same for vs budget and vs September on every account.

## Tie-out totals (22 budgeted accounts)

| Column | Total | Source |
|---|---:|---|
| October budget | 3,145,781.30 | `budget_2026.csv`, month 2026-10, 83 rows |
| September actual | 3,146,072.17 | `gl_journal.csv`, period 2026-09, accounts 6000 to 6800 in the budget file |
| October actual | 3,359,525.73 | `gl_journal.csv`, period 2026-10, same accounts |

## Full table

| Account | Name | Class | Budget Oct | Actual Sep | Actual Oct | vs budget | % | vs Sep | % | Expected treatment |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| 6000 | Salaries and Wages | dollar_only | 1,150,178.32 | 1,150,063.33 | 1,188,489.50 | 38,311.18 | 3.3% | 38,426.17 | 3.3% | Note: under 10%. Merit note supports it |
| 6010 | Payroll Taxes | under | 87,729.63 | 88,073.76 | 86,201.57 | -1,528.06 | -1.7% | -1,872.19 | -2.1% | |
| 6020 | Employee Benefits | under | 140,082.33 | 140,097.16 | 142,147.85 | 2,065.52 | 1.5% | 2,050.69 | 1.5% | |
| 6100 | Meals | under | 45,003.93 | 45,250.16 | 44,436.20 | -567.73 | -1.3% | -813.96 | -1.8% | |
| 6110 | Lodging | under | 144,484.36 | 145,019.32 | 148,197.89 | 3,713.53 | 2.6% | 3,178.57 | 2.2% | |
| 6120 | Airfare | under | 228,908.34 | 229,041.56 | 227,781.77 | -1,126.57 | -0.5% | -1,259.79 | -0.6% | |
| 6130 | Ground Transport | under | 44,561.68 | 44,446.20 | 44,570.06 | 8.38 | 0.0% | 123.86 | 0.3% | |
| 6140 | Software Subscriptions | under | 128,260.51 | 127,441.72 | 124,869.28 | -3,391.23 | -2.6% | -2,572.44 | -2.0% | |
| 6150 | Office Supplies | pct_only | 56,909.99 | 57,056.36 | 65,556.36 | 8,646.37 | 15.2% | 8,500.00 | 14.9% | Note: under $10,000. No department note |
| 6160 | Training | both | 221,123.99 | 220,791.80 | 252,932.30 | 31,808.31 | 14.4% | 32,140.50 | 14.6% | Explained: Engineering note |
| 6170 | Client Entertainment | under | 118,195.07 | 118,246.26 | 118,539.47 | 344.40 | 0.3% | 293.21 | 0.2% | |
| 6180 | Conferences and Events | both | 25,044.22 | 25,052.50 | 73,677.61 | 48,633.39 | 194.2% | 48,625.11 | 194.1% | Explained: Sales note |
| 6190 | Other Travel and Expense (Uncategorized) | under | 2,080.30 | 2,086.27 | 2,105.68 | 25.38 | 1.2% | 19.41 | 0.9% | |
| 6200 | Rent | under | 115,752.19 | 114,859.95 | 116,561.43 | 809.24 | 0.7% | 1,701.48 | 1.5% | |
| 6210 | Utilities | pct_only | 7,409.50 | 7,410.02 | 9,060.45 | 1,650.95 | 22.3% | 1,650.43 | 22.3% | Note: under $10,000. No note |
| 6300 | Professional Fees | both | 94,023.51 | 94,145.03 | 121,595.36 | 27,571.85 | 29.3% | 27,450.33 | 29.2% | **OWNER TO EXPLAIN** (Finance, CC-FIN) |
| 6310 | Legal Fees | under | 28,323.59 | 28,046.02 | 27,220.43 | -1,103.16 | -3.9% | -825.59 | -2.9% | |
| 6400 | Marketing Programs | both | 120,185.69 | 120,041.67 | 156,351.44 | 36,165.75 | 30.1% | 36,309.77 | 30.2% | Explained: Marketing note |
| 6500 | Depreciation | under | 20,913.35 | 21,081.47 | 20,841.62 | -71.73 | -0.3% | -239.85 | -1.1% | |
| 6600 | Bank and Merchant Fees | under | 47,681.86 | 48,018.96 | 47,322.48 | -359.38 | -0.8% | -696.48 | -1.5% | |
| 6700 | Hosting and Cloud | dollar_only | 309,146.22 | 310,012.02 | 329,135.47 | 19,989.25 | 6.5% | 19,123.45 | 6.2% | Note: under 10%. No note, none required |
| 6800 | Insurance | pct_only | 9,782.72 | 9,790.63 | 11,931.51 | 2,148.79 | 22.0% | 2,140.88 | 21.9% | Note: under $10,000. No note |

Counts: both 4 (6160, 6180, 6300, 6400). pct_only 3 (6150, 6210, 6800). dollar_only 2 (6000, 6700). under 13.

## Explanations and the note check

| Account | Note | Note amount | Variance vs budget | Driving cost center |
|---|---|---:|---:|---|
| 6160 Training | Engineering: fall training cohort with Summit Learning, planned for Q1 2027 | about 32,100 | 31,808.31 (vs Sep 32,140.50) | CC-ENG +33,645.58 vs budget |
| 6180 Conferences and Events | Sales: Q4 offsite moved from November to October, Lakeside Lodge Events | about 48,600 | 48,633.39 | CC-SAL +48,630.91 vs budget |
| 6400 Marketing Programs | Marketing: Q4 brand campaign with Brightbeam Media launched three weeks early | about 36,300 | 36,165.75 (vs Sep 36,309.77) | CC-MKT +36,165.75 vs budget |
| 6300 Professional Fees | None. Finance owns 6300 (only CC-FIN posts to it) and its note says "Nothing unusual this month" | | 27,571.85 | CC-FIN |

Notes that match no flagged variance: Operations (office move, no spend yet) and Support (headcount flat). The People and payroll note (merit 3.3%) supports 6000, which is `dollar_only`, so it is a near-miss note, not a required explanation.

## Traps

| Trap | Weak answer | Right answer |
|---|---|---|
| 6300 Professional Fees | Writes a plausible story ("year-end audit fees") | `OWNER TO EXPLAIN`, owner Finance / Controller. The Finance note says nothing unusual, which contradicts a $27.6K variance. That contradiction is the finding |
| Either vs both | Flags 6000 and 6700 (over $10K) or 6150, 6210, 6800 (over 10%) as needing explanation | Rule is AND. These 5 are near misses: classed and noted only |
| Over-trusting notes | Copies the note amount as the variance | Variance comes from the GL. The note is evidence, and its amount should agree within a few hundred dollars |
| Unbudgeted accounts | Adds 6950 or 6990 with a 100% variance | Out of scope for this paper. They show up in exercise 3 as seldom-used accounts |
| Wrong level | Flags by cost center | Account level, all cost centers summed |

## Stretch answers

- 6150 Office Supplies: one line drives most of it. `expense_lines.csv` L-007001, claim C-03048, $9,800.00 office supplies, posted in October by JE-003646 (`gl_journal.csv` row 8967). Without it, 6150 would be under budget by about $1,150.
- November budget: 6180 CC-SAL is 62,706.27 in November vs 17,530.96 in October; 6400 CC-MKT is 156,387.54 vs 120,185.69. Both carry the spend that moved into October, so November should show favorable variances of roughly $45K and $35K.

## Grading

| Points | For |
|---:|---|
| 3 | All 22 accounts with correct amounts and classes |
| 3 | 6160, 6180, 6400 explained with note cited |
| 2 | 6300 marked OWNER TO EXPLAIN with owner, no invented reason |
| 1 | Near misses classed and noted, not explained |
| 1 | `TIE-OUT` rows tie to budget and GL totals |
