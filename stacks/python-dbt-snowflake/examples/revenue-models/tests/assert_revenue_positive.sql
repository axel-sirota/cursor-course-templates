-- Custom data test: assert_revenue_positive
--
-- This test returns rows when it FAILS. A passing test returns 0 rows.
-- Business rule: daily net revenue must never be negative.
-- A negative net_revenue_cents indicates a data quality issue — either
-- discount amounts exceed gross revenue, or a data pipeline error has
-- produced invalid values.
--
-- Returns: rows from fct_revenue where net_revenue_cents < 0

SELECT
    revenue_id,
    order_date,
    gross_revenue_cents,
    total_discounts_cents,
    net_revenue_cents
FROM {{ ref('fct_revenue') }}
WHERE net_revenue_cents < 0
