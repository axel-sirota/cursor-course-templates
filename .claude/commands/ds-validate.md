# /ds-validate

Validate model on held-out data, check for bias and distribution drift.

## Prerequisites

- A trained model artifact from `/ds-experiment` (in `artifacts/`)
- A held-out test set that was NOT used during training or validation

## Steps

1. **Load model and test set** — Load the model artifact from `artifacts/` and the held-out test set. Confirm with the user that the test set has not been used during training or validation. If uncertain, stop and ask.

2. **Compute test metrics** — Evaluate the model on the test set using the same metric(s) from the experiment doc. Compare test metrics against validation metrics to check for overfitting:
   - Large gap (>5% relative) between val and test performance → flag as overfit risk
   - Test performance significantly worse than reported → flag for investigation

3. **Bias check** — If the dataset contains demographic or categorical columns (e.g., gender, age group, region, product category), split the test metrics by each key column and compare:
   - Flag any subgroup where performance is more than 10% relatively worse than the overall metric
   - Note subgroups with fewer than 30 samples as statistically unreliable

4. **Distribution drift check** — Compare training data distributions vs. test data distributions for each feature:
   - Numeric features: compare means and standard deviations
   - Categorical features: compare value frequencies
   - Flag features where distributions diverge significantly (>20% shift in mean or dominant category)

5. **Delegate to `reproducibility-checker`** — Invoke the `reproducibility-checker` subagent to verify the experiment can be reproduced from the logged seed. Record pass/fail per check.

6. **Output `docs/validation-{model-name}.md`** containing:
   - **Test metrics vs validation metrics** — side-by-side comparison, overfitting assessment
   - **Bias findings** — metric breakdown by subgroup; any flagged disparities
   - **Drift findings** — feature-by-feature drift summary; any flagged features
   - **Reproducibility** — pass/fail per reproducibility check from `reproducibility-checker`
   - **Risk summary** — a concise paragraph summarizing risks for inclusion in the model card

## Notes

- Do not retrain or tune the model during this step — validation is read-only assessment.
- If no demographic columns exist, note that bias analysis was not applicable and state why.
- If the test set is very small (<100 samples), note this as a validation limitation.
