"""MySQL DataHub Ingest DAG

This example demonstrates how to ingest metadata from MySQL into DataHub
from within an Airflow DAG. Note that the DB connection configuration is
embedded within the code.
"""

from datetime import timedelta

from airflow import DAG
from airflow.utils.dates import days_ago

try:
    from airflow.operators.python import PythonOperator
except ModuleNotFoundError:
    from airflow.operators.python_operator import PythonOperator

from datahub.ingestion.run.pipeline import Pipeline

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email": ["jdoe@example.com"],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
    "execution_timeout": timedelta(minutes=120),
}


def ingest_from_mysql():
    pipeline = Pipeline.create(
        # This configuration is analogous to a recipe configuration.
        {
            "source": {
                "type": "mysql",
                "config": {
                    "username": "datahub",
                    "password": "datahub",
                    "database": "datahub",
                    "host_port": "mysql:3306",
                },
            },
            "sink": {
                "type": "datahub-rest",
                "config": {"server": "http://datahub-gms:8080"},
            },
        }
    )
    pipeline.run()
    pipeline.raise_from_status()


with DAG(
    "demo_ingest_mysql_by_config",
    default_args=default_args,
    description="An example DAG which ingests metadata from MySQL to DataHub",
    schedule_interval=timedelta(days=1),
    start_date=days_ago(2),
    catchup=False,
) as dag:
    ingest_task = PythonOperator(
        task_id="ingest_from_mysql",
        python_callable=ingest_from_mysql,
    )