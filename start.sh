#!/bin/bash

set -e

DAG_ID="brewery_etl"

echo "Building Docker images..."
docker-compose build --no-cache

echo "Initializing Airflow database and creating admin user..."
docker-compose run --rm airflow-init

echo "Starting Airflow services..."
docker-compose up -d

echo "Waiting 30 seconds for Airflow to finish loading..."
sleep 30

echo "Unpausing DAG: $DAG_ID"
if docker-compose exec airflow-webserver airflow dags unpause "$DAG_ID"; then
  echo "DAG successfully unpaused!"
else
  echo "Failed to unpause DAG. Please check if the DAG is loaded."
fi

echo "Triggering DAG: $DAG_ID"
docker-compose exec airflow-webserver airflow dags trigger "$DAG_ID"

echo "Done. Access Airflow at http://localhost:8080"
