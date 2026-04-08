{{ config(materialized='view') }}

WITH source AS (
    SELECT
        *
    FROM {{ source('raw', 'order_items') }}
),

renamed AS (
    SELECT
        "order_id" AS order_id,
        "product_id" AS product_id,
        "quantity" AS quantity
    FROM source
)

SELECT
    *
FROM renamed