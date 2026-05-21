# R + Tidyverse Architecture Vibe

## When R, Not Python

The honest answer is: R wins when the domain owns R.

**Actuarial math** — survival analysis (`survival`, `flexsurv`), GLMs with offset terms, credibility theory — these are written first in R, documented in R, and the actuaries who review them know R. Translating to Python introduces translation risk with zero statistical gain.

**Clinical trials** — R is the FDA-standard language for statistical analysis in drug development (CDISC, ADaM datasets, `Hmisc`, `rms`). The submission packages are R Markdown / Quarto documents rendered to PDF. If your deliverable is a clinical study report, it is R.

**Econometrics** — instrumental variables, panel data, difference-in-differences, time series with `forecast`/`fable` — the econometrics R ecosystem (`AER`, `plm`, `lmtest`, `sandwich`) has decades of peer-reviewed work behind it. Python equivalents exist but are thinner.

**When stakeholders speak ggplot2** — if your stakeholders are statisticians who paste ggplot2 code into their slides, producing Python matplotlib output creates friction. Meet them in their tool.

Use python-datascience when: the team is Python-native, the model is sklearn/PyTorch/TensorFlow, or the deliverable plugs into a Python microservice ecosystem.

---

## tidymodels as the ML Framework

tidymodels is what caret tried to be: a unified interface for the entire ML workflow, built on tidy principles.

**Why tidymodels > caret:**
- Modern API — caret was designed before the tidyverse. tidymodels is designed for it.
- `parsnip` abstracts engine-specific APIs behind a consistent interface. The same code trains logistic regression (`glm`), random forest (`ranger`), and gradient boosting (`xgboost`) — swap one line.
- `recipes` makes preprocessing a first-class, reproducible, pipeable object. Steps are applied to training data and learned transformations are applied to test data automatically — no data leakage.
- `workflows` bundles recipe + model into a single object that you fit, predict, and save together. The bundle goes to production, not the model alone.
- `tune` + `rsample` + `yardstick` form a complete cross-validation loop with tidy metrics output.

**The tidymodels mental model:**

```
rsample::vfold_cv()     # define resampling strategy
recipes::recipe()       # define preprocessing steps
parsnip::model_spec()   # define model type + engine
workflows::workflow()   # bundle recipe + model
tune::tune_grid()       # search hyperparameter space
yardstick::metrics()    # evaluate on holdout
workflows::fit()        # refit on full training data
```

Everything is a tidy data frame. Metrics are rows. Hyperparameters are columns. You can `dplyr::filter()` your tuning results.

---

## Quarto Over R Markdown

Quarto is the successor to R Markdown, built by Posit and designed to be language-agnostic from day one.

**Why Quarto:**
- Python, Julia, and Observable JS chunks work natively — the document is not tied to R.
- Cross-referencing is built in (`@fig-tenure-plot`, `@tbl-summary`) without knitr hacks.
- Native reveal.js slides, Beamer PDF slides, Word, and HTML book formats — same syntax, different `format:` key.
- `freeze: auto` in `_quarto.yml` means chunks only re-execute when source changes — fast iteration on large documents.
- `embed-resources: true` produces a single HTML file with all assets inlined — safe to email to stakeholders.

**The render contract:** A Quarto document renders cleanly in a fresh R session or it does not exist. Objects from a previous interactive session are invisible to `quarto render`. This is enforced by design and by CI.

---

## renv Is Non-Negotiable

R's package ecosystem changes silently. A `ggplot2` version bump can change plot output. A `dplyr` version bump can change column ordering behavior. Without version pinning, an analysis that was correct in January may produce different numbers in July — with no warning.

`renv` is the answer. It pins every package version (and the R version itself, in `.rprofile`) to a lockfile that can reproduce the exact library state on any machine.

**The mental model:** `renv.lock` is to R what `package-lock.json` is to Node, or what `requirements.txt` + `pip freeze` is to Python — except R's base library also varies between R versions, so you need to pin that too (via the `R` field in `renv.lock`).

**The three commands:**
- `renv::restore()` — bring your library to the lockfile state. Run at the start of every session and in CI.
- `renv::install()` — install a package and track it. Never use `install.packages()` directly.
- `renv::snapshot()` — update the lockfile after installs. Commit the result.

**What happens without renv:** A collaborator runs your analysis six months later, gets different numbers, and can't tell if the code changed or the packages changed. That is a reproducibility failure. In regulated industries (pharma, finance), it is a compliance failure.

---

## Plumber as the Production Handoff

When the statistical analysis is complete and the fitted model needs to be consumed by an engineering system (Node backend, Python microservice, dashboard), Plumber is the bridge.

**The pattern:**
1. Fit the model, save it with `saveRDS()`.
2. Write `R/modeling.R` predict function that loads the model and returns predictions.
3. Write `plumber/api.R` as a thin HTTP wrapper around that function.
4. Engineering calls `POST /predict` with JSON — they never need to understand R.

**What Plumber is:**
- An HTTP API server for R functions. One `#*` decorator per endpoint.
- Fast enough for moderate inference loads (hundreds of requests/minute).
- The right tool for exposing R models to non-R consumers.

**What Plumber is not:**
- A production-grade web server. Put nginx or a load balancer in front of it.
- An async server. Each request blocks an R process. Scale horizontally with multiple Plumber processes behind a proxy.
- A replacement for MLflow model serving or Vetiver for high-throughput production. Use `vetiver` + `pins` for model versioning when scale matters.

**The Vetiver upgrade path:** When Plumber-direct becomes insufficient, `vetiver::vetiver_model()` wraps a tidymodels workflow into a versioned, deployable object. `vetiver::vetiver_api()` generates the Plumber router automatically. The handoff to engineering stays the same; the internals get production-hardened.
