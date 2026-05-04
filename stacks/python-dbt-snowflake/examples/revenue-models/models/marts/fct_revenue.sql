{{
    config(
        materialized='incremental',
        unique_key='revenue_id',
        on_schema_change='sync_all_columns'
    )
}}

WITH orders AS (

    SELECT
        order_id,
        customer_id,
        order_date,
        updated_at,
        status,
        total_amount_cents,
        discount_amount_cents,
        is_deleted
    FROM {{ ref('stg_orders') }}
    WHERE is_deleted = FALSE

),

order_items AS (

    SELECT
        order_id,
        SUM(quantity)           AS total_items,
        SUM(line_amount_cents)  AS items_total_cents
    FROM {{ ref('stg_order_items') }}
    GROUP BY order_id

),

joined AS (

    SELECT
        orders.order_id,
        orders.customer_id,
        orders.order_date,
        orders.updated_at,
        orders.status,
        orders.total_amount_cents,
        orders.discount_amount_cents,
        COALESCE(order_items.total_items, 0)        AS total_items,
        COALESCE(order_items.items_total_cents, 0)  AS items_total_cents
    FROM orders
    LEFT JOIN order_items
        ON orders.order_id = order_items.order_id

),

daily_revenue AS (

    SELECT
        order_date,
        COUNT(DISTINCT order_id)                                AS order_count,
        COUNT(DISTINCT customer_id)                             AS customer_count,
        SUM(total_amount_cents)                                 AS gross_revenue_cents,
        SUM(discount_amount_cents)                              AS total_discounts_cents,
        SUM(total_amount_cents) - SUM(discount_amount_cents)    AS net_revenue_cents,
        SUM(total_items)                                        AS total_items_sold
    FROM joined
    WHERE status = 'completed'

    {% if is_incremental() %}
    AND updated_at > (SELECT MAX(updated_at) FROM {{ this }})
    {% endif %}

    GROUP BY order_date

),

final AS (

    SELECT
        {{ dbt_utils.generate_surrogate_key(['order_date']) }}  AS revenue_id,
        order_date,
        order_count,
        customer_count,
        gross_revenue_cents,
        total_discounts_cents,
        net_revenue_cents,
        total_items_sold,
        CURRENT_TIMESTAMP                                       AS _loaded_at
    FROM daily_revenue

)

SELECT * FROM final
