# R + Tidyverse Development Lifecycle Vibe

> Git workflow and session management: see `stacks/shared/vibe_git_workflow.md` and `stacks/shared/vibe_session_workflow.md`. This document covers R-specific lifecycle additions only.

---

## Quarto Document Lifecycle

A Quarto document moves through five states. Each state has a clear exit condition.

**1. Draft**
The document exists, chunks are named, `set.seed()` is in the setup chunk, and `quarto render` completes without error. Content is placeholder or partial. The exit condition is: it renders.

**2. In-Progress**
Analysis is being written. Functions are being extracted to `R/`. Tests are being added. The document may have `#| eval: false` chunks for unfinished sections. The exit condition is: all eval-true chunks render and all `R/` functions tested.

**3. Review**
All chunks render. All `R/` functions have testthat coverage > 80%. The document is rendered to HTML and shared with a reviewer. Comments are addressed in the document, not in Slack. The exit condition is: reviewer approval.

**4. Render-to-HTML (Final HTML)**
`quarto render --to html` with `embed-resources: true`. Output is a single self-contained `.html` file. Sent to stakeholders for feedback. No code changes after this point without incrementing the document version.

**5. Render-to-PDF (Final PDF)**
`quarto render --to pdf`. LaTeX or typst backend. Used for regulatory submissions, formal reports, and archiving. PDF output is committed to `_output/` and tagged in git.

---

## renv Session Start Protocol

This is mandatory. Every R session in this project begins with:

```r
renv::restore()
```

This ensures your local library matches `renv.lock` before you touch any code. If `renv::restore()` reports nothing to do, you're clean. If it installs packages, those were missing from your local cache — that's fine, it's doing its job.

CI does this automatically via `.github/workflows/`. You do it manually in interactive sessions.

**Why this matters:** R loads packages at session start. If your library diverged from `renv.lock` (you installed something for a personal experiment, a colleague changed the lockfile), you may be running different package versions than the lockfile specifies. `renv::restore()` fixes this before it causes a problem.

---

## Package Upgrade Discipline

Upgrading packages in R is a branch operation, never a main-branch operation.

**The upgrade workflow:**

```bash
git checkout -b upgrade/renv-2024-q4
```

```r
renv::update()           # update all packages to latest compatible versions
testthat::test_dir("tests/testthat/")  # run full test suite
```

```bash
quarto render analysis/01_eda.qmd
quarto render analysis/02_modeling.qmd
quarto render analysis/03_report.qmd
```

If all tests pass and all documents render, commit `renv.lock` and open a PR. Do not merge until someone else reviews the lockfile diff and the CI gate passes.

**Why this discipline:** `dplyr` and `ggplot2` have both shipped breaking changes in minor versions. An unreviewed upgrade that changes plot output or silently changes a `summarise()` result is a regression that may not be caught until stakeholder review. Treat package upgrades like dependency upgrades in any other language — with a PR, a diff, and a gate.

---

## Collaboration: renv.lock is package-lock.json

When two people work on the same R project, the source of truth for package versions is `renv.lock`. This is not optional and it is not a personal preference file — it is the reproducibility contract.

**Rules for collaboration:**

- `renv.lock` is committed. Never gitignore it.
- When you add a package, you commit the updated `renv.lock` in the same commit as the code that uses it. Never let the lockfile lag behind the code.
- When you pull changes that include a `renv.lock` update, run `renv::restore()` before running any R code.
- When there is a merge conflict in `renv.lock`, do not manually edit the JSON. Instead:
  1. Accept one version of `renv.lock`.
  2. Run `renv::install()` for any packages from the other branch's additions.
  3. Run `renv::snapshot()` to regenerate a clean lockfile.
  4. Commit the result.

**The parallel to the Node ecosystem:** `renv.lock` is `package-lock.json`. `renv::restore()` is `npm ci`. `renv::install()` + `renv::snapshot()` is `npm install <pkg>`. The mental model is identical; the tooling is R-specific.

---

## CI Configuration Reference

A minimal GitHub Actions workflow for R + Quarto:

```yaml
name: R CI

on: [push, pull_request]

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: r-lib/actions/setup-r@v2
        with:
          r-version: '4.4'

      - uses: r-lib/actions/setup-renv@v2

      - uses: quarto-dev/quarto-actions/setup@v2

      - name: Lint
        run: Rscript -e 'lintr::lint_dir("R/")'

      - name: Style check
        run: Rscript -e 'styler::style_dir("R/", dry = "fail")'

      - name: Test
        run: Rscript -e 'testthat::test_dir("tests/testthat/")'

      - name: Render
        run: quarto render
```

The `r-lib/actions/setup-renv@v2` action automatically runs `renv::restore()` using the committed lockfile. No manual restore step needed in CI.
