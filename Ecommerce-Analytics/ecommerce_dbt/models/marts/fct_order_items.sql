{{ config(materialized='table') }}

SELECT
    order_id,
    customer_id,
    order_date,
    status,
    product_id,
    product_name,
    category,
    quantity,
    price,
    custo,
    valor_da_linha,
    custo_total,
    lucro
FROM {{ ref('int_order_details') }}