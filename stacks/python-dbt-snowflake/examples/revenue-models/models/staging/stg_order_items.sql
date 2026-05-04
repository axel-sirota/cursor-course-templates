with source as (

    select * from {{ source('raw_ecommerce', 'order_items') }}

),

renamed as (

    select
        order_item_id,
        order_id,
        product_id,
        quantity,
        unit_price,
        quantity * unit_price  as line_amount_cents,
        created_at::date        as item_date

    from source

)

select * from renamed
