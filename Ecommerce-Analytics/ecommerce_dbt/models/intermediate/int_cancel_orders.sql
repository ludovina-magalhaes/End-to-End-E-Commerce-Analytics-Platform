{{ config(materialized='view') }}

WITH cancelamentos AS (
    SELECT
        order_id,
        cancel_reason,
        cancel_date
    FROM {{ ref('stg_cancelamentos') }}
),

orders AS (
    SELECT
        order_id,
        customer_id,
        order_date,
        status
    FROM {{ ref('stg_orders') }}
),

joined AS (
    SELECT
        c.order_id,
        o.customer_id,
        o.order_date,
        o.status,
        c.cancel_reason,
        c.cancel_date
    FROM cancelamentos c
    LEFT JOIN orders o
        ON c.order_id = o.order_id
)

SELECT *
FROM joined