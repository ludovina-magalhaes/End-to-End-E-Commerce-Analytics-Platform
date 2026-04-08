{{ config(materialized='table') }}

WITH order_details AS (
    SELECT
        order_id,
        customer_id,
        order_date,
        status,
        quantity,
        valor_da_linha,
        custo_total,
        lucro
    FROM {{ ref('int_order_details') }}
)

SELECT
    order_id,
    customer_id,
    order_date,
    status,
    SUM(quantity) AS total_items,
    SUM(valor_da_linha) AS total_revenue,
    SUM(custo_total) AS total_cost,
    SUM(lucro) AS total_profit
FROM order_details
GROUP BY
    order_id,
    customer_id,
    order_date,
    status