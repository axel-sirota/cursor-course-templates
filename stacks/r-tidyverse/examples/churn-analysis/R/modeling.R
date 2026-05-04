#' Fit a logistic regression churn model using tidymodels
#'
#' Builds a tidymodels workflow with a normalisation recipe and a logistic
#' regression model (glm engine). The `customer_id` column is assigned the
#' "ID" role so it is excluded from predictors while remaining in the data.
#'
#' @param df A data frame with features — output of [compute_features()].
#'   Must contain columns: `customer_id`, `tenure_months`, `monthly_spend`,
#'   `support_tickets`, `high_value`, `churned`.
#' @return A fitted `workflows::workflow` object.
#' @export
fit_churn_model <- function(df) {
  churn_recipe <- recipes::recipe(churned ~ ., data = df) |>
    recipes::update_role(customer_id, new_role = "ID") |>
    recipes::step_normalize(recipes::all_numeric_predictors())

  model_spec <- parsnip::logistic_reg() |>
    parsnip::set_engine("glm") |>
    parsnip::set_mode("classification")

  churn_workflow <- workflows::workflow() |>
    workflows::add_recipe(churn_recipe) |>
    workflows::add_model(model_spec)

  workflows::fit(churn_workflow, data = df)
}

#' Evaluate a fitted workflow using cross-validation
#'
#' @param df A data frame with features (output of [compute_features()]).
#' @param workflow_spec An unfitted `workflows::workflow` object.
#' @param folds An `rsample::vfold_cv` resampling object.
#' @return A data frame of yardstick metrics (accuracy, roc_auc) per fold.
#' @export
evaluate_cv <- function(df, workflow_spec, folds) {
  metrics <- yardstick::metric_set(
    yardstick::accuracy,
    yardstick::roc_auc
  )
  tune::fit_resamples(
    workflow_spec,
    resamples = folds,
    metrics = metrics
  ) |>
    tune::collect_metrics()
}
