{{ config(materialized='table') }}

WITH orders AS (
    SELECT
        order_id,
        order_date,
        status,
        total_revenue,
        total_cost,
        total_profit
    FROM {{ ref('fct_orders') }}
)

SELECT
    order_date,
    COUNT(*) AS total_cancelled_orders,
    SUM(total_revenue) AS lost_revenue,
    SUM(total_cost) AS lost_cost,
    SUM(total_profit) AS lost_profit
FROM orders
WHERE status = 'cancelado'
GROUP BY order_date
ORDER BY order_date