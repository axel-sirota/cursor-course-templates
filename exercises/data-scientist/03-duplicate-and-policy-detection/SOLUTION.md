# Exercise 3: instructor key

All expected sets and the v1 / v2 / sweep tables are in `checks/expected_findings.md`. This file has the reference rules, the reference precision and recall, what each v1 error teaches, and what the model card must contain.

## Reference detector (v2) and its measured precision / recall

| Rule | Reference implementation | P | R |
|---|---|---|---|
| Duplicate pair | Self-join lines on employee (via claim), merchant, currency; keep `line_id_a < line_id_b`, `claim_id_a != claim_id_b`, `abs(amount diff) <= 1`, `abs(date diff) <= 1 day` | 1.0000 (135/135) | 1.0000 |
| Duplicate claim | `claim_id` of `max(line_id_a, line_id_b)` per pair | 1.0000 (132/132) | 1.0000 |
| Missing receipt | `usd_cents > policy.receipt_required_over_cents` and `receipt_attached == "false"` | 1.0000 (10/10) | 1.0000 |
| Meal limit | Meals lines grouped by employee and `expense_date`; flag all lines of the group when `sum(usd) > Meals.limit_cents x attendees` | 1.0000 (5/5) | 1.0000 |
| Alcohol | case-insensitive regex `wine\|beer\|cocktail\|bar tab\|brewery\|whiskey` on `description` | 1.0000 (25/25) | 1.0000 |
| Weekend | weekday of `expense_date` is Saturday or Sunday | 1.0000 (30/30) | 1.0000 |
| Self-approval | `approver_id == employee_id` | 1.0000 (5/5) | 1.0000 |
| Approval above limit | claim USD total (sum of line USD) > approver's `approval_limit_cents`, status approved or paid | 1.0000 (5/5) | 1.0000 |
| Micro, six policy rules | | 1.0000 (80/80) | 1.0000 |

Reference naive v1 (the version an agent writes without the exercise 1 definitions), micro over the six policy rules: 312 flags, 70 true, **precision 0.2244, recall 0.8750**. That gap is the lesson: 242 of 312 flags would land on a reviewer's desk for nothing.

## What each v1 error teaches

| Rule | v1 error | Lesson |
|---|---|---|
| Missing receipt | Raw `amount_cents` (8 CAD false positives) | Thresholds are in USD. Convert first, then compare |
| Meal limit | Per line at 7500 (232 false positives) | Read the `per` field in the policy: `person_per_day`. Team dinners have attendees. In this data a per-line check against 7500 x attendees also gives 5/5, but the policy says per day, so a correct detector sums per day |
| Alcohol | `wine\|beer\|bar` misses 9 "cocktails" lines | Keyword lists come from looking at the data. Print the descriptions of known Meals outliers before writing a regex. `bar` also risks false hits on words like "barbecue" in real data (none here) |
| Duplicate | Exact only (R 0.67) or wide window (P 0.84) | Precision and recall trade off with tolerance; pick the window from the sweep, not by feel |
| Approval above limit | Claim currency total (2 FP CAD, 1 FN GBP) | Same as receipt: USD first |
| Weekend, self-approval | Usually right first time | Not every rule needs work; say so and move on |

Things to stop on during the class:
- An agent that edits a rule until it matches by adding a `line_id` list or reading `answer_key.json` inside the detector. That is overfitting to labels; the rule must stand on the policy alone.
- The 3 claims with blank `fx_rate` (C-03817, C-03986, C-03996) have no USD value. A good detector flags them as "cannot evaluate" instead of silently passing them. They do not affect any rule's precision or recall here.
- Nothing equals the threshold: `usd >= 7500` and `usd > 7500` give the same 10 receipt lines. Students who used `>=` are wrong by policy text, not by count.

## Model card (`/ds-handoff`): required content

| Section | Must say |
|---|---|
| What it does | Screens expense claims before approval with 8 deterministic rules from `expense_policy.json` 2026.1 and flags line pairs, lines or claims |
| What it doesn't do | No learned model. Does not detect: duplicates with more than 1 cent or 1 day difference, alcohol not named in the description, claims with blank `fx_rate` (reported as "cannot evaluate"), approval-chain breaks beyond self-approval (stretch), receipt fraud |
| Training data | None trained. Rules validated on 4,000 claims / 9,176 lines, Aug to Oct 2026, against the audit team's labels |
| Performance | Per-rule precision and recall table (v2 all 1.00), the v1 table for contrast, the duplicate sweep |
| Fairness | Rules do not use department, role or name. Report flags per department next to each department's line count, and call out any department flagged well above its share |
| Deployment requirements | Input schema of the three CSVs (column names and types), policy file version, USD conversion rule (half up per line), runtime (seconds on a laptop) |
| Retraining triggers | Policy file change, new currency, new merchant descriptor formats, any rule falling below 0.95 precision on a monthly audit sample |
| Contacts | Student's name, the controller as business owner |

The handoff checklist must pass: card written, validation doc present, experiments logged, no files from `data/` staged.

## Grading

| Grade | Bar |
|---|---|
| Pass | v1 and v2 tables with TP/FP/FN, v2 at 1.00 / 1.00 for all 8 rules, thresholds read from the policy file, model card exists |
| Strong | Error notes per rule, the tolerance sweep with a justified pick, blank-fx claims handled explicitly, stretch approval-chain answer (5, all self-approvals) |
| Redo | Ids from the answer key inside the detector, or precision/recall computed on the wrong unit (for example lines vs pairs for duplicates) |
