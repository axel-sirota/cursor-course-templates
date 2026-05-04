#' Compute churn risk features from raw customer data
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
compute_features <- function(df) {
  df |>
    dplyr::mutate(
      tenure_months = tenure_days / 30,
      high_value = dplyr::if_else(monthly_spend > 100, 1L, 0L)
    ) |>
    dplyr::select(-tenure_days)
}
