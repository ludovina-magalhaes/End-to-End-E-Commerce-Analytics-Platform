import os
import random
from datetime import timedelta

import pandas as pd
from faker import Faker
from dotenv import load_dotenv
import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas

# ---------- CONFIG ----------
load_dotenv()

fake = Faker()

N_CUSTOMERS = int(os.getenv("N_CUSTOMERS", 500))
N_PRODUCTS = int(os.getenv("N_PRODUCTS", 100))
N_ORDERS = int(os.getenv("N_ORDERS", 1000))

categories = ["Eletrónica", "Roupa", "Casa", "Desporto", "Beleza"]

SF_ACCOUNT = os.getenv("SF_ACCOUNT")
SF_USER = os.getenv("SF_USER")
SF_PASSWORD = os.getenv("SF_PASSWORD")
SF_DATABASE = os.getenv("SF_DATABASE")
SF_SCHEMA = os.getenv("SF_SCHEMA")
SF_WAREHOUSE = os.getenv("SF_WAREHOUSE")

required_vars = {
    "SF_ACCOUNT": SF_ACCOUNT,
    "SF_USER": SF_USER,
    "SF_PASSWORD": SF_PASSWORD,
    "SF_DATABASE": SF_DATABASE,
    "SF_SCHEMA": SF_SCHEMA,
    "SF_WAREHOUSE": SF_WAREHOUSE,
}

missing = [k for k, v in required_vars.items() if not v]

if missing:
    raise ValueError(
        f"Faltam variáveis no .env: {', '.join(missing)}"
    )

print("✅ Variáveis lidas do .env")
print(f"Database: {SF_DATABASE}")
print(f"Schema: {SF_SCHEMA}")
print(f"Warehouse: {SF_WAREHOUSE}")
print(f"User: {SF_USER}")

# ---------- LIGAÇÃO AO SNOWFLAKE ----------
conn = snowflake.connector.connect(
    account=SF_ACCOUNT,
    user=SF_USER,
    password=SF_PASSWORD,
    warehouse=SF_WAREHOUSE,
    database=SF_DATABASE,
    schema=SF_SCHEMA
)

cur = conn.cursor()

try:
    cur.execute(f'USE WAREHOUSE "{SF_WAREHOUSE}"')
    cur.execute(f'USE DATABASE "{SF_DATABASE}"')
    cur.execute(f'USE SCHEMA "{SF_SCHEMA}"')
    print("✅ Sessão Snowflake configurada")
except Exception as e:
    print("❌ Erro ao configurar sessão Snowflake")
    print(e)
    raise

def upload_to_snowflake(df: pd.DataFrame, table_name: str) -> None:
    try:
        success, nchunks, nrows, _ = write_pandas(
            conn=conn,
            df=df,
            table_name=table_name,
            database=SF_DATABASE,
            schema=SF_SCHEMA,
            auto_create_table=True,
            overwrite=True
        )

        if success:
            print(f"✅ {table_name} carregada com {nrows} linhas")
        else:
            print(f"❌ Falha ao carregar {table_name}")

    except Exception as e:
        print(f"❌ Erro ao carregar tabela {table_name}")
        print(e)
        raise

# ---------- 1. CLIENTES ----------
customers = []
for i in range(1, N_CUSTOMERS + 1):
    customers.append({
        "customer_id": i,
        "name": fake.name(),
        "email": fake.email(),
        "country": fake.country()
    })

df_customers = pd.DataFrame(customers)
upload_to_snowflake(df_customers, "CUSTOMERS")

# ---------- 2. PRODUTOS ----------
products = []
for i in range(1, N_PRODUCTS + 1):
    categoria = random.choice(categories)
    custo = round(random.uniform(5, 100), 2)
    preco = round(custo * random.uniform(1.2, 2.5), 2)

    products.append({
        "product_id": i,
        "product_name": fake.word().capitalize() + " " + fake.word().capitalize(),
        "category": categoria,
        "custo": custo,
        "price": preco
    })

df_products = pd.DataFrame(products)
upload_to_snowflake(df_products, "PRODUCTS")

# ---------- 3. PEDIDOS ----------
orders = []
order_items = []

for i in range(1, N_ORDERS + 1):
    customer_id = random.randint(1, N_CUSTOMERS)
    order_date = fake.date_between(start_date="-1y", end_date="today")
    status = random.choices(["completo", "cancelado"], weights=[0.85, 0.15])[0]

    orders.append({
        "order_id": i,
        "customer_id": customer_id,
        "order_date": order_date,
        "status": status
    })

    n_items = random.randint(1, 4)
    for _ in range(n_items):
        product_id = random.randint(1, N_PRODUCTS)
        quantity = random.randint(1, 3)

        order_items.append({
            "order_id": i,
            "product_id": product_id,
            "quantity": quantity
        })

df_orders = pd.DataFrame(orders)
upload_to_snowflake(df_orders, "ORDERS")

df_order_items = pd.DataFrame(order_items)
upload_to_snowflake(df_order_items, "ORDER_ITEMS")

# ---------- 4. CANCELAMENTOS ----------
cancelamentos = df_orders[df_orders["status"] == "cancelado"].copy()

cancelamentos["cancel_reason"] = [
    fake.sentence(nb_words=4) for _ in range(len(cancelamentos))
]

cancelamentos["cancel_date"] = cancelamentos["order_date"].apply(
    lambda d: d + timedelta(days=random.randint(1, 3))
)

df_canc = cancelamentos[["order_id", "cancel_reason", "cancel_date"]]
upload_to_snowflake(df_canc, "CANCELAMENTOS")

cur.close()
conn.close()

print(" Dados gerados e carregados no Snowflake com sucesso")