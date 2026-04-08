{{ config(materialized='table') }}

WITH order_details AS (
    SELECT
        customer_id,
        order_id,
        order_date,
        status,
        quantity,
        valor_da_linha,
        custo_total,
        lucro
    FROM {{ ref('int_order_details') }}
),

customer_orders AS (
    SELECT
        customer_id,
        order_id,
        order_date,
        status,
        SUM(quantity) AS total_items_order,
        SUM(valor_da_linha) AS total_revenue_order,
        SUM(custo_total) AS total_cost_order,
        SUM(lucro) AS total_profit_order
    FROM order_details
    GROUP BY
        customer_id,
        order_id,
        order_date,
        status
)

SELECT
    customer_id,
    COUNT(DISTINCT order_id) AS total_orders,
    COUNT(DISTINCT CASE WHEN status = 'completo' THEN order_id END) AS completed_orders,
    COUNT(DISTINCT CASE WHEN status = 'cancelado' THEN order_id END) AS cancelled_orders,
    MIN(CASE WHEN status = 'completo' THEN order_date END) AS first_purchase_date,
    MAX(CASE WHEN status = 'completo' THEN order_date END) AS last_purchase_date,
    SUM(CASE WHEN status = 'completo' THEN total_items_order ELSE 0 END) AS total_items_purchased,
    SUM(CASE WHEN status = 'completo' THEN total_revenue_order ELSE 0 END) AS total_revenue,
    SUM(CASE WHEN status = 'completo' THEN total_cost_order ELSE 0 END) AS total_cost,
    SUM(CASE WHEN status = 'completo' THEN total_profit_order ELSE 0 END) AS total_profit,
    AVG(CASE WHEN status = 'completo' THEN total_revenue_order END) AS avg_order_value
FROM customer_orders
GROUP BY customer_id