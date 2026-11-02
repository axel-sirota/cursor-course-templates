# Experiment Philosophy

The mindset behind how we do data science work — not just rules, but the reasoning.

---

## Why EDA before modeling

Every skipped EDA step is a wasted experiment. Data always lies — or at least misleads. Before you write a single line of training code, you must understand:

- What the distributions actually look like (not what the data dictionary says)
- Where the missing values are and why they're missing
- Which features are correlated — highly correlated features will make your model look better than it is
- Whether the label distribution is what you expect

The instinct to "just run a quick model and see" is almost always wrong. The quick model tells you almost nothing because you haven't controlled for the assumptions it's making about your data. EDA is not overhead — it is the work.

---

## Hypothesis-driven experimentation

Never run a model "to see what happens." Write the hypothesis before running:
- What do you expect the result to be?
- Why do you expect that?
- What would falsify it?

Log the hypothesis as an MLflow tag before the run:
```python
mlflow.set_tag("hypothesis", "Adding interaction features between age and income will improve AUC by >2%")
```

This practice forces you to think before you compute, makes experiments comparable, and prevents p-hacking — the habit of running 40 experiments and reporting the best one as if it were intentional.

---

## The reproducibility contract

If another data scientist cannot reproduce your result from the git repo + DVC remote alone, the experiment doesn't count. No "it worked on my machine." No "I had a slightly different version of the data."

The contract has three parts:
1. **Code**: pinned in git at the commit SHA logged in MLflow
2. **Data**: versioned with DVC, hash logged in MLflow
3. **Environment**: `requirements.txt` pinned and committed

If any of these three are missing, the result is anecdote, not science. Treat reproducibility as a hard requirement, not a nice-to-have.

---

## When to stop iterating

Diminishing returns are real. If the last 3 experiments improved the key metric by less than 1%, stop optimizing. Validate what you have.

The trap is: there is always one more thing to try. Feature engineering. A different algorithm. Hyperparameter tuning. Ensembling. Each has a cost: time, complexity, interpretability, maintenance burden. At some point, a 0.3% improvement in AUC is not worth doubling the model complexity or adding a week to the project.

Stopping rule: if 3 consecutive experiments yield <1% improvement on the validation metric, move to validation and handoff. Ship, measure in production, then iterate based on real-world feedback — not held-out benchmark performance.

---

## What "done" looks like

"Done" is not "accuracy is high." Done means:

- [ ] Model card complete — all sections filled, no placeholder text
- [ ] Test set evaluation run exactly once (not used for any tuning decision)
- [ ] Engineering handoff doc written: inputs, outputs, inference latency, memory requirements
- [ ] MLflow run tagged `"champion"` in the Model Registry
- [ ] Notebook runs top-to-bottom from a clean kernel without errors

If any of these are missing, the experiment is not done — it is a prototype. Prototypes are useful. Prototypes are not handoffs.

---

## Local vs Databricks/Spark

This stack (`python-datascience`) is for local/scikit-learn experiments. It is designed for datasets that fit in memory on a single machine — typically up to a few GB.

When to switch stacks:
- Data doesn't fit in memory → move to `python-spark`
- You need distributed feature engineering → move to `python-spark`
- You need SQL-first transformations at scale → move to `python-dbt-snowflake`

Don't fight pandas with 100GB datasets. The tool matters as much as the technique. Knowing when to switch is part of the skill.
