{{ config(materialized='table') }}

WITH orders AS (
    SELECT
        order_date,
        status,
        total_revenue,
        total_cost,
        total_profit
    FROM {{ ref('fct_orders') }}
)

SELECT
    order_date,
    COUNT(*) AS total_orders,
    SUM(total_revenue) AS total_revenue,
    SUM(total_cost) AS total_cost,
    SUM(total_profit) AS total_profit
FROM orders
WHERE status = 'completo'
GROUP BY order_date
ORDER BY order_date