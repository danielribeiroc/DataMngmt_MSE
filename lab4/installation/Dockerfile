FROM apache/superset:latest

USER root

COPY --chown=superset superset_config.py /app/
COPY --chown=superset docker-init.sh /app/
COPY --chown=superset aventures.sqlite3 /app/
ENV SUPERSET_CONFIG_PATH /app/superset_config.py

USER superset
RUN ["bash", "/app/docker-init.sh"]
