# /ds-experiment

Run a model experiment with tracked params, metrics, and seed.

## Prerequisites

- `docs/eda-{dataset}.md` exists (produced by `/ds-explore`)
- A random seed value is defined or agreed upon for this session

## Steps

1. **Read the EDA doc** — Load `docs/eda-{dataset}.md`. Identify which hypothesis from the EDA doc is being tested in this experiment. If multiple hypotheses exist, ask the user which one to address.

2. **Set and log the seed** — Define the experiment seed. Emit the seed-setting code before any random operation:
   ```python
   import random, numpy as np
   SEED = 42  # or user-specified value
   random.seed(SEED)
   np.random.seed(SEED)
   # torch.manual_seed(SEED) if using PyTorch
   # tf.random.set_seed(SEED) if using TensorFlow
   ```
   Record the seed value in the experiment definition.

3. **Define the experiment** — Specify and confirm with the user:
   - Model type (e.g., LogisticRegression, RandomForest, XGBoost, neural net)
   - Hyperparameters
   - Feature set and target column
   - Train/validation split ratio (e.g., 80/20)
   - Evaluation metric(s) appropriate to the task (accuracy + F1 for classification; RMSE + MAE for regression)

4. **Run the experiment** — Implement and execute the experiment in a notebook (`notebooks/`) or `.py` script. Save the trained model artifact to `artifacts/`.

5. **Delegate to `experiment-tracker`** — Invoke the `experiment-tracker` subagent to append a structured entry to `docs/experiments/log.md`.

6. **Output `docs/experiments/{date}-{experiment-name}.md`** containing:
   - **Hypothesis tested** — copied from EDA doc
   - **Seed value** — the exact integer used
   - **Model config** — type, hyperparameters, feature list, target, split ratio
   - **Train metrics** — on the training set
   - **Validation metrics** — on the held-out validation set
   - **Artifact paths** — saved model file, feature importance plot (if applicable)
   - **Next experiment to try** — one concrete follow-up based on these results

## Notes

- The test set (if one exists) is held out and NEVER used during this step — it is reserved for `/ds-validate`.
- If `docs/experiments/` does not exist, create it before writing the output file.
- If `artifacts/` does not exist, create it before saving model artifacts.
- Each experiment gets its own dated doc — do not overwrite previous experiment docs.
