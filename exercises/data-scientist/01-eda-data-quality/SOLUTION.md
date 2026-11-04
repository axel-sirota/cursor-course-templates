# Exercise 1: instructor key

Full id lists are in `checks/expected_findings.md`. This file has the counts, what a good doc says about each issue, and the wrong answers students hit, with the number each wrong answer produces. All values recomputed from the seed-2026 CSVs.

## Expected counts

| # | Issue | Count | What the doc should say it breaks |
|---|---|---|---|
| 1 | Exact duplicates | 90 pairs, 90 claims | Double reimbursement. 2,548,410 cents in claim currency paid twice if approved. A model trained on them sees the same row twice and can leak across a random split |
| 2 | Near-duplicates | 45 pairs (23 amount 1 cent, 22 date 1 day) | Same as above, but invisible to an exact-match check |
| 3 | Split under receipt threshold | 6 groups, 15 lines | Policy evasion: each line under $75 so no receipt, total above it |
| 4 | Weekend expenses | 30 lines | Review flag per policy (`weekend_expenses: flag_for_review`). Normal lines are all on weekdays, so every weekend line is seeded |
| 5 | Missing category | 8 lines | Posts to 6190 Uncategorized; unlabeled rows must be dropped from training and are the natural "predict these" set in exercise 2 |
| 6 | Mixed currency without fx | 3 lines on 3 claims (C-03817, C-03986, C-03996) | USD value cannot be computed; `total_cents` adds pounds, euros or Canadian dollars to dollars. All 3 are still `submitted`, so not yet in the GL |
| 7 | Outlier | 1 line, L-007001, 980000 cents | Office supplies at Deskworks, about 41 times the next largest Office supplies line (23995). Drives the 6150 flux in the accountant exercises |
| 8 | Alcohol | 25 lines, all Meals | Not reimbursable |
| 9 | Over policy limit | 10 lines (Meals 5, Lodging 4, Office supplies 1) | The outlier L-007001 is also here |
| 10 | Missing receipt over $75 | 10 lines | Audit finding |
| 11 | Older than 60 days | 4 lines | Late submission; also why `expense_date` starts in May |
| 12 | Leakage column | `gl_account_hint` | 1:1 copy of the label. Must never be a feature (exercise 2) |

Small sets to check id by id: issues 5, 6, 7, 11, and the stretch approval sets.

## Wrong answers you will see

| Mistake | Number it produces | Correct |
|---|---|---|
| `/ds-explore` default outlier rule: 1.5 x IQR on raw `amount_cents` over all lines | 836 "outliers" | IQR per category on USD: 1 in Office supplies (L-007001) |
| Near-duplicate window widened to amount within $1.00 and date within 3 days | 160 pairs, 25 of them false (Metro Transit fares and car rentals that just look alike) | 45 |
| Near-duplicate rule without "different claims" or without excluding exact matches | Counts mix with issue 1 | Report exact (90) and near (45) separately |
| Counting each pair twice in a self-join (no `line_id_a < line_id_b`) | 180 exact, 90 near | 90 and 45 |
| Alcohol regex `wine\|beer\|bar` | 16 lines, misses the 9 "cocktails" lines | 25 |
| Alcohol by merchant (Copper Kettle Taproom only) | 6 lines | 25 |
| Meals limit per line at 7500, ignoring attendees | 237 lines | 5 |
| Receipt rule on raw `amount_cents` instead of USD | 18 lines (8 false, all CAD lines above 7500 CAD but under 7500 USD) | 10 |
| Weekend from `submitted_at` instead of `expense_date` | 373 claims submitted on a weekend, which is not a policy issue | 30 lines |
| pandas `read_csv` defaults turn blank `fx_rate` into NaN and the USD math silently yields NaN, then `sum()` treats it as 0 | 3 claims look valid with a too-small USD total | Flag the 3 claims, give their lines no USD value |
| Missing category counted from `category.isna()` after `fillna("")` or `astype(str)` | 0 (the string "nan" is not blank) | 8 |

## Rounding

USD value uses half up. No line in this dataset produces exactly half a cent (amount is an integer, `fx_rate` has 4 decimals, and none of the 9,166 convertible products ends in .5000; the other 10 lines sit on the 3 blank-fx claims), and float math with Python `round()` matches half up on every line. So a student using floats gets the right counts. Their unit test for half up should still construct a synthetic .5 case.

## Expected `/ds-explore` hypotheses (examples of good ones)

- "Some lines are re-submitted on a second claim by the same employee; exact matching on employee, merchant, date, amount and currency will find them."
- "`gl_account_hint` is derived from `category`; a crosstab will show one account per category."
- "Merchant descriptor text predicts category except for Boxmart Marketplace, which sells both Software and Office supplies." (Boxmart: 296 Office supplies, 236 Software, 1 blank.)
- "Amounts scale differs by category, so outliers must be found per category."

## Grading

| Grade | Bar |
|---|---|
| Pass | All 12 counts right, small-set ids right, USD function tested |
| Strong | Plus the "what it breaks" sentence per issue, and the duplicate and approval stretch answers (90 / 132 claims, 5 self-approved, 5 above limit) |
| Redo | Any of issues 1, 2, 6 or 12 missing, or counts taken from the answer key instead of computed |
