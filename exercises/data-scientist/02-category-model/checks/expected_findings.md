# Exercise 2: expected findings

Open this after your four runs are logged. Reference values come from scikit-learn 1.9 with `GroupShuffleSplit(test_size=0.2, random_state=42)` grouped by `claim_id`. Other libraries and other split methods give a different split, so check against the **band**, not the exact value.

## Split

| Check | Reference (sklearn, seed 42) | Must hold in every stack |
|---|---|---|
| Labeled lines | 9,168 (9,176 minus 8 blank category) | Same |
| Train / test lines | 7,297 / 1,871 | Test is 18% to 22% of lines |
| Train / test claims | 3,199 / 800 | Test is about 20% of claims |
| Claims in both sets | 0 | 0 |
| Same split done row-level (`train_test_split`, stratified, seed 42) | 1,002 claims in both sets | Not allowed |

## Runs

| Run | Features | Reference accuracy | Reference macro F1 | Band (any stack, any seed) |
|---|---|---|---|---|
| 1. Majority class (Ground transport) | none | 0.2480 | 0.0497 | 0.20 to 0.27 |
| 2. First-word rule | first word of `merchant_category_text` | 0.9482 | 0.9350 | 0.92 to 0.97 |
| 3. Model | `merchant_category_text` + `amount_cents` | 0.9824 | 0.9762 | 0.96 to 0.99 |
| 4. Leakage check | run 3 + `gl_account_hint` | 1.0000 | 1.0000 | 1.0 (this is the point) |

Seed sweep with the reference code (seeds 42, 0, 1, 2, 3): majority 0.2235 to 0.2480, rule 0.9354 to 0.9526, model 0.9734 to 0.9838.

**Run 3 at 1.00 is a fail.** With descriptor and amount only, the ceiling is below 1.0 because Boxmart Marketplace sells both Software and Office supplies under the same descriptors. A perfect score means `gl_account_hint` or `description` got into the features.

## What the errors are

| Run | Errors on the reference test set | Cause |
|---|---|---|
| 2. Rule | 97: 61 Client entertainment predicted as Meals, 36 Software predicted as Office supplies | `SQ *RIVERSIDE GRILL` and `TST* SKYLINE STEAK` start with a point-of-sale prefix (`SQ`, `TST`) shared with Meals merchants, so the first word is not the merchant. Boxmart maps to its majority category |
| 3. Model | 33, all Boxmart Marketplace: 25 Software predicted as Office supplies, 8 the other way | Same descriptors (`BOXMART MKTP US*2K4`, `BOXMART MKTPLACE`) for both categories, and amounts overlap (train medians 12,732 vs 15,004 cents). Not fixable with card-feed features |

## Leakage

| Check | Expected |
|---|---|
| `gl_account_hint` vs `category` crosstab | Exactly one account per category and one category per account (6100 Meals, 6110 Lodging, 6120 Airfare, 6130 Ground transport, 6140 Software, 6150 Office supplies, 6160 Training, 6170 Client entertainment) |
| Blank pattern | `gl_account_hint` is blank on exactly the 8 lines where `category` is blank |
| Model on `gl_account_hint` alone | 1.0000 |
| Doc says | The column is filled from the label after categorization, so it does not exist when the card transaction arrives. The 100% measures a copy of the answer, not the model. Excluded |

## Validation (reference model)

| Slice | Test lines | Accuracy |
|---|---|---|
| USD | 1,706 | 0.9830 |
| EUR | 67 | 0.9851 |
| GBP | 62 | 0.9839 |
| CAD | 36 | 0.9444 (under 100 lines: note as unreliable) |
| Engineering / Finance / Marketing / Operations / Sales / Support | 371 / 58 / 227 / 143 / 813 / 259 | 0.9892 / 0.9828 / 0.9736 / 0.9930 / 0.9803 / 0.9807 |

No slice is more than 10% relatively worse than overall, so nothing is flagged. Train accuracy 0.9746 vs test 0.9824: no overfitting. Class mix shifts a little between train and test (Ground transport 21.9% train vs 24.8% test) because whole claims move together.

## The 8 unlabeled lines (reference model)

| line_id | descriptor | predicted | probability | likely right? |
|---|---|---|---|---|
| L-000092 | BOXMART MKTPLACE | Office supplies | 0.627 | No: the description is "Screen recorder license", so Software. Lowest confidence of the 8 |
| L-000542 | SWIFTCAB*FARE | Ground transport | 0.976 | Yes |
| L-002881 | DESKWORKS STORE 88 | Office supplies | 0.973 | Yes |
| L-004343 | DESKWORKS STORE 88 | Office supplies | 0.977 | Yes |
| L-005471 | TST* SKYLINE STEAK | Client entertainment | 0.977 | Yes ("Client dinner") |
| L-005932 | RIDEO *TRIP HELP.RIDEO | Ground transport | 0.986 | Yes |
| L-006886 | ROADRUNNER RAC | Ground transport | 0.978 | Yes |
| L-007780 | RIDEO *TRIP HELP.RIDEO | Ground transport | 0.989 | Yes |

## Stretch

| Question | Reference answer |
|---|---|
| Run 5, + `description` | 1.0000 on the reference split (0.9973 to 1.0000 across seeds for a description-only lookup). Every description string in this dataset appears under exactly one category, so it is a near-perfect label proxy. Not the same as run 4: an employee really types it before submitting, so it is a legal feature at submission time. Still not available in the card-feed scenario, and real free text is never this clean, so it needs a check with the data owner |
| Exact-duplicate pairs split across train and test | 32 of 90 |
| Run 3 with a split by `employee_id` (seed 42) | 1,822 test lines from 24 employees, accuracy 0.9726. Slightly lower than 0.9824: no employee's own repeat purchases help the test score |
| Seed spread, seeds 42, 0, 1, 2, 3 | See the seed sweep line under "Runs" |
