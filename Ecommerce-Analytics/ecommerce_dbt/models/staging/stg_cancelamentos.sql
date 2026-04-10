{{ config(materialized='view') }}

WITH source AS (
    SELECT
        *
    FROM {{ source('raw', 'cancelamentos') }}
),

renamed AS (
    SELECT
        "order_id" AS order_id,
        LOWER(TRIM("cancel_reason")) AS cancel_reason,
        CAST("cancel_date" AS DATE) AS cancel_date
    FROM source
)

SELECT
    *
FROM renamed