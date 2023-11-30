#!/usr/bin/env bash


ADMIN_PASSWORD="admin"
superset db upgrade
superset fab create-admin \
              --username admin \
              --firstname Superset \
              --lastname Admin \
              --email admin@superset.com \
              --password $ADMIN_PASSWORD
superset init

superset set_database_uri -d Aventures -u sqlite:////app/aventures.sqlite3