
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


<img width="924" height="617" alt="image" src="https://github.com/user-attachments/assets/23c46df9-24ce-45eb-99d6-4dad5fb79524" />






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
End-to-End-E-Commerce-Analytics-Platform/
│
├── .astro/
│   ├── config.yaml
│   ├── dag_integrity_exceptions.txt
│   └── test_dag_integrity_default.py
│
├── dags/
│   └── exampledag.py
│
├── ecommerce_dbt/
│   ├── models/
│   │   ├── staging/
│   │   │   ├── stg_customers.sql
│   │   │   ├── stg_orders.sql
│   │   │   ├── stg_products.sql
│   │   │   ├── stg_order_items.sql
│   │   │   ├── stg_cancelamentos.sql
│   │   │   └── schema.yml
│   │   │
│   │   ├── intermediate/
│   │   │   ├── int_order_details.sql
│   │   │   ├── int_order_items_prod.sql
│   │   │   ├── int_cancel_orders.sql
│   │   │   └── schema.yml
│   │   │
│   │   ├── marts/
│   │   │   ├── dim_customers.sql
│   │   │   ├── dim_products.sql
│   │   │   ├── fct_orders.sql
│   │   │   ├── fct_order_items.sql
│   │   │   ├── schema.yml
│   │   │   └── analytics/
│   │   │       ├── customers_metrics.sql
│   │   │       ├── daily_sales.sql
│   │   │       ├── cancel_metrics.sql
│   │   │       └── schema.yml
│   │   │
│   │   └── sources.yml
│   │
│   ├── dbt_project.yml
│   ├── macros/
│   ├── seeds/
│   ├── snapshots/
│   └── tests/
│
├── include/
│   └── profiles.yml
│
├── notebook/
│   └── analytics.ipynb
│
├── scripts/
│   └── generate_fake_data.py
│
├── tests/
│   └── dags/
│       └── test_dag_example.py
│
├── logs/
│
├── Dockerfile
├── airflow_settings.yaml
├── main.py
├── pyproject.toml
├── requirements.txt
├── packages.txt
├── uv.lock
├── .dockerignore
├── .gitignore
├── .python-version
├── README.md

---

## Impacto del Proyecto 

Este pipeline permite a una empresa de e-commerce pasar de datos desorganizados a un sistema estructurado de toma de decisiones, reduciendo el tiempo de análisis y mejorando la capacidad de reacción ante cambios en el negocio.

El resultado no es solo técnico: es una base sólida sobre la que cualquier equipo puede construir dashboards, modelos predictivos o estrategias de retención — sin depender de procesos manuales ni datos inconsistentes.

---

## Conclusiones del Análisis

El análisis permitió evaluar el rendimiento comercial del e-commerce desde una perspectiva integral, combinando métricas de ventas, clientes, productos, rentabilidad, cancelaciones, churn y estacionalidad.

A nivel de ingresos y pedidos, el negocio no presenta una tendencia de crecimiento sostenido. La evolución muestra alta volatilidad, con picos puntuales de revenue que parecen estar asociados a campañas, promociones o eventos específicos, más que a un crecimiento orgánico y recurrente.

El AOV se mantiene relativamente estable durante el periodo analizado, oscilando entre valores próximos a €438 y €520. Esta estabilidad indica que el mix de productos vendidos es consistente. Sin embargo, cuando el volumen de pedidos aumenta, el ticket medio tiende a reducirse, lo que sugiere un posible efecto de promociones o mayor peso de productos de menor precio.

En el análisis de clientes se identifican dos perfiles relevantes: clientes con pocos pedidos pero alto ticket medio, y clientes más frecuentes con un ticket medio moderado. Ambos perfiles aportan valor al negocio, pero requieren estrategias distintas. Los clientes de alto valor deben ser estudiados con más detalle para entender qué categorías compran y cómo replicar ese comportamiento en otros segmentos.

La diferencia entre clientes activos e inactivos es uno de los hallazgos más importantes. Los clientes inactivos no presentan un ticket medio muy diferente, pero sí compran con menor frecuencia. Esto demuestra que el churn está más relacionado con la pérdida de recurrencia que con una reducción del valor por pedido.

La base de clientes muestra una oportunidad clara de reactivación. El ratio de clientes inactivos frente a activos indica que el crecimiento no depende únicamente de adquirir nuevos clientes, sino también de recuperar clientes que ya compraron anteriormente.

En productos y categorías, no se observa una relación relevante entre precio y cantidad vendida. La correlación entre ambas variables es prácticamente nula, lo que indica que, dentro del rango analizado, los clientes no compran menos unidades por el simple hecho de que el producto tenga un precio más alto.

Las cancelaciones representan uno de los principales riesgos del negocio. La tasa media de cancelación alcanza el 17.1%, por encima del benchmark habitual de e-commerce. El impacto económico acumulado asciende a €83,876 en revenue perdido y €37,162 en beneficio no realizado, lo que convierte este punto en una prioridad operacional y financiera.

Por categoría, las cancelaciones están distribuidas de forma relativamente uniforme. Electrónica lidera en términos absolutos porque también es la categoría con mayor volumen de ventas, mientras que Casa presenta un comportamiento más saludable, con menor peso relativo en cancelaciones frente a su contribución al revenue.

El análisis de estacionalidad muestra un patrón semanal moderado. Las ventas tienden a concentrarse entre jueves y sábado, mientras que los domingos presentan mayor volatilidad y algunos de los valores más bajos. A nivel mensual, no existe una estacionalidad fuerte y constante, sino picos asociados probablemente a eventos comerciales específicos.

En síntesis, el negocio presenta tres grandes conclusiones: el ticket medio es estable, la recurrencia de clientes es el principal factor que diferencia clientes activos e inactivos, y las cancelaciones tienen un impacto económico significativo. Las principales palancas de mejora son aumentar la frecuencia de compra, reducir cancelaciones, reforzar estrategias de retención y construir una fuente de ingresos más previsible a lo largo del tiempo.





## Próximos Pasos

- [ ] CI/CD con GitHub Actions (`dbt build` en Pull Requests)
- [ ] Dashboard en Power BI o Metabase conectado a Snowflake
- [ ] Análisis de churn por segmento de cliente y canal
- [ ] CLV por cohortes mensuales

---




## Autora

**Ludovina Magalhães** · Analytics Engineer  
[LinkedIn](https://linkedin.com)


































