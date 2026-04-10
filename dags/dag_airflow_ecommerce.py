import os
from datetime import datetime, timedelta

from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from airflow.providers.standard.operators.bash import BashOperator

DBT_DIR = os.getenv("DBT_DIR")
SCRIPTS_PATH = os.getenv("SCRIPTS_PATH")

default_args = {
    "owner": "Ludovina",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}


def generar_datos():
    """Ejecuta el script que genera datos fake y los carga directamente en Snowflake"""
    os.system(f'python "{os.path.join(SCRIPTS_PATH, "generate_fake_data.py")}"')


with DAG(
    dag_id="ludovina_ecommerce_pipeline",
    start_date=datetime(2025, 1, 1),
    schedule="@weekly",
    catchup=False,
    default_args=default_args,
    tags=["ludovina", "ecommerce", "snowflake", "dbt"],
) as dag:

    t1_generar_datos = PythonOperator(
        task_id="generar_datos_fake",
        python_callable=generar_datos,
    )

    t2_dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command=f'cd "{DBT_DIR}" && dbt run --profiles-dir /home/astro/.dbt',
    )

    t3_dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command=f'cd "{DBT_DIR}" && dbt test --profiles-dir /home/astro/.dbt',
    )

    t4_generar_reporte = BashOperator(
        task_id="generar_reporte",
        bash_command=f'python "{os.path.join(SCRIPTS_PATH, "generate_report.py")}"',
    )

    t1_generar_datos >> t2_dbt_run >> t3_dbt_test >> t4_generar_reporte