# Exercise 2: Category model

**Time:** 75 to 90 minutes
**You produce:** four logged experiments in `experiments/log.md` (two baselines, one model, one leakage check), `docs/validation-category-model.md` from `/ds-validate`, and predictions for the 8 lines with no category.

## Scenario

When a card transaction lands in Northwind Expense, the app should pre-fill the expense category before the employee opens the claim. At that moment the app has the card feed only: the raw descriptor (`merchant_category_text`, for example `SQ *RIVERSIDE GRILL`), the amount, the currency and the date. The employee has not typed a description yet, and nobody has coded the line to a GL account.

Product wants to know: how accurate can this be, and is it better than a lookup table? A colleague already tried and reported "100% accuracy". Your manager does not believe it. Neither should you.

## Inputs

| File | Use |
|---|---|
| `data/expense_lines.csv` | Features and the `category` label |
| `data/expense_claims.csv` | Only for grouping by claim |
| `docs/eda/data-quality-findings.md` | Your exercise 1 doc. `/ds-experiment` reads it for the hypothesis |

## Rules for this exercise

| Rule | Why |
|---|---|
| Seed `42`, set before any random step, logged in every run | Reproducibility; the expected numbers use it |
| Drop the 8 lines with blank `category` from training and test. Keep them aside as the "predict these" set | They have no label |
| Split 80/20 **by `claim_id`**: every line of a claim goes to the same side. Assert zero claims in both sets | Lines on one claim share employee, trip and dates. A row-level random split puts 1,002 claims on both sides |
| Features for the scored model: `merchant_category_text` and `amount_cents` only | That is what exists when the card transaction arrives |
| Baselines first, model second | A model that does not beat a lookup table is not worth deploying |
| Accuracy and macro F1 on the test set for every run | Ground transport is 25% of lines; accuracy alone hides weak small classes |

## Task

1. **Plan.** `/architect data-scientist exercises/data-scientist/02-category-model/README.md`. The experiment plan must list the four runs below before you start.
2. **Split.** Group split by `claim_id`, test size 0.2, seed 42. Print line and claim counts per side and the overlap (must be 0).
3. **Run 1, baseline A: majority class.** Predict the most common training category for every test line.
4. **Run 2, baseline B: simple rule.** Take the first word of `merchant_category_text` (split on space and `*`, drop `&`), map it to the most common category for that word in the training set, fall back to the majority class. No ML.
5. **Run 3, model.** Any classifier you like on `merchant_category_text` + `amount_cents`. Reference: character n-gram TF-IDF (2 to 4) on the descriptor, `log1p(amount_cents)`, logistic regression. Log train and test metrics and the confusion matrix. Read the errors: which merchant causes most of them, and why can no model on these features fix it?
6. **Run 4, leakage check.** Add `gl_account_hint` to the run 3 features and train again. Record what happens. Then answer in the validation doc: what is this column, when is it filled in, would it exist at prediction time, and what does it mean that the score jumped? Drop it.
7. **Validate.** `/ds-validate artifacts/<run 3 model>`: test metrics, accuracy by `currency` and by department (join claims and employees), train vs test class distribution, reproducibility check from the logged seed.
8. **Predict the 8 unlabeled lines** with the run 3 model. List line_id, predicted category and the predicted probability. Compare with your guesses from exercise 1. Which one is the model least sure about, and is it right?

## Done when

- [ ] `experiments/log.md` has 4 rows, each with seed 42, feature list, train and test sizes, accuracy and macro F1
- [ ] The split assertion (0 claims in both sets) is in code and passes
- [ ] Run 2 beats run 1 by a wide margin, and run 3 beats run 2
- [ ] Run 3 test accuracy is in the band in `checks/expected_findings.md`
- [ ] `docs/validation-category-model.md` explains run 4 as leakage in your own words and states `gl_account_hint` is excluded
- [ ] Predictions for the 8 unlabeled lines are in the validation doc
- [ ] The notebook or pipeline runs top to bottom from a clean state

## Commands to use

```
/architect data-scientist exercises/data-scientist/02-category-model/README.md
/start-session data-scientist
/ds-experiment            # once per run, 4 times
/ds-validate artifacts/<model file>
/next-session
```

- `/ds-experiment` asks which EDA hypothesis the run tests. Point it at the Boxmart and the `gl_account_hint` hypotheses from exercise 1.
- `/ds-validate` asks you to confirm the test set was not used for training. Say no if you tuned anything on it.
- If the agent reports 100% on run 3, ask it to list the features it used. That is the most common way this exercise goes wrong.

## Stretch

- **Submission-time variant.** Add `description` to the run 3 features (as if the model ran after the employee types). Log it as run 5. Is the jump the same kind of problem as run 4? Look at how many categories each `description` string appears under, and write one paragraph on what you would ask the data owner before trusting it.
- **Duplicate leak.** Count how many exact-duplicate pairs from exercise 1 have one line in train and one in test. Split by `employee_id` instead of `claim_id` and compare run 3 accuracy.
- **Seeds.** Re-run runs 1 to 3 with seeds 0, 1, 2, 3 and report the spread.

## Per stack notes

| Stack | How to do this exercise |
|---|---|
| python-datascience | scikit-learn: `GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=42)` with `groups=claim_id`; `ColumnTransformer` with `TfidfVectorizer(analyzer="char_wb", ngram_range=(2,4), min_df=2)` and a `FunctionTransformer(np.log1p)`; `LogisticRegression(max_iter=2000, random_state=42)`. Save with `joblib` to `artifacts/` |
| python-mlops | Same model as a `train` step; log each run to MLflow with params (seed, features, split sizes), metrics and the model. The leakage run is tagged `leakage_check=true` so nobody promotes it |
| python-spark | `pyspark.ml`: `RegexTokenizer` + `NGram` + `HashingTF` + `IDF` on the descriptor, `VectorAssembler` with `log1p(amount)`, `LogisticRegression`. `randomSplit` splits rows, not claims: build the split from `abs(xxhash64(claim_id)) % 5 == 0` for test. Your split sizes will differ from sklearn's; the accuracy band still applies |
| python-dbt-snowflake | dbt builds the features: `stg_expense_lines` then `mart_category_training` with `split` computed from a hash of `claim_id` (e.g. `abs(hash(claim_id)) % 5 = 0` is test). Add a dbt test that no `claim_id` has both splits. Train in a Python notebook or script that reads the mart (`duckdb.connect("dev.duckdb")` locally; Snowpark or a dbt Python model on Snowflake). Baseline B can be pure SQL |
| r-tidyverse | tidymodels: `rsample::group_initial_split(lines, group = claim_id, prop = 0.8)` after `set.seed(42)`; recipe with `textrecipes::step_tokenize(merchant_category_text, token = "character_shingle")` or word tokens + `step_tfidf`, `step_log(amount_cents, offset = 1)`; `multinom_reg(penalty = 0.001) %>% set_engine("glmnet")`. `yardstick::accuracy` and `f_meas(estimator = "macro")` |
