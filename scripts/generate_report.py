import os
import pandas as pd
import requests
from dotenv import load_dotenv
import snowflake.connector

# Carregar variáveis do .env
load_dotenv()

# Variáveis do ambiente
DBT_DIR = os.getenv('DBT_DIR')
LOAD_TO_SNOWFLAKE = os.getenv('LOAD_TO_SNOWFLAKE', 'false').lower() == 'true'

# Snowflake
SF_ACCOUNT = os.getenv('SF_ACCOUNT')
SF_USER = os.getenv('SF_USER')
SF_PASSWORD = os.getenv('SF_PASSWORD')
SF_DATABASE = os.getenv('SF_DATABASE')
SF_SCHEMA = os.getenv('SF_SCHEMA')
SF_WAREHOUSE = os.getenv('SF_WAREHOUSE')

# Telegram
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')


def get_snowflake_connection():
    return snowflake.connector.connect(
        account=SF_ACCOUNT,
        user=SF_USER,
        password=SF_PASSWORD,
        warehouse=SF_WAREHOUSE,
        database=SF_DATABASE,
        schema=SF_SCHEMA
    )


def load_data():
    if LOAD_TO_SNOWFLAKE:
        print("Cargando datos desde Snowflake...")

        conn = get_snowflake_connection()

        query_orders = "SELECT * FROM ORDERS"
        query_products = "SELECT * FROM PRODUCTS"

        orders_df = pd.read_sql(query_orders, conn)
        products_df = pd.read_sql(query_products, conn)

        conn.close()
    else:
        print("Cargando datos desde CSV...")

        orders_df = pd.read_csv(f"{DBT_DIR}/seeds/orders.csv")
        products_df = pd.read_csv(f"{DBT_DIR}/seeds/products.csv")

    return orders_df, products_df


def render_report_text():
    orders_df, products_df = load_data()

    # Métricas
    total_pedidos = len(orders_df)
    total_cancelados = len(orders_df[orders_df["status"] == "cancelado"])
    tasa_cancelacion = round((total_cancelados / total_pedidos) * 100, 2)

    producto_top = products_df.sort_values(by="price", ascending=False).iloc[0]["product_name"]

    # Mensagem 
    message = (
        "📊 *Reporte Semanal - E-commerce*\n\n"
        f"• Total de pedidos: *{total_pedidos}*\n"
        f"• Pedidos cancelados: *{total_cancelados}*\n"
        f"• Tasa de cancelación: *{tasa_cancelacion}%*\n"
        f"• Producto más caro: *{producto_top}*\n"
    )

    return message

    # 
def send_telegram_message(message: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }

    response = requests.post(url, data=payload)

    if response.status_code != 200:
        print(f"Error al enviar mensaje: {response.text}")
        response.raise_for_status()
    else:
        print("Mensaje enviado con éxito!")


def notify_weekly_report_telegram():
    message = render_report_text()
    send_telegram_message(message)


if __name__ == "__main__":
    notify_weekly_report_telegram()