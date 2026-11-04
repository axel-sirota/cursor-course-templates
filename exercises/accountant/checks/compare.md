# Comparing a student paper to expected.csv

Each exercise has `checks/expected.csv` with the figures a correct paper must show. You compare the student's working paper to it in one of two ways. No script is needed.

| Exercise | Student paper | Key | Match on | Compare |
|---|---|---|---|---|
| 1 Bank rec | `working/recon-1010-2026-10.csv` | `01-october-bank-rec/checks/expected.csv` | `reference` (or `je_id`) | amount, side, category |
| 2 Flux | `working/flux-2026-10.csv` | `02-flux-analysis/checks/expected.csv` | `account` | actual, var_vs_budget, class, explanation status |
| 3 JE testing | `working/je-test-2026-10.csv` | `03-je-testing-close-memo/checks/expected.csv` | `je_id` + `test` | total_debit, source_row |
| 3 Accrual | `working/accrual-2150-2026-10.csv` | same file, `section = ACCRUAL` | line name | amount |

## Pass rule

- Every `ITEM`, `LINE` with class `both`, `EXCEPTION` and `ACCRUAL` row in the key is on the student paper with the same id and amount (to the cent).
- Every `TOTAL` row agrees (difference 0.00, totals to the cent).
- `NOT-AN-ITEM` rows are **not** on the paper.
- Extra rows on the student paper are fine only if the student gives a reason. Ask for it.
- Percent columns may differ by 0.1 from rounding. Amounts may not differ at all.

## Option A: by eye (10 minutes per paper)

1. Open the student paper and the key side by side in Excel or Google Sheets.
2. On the student paper, filter to the rows that hold results (`section` = BANK / BOOK, LINE, or EXCEPTION).
3. Sort both files by the match column (reference, account, or je_id).
4. Walk down the key. For each row, find the student row and tick the amount. Mark misses in a new column at the right of the key copy (not the original).
5. Check the student's `TIE-OUT` rows: every difference 0.00.
6. Spot-check two citations: follow `source_file` + `source_row` to the source in `exercises/_data/northwind/`.

Tip for exercise 1: sort the key by `amount`. The nine reconciling items range from -1,158.70 to 20,983.67. Totals go first: adjusted bank and adjusted book both 5,361,464.56.

## Option B: with the agent (2 minutes per paper)

Open Cursor in the student's workspace and paste:

```
Compare workspaces/accountant/working/<student paper> to
exercises/accountant/<exercise>/checks/expected.csv.
Match rows on <match column>. Amounts must agree to the cent.
Give me one table: key row, found on paper (yes/no), student amount, expected amount, difference.
Then list rows on the paper that are not in the key, and any NOT-AN-ITEM rows the paper includes.
Do not change either file.
```

Then confirm two of the agent's "yes" rows yourself. The agent's comparison is a draft, not the grade.

## Common mismatches and what they mean

| What you see | Likely cause |
|---|---|
| Ex 1 difference is 9.00 | Transposition JE-004388 was matched on reference only |
| Ex 1 difference is 826.95 | Duplicate JE-003980 was matched to the same bank line as JE-003979 |
| Ex 1 includes CHK 010231 or CHK 010243 | Distractor checks treated as outstanding |
| Ex 1 off by 100x | Cents not divided by 100, or divided twice |
| Ex 2 has 9 flagged accounts | Used OR instead of AND |
| Ex 2 has a reason for 6300 | Explanation invented; must be OWNER TO EXPLAIN |
| Ex 3 has 16 exceptions | Tested October only |
| Ex 3 accrual gap not 0.00 after items | Sign error on 2150 (credit balance) or fx not applied to non-USD claims |
