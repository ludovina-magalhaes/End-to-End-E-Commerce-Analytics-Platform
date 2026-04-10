{{ config(materialized='view') }}

WITH orders AS (
    SELECT
        order_id,
        customer_id,
        order_date,
        status
    FROM {{ ref('stg_orders') }}
),

order_items AS (
    SELECT
        order_id,
        product_id,
        quantity
    FROM {{ ref('stg_order_items') }}
),

products AS (
    SELECT
        product_id,
        product_name,
        category,
        custo,
        price
    FROM {{ ref('stg_products') }}
),

joined AS (
    SELECT
        o.order_id,
        o.customer_id,
        o.order_date,
        o.status,
        oi.product_id,
        p.product_name,
        p.category,
        oi.quantity,
        p.price,
        p.custo,
        oi.quantity * p.price AS valor_da_linha,
        oi.quantity * p.custo AS custo_total,
        (oi.quantity * p.price) - (oi.quantity * p.custo) AS lucro
    FROM orders o
    LEFT JOIN order_items oi
        ON o.order_id = oi.order_id
    LEFT JOIN products p
        ON oi.product_id = p.product_id
)

SELECT *
FROM joined