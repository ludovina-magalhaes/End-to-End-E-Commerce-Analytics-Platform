{{ config(materialized='view') }}

WITH source AS (
    SELECT
        *
    FROM {{ source('raw', 'orders') }}
),

renamed AS (
    SELECT
        "order_id" AS order_id,
        "customer_id" AS customer_id,
        CAST("order_date" AS DATE) AS order_date,
        LOWER(TRIM("status")) AS status
    FROM source
)

SELECT
    *
FROM renamed