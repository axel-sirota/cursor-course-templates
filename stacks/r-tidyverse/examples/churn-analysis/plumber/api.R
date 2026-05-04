library(plumber)
library(jsonlite)
library(here)

source(here::here("R/features.R"))
source(here::here("R/modeling.R"))

# Load fitted model once at startup — not per request
fitted_model <- readRDS(here::here("models/churn_model.rds"))

#* Health check
#*
#* @get /health
#* @serializer json
function() {
  list(status = "ok", timestamp = format(Sys.time(), iso.8601 = TRUE))
}

#* Predict churn probability for a batch of customers
#*
#* Accepts a JSON array of customer records. Each record must have:
#* customer_id (string), tenure_days (int), monthly_spend (double),
#* support_tickets (int).
#*
#* @post /predict
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
