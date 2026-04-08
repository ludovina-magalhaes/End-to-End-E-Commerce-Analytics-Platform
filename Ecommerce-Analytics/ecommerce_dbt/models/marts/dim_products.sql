{{ config(materialized='table') }}

SELECT
    product_id,
    product_name,
    category,
    custo,
    price
FROM {{ ref('stg_products') }}