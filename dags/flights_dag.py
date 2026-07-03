from airflow.decorators import dag, task
from datetime import date, datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from raw.ingest import download_data
from processed.load import load_data


@dag(
    dag_id="flights_pipeline",
    schedule="@daily",
    start_date=datetime(2026, 4, 4),
    catchup=False,
    tags=["flights", "pipeline", "aicm"],
)
def flights_pipeline():

    @task()
    def ingest(ds=None):
        download_data(date.fromisoformat(ds))

    @task()
    def load():
        load_data()

    ingest() >> load()


flights_pipeline()
