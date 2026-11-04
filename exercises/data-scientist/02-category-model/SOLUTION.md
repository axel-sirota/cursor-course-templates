# Exercise 2: instructor key

Expected numbers and bands are in `checks/expected_findings.md`. This file is the reference approach, the leakage explanation you want to hear, and what to look for when a student's numbers are off.

## Reference numbers (computed, seed 42)

| Item | Value |
|---|---|
| Split | sklearn `GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=42)`, groups `claim_id`: 7,297 train lines on 3,199 claims, 1,871 test lines on 800 claims, overlap 0 |
| Baseline A, majority class | Ground transport. Accuracy **0.2480**, macro F1 0.0497 |
| Baseline B, first-word rule | 38 distinct first words in train. Accuracy **0.9482**, macro F1 0.9350 |
| Lookup on the full descriptor string (alternative rule) | Accuracy 0.9808 |
| Reference model | char_wb TF-IDF (2 to 4, min_df 2) on `merchant_category_text` + `log1p(amount_cents)`, `LogisticRegression(max_iter=2000, random_state=42)`. Train accuracy 0.9746, **test accuracy 0.9824**, macro F1 0.9762, 33 errors |
| Same model, word TF-IDF, no amount | 0.9808 |
| Leakage run (+ `gl_account_hint` one-hot) | **1.0000** |
| `gl_account_hint` alone | 1.0000 |
| + `description` (stretch) | 1.0000 |

Reference code outline (python-datascience):

```python
SEED = 42
random.seed(SEED); np.random.seed(SEED)
lines = pd.read_csv("data/expense_lines.csv", dtype=str, keep_default_na=False)
lines["amount_cents"] = lines["amount_cents"].astype(int)
lab = lines[lines["category"] != ""].reset_index(drop=True)
tr_idx, te_idx = next(GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=SEED)
                      .split(lab, groups=lab["claim_id"]))
train, test = lab.iloc[tr_idx], lab.iloc[te_idx]
assert not set(train.claim_id) & set(test.claim_id)

features = ColumnTransformer([
    ("desc", TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 4), min_df=2), "merchant_category_text"),
    ("amt", FunctionTransformer(np.log1p), ["amount_cents"]),
])
model = Pipeline([("features", features),
                  ("clf", LogisticRegression(max_iter=2000, random_state=SEED))])
model.fit(train, train["category"])
```

## The leakage explanation you want to hear

1. `gl_account_hint` is the GL account the line will post to. The expense system fills it from `category` after the line is categorized. It is a 1:1 recoding of the label (crosstab: one account per category, blank exactly where category is blank).
2. At prediction time (card transaction just arrived, not yet categorized) the column is empty. A model that relies on it has nothing to work with in production.
3. So the 100% is not model quality. It is the model reading the answer. The honest number is run 3, about 98%.
4. Detection habits worth naming: any result at or near 100% on a real problem is a bug until proven otherwise; ablate one feature at a time; for each feature ask "when is this filled in, and by whom?"
5. Second trap (stretch): `description` also yields 100% here because each string belongs to one category. Unlike the hint, it is typed by the employee before submission, so it is legal for a submission-time model. It is not legal for the card-feed scenario. The point is that "legal" depends on the prediction moment, which must be written in the plan.

## Why 98% and not higher

All 33 run 3 errors are Boxmart Marketplace (532 labeled lines: 296 Office supplies, 236 Software). The same two descriptors appear for both categories and amounts overlap, so no card-feed feature separates them. Strong students say this, propose asking for the item-level data or a "needs review" output when the top probability is low, and note that L-000092 (unlabeled, Boxmart, 0.627) is the case in point.

## Why the rule loses to the model

61 of the rule's 97 errors come from point-of-sale prefixes: `SQ *RIVERSIDE GRILL` and `TST* SKYLINE STEAK` are Client entertainment but their first word (`SQ`, `TST`) is shared with Meals merchants (`SQ *LUMEN CAFE`). The other 36 are Boxmart. Character n-grams see the whole descriptor, so the model gets the POS cases right. A rule on the full descriptor string gets 0.9808, which is close to the model: a fair student conclusion is "a lookup table on the full descriptor is almost as good and easier to explain".

## Debugging off numbers

| Student result | Likely cause |
|---|---|
| Run 3 at 1.0000 | `gl_account_hint` or `description` in the features. Ask for the feature list |
| Run 3 in band but split is row-level | Accuracy does not give it away (row-level split, same model: 0.9782). Check the code: 1,002 claims would be on both sides. Fail the split requirement |
| Run 1 around 0.22 or 0.23 | Different split method or seed; fine, check the band |
| Run 2 below 0.92 | Forgot the majority fallback for unseen words, or built the rule on test data |
| `ConvergenceWarning` from LogisticRegression | Raw `amount_cents` fed unscaled. Accuracy barely moves (0.9802) but the warning means the fit did not finish; use `log1p` or a scaler |
| Run 3 below 0.96 | Usually a bug: labels shifted against rows after a merge, or blank-category lines kept. Descriptor-only variants all score about 0.98 (char n-grams 0.9808, word TF-IDF 0.9808) |
| Errors include NaN or 9,176 rows | Blank category lines not dropped |
| Different numbers on re-run | Seed not set before the split, or set after a random call |

## Validation doc: what good looks like

- Test vs train: 0.9824 vs 0.9746, no overfit flag.
- Slices: CAD is lowest (0.9444) but has 36 test lines, so it is flagged as unreliable, not as bias. No slice more than 10% relatively worse.
- Drift: class mix shifts by up to 3 points between train and test because claims move as a whole. Expected, not a data problem.
- Reproducibility: seed logged, re-run gives the same metrics.
- Risk paragraph: Boxmart ambiguity, the excluded leakage column, and the fact that the training data is three months of one company.

## Grading

| Grade | Bar |
|---|---|
| Pass | Grouped split with assertion, both baselines, run 3 in band, run 4 explained as leakage and dropped |
| Strong | Error analysis names Boxmart and the POS prefixes, the 8 predictions include the L-000092 doubt, stretch run 5 discussed |
| Redo | Reports run 3 or run 4 at 100% as the result, or no baselines, or row-level split |
