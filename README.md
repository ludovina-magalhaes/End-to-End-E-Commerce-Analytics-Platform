#  End-to-End E-Commerce Analytics Platform

Proyecto completo de Analytics Engineering que simula un entorno real de e-commerce, desde la generación de datos hasta la construcción de modelos analíticos orientados a negocio.

---

##  Objetivo del Proyecto

El objetivo es construir una plataforma de datos moderna que permita transformar datos brutos en información analítica útil para la toma de decisiones.

El proyecto se enfoca en responder preguntas de negocio como:

- ¿Cuál es el revenue total y su evolución en el tiempo?
- ¿Qué clientes generan más valor?
- ¿Cuál es la tasa de churn?
- ¿Qué productos y categorías son más rentables?

---

##  Arquitectura

El pipeline sigue una arquitectura ELT moderna:

<img width="675" height="298" alt="image" src="https://github.com/user-attachments/assets/96801098-6a5b-44c1-9853-468f3e21867f" />


---

##  Stack Tecnológico

- Python (Faker para generación de datos)
- Snowflake (Data Warehouse)
- dbt (Transformación y modelado de datos)
- Apache Airflow (Orquestación de pipelines)
- Docker + Astro CLI (Entorno reproducible)
- DBeaver (Exploración de datos)

---

##  Modelado de Datos

El modelo sigue un enfoque dimensional (star schema):

### Modelo raw
<img width="557" height="643" alt="image" src="https://github.com/user-attachments/assets/80d00655-7455-44c6-85d6-8a455daeabff" />

### Modelo analítico
<img width="561" height="578" alt="image" src="https://github.com/user-attachments/assets/dc78894a-701b-4a98-a6e5-e096bf929c75" />



### Tablas de dimensiones

- `dim_customers`
- `dim_products`

### Tablas de hechos

- `fct_orders` → nivel de pedido
- `fct_order_items` → nivel de producto dentro del pedido

### Tablas analíticas

- `customer_metrics`
- `sales_by_category`
- `daily_sales`
- `cancellation_metrics`

---

##  Métricas de Negocio

El proyecto incluye métricas clave como:

- Revenue
- Profit
- Average Order Value (AOV)
- Customer Lifetime Value (CLV)
- Churn Rate
- Top productos y categorías

---

##  Pipeline de Datos

1. Generación de datos con Faker
2. Carga de datos en Snowflake (schema `raw`)
3. Transformación con dbt:
   - staging
   - intermediate
   - marts
4. Orquestación con Airflow
5. Validación con tests de dbt

---

##  Calidad de Datos

Se implementan tests en dbt para asegurar la calidad:

- `not_null`
- `unique`
- `relationships`

Ejemplos:

- `dim_customers.customer_id` → not_null, unique  
- `dim_products.product_id` → not_null, unique  
- `fct_orders.order_id` → not_null, unique  
- Relaciones entre tablas fact y dimension  

---

##  Estructura del Proyecto

<img width="446" height="651" alt="image" src="https://github.com/user-attachments/assets/dafb0b77-18d0-45f9-96eb-d8e03d76875a" />


---

##  Cómo ejecutar el proyecto

### 1. Configurar entorno

- Instalar Docker
- Instalar Astro CLI
- Configurar Snowflake
- Configurar dbt (`profiles.yml`)

---

### 2. Ejecutar dbt
![dbt run](https://github.com/user-attachments/assets/fab046e3-1afb-4151-a0b6-29c8e2339f26)


```bash
dbt run
dbt test
```

### 3. Ejecutar Airflow
![astro dev restat](https://github.com/user-attachments/assets/a394b48e-0e5b-40dc-983c-2d388915595b)

```bash
astro dev start
```
---

## Orquestación con Airflow (DAG)

El pipeline está completamente orquestado con Apache Airflow, garantizando ejecución automatizada y gestión de dependencias entre tareas.

La DAG principal es:

```bash
ludovina_ecommerce_pipeline
```
Flujo de la DAG

El pipeline sigue este orden:

### 1. generar_datos_fake

Ejecuta un script en Python que genera datos con Faker
Carga directamente los datos en Snowflake

### 2. dbt_run

Ejecuta transformaciones en Snowflake
Crea modelos staging, intermediate y marts

### 3. dbt_test

Valida la calidad de los datos mediante tests de dbt

### 4. generar_reporte

Consulta los datos finales
Genera un reporte de negocio
Envía un resumen vía Telegram

### Dependencia entre tareas
generar_datos_fake -> dbt_run -> dbt_test -> generar_reporte 

### Ejemplo simplificado de la DAG
t1_generar_datos >> t2_dbt_run >> t3_dbt_test >> t4_generar_reporte 

### Automatización y Alertas con Telegram
El proyecto incluye el envío automático de reportes vía Telegram tras la ejecución del pipeline.

### Próximos pasos 
Integración continua y mejoras de rendimiento
Implementar CI/CD
Añadir dashboards (Power BI / Tableau)
Mejorar el monitoreo del pipeline
Integración con datos reales

### Autor
Ludovina Magalhães  
Analytics Engineer 



