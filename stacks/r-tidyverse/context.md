# Project Context: R + Tidyverse

## Architecture Shape
Statistical Computing / Notebook — reproducible R analysis, statistical modeling, and optional API output via Plumber (advanced — not required for analysis deliverables). Use for: actuarial analysis, statistical hypothesis testing, regulatory reporting, exploratory data analysis with formal write-up.
Use python-datascience for: ML-first work, Python-native data teams, sklearn/deep learning models.
Use python-spark for: distributed data at scale (>1TB), cluster-based processing.

## Tech Stack
- **Language**: R 4.4+
- **Core packages**: tidyverse 2.0+ (dplyr, ggplot2, tidyr, purrr, readr, stringr, forcats, lubridate)
- **Modeling**: tidymodels 1.2+ (recipes, parsnip, rsample, yardstick, tune, workflows)
- **Reporting**: Quarto 1.5+ (replaces R Markdown; .qmd files)
- **API** (optional): Plumber 1.2+ — expose R analysis functions as REST endpoints when integration with other systems is needed. Not required for analysis-only projects.
- **Testing**: testthat 3.2+ (3rd edition — use `expect_snapshot()`, `expect_error()`)
- **Linting/Style**: lintr 3.1+ (tidyverse style guide enforced), styler 1.10+
- **Reproducibility**: renv 1.0+ (lockfile-based package management, committed to repo)
- **Data versioning**: pins 1.3+ (board-based artifact storage) or DVC

## Vibe & Style
- **Coding Style**: snake_case for all objects and functions. `<-` for assignment (never `=`). Pipe operator `|>` (native R 4.1+, not magrittr `%>%`).
- **Architecture**: Script → Function → Package progression. Analysis lives in Quarto documents. Reusable logic extracted to `R/` functions. No raw scripts in root.
- **Pattern**: Tidy data principles. Long > wide. One observation per row. Explicit column selection — never positional `[,1]`.
- **Reproducibility**: `renv::snapshot()` after every package add. `set.seed()` before any random operation. Quarto renders must be self-contained.

## Key Rules
- **renv lockfile is sacred**: `renv.lock` is committed. `renv::restore()` must reproduce the environment exactly. Never `install.packages()` without `renv::snapshot()` after.
- **Functions over scripts**: analysis logic in `R/*.R` functions, orchestrated by Quarto. No 300-line analysis scripts.
- **Tidy evaluation**: use `{{ }}` (curly-curly) for column name arguments in custom dplyr functions. Never use `deparse(substitute())` hacks.
- **ggplot2 theme**: every plot sets `theme_minimal()` + explicit labels (`labs(title=, x=, y=, caption=)`). No default grey background in deliverables.
- **testthat 3rd edition**: `local_edition(3)` in every test file. Use `expect_snapshot()` for complex outputs.

## Entry Point & Structure
- **Entry point**: `analysis/01_eda.qmd` — start here; renders the full exploratory analysis
- **Rendering**: `quarto render analysis/` — renders all numbered analysis documents in sequence
- **Config/env**: `.Renviron` for secrets (API keys, DB passwords) loaded automatically by R on startup; `dotenv::load_dot_env()` for explicit `.env` file in scripts; data paths passed as function arguments (never `Sys.getenv()` inside functions)
- **Persistence**: local files (`data/raw/`, `data/processed/`); `pins` board for shared artifacts; no database unless Plumber API uses one
- **Test command**: `testthat::test_dir("tests/testthat/")` or `Rscript -e 'testthat::test_dir("tests/testthat/")'`

## Active Phase
- Current: Phase 0 (Skeleton)
