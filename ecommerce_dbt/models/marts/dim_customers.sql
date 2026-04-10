select
    customer_id,
    name,
    email,
    country
from {{ ref('stg_customers') }}