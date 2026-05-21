# /ds-explore

EDA loop — profile dataset, visualize distributions, and document hypotheses.

## Steps

1. **Identify the dataset** — Ask the user for the dataset path. Default: list files in `data/` and ask which to use.

2. **Delegate to `data-profiler`** — Invoke the `data-profiler` subagent to produce a statistical profile of the dataset. The subagent reads the file via the `filesystem` MCP and saves `docs/profile-{dataset-name}.md`.

3. **Generate `docs/eda-{dataset-name}.md`** containing:
   - **Dataset shape** — row count, column count
   - **Data types** — dtype per column with null counts and null percentage
   - **Distribution summaries** — mean, median, std, min, max for numeric columns; top value counts for categorical columns
   - **Correlation matrix highlights** — top 5 positively and negatively correlated pairs
   - **Outlier flags** — columns with values beyond 1.5× IQR, with count and percentage of outliers
   - **3–5 hypotheses to test** — concrete, testable statements derived from the profile (e.g., "Feature X is predictive of target Y because their correlation is 0.72")

4. **Review hypotheses with the user** — Present the hypotheses and ask the user to confirm, revise, or replace them before proceeding. Do not move to `/ds-experiment` until the user approves the hypothesis list.

## Output

`docs/eda-{dataset-name}.md` — The experiment plan starts here. This file is the required input for `/ds-experiment`.

## Notes

- Do not modify the dataset — this command is read-only analysis.
- If `docs/` does not exist, create it before writing the output file.
- If the dataset is too large to profile in full, sample 10,000 rows and note the sampling in the EDA doc.
- If no dataset exists in `data/`, ask the user to place their data file there before continuing.
