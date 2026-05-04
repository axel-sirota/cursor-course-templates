# R + Tidyverse Phase Checklist

## Phase 0 — Skeleton

- [ ] `renv::init()` run, `renv.lock` committed to version control
- [ ] `_quarto.yml` configured with project title and `output-dir`
- [ ] `DESCRIPTION` file present (enables `devtools::document()` and `covr`)
- [ ] `R/` directory created with at least one stub function file per domain area
- [ ] `tests/testthat/` initialized (`usethis::use_testthat()` or manual setup) with at least one passing test
- [ ] `quarto render` succeeds on skeleton analysis document (`analysis/01_eda.qmd`)
- [ ] `lintr::lint_dir("R/")` passes with zero errors
- [ ] `.lintr` config file committed enforcing 80-char line length and snake_case
- [ ] `data/raw/`, `data/processed/` added to `.gitignore`
- [ ] `data/fixtures/` committed with at least one fixture CSV

---

## Phase 1 — Analysis (EDA)

- [ ] EDA Quarto document (`analysis/01_eda.qmd`) complete and renders cleanly from scratch
- [ ] All feature engineering logic extracted to `R/features.R` (no inline analysis logic in Quarto)
- [ ] testthat coverage on `R/features.R` > 80% (`covr::package_coverage()`)
- [ ] `set.seed(42)` called at top of every Quarto setup chunk and any test using randomness
- [ ] All plots use `theme_minimal()` + full `labs(title=, x=, y=, caption=)`
- [ ] `lintr::lint_dir("R/")` and `styler::style_dir("R/", dry = "fail")` both pass
- [ ] `renv::snapshot()` run after any new package installs; lockfile committed

---

## Phase 2 — Modeling

- [ ] tidymodels workflow defined: `recipe` + `parsnip` model spec + `workflow` object in `R/modeling.R`
- [ ] Cross-validation executed with `rsample::vfold_cv()` and metrics logged with `yardstick`
- [ ] Model card section drafted in `analysis/02_modeling.qmd` (data description, metrics, limitations)
- [ ] `fit_churn_model()` (or equivalent) has roxygen2 documentation with `@param` and `@return`
- [ ] Test for model evaluation function using known fixture data (predictable output, fixed seed)
- [ ] `testthat::test_dir("tests/testthat/")` passes with zero failures
- [ ] `set.seed()` set before every `rsample` split, `tune` operation, or model fit
- [ ] Fitted model saved to `models/` with `saveRDS()`; `models/` gitignored if > 50MB

---

## Phase 3 — Output / API

- [ ] Plumber API defined in `plumber/api.R` with at least `/predict` and `/health` endpoints
- [ ] Plumber endpoints are thin wrappers — all logic lives in `R/` functions, not in the endpoint body
- [ ] Plumber API tested locally with `httr2` or `curl` (document test commands in `plumber/README.md`)
- [ ] Report Quarto document (`analysis/03_report.qmd`) renders to both HTML and PDF without errors
- [ ] All `R/` functions have complete roxygen2 documentation (`devtools::document()` runs cleanly)
- [ ] `quarto render` succeeds for all three analysis documents in sequence
- [ ] Full CI gate passes: lint → style check → testthat → quarto render

---

## Pre-Merge Gate (all phases)

- [ ] `renv::restore()` produces a working environment from `renv.lock` alone
- [ ] `lintr::lint_dir("R/")` — zero linting errors
- [ ] `styler::style_dir("R/", dry = "fail")` — no style violations
- [ ] `testthat::test_dir("tests/testthat/")` — all tests green
- [ ] `quarto render` on all `.qmd` files — clean render, no warnings elevated to errors
- [ ] `covr::package_coverage()` on `R/` — > 80% line coverage
- [ ] No hardcoded absolute paths anywhere in `R/`, `tests/`, or `analysis/`
- [ ] `set.seed()` present before every random operation
