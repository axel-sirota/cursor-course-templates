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
