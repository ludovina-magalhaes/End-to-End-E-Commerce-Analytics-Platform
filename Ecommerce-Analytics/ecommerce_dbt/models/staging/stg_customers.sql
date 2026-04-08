{{ config(materialized='view') }}

WITH source AS (
    SELECT 
        * 
    FROM {{ source('raw', 'customers') }}
),

renamed AS (
    SELECT
        "customer_id" AS customer_id,
        LOWER(TRIM("name")) AS name,
        LOWER(TRIM("email")) AS email,
        LOWER(TRIM("country")) AS country
    FROM source
)

SELECT 
    * 
FROM renamed