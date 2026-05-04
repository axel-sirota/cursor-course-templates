# R + Tidyverse Project Starter

This document provides scaffold commands and file templates for initializing a new R/Tidyverse project. Follow the steps in order. All commands are run from the R console unless noted otherwise.

---

## 1. Initialize renv

Open R in the project root and run:

```r
# Initialize renv for this project
renv::init()

# Install all core packages
renv::install(c(
  "tidyverse",
  "tidymodels",
  "quarto",
  "plumber",
  "testthat",
  "lintr",
  "styler",
  "withr",
  "pins",
  "here",
  "httptest2",
  "covr",
  "roxygen2",
  "devtools",
  "jsonlite"
))

# Snapshot the lockfile (commit this file)
renv::snapshot()
```

The generated `renv.lock` must be committed to version control. Never gitignore it.

---

## 2. `_quarto.yml` — Project-Level Config

Place in project root:

```yaml
project:
  title: "Your Project Name"
  type: default
  output-dir: _output

execute:
  freeze: auto
  echo: true
  warning: false
  message: false

format:
  html:
    theme: cosmo
    toc: true
    toc-depth: 3
    code-fold: true
    embed-resources: true
  pdf:
    documentclass: article
    toc: true
```

---

## 3. `DESCRIPTION` — Package Metadata (enables devtools + covr)

Even for non-package projects, a `DESCRIPTION` file enables `devtools::document()` for roxygen2 and `covr::package_coverage()` for coverage:

```
Package: projectname
Title: Your Project Title
Version: 0.1.0
Authors@R:
    person("First", "Last", email = "first.last@example.com", role = c("aut", "cre"))
Description: Short description of the project purpose.
License: MIT + file LICENSE
Encoding: UTF-8
Roxygen: list(markdown = TRUE)
RoxygenNote: 7.3.2
Imports:
    dplyr,
    ggplot2,
    tidyr,
    purrr,
    readr,
    tidymodels,
    recipes,
    parsnip,
    workflows,
    yardstick,
    rsample,
    here
Suggests:
    testthat (>= 3.0.0),
    withr,
    covr
```

---

## 4. `.lintr` — Linting Configuration

Place in project root:

```ini
linters: linters_with_defaults(
  line_length_linter(80),
  assignment_linter(),
  object_name_linter("snake_case"),
  pipe_consistency_linter(),
  trailing_whitespace_linter(),
  commented_code_linter()
)
exclusions: list("renv")
```

---

## 5. Example `R/features.R` — Roxygen2 + Tidy Eval

```r
#' Compute derived features from raw customer data
#'
#' Adds `tenure_months` (continuous) and `high_value` (binary integer flag)
#' to the input data frame. Removes `tenure_days` to avoid redundancy.
#'
#' @param df A data frame with columns: `customer_id`, `tenure_days`
#'   (integer), `monthly_spend` (double), `support_tickets` (integer),
#'   `churned` (integer 0/1).
#' @return A data frame with `tenure_days` replaced by `tenure_months`
#'   and a new `high_value` column.
#' @export
#'
#' @examples
#' df <- data.frame(
#'   customer_id = "c1", tenure_days = 365L,
#'   monthly_spend = 120.0, support_tickets = 0L, churned = 0L
#' )
#' compute_features(df)
compute_features <- function(df) {
  df |>
    dplyr::mutate(
      tenure_months = tenure_days / 30,
      high_value = dplyr::if_else(monthly_spend > 100, 1L, 0L)
    ) |>
    dplyr::select(-tenure_days)
}

#' Generic ratio computer using tidy evaluation
#'
#' @param df A data frame.
#' @param numerator <[`data-masking`][dplyr::dplyr_data_masking]> Column to use
#'   as numerator.
#' @param denominator <[`data-masking`][dplyr::dplyr_data_masking]> Column to
#'   use as denominator.
#' @return A data frame with an added `ratio` column.
#' @export
compute_ratio <- function(df, numerator, denominator) {
  df |>
    dplyr::mutate(ratio = {{ numerator }} / {{ denominator }})
}
```

---

## 6. Example `tests/testthat/test-features.R` — testthat 3rd Edition

```r
local_edition(3)

test_df <- data.frame(
  customer_id = c("c1", "c2", "c3"),
  tenure_days = c(365L, 90L, 730L),
  monthly_spend = c(50.0, 120.0, 200.0),
  support_tickets = c(1L, 5L, 0L),
  churned = c(0L, 1L, 0L)
)

test_that("compute_features adds tenure_months", {
  result <- compute_features(test_df)
  expect_true("tenure_months" %in% names(result))
  expect_equal(result$tenure_months[1], 365 / 30)
})

test_that("compute_features adds high_value flag", {
  result <- compute_features(test_df)
  expect_equal(result$high_value, c(0L, 1L, 1L))
})

test_that("compute_features removes tenure_days", {
  result <- compute_features(test_df)
  expect_false("tenure_days" %in% names(result))
})

test_that("compute_features handles empty data frame", {
  empty_df <- test_df[0, ]
  result <- compute_features(empty_df)
  expect_equal(nrow(result), 0L)
  expect_true("tenure_months" %in% names(result))
})

test_that("compute_features handles NA in monthly_spend", {
  na_df <- test_df
  na_df$monthly_spend[1] <- NA_real_
  result <- compute_features(na_df)
  expect_true(is.na(result$high_value[1]))
})
```

---

## 7. Example `analysis/01_eda.qmd` — Named Chunks + Tidy Pipeline

```qmd
---
title: "Exploratory Data Analysis"
author: "{Your Name}"
date: today
format:
  html:
    code-fold: true
    toc: true
---

```{r setup}
#| include: false
set.seed(42)
library(tidyverse)
library(here)
source(here::here("R/features.R"))
```

## Data Loading

```{r load-data}
df_raw <- readr::read_csv(
  here::here("data/raw/customers.csv"),
  show_col_types = FALSE
)
dplyr::glimpse(df_raw)
```

## Feature Engineering

```{r compute-features}
df <- compute_features(df_raw)
```

## Summary Statistics

```{r summary-stats}
df |>
  dplyr::summarise(
    n = dplyr::n(),
    churn_rate = mean(churned),
    median_tenure_months = median(tenure_months),
    median_spend = median(monthly_spend)
  )
```

## Churn Rate by Tenure

```{r plot-tenure-churn}
df |>
  dplyr::mutate(
    churned_label = factor(churned, labels = c("Retained", "Churned"))
  ) |>
  ggplot2::ggplot(ggplot2::aes(x = tenure_months, fill = churned_label)) +
  ggplot2::geom_histogram(bins = 30, alpha = 0.7, position = "identity") +
  ggplot2::labs(
    title = "Tenure Distribution by Churn Status",
    x = "Tenure (months)",
    y = "Count",
    fill = "Status",
    caption = "Source: customer_churn dataset"
  ) +
  ggplot2::theme_minimal()
```
```

---

## 8. Example `plumber/api.R` — REST Endpoint Skeleton

```r
library(plumber)
library(jsonlite)
source(here::here("R/features.R"))
source(here::here("R/modeling.R"))

# Load model once at startup (not per request)
fitted_model <- readRDS(here::here("models/churn_model.rds"))

#* Health check
#* @get /health
function() {
  list(status = "ok", timestamp = Sys.time())
}

#* Predict churn probability for a batch of customers
#*
#* @post /predict
#* @param body:object A JSON array of customer records
#* @serializer json
function(req) {
  df_input <- jsonlite::fromJSON(req$postBody, simplifyDataFrame = TRUE)
  df_features <- compute_features(df_input)
  predictions <- predict(fitted_model, df_features, type = "prob")
  list(
    predictions = predictions$.pred_1,
    n = nrow(predictions)
  )
}
```

To run locally:

```r
pr <- plumber::plumb("plumber/api.R")
pr$run(port = 8000)
```

---

## 9. Session Start Checklist

Run these at the start of every R session:

```r
renv::restore()          # sync packages to lockfile
testthat::test_dir("tests/testthat/")  # confirm baseline is green
lintr::lint_dir("R/")    # check style before touching code
```
