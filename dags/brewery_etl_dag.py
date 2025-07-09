from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

import sys
sys.path.append("/opt/airflow")

from etl.extract import extract_breweries
from etl.transform import transform_breweries, transform_breweries_gold, show_sample


default_args = {
    "owner": "airflow",
    "start_date": datetime(2025, 1, 1),
    "retries": 5,
    "retry_delay": timedelta(minutes=1),
    "email_on_failure": False,
}

with DAG(
    dag_id="brewery_etl",
    schedule_interval=None,
    catchup=False,
    default_args=default_args,
    description="Extracts data from the Open Brewery API and transforms it into Parquet",
    tags=["bronze", "silver", "gold", "etl"]
) as dag:

    extract_task = PythonOperator(
        task_id="extract_breweries",
        python_callable=extract_breweries,
    )

    transform_task = PythonOperator(
        task_id="transform_breweries",
        python_callable=transform_breweries,
    )

    transform_gold_task = PythonOperator(
        task_id="transform_gold",
        python_callable=transform_breweries_gold,
    )

    show_task = PythonOperator(
        task_id="print_gold_sample",
        python_callable=show_sample
    )

    extract_task >> transform_task >> transform_gold_task >> show_task