#  End-to-End E-Commerce Analytics Platform


Plataforma completa de **Analytics Engineering** que simula un entorno real de e-commerce, abarcando desde la generación de datos sintéticos hasta la entrega automatizada de insights de negocio vía Telegram.

---

##  Preguntas de Negocio que Responde

- ¿Cuál es el revenue total y su evolución en el tiempo?
- ¿Qué clientes generan más valor? ¿Cuál es su CLV?
- ¿Cuál es la tasa de churn y qué la impulsa?
- ¿Qué productos y categorías son más rentables?
- ¿Qué impacto financiero tienen las cancelaciones?

---

##  Stack Tecnológico

| Capa | Herramienta |
|---|---|
| Generación de datos | Python · Faker |
| Data Warehouse | Snowflake ❄️ |
| Transformación y modelado | dbt Core 📦 |
| Orquestación | Apache Airflow · Astro CLI |
| Contenedores | Docker |
| Exploración de datos | DBeaver |
| Alertas | Telegram Bot 🤖 |

---

## 🏗️ Arquitectura ELT

El pipeline sigue una arquitectura **ELT moderna**: los datos se generan en Python, se cargan directamente en Snowflake y se transforman dentro del propio Data Warehouse mediante dbt Core.


<img width="664" height="355" alt="image" src="https://github.com/user-attachments/assets/bcb38a51-6214-498b-b76e-376054868d6f" />

'''

Python (Faker)
      │
      ▼
 Snowflake RAW          ← Datos brutos sin transformar
      │
      ▼
  dbt Staging           ← Limpieza y estandarización
      │
      ▼
dbt Intermediate        ← Joins, agregaciones, reglas de negocio
      │
      ▼
   dbt Marts            ← Star schema: dims + facts + analytics
      │
      ▼
 Airflow DAG            ← Orquestación semanal automatizada
      │
      ▼
generate_report.py      ← Reporte de negocio + alerta Telegram
'''

---

##  Modelado de Datos

### Modelo Raw

<!-- [imagen modelo raw] -->

### Modelo Analítico (Star Schema)

<!-- [imagen modelo analítico] -->

### Tablas de Dimensiones
- `dim_customers` — atributos completos de clientes, deduplicados
- `dim_products` — catálogo de productos con categorías y precios

### Tablas de Hechos
- `fct_orders` → métricas agregadas a nivel de pedido
- `fct_order_items` → granularidad a nivel de ítem, con FK a dimensiones

### Tablas Analíticas (KPIs listos para BI)
- `customer_metrics` — CLV, total gastado, frecuencia de compra
- `sales_by_category` — revenue y profit por categoría de producto
- `daily_sales` — ventas diarias, AOV y número de pedidos por día
- `cancellation_metrics` — tasa de cancelación e impacto financiero por motivo

---

##  Transformaciones dbt por Capa

### Staging — Limpieza sin lógica de negocio

| Modelo | Operación principal |
|---|---|
| `stg_customers` | Renombrado, filtrado de nulos en `customer_id`, tests not_null + unique |
| `stg_orders` | Estandarización de fechas y estados, deduplicación con `ROW_NUMBER()` |
| `stg_products` | Normalización de nombres, tests not_null + unique en `product_id` |
| `stg_order_items` | Validación de cantidades positivas, `unique_combination_of_columns` |
| `stg_cancelamentos` | Estandarización de motivos, filtrado de registros inválidos |

### Intermediate — Lógica de negocio y joins

| Modelo | Descripción |
|---|---|
| `int_order_details` | JOIN stg_orders × stg_customers, enriquecimiento y filtrado por fechas |
| `int_order_items_prod` | JOIN stg_order_items × stg_products, cálculo de subtotales por ítem |
| `int_cancel_orders` | Cruce cancelaciones × pedidos, impacto financiero por motivo |

### Marts — Tablas finales materializadas como `table`

| Modelo | Tipo | Descripción |
|---|---|---|
| `dim_customers` | Dimensión | Clientes con atributos completos, sin duplicados |
| `dim_products` | Dimensión | Productos con categorías y precios |
| `fct_orders` | Hechos | Métricas agregadas por pedido |
| `fct_order_items` | Hechos | Granularidad a nivel de ítem con FK a dims |
| `daily_sales` | KPI | Ventas diarias + ticket medio |
| `customer_metrics` | KPI | CLV, LTV, frecuencia de compra por cliente |
| `cancellation_metrics` | KPI | Tasa de cancelación e impacto en ingresos |

---

##  Métricas de Negocio Implementadas

- **Revenue** — ingresos totales y evolución temporal
- **Profit** — margen neto por producto y categoría
- **AOV** (Average Order Value) — ticket medio por pedido
- **CLV** (Customer Lifetime Value) — valor total por cliente
- **Churn Rate** — tasa de abandono estimada
- **Cancellation Rate** — tasa e impacto financiero de cancelaciones
- **Top productos y categorías** — ranking por revenue y volumen

---

##  Calidad de Datos

Tests dbt implementados en todos los modelos:

```yaml
# Ejemplos de tests en schema.yml
models:
  - name: dim_customers
    columns:
      - name: customer_id
        tests: [not_null, unique]

  - name: fct_orders
    columns:
      - name: order_id
        tests: [not_null, unique]
      - name: customer_id
        tests:
          - relationships:
              to: ref('dim_customers')
              field: customer_id

  - name: stg_order_items
    columns:
      - name: order_id
        tests:
          - dbt_utils.unique_combination_of_columns:
              combination_of_columns: [order_id, product_id]
```

**Tests implementados:** `not_null` · `unique` · `relationships` · `unique_combination_of_columns`

---

##  Orquestación con Apache Airflow

### DAG: `ludovina_ecommerce_pipeline`

| Parámetro | Valor |
|---|---|
| Schedule | `@weekly` |
| Catchup | `False` |
| Retries | `2` con delay de 5 min |
| Tags | ludovina · ecommerce · snowflake · dbt |

### Flujo de tareas

```
generar_datos_fake → dbt_run → dbt_test → generar_reporte
```

| Tarea | Operador | Descripción |
|---|---|---|
| `generar_datos_fake` | PythonOperator | Genera datos con Faker y carga en Snowflake RAW |
| `dbt_run` | BashOperator | Ejecuta `dbt run` — materializa staging → marts |
| `dbt_test` | BashOperator | Ejecuta `dbt test` — valida calidad en todos los modelos |
| `generar_reporte` | BashOperator | Genera reporte de negocio y envía alerta vía Telegram |

### Entorno Docker con Astro CLI

Astro CLI levanta automáticamente todos los servicios necesarios (webserver, scheduler, triggerer, PostgreSQL) sin configuración manual de docker-compose.

```
Ecommerce-Analytics/
├── dags/
│   └── ecommerce_pipeline.py     # DAG principal
├── include/
│   └── scripts/
│       ├── generate_fake_data.py
│       └── generate_report.py
├── plugins/
├── requirements.txt
├── airflow_settings.yaml
└── Dockerfile
```

### Demo en ejecución

**dbt run + dbt test**

![dbt run](https://github.com/user-attachments/assets/fab046e3-1afb-4151-a0b6-29c8e2339f26)

**astro dev start**

![astro dev restat](https://github.com/user-attachments/assets/a394b48e-0e5b-40dc-983c-2d388915595b)


**Airflow DAG**

![airflow](https://github.com/user-attachments/assets/5b99e46c-2326-468a-8d7a-8ac3c3c4ab92)

**Alerta Telegram**

<img width="381" height="759" alt="image" src="https://github.com/user-attachments/assets/00d451ce-b132-4fa0-997f-5990156d8841" />

---

##  Resultado Final en Snowflake

```
ECOMMERCE_BD
└── PUBLIC
    ├── Tablas (12)
    │   ├── dim_customers         # Dimensión clientes
    │   ├── dim_products          # Dimensión productos
    │   ├── fct_orders            # Hechos de pedidos
    │   ├── fct_order_items       # Hechos de ítems (granular)
    │   ├── customer_metrics      # KPI: métricas por cliente
    │   ├── daily_sales           # KPI: ventas diarias
    │   ├── cancellation_metrics  # KPI: cancelaciones
    │   └── ... (tablas RAW)
    └── Vistas (9)
        ├── stg_*                 # Capa staging
        └── int_*                 # Capa intermediate
```

> Las vistas de staging e intermediate no consumen almacenamiento adicional.
> Los marts se materializan como `table` para garantizar rendimiento en dashboards.

---

##  Cómo Ejecutar el Proyecto

### Requisitos previos

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) instalado y en ejecución
- [Astro CLI](https://www.astronomer.io/docs/astro/cli/install-cli) instalado
- Cuenta de Snowflake configurada

### 1. Clonar el repositorio

```bash
git clone https://github.com/ludovina-magalhaes/End-to-End-E-Commerce-Analytics-Platform.git
cd End-to-End-E-Commerce-Analytics-Platform/Ecommerce-Analytics
```

### 2. Configurar `~/.dbt/profiles.yml`

```yaml
ecommerce_analytics:
  outputs:
    dev:
      type: snowflake
      account: <tu_cuenta>
      user: <tu_usuario>
      password: <tu_contraseña>
      role: <tu_rol>
      database: ECOMMERCE_BD
      warehouse: COMPUTE_WH
      schema: PUBLIC
      threads: 4
  target: dev
```

>  Nunca versiones este archivo. Usa variables de entorno para producción.

### 3. Instalar dependencias dbt

```bash
dbt deps    # Instala dbt_utils y otros packages
```

### 4. Iniciar Airflow con Astro CLI

```bash
astro dev start
```

Accede a la interfaz en: `http://localhost:8080` (usuario: `admin` / contraseña: `admin`)

### 5. Ejecutar la DAG manualmente

Busca `ludovina_ecommerce_pipeline` → activa el toggle → haz clic en ▶️ **Trigger DAG**

### 6. Ejecutar dbt directamente (opcional)

```bash
dbt run --select staging        # Solo capa staging
dbt run --select intermediate   # Solo capa intermediate
dbt run --select marts          # Solo capa marts
dbt run                         # Todo el pipeline
dbt test                        # Validar calidad de datos
dbt build                       # run + test (recomendado para CI/CD)
```

### 7. Parar el entorno

```bash
astro dev stop
```

---

##  Estructura del Proyecto

```
End-to-End-E-Commerce-Analytics-Platform/
│
└── Ecommerce-Analytics/
    ├── dags/
    │   └── ecommerce_pipeline.py
    ├── include/
    │   └── scripts/
    │       ├── generate_fake_data.py
    │       └── generate_report.py
    ├── models/
    │   ├── staging/
    │   │   ├── stg_customers.sql
    │   │   ├── stg_orders.sql
    │   │   ├── stg_products.sql
    │   │   ├── stg_order_items.sql
    │   │   ├── stg_cancelamentos.sql
    │   │   └── schema.yml
    │   ├── intermediate/
    │   │   ├── int_order_details.sql
    │   │   ├── int_order_items_prod.sql
    │   │   ├── int_cancel_orders.sql
    │   │   └── schema.yml
    │   └── marts/
    │       ├── dim_customers.sql
    │       ├── dim_products.sql
    │       ├── fct_orders.sql
    │       ├── fct_order_items.sql
    │       ├── schema.yml
    │       └── analytics/
    │           ├── customer_metrics.sql
    │           ├── daily_sales.sql
    │           ├── cancellation_metrics.sql
    │           └── schema.yml
    ├── packages.yml
    ├── dbt_project.yml
    ├── Dockerfile
    ├── airflow_settings.yaml
    └── requirements.txt
```

---

### Próximos pasos 

- [ ] CI/CD con GitHub Actions (`dbt build` en Pull Requests)
- [ ] Dashboard en Metabase o Power BI conectado a Snowflake
- [ ] Integración con datos reales vía API

---

## Autora

**Ludovina Magalhães** · Analytics Engineer

[![LinkedIn](https://img.shields.io/badge/LinkedIn-ludovina--magalhaes-0A66C2?logo=linkedin)](https://www.linkedin.com/in/ludovina-magalhaes)
[![GitHub](https://img.shields.io/badge/GitHub-ludovina--magalhaes-181717?logo=github)](https://github.com/ludovina-magalhaes)
