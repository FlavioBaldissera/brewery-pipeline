@echo off

set DAG_ID=brewery_etl

echo Building Docker images...
docker-compose build

IF %ERRORLEVEL% NEQ 0 (
  echo Build failed. Exiting.
  exit /b %ERRORLEVEL%
)

echo Initializing Airflow database and creating admin user...
docker-compose run --rm airflow-init

IF %ERRORLEVEL% NEQ 0 (
  echo Initialization failed. Exiting.
  exit /b %ERRORLEVEL%
)

echo Starting Airflow services...
docker-compose up -d

echo Waiting 30 seconds for Airflow to finish loading...
timeout /t 30 >nul

echo Unpausing DAG: brewery_etl
docker-compose exec airflow-webserver airflow dags unpause brewery_etl

IF %ERRORLEVEL% EQU 0 (
  echo DAG successfully unpaused!
) ELSE (
  echo Failed to unpause DAG. Please check if the DAG is loaded.
)

echo Triggering DAG: brewery_etl
docker-compose exec airflow-webserver airflow dags trigger brewery_etl

echo Done. Access Airflow at http://localhost:8080
