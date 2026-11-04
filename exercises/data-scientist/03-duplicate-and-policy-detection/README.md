# Exercise 3: Duplicate and policy detection

**Time:** 75 to 90 minutes
**You produce:** a detector that flags duplicate claims and policy violations, `docs/eval-detector.md` with precision and recall per rule against the answer key, and `docs/model-card-expense-detector.md` from `/ds-handoff`.

## Scenario

Northwind's controller wants every claim screened before approval. The audit team marked up three months of claims by hand, and that markup is the answer key. Your detector has to find what they found, and the controller wants to see, per rule, how many flags are real (precision) and how many real issues the detector misses (recall). A detector that flags 300 claims to find 80 problems will be switched off in a week.

The first version usually gets written in ten minutes and looks fine. The point of this exercise is to measure it, see where it is wrong, and fix it with the numbers in front of you.

## Inputs

| File | Use |
|---|---|
| `data/expense_lines.csv`, `data/expense_claims.csv`, `data/employees.csv` | What the detector reads |
| `data/expense_policy.json` | Thresholds. Read limits from this file, do not hard-code them |
| `data/labels/answer_key.json` | The labels. Copy it now: `mkdir -p workspaces/data-scientist/data/labels && cp exercises/_data/northwind/answer_key.json workspaces/data-scientist/data/labels/` |
| Your exercise 1 USD function and findings doc | Reuse them |

Label keys you score against:

| Rule | Label key in `answer_key.json` | Unit |
|---|---|---|
| Duplicate | `expense_lines.exact_duplicates` + `expense_lines.near_duplicates` | Unordered line pair |
| Duplicate claim | Claims holding the later line of each pair above | claim_id |
| Missing receipt over $75 | `expense_lines.missing_receipt_over_threshold` | line_id |
| Meal limit | `expense_lines.over_policy_limit` where `rule == "Meals"` | line_id |
| Alcohol | `expense_lines.alcohol_in_meals` | line_id |
| Weekend | `expense_lines.weekend_expenses` | line_id |
| Self-approval | `expense_claims.self_approved` | claim_id |
| Approval above limit | `expense_claims.approved_above_limit` | claim_id |

## Task

1. **Plan.** `/architect data-scientist exercises/data-scientist/03-duplicate-and-policy-detection/README.md`. One detector function per rule, one evaluation function shared by all.
2. **v1: write it fast.** Ask the agent for a first detector for all eight rules from the policy file and the scenario only. Do not give it the exercise 1 definitions. Run `/ds-experiment` and log it as `detector-v1`.
3. **Evaluate.** For each rule: predicted count, true count, TP, FP, FN, precision, recall. Precision = TP / predicted, recall = TP / true. Also a micro total over the six policy rules. Write it into `docs/eval-detector.md`.
4. **Read the errors.** For each rule below 1.00, print 5 false positives and 5 false negatives with the columns that matter. Write one line per rule on why it is wrong.
5. **v2: fix it.** Change the rules, not the labels. Log `detector-v2`. Repeat until every rule is at 1.00 / 1.00, or write down why a gap remains.
6. **Duplicate tolerance sweep.** Run the duplicate rule with amount tolerance 0, 1 and 100 cents and date tolerance 0, 1 and 3 days. Table of precision and recall for each of the 9 settings. Pick one and say why.
7. **Validate and hand off.** `/ds-validate` on v2 (there is no training, so "held-out" means: the rules were written from the policy, not from the labels; say so), then `/ds-handoff` for the model card. The card must say what each rule checks, the measured precision and recall, what it does not detect, and the input schema.

## Done when

- [ ] `experiments/log.md` has `detector-v1` and `detector-v2` with per-rule metrics
- [ ] `docs/eval-detector.md` has the v1 and v2 tables and the error notes
- [ ] v2 precision and recall match `checks/expected_findings.md` for every rule
- [ ] The tolerance sweep table is in the eval doc
- [ ] Every threshold comes from `expense_policy.json`
- [ ] `docs/model-card-expense-detector.md` exists and the `/ds-handoff` checklist passes
- [ ] Unit tests cover at least: a CAD line above 7500 CAD but under 7500 USD, a team meal with 4 attendees, a cocktails description, a duplicate pair on the same claim (not a duplicate by the definition)

## Commands to use

```
/architect data-scientist exercises/data-scientist/03-duplicate-and-policy-detection/README.md
/start-session data-scientist
/ds-experiment          # detector-v1, then detector-v2
/ds-validate            # on detector-v2
/ds-handoff             # model card
/next-session
```

- `/ds-experiment` expects a seed. The rules are deterministic; log seed `42` and note it is unused, so the reproducibility checker passes.
- `/ds-handoff` refuses to write the card without the validation doc. Run `/ds-validate` first.
- Watch that the agent does not "fix" a rule by reading ids out of `answer_key.json`. A rule that contains a line_id is cheating.

## Stretch

- Approval chain: the policy says the approver must be in the submitter's management chain. Check `approver_id` against the chain from `employees.csv`. How many approved or paid claims break it?
- Add the other limits (Lodging, Office supplies) and the 60-day rule. Expected sets are in exercise 1.
- An unsupervised score (for example IsolationForest on USD amount per category) for the outlier. Report where L-007001 ranks.

## Per stack notes

| Stack | How to do this exercise |
|---|---|
| python-datascience | `src/detectors.py` (one pure function per rule returning a set of ids), `src/evaluation.py` (`precision_recall(pred: set, truth: set)`), pytest for both. Notebook `notebooks/03_detector.ipynb` shows the tables |
| python-mlops | Detectors as a `screen` step with a CLI; MLflow run per version with one metric per rule (`precision_receipt`, `recall_receipt`, ...). The model card is logged as an artifact |
| python-spark | Gold transforms, one per rule, each returning ids. Duplicates: self-join on employee + merchant + currency with `a.line_id < b.line_id` and `a.claim_id != b.claim_id`, then filter on tolerance. Collect the small id sets to the driver for scoring; chispa tests on fixtures |
| python-dbt-snowflake | One mart per rule (`flag_receipt`, `flag_meal_limit`, ...) and a `flag_all` union. Load the label sets as seeds (flatten `answer_key.json` into `seeds/labels_<rule>.csv` with a short script) and compute TP/FP/FN in `analyses/` or a mart. Add a singular test per rule that fails if the mart and the seed disagree. Local: `dbt-duckdb` |
| r-tidyverse | `R/detectors.R` returning tibbles of ids, `R/evaluate.R`, testthat. `jsonlite::fromJSON("data/labels/answer_key.json")` gives data frames for each label list. Duplicates with `dplyr::inner_join(lines, lines, by = c("employee_id","merchant","currency"), relationship = "many-to-many")` then filter |
