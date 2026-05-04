WITH source AS (

    SELECT * FROM {{ source('raw_ecommerce', 'orders') }}

),

renamed AS (

    SELECT
        id                          AS order_id,
        customer_id,
        created_at::DATE            AS order_date,
        updated_at                  AS updated_at,
        status,
        total_amount_cents,
        discount_amount_cents,
        COALESCE(is_deleted, FALSE)  AS is_deleted
    FROM source

),

final AS (

    SELECT
        order_id,
        customer_id,
        order_date,
        updated_at,
        status,
        total_amount_cents,
        discount_amount_cents,
        is_deleted
    FROM renamed

)

SELECT * FROM final
