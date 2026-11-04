# Exercise 3: expected findings

Open this after you have your v1 evaluation table. Truth sets come from `answer_key.json` (seed 2026). Every number below was recomputed from the CSVs.

## Truth set sizes

| Rule | True count | Unit |
|---|---|---|
| Duplicate (exact 90 + near 45) | 135 | line pairs |
| Duplicate claim (holds the later line of a pair) | 132 | claims |
| Missing receipt over $75 | 10 | lines |
| Meal limit | 5 | lines (L-005412, L-005737, L-007409, L-007822, L-007838) |
| Alcohol | 25 | lines |
| Weekend | 30 | lines |
| Self-approval | 5 | claims (C-01045, C-01201, C-01904, C-02145, C-02468) |
| Approval above limit | 5 | claims (C-01395, C-02645, C-03040, C-03115, C-03439) |
| Six policy rules, micro total | 80 | (rule, id) pairs |

Full id lists: `../01-eda-data-quality/checks/expected_findings.md`.

## v2 target: every rule at 1.00 / 1.00

| Rule | Correct definition | Predicted | TP | FP | FN | Precision | Recall |
|---|---|---|---|---|---|---|---|
| Duplicate | same employee, merchant, currency, different claims, amount within 1 cent and date within 1 day | 135 | 135 | 0 | 0 | 1.0000 | 1.0000 |
| Duplicate claim | claim of the later line of each pair | 132 | 132 | 0 | 0 | 1.0000 | 1.0000 |
| Missing receipt | USD value > 7500 and no receipt | 10 | 10 | 0 | 0 | 1.0000 | 1.0000 |
| Meal limit | Meals USD summed per employee per date > 7500 x attendees (blank = 1) | 5 | 5 | 0 | 0 | 1.0000 | 1.0000 |
| Alcohol | description matches wine, beer, cocktail, bar tab, brewery, whiskey | 25 | 25 | 0 | 0 | 1.0000 | 1.0000 |
| Weekend | `expense_date` Saturday or Sunday | 30 | 30 | 0 | 0 | 1.0000 | 1.0000 |
| Self-approval | `approver_id == employee_id` | 5 | 5 | 0 | 0 | 1.0000 | 1.0000 |
| Approval above limit | claim USD total > approver `approval_limit_cents`, status approved or paid | 5 | 5 | 0 | 0 | 1.0000 | 1.0000 |
| Micro, six policy rules | | 80 | 80 | 0 | 0 | 1.0000 | 1.0000 |

## Typical v1 mistakes and their numbers

| Rule | v1 mistake | Predicted | TP | FP | FN | Precision | Recall |
|---|---|---|---|---|---|---|---|
| Duplicate | exact match only | 90 | 90 | 0 | 45 | 1.0000 | 0.6667 |
| Duplicate | amount within $1.00, date within 3 days | 160 | 135 | 25 | 0 | 0.8438 | 1.0000 |
| Missing receipt | raw `amount_cents` > 7500, no currency conversion | 18 | 10 | 8 | 0 | 0.5556 | 1.0000 |
| Meal limit | each Meals line > 7500, attendees ignored | 237 | 5 | 232 | 0 | 0.0211 | 1.0000 |
| Alcohol | regex `wine\|beer\|bar` | 16 | 16 | 0 | 9 | 1.0000 | 0.6400 |
| Alcohol | merchant is Copper Kettle Taproom | 6 | 6 | 0 | 19 | 1.0000 | 0.2400 |
| Approval above limit | `total_cents` in claim currency vs limit | 6 | 4 | 2 | 1 | 0.6667 | 0.8000 |
| Micro, six policy rules | receipt raw, meal per line, `wine\|beer\|bar`, weekend, self, above-limit raw | 312 | 70 | 242 | 10 | 0.2244 | 0.8750 |

Approval above limit v1 errors: false positives C-00629 and C-02384 (CAD claims, above 250000 in CAD, under it in USD), false negative C-02645 (GBP claim, under 250000 in GBP, 306118 in USD).

Receipt v1 false positives: L-002133, L-003390, L-004435, L-004459, L-006572, L-007192, L-007714, L-008617 (all CAD).

## Duplicate tolerance sweep

| Amount tolerance | Date tolerance | Predicted | TP | Precision | Recall |
|---|---|---|---|---|---|
| 0 | 0 days | 90 | 90 | 1.0000 | 0.6667 |
| 0 | 1 day | 112 | 112 | 1.0000 | 0.8296 |
| 0 | 3 days | 112 | 112 | 1.0000 | 0.8296 |
| 1 cent | 0 days | 113 | 113 | 1.0000 | 0.8370 |
| 1 cent | 1 day | 135 | 135 | 1.0000 | 1.0000 |
| 1 cent | 3 days | 135 | 135 | 1.0000 | 1.0000 |
| 100 cents | 0 days | 113 | 113 | 1.0000 | 0.8370 |
| 100 cents | 1 day | 143 | 135 | 0.9441 | 1.0000 |
| 100 cents | 3 days | 160 | 135 | 0.8438 | 1.0000 |

Pick: 1 cent and 1 day. False positives at wider windows are recurring small charges (Metro Transit 8 of the 25 at $1.00 / 3 days, then car rentals, hotels, cabs, cafes).

## Stretch answers

| Question | Answer |
|---|---|
| Claims whose approver is outside the submitter's management chain (VP claims by the CFO and the CFO's by the VP of Operations count as in chain) | 5, the same 5 self-approved claims. Every other approver is in the chain |
| IsolationForest (seed 42) on USD, Office supplies only | L-007001 ranks 1 of 958 |
| IsolationForest per category, scores pooled across categories | L-007001 ranks 18 of 9,158: per-category scores are not comparable across categories |
