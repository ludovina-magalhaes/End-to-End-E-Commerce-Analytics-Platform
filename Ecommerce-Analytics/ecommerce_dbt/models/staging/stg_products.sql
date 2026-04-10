{{ config(materialized='view') }}

WITH source AS (
    SELECT
        *
    FROM {{ source('raw', 'products') }}
),

renamed AS (
    SELECT
        "product_id" AS product_id,
        LOWER(TRIM("product_name")) AS product_name,
        LOWER(TRIM("category")) AS category,
        CAST("custo" AS FLOAT) AS custo,
        CAST("price" AS FLOAT) AS price
    FROM source
)

SELECT
    *
FROM renamed