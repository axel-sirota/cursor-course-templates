# /ds-handoff

Generate model card + handoff notes for engineering or stakeholders.

## Prerequisites

- `docs/eda-{dataset}.md` exists
- At least one `docs/experiments/{date}-{experiment-name}.md` exists
- `docs/validation-{model}.md` exists (produced by `/ds-validate`)

## Steps

1. **Read all source documents** — Load and synthesize:
   - `docs/eda-{dataset}.md` — data provenance, shape, known issues
   - All relevant `docs/experiments/` files — experiment history, best model config
   - `docs/validation-{model}.md` — test metrics, bias findings, drift findings, reproducibility status

2. **Generate `docs/model-card-{name}.md`** with the following sections:

   ### What it does
   One paragraph in plain language for a non-technical audience. What problem does this model solve? What does it predict or classify?

   ### What it doesn't do
   Explicit limitations. Examples: "Does not generalize to users outside the training demographic," "Not designed for real-time inference (<100ms latency)," "Retrains required monthly."

   ### Training data
   - Source and collection method
   - Date range of data
   - Size (rows × columns after preprocessing)
   - Known biases or gaps in the training data

   ### Performance
   - Primary metric on representative test slice
   - Secondary metrics where applicable
   - Confidence intervals or variance if available

   ### Fairness
   - Bias findings from the validation report
   - Subgroups where performance degrades and by how much
   - Mitigation steps taken (if any)

   ### Deployment requirements
   - Python version and key dependencies (with pinned versions)
   - Expected input schema (column names, types, required vs optional)
   - Output schema (prediction format, probability scores, class labels)
   - Estimated inference latency per sample
   - Memory and compute requirements

   ### Retraining triggers
   - Data drift threshold that should trigger retraining
   - Performance degradation threshold that should trigger retraining
   - Recommended retraining cadence

   ### Contacts
   - Model owner (name + contact)
   - Team or project this model belongs to

3. **Output handoff checklist** — After the model card, produce a checklist:
   - [ ] Model card complete (`docs/model-card-{name}.md` written)
   - [ ] Validation passed (`docs/validation-{model}.md` shows acceptable test metrics)
   - [ ] Reproducibility confirmed (reproducibility-checker: all checks pass)
   - [ ] Model artifact saved (`artifacts/` contains trained model file)
   - [ ] Experiment log up to date (`docs/experiments/log.md` includes this run)
   - [ ] No raw data committed (verify with `git status` — no CSVs or Parquets staged)

## Notes

- Do not write the model card until validation is complete — a model card without a validation report is incomplete.
- If any checklist item fails, surface it clearly and block the handoff until resolved.
- The model card is the deliverable for engineering and stakeholders — write it for them, not for yourself.
