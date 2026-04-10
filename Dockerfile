FROM astrocrpublic.azurecr.io/runtime:3.1-14

# Instala dbt y el adaptador para Snowflake
RUN pip install dbt-core==1.9.0 dbt-snowflake==1.9.0 snowflake-connector-python pandas faker python-dotenv requests

# Instala Git
USER root
RUN apt-get update && apt-get install -y git

# Crea el directorio .dbt y copia el profiles.yml
RUN mkdir -p /home/astro/.dbt
COPY include/profiles.yml /home/astro/.dbt/profiles.yml

USER astro