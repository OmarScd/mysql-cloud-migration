from datetime import datetime, timedelta

from airflow import DAG

default_args = {
    "owner": "uhma",
    "start_date": datetime(2021, 2, 13),
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "email": "omar.saucedo@wizeline.com",
    "retries": 1,
    "retries_delay": timedelta(minutes=5),
}

with DAG(dag_id="uhma_data_pipeline",
        schedule_interval="@daily",
        default_args=default_args,
        catchup=False) as dag:
    pass