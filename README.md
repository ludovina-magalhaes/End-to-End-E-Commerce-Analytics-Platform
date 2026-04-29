# End-to-End E-Commerce Analytics Platform

> Proyecto diseñado para replicar un entorno real de trabajo de un Analytics Engineer, construyendo un pipeline de datos orientado a decisiones de negocio: desde la ingesta hasta métricas accionables, automatizadas y con calidad garantizada.

---

## Contexto de Negocio

En una empresa de e-commerce, distintos equipos (marketing, operaciones, finanzas) necesitan tomar decisiones rápidas basadas en datos fiables.

Sin embargo:

* Marketing no puede identificar qué canales generan clientes con mayor churn
* Operaciones no tiene visibilidad sobre el impacto real de las cancelaciones
* Finanzas no dispone de métricas consistentes de revenue y rentabilidad

El resultado: decisiones lentas, inconsistentes y con impacto directo en ingresos.

---

## El Problema

Los datos están dispersos, desactualizados y sin una definición clara de métricas clave como churn, CLV o revenue.

Esto impide:

* Detectar caídas de ingresos a tiempo
* Identificar segmentos de clientes en riesgo
* Medir el impacto financiero de decisiones operativas

---

## La Solución

Este proyecto implementa un pipeline **ELT end-to-end** que:

* Carga datos automáticamente en Snowflake (capa RAW)
* Transforma y modela con dbt (staging → intermediate → marts)
* Orquesta todo con Apache Airflow (ejecución semanal)
* Genera métricas listas para análisis y alertas automáticas vía Telegram

Resultado:

* Sin intervención manual
* Métricas consistentes y centralizadas
* Datos listos para toma de decisiones en tiempo real

---

## Arquitectura

<img width="664" height="355" alt="image" src="https://github.com/user-attachments/assets/bcb38a51-6214-498b-b76e-376054868d6f" />



**Stack:**

| Capa           | Tecnología                 | Función                           |
| -------------- | -------------------------- | --------------------------------- |
| Generación     | Python + Faker             | Simulación de datos de e-commerce |
| Almacenamiento | Snowflake                  | Data Warehouse cloud-native       |
| Transformación | dbt Core                   | Modelado, tests y documentación   |
| Orquestación   | Apache Airflow + Astro CLI | Automatización y monitorización   |
| Entorno        | Docker                     | Reproducibilidad local            |

---

## Métricas de Negocio

### Revenue

**Qué es:** Ingresos totales y evolución por producto, categoría y periodo
**Lógica:** `quantity × unit_price` por pedido, excluyendo cancelaciones
**Decisión:** Ajustar pricing, detectar caídas de ingresos y optimizar categorías

---

### Customer Lifetime Value (CLV)

**Qué es:** Valor total generado por cliente
**Lógica:** Gasto acumulado por cliente + frecuencia de compra
**Decisión:** Priorizar clientes de alto valor y optimizar inversión en adquisición

---

### Churn Rate

**Qué es:** Porcentaje de clientes que dejan de comprar
**Lógica:** Clientes sin pedidos en los últimos N días sobre la base activa
**Decisión:** Activar campañas de reactivación y anticipar pérdida de ingresos

---

### Tasa de Cancelación

**Qué es:** Porcentaje de pedidos cancelados y su impacto económico
**Lógica:** `canceled_orders / total_orders` + cálculo de revenue perdido
**Decisión:** Reducir causas principales de cancelación y mejorar operaciones

---

### AOV (Average Order Value)

**Qué es:** Ticket medio por pedido
**Lógica:** `total_revenue / total_orders`
**Decisión:** Evaluar estrategias de upselling y promociones

---

## Ejemplos de Insights

Este pipeline permite obtener insights accionables como:

* Canales de adquisición con menor frecuencia de compra concentran mayor churn → redirigir inversión hacia canales con mayor retención
* Clientes con bajo AOV y alta tasa de cancelación representan el mayor riesgo de abandono → activar campañas de reactivación segmentadas
* Determinadas categorías generan alto volumen de ventas pero margen negativo → priorizar catálogo por rentabilidad, no solo por volumen

Estos insights permiten pasar de análisis descriptivo a decisiones estratégicas.

---

## Modelado de Datos

El modelo sigue una **Star Schema**, separando claramente dimensiones y hechos.

### Modelo RAW
<img width="740" height="651" alt="image" src="https://github.com/user-attachments/assets/f1c113a5-30f6-4fde-a8d1-2c1806bd6fab" />


### Modelo Analitico
<img width="689" height="728" alt="image" src="https://github.com/user-attachments/assets/9150fa79-c2bf-4ad8-81bd-b847977e2f93" />


**Grain:**

* `fct_orders` → una fila por pedido
* `fct_order_items` → una fila por producto dentro del pedido

**Tablas analíticas (KPIs materializados):**

| Tabla                  | Contenido                                           |
| ---------------------- | --------------------------------------------------- |
| `customer_metrics`     | CLV, gasto total y frecuencia de compra por cliente |
| `daily_sales`          | Revenue diario, AOV y número de pedidos             |
| `cancellation_metrics` | Tasa de cancelación e impacto financiero por motivo |
| `sales_by_category`    | Revenue y margen por categoría de producto          |

---

## Organización dbt por Capa

### Staging — limpieza sin lógica de negocio

| Modelo              | Operación principal                                                   |
| ------------------- | --------------------------------------------------------------------- |
| `stg_customers`     | Renombrado de columnas, filtro de nulos en `customer_id`              |
| `stg_orders`        | Estandarización de fechas y estados, deduplicación con `ROW_NUMBER()` |
| `stg_products`      | Normalización de nombres, validación de `product_id`                  |
| `stg_order_items`   | Validación de cantidades positivas, unicidad `order_id + product_id`  |
| `stg_cancelamentos` | Estandarización de motivos, filtro de registros inválidos             |

> Staging se materializa como **view** — sin coste adicional de almacenamiento.

### Intermediate — lógica de negocio y joins

| Modelo                 | Descripción                                                  |
| ---------------------- | ------------------------------------------------------------ |
| `int_order_details`    | JOIN orders × customers, enriquecimiento y filtro por fechas |
| `int_order_items_prod` | JOIN order_items × products, cálculo de subtotales por ítem  |
| `int_cancel_orders`    | Cruce cancelaciones × pedidos, impacto financiero por motivo |

### Marts — tablas finales para consumo

Materializados como **table** para garantizar rendimiento en dashboards y queries analíticas.

| Modelo                 | Tipo      | Descripción                                       |
| ---------------------- | --------- | ------------------------------------------------- |
| `dim_customers`        | Dimensión | Clientes con atributos completos, sin duplicados  |
| `dim_products`         | Dimensión | Productos con categorías y precios                |
| `fct_orders`           | Hechos    | Métricas agregadas por pedido                     |
| `fct_order_items`      | Hechos    | Granularidad a nivel de ítem con FK a dimensiones |
| `daily_sales`          | KPI       | Ventas diarias y ticket medio                     |
| `customer_metrics`     | KPI       | CLV, LTV y frecuencia de compra por cliente       |
| `cancellation_metrics` | KPI       | Tasa de cancelación e impacto en ingresos         |

---

## Calidad de Datos

Todos los modelos incluyen tests dbt. Ninguna ejecución pasa sin validación.

```yaml
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

## Orquestación con Airflow

**DAG:** `ludovina_ecommerce_pipeline` · Frecuencia: `@weekly` · Retries: 2 (delay 5 min)

```
generar_datos_fake → dbt_run → dbt_test → generar_reporte
```

| Tarea                | Operador       | Descripción                                           |
| -------------------- | -------------- | ----------------------------------------------------- |
| `generar_datos_fake` | PythonOperator | Genera datos con Faker y carga en Snowflake RAW       |
| `dbt_run`            | BashOperator   | Materializa todas las capas (staging → marts)         |
| `dbt_test`           | BashOperator   | Valida calidad en todos los modelos                   |
| `generar_reporte`    | BashOperator   | Genera reporte de negocio y envía alerta vía Telegram |

---

## Decisiones Técnicas

**¿Por qué Snowflake?**
La arquitectura ELT requiere un DWH que ejecute transformaciones pesadas de forma eficiente. Snowflake separa compute y storage, lo que permite escalar el warehouse solo durante las ejecuciones de dbt y reducir coste en el resto del tiempo. Alternativas como BigQuery o Redshift servirían, pero Snowflake ofrece mejor soporte nativo a entornos multi-schema (RAW / DEV / PROD) sin duplicar datos.

**¿Por qué dbt?**
Las transformaciones SQL viven como código versionado en Git, con tests automáticos y documentación integrada en `schema.yml`. La separación en capas (staging → intermediate → marts) garantiza que cada modelo tenga una única responsabilidad y sea reutilizable. Sin dbt, la misma lógica estaría dispersa en scripts sin tests ni trazabilidad.

**¿Por qué Airflow + Astro CLI?**
Airflow ofrece visibilidad completa sobre cada ejecución: logs, reintentos, dependencias entre tareas y alertas en caso de fallo. Astro CLI elimina la configuración manual de docker-compose, levantando todos los servicios con un único comando. Para un pipeline con dependencias ordenadas (generar → transformar → validar → reportar), un orquestador es imprescindible frente a cron jobs aislados.

**¿Por qué ELT y no ETL?**
Los datos llegan a Snowflake en estado raw y se transforman dentro del propio DWH. Esto elimina dependencias de herramientas externas de transformación, aprovecha la capacidad de cómputo de Snowflake y simplifica el debugging — cualquier error es trazable directamente en SQL.

**¿Por qué staging como view y marts como table?**
Las views de staging no consumen almacenamiento y son suficientes para capas intermedias que no se consultan directamente. Los marts se materializan como table porque son consumidos frecuentemente por dashboards y queries analíticas — aquí la latencia importa y el coste de almacenamiento está justificado.

---

## Resultado en Snowflake

```
ECOMMERCE_BD
└── PUBLIC
    ├── Tablas (12)
    │   ├── dim_customers
    │   ├── dim_products
    │   ├── fct_orders
    │   ├── fct_order_items
    │   ├── customer_metrics
    │   ├── daily_sales
    │   ├── cancellation_metrics
    │   └── ... (tablas RAW)
    └── Vistas (9)
        ├── stg_*   ← staging
        └── int_*   ← intermediate
```

12 tablas materializadas · 9 vistas · pipeline completamente automatizado · calidad validada en cada ejecución.

---

## Cómo Ejecutar

### Requisitos previos
- Docker Desktop en ejecución
- Astro CLI instalado
- Cuenta Snowflake configurada

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
> Nunca versiones este archivo. Usa variables de entorno en producción.

### 3. Instalar packages dbt
```bash
dbt deps
```

### 4. Iniciar Airflow
```bash
astro dev start
# Interfaz disponible en http://localhost:8080
# user: admin | password: admin
```

**dbt run + dbt test**

![dbt run](https://github.com/user-attachments/assets/fab046e3-1afb-4151-a0b6-29c8e2339f26)

**astro dev start**

![astro dev restat](https://github.com/user-attachments/assets/a394b48e-0e5b-40dc-983c-2d388915595b)


**Airflow DAG**

![airflow](https://github.com/user-attachments/assets/5b99e46c-2326-468a-8d7a-8ac3c3c4ab92)

**Alerta Telegram**

<img width="381" height="759" alt="image" src="https://github.com/user-attachments/assets/00d451ce-b132-4fa0-997f-5990156d8841" />

### 5. Ejecutar la DAG
Airflow UI → `ludovina_ecommerce_pipeline` → toggle ON → ▶️ Trigger DAG

### 6. Ejecutar dbt directamente (opcional)
```bash
dbt run --select staging        # Solo staging
dbt run --select intermediate   # Solo intermediate
dbt run --select marts          # Solo marts
dbt run                         # Pipeline completo
dbt test                        # Validar calidad
dbt build                       # run + test (recomendado para CI/CD)
```

### 7. Parar el entorno
```bash
astro dev stop
```

---

## Estructura del Proyecto

```
Ecommerce-Analytics/
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

## Impacto del Proyecto

Este pipeline permite a una empresa de e-commerce pasar de datos desorganizados a un sistema estructurado de toma de decisiones, reduciendo el tiempo de análisis y mejorando la capacidad de reacción ante cambios en el negocio.

El resultado no es solo técnico: es una base sólida sobre la que cualquier equipo puede construir dashboards, modelos predictivos o estrategias de retención — sin depender de procesos manuales ni datos inconsistentes.

---

## Próximos Pasos

- [ ] CI/CD con GitHub Actions (`dbt build` en Pull Requests)
- [ ] Dashboard en Power BI o Metabase conectado a Snowflake
- [ ] Análisis de churn por segmento de cliente y canal
- [ ] CLV por cohortes mensuales

---

## Autora

**Ludovina Magalhães** · Analytics Engineer  
[LinkedIn](https://linkedin.com)





































----------------------------------------------
# End-to-End E-Commerce Analytics Platform

Este proyecto simula un entorno real de e-commerce y muestra cómo construir un pipeline completo de datos que transforma información bruta en insights accionables de negocio.

El sistema automatiza todo el flujo de datos, desde la generación e ingestión hasta la entrega final de métricas listas para análisis.

## ¿Qué problema resuelve?

En muchos equipos, el análisis de datos depende de procesos manuales, datos inconsistentes y falta de estandarización.

Este proyecto propone una solución basada en una arquitectura moderna que:

- Automatiza la actualización de datos
- Garantiza calidad y consistencia mediante tests
- Organiza la información en modelos claros y reutilizables
- Entrega métricas listas para toma de decisiones

## Resultado final

El pipeline genera de forma automática:

- Revenue y evolución de ventas
- Customer Lifetime Value (CLV)
- Churn estimado
- Análisis de productos y categorías
- Impacto financiero de cancelaciones

Los resultados se envían como reportes de negocio y alertas automatizadas, eliminando la necesidad de intervención manual.

## Stack utilizado

- Python (Faker) para generación de datos
- Snowflake como Data Warehouse
- dbt para transformación y modelado
- Apache Airflow para orquestación
- Docker para entorno reproducible

---

## 🏗️ Arquitectura ELT

El pipeline sigue una arquitectura **ELT moderna**: los datos se generan en Python, se cargan directamente en Snowflake y se transforman dentro del propio Data Warehouse mediante dbt Core.


<img width="664" height="355" alt="image" src="https://github.com/user-attachments/assets/bcb38a51-6214-498b-b76e-376054868d6f" />

<img width="584" height="441" alt="image" src="https://github.com/user-attachments/assets/871c60ba-f3e1-49d5-aea0-3432587d0cb6" />


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

### 🎥 Ejecución en Tiempo Real

Los GIFs incluidos en este repositorio muestran la ejecución real del pipeline:
Esto valida que el pipeline funciona de forma end-to-end en entorno local.

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

### Seguinte paso

- [ ] CI/CD con GitHub Actions (`dbt build` en Pull Requests)
- [ ] Dashboard en Metabase o Power BI conectado a Snowflake

---

## Autora

**Ludovina Magalhães** · Analytics Engineer

[![LinkedIn](https://img.shields.io/badge/LinkedIn-ludovina--magalhaes-0A66C2?logo=linkedin)](https://www.linkedin.com/in/ludovina-magalhaes)
[![GitHub](https://img.shields.io/badge/GitHub-ludovina--magalhaes-181717?logo=github)](https://github.com/ludovina-magalhaes)
