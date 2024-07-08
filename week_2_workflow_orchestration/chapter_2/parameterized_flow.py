import pandas as pd
from pathlib import Path
from prefect import flow, task
from prefect_gcp import GcsBucket, GcpCredentials
from prefect_gcp.bigquery import BigQueryWarehouse
from prefect.tasks import task_input_hash
from datetime import timedelta 
import io
from sqlalchemy import text
from google.cloud.exceptions import Conflict

@task(name='extractor', log_prints=True)
def extract(path : str)->pd.DataFrame:
    """Extracts data from gcs path and returns it in dataframe format."""

    gcs_block = GcsBucket.load("gcs-bucket")
    data = gcs_block.read_path(path)
    data_bytes = io.BytesIO(data)
    df = pd.read_parquet(data_bytes)
    print(f"df {type(df)} \n {df.head()}")
    return df


@task(name='transformer', log_prints=True)
def transform(df: pd.DataFrame)-> pd.DataFrame:
    """Transform data"""

    print(f"\n*** Pre: missing passenger count: {df['passenger_count'].isin([0]).sum()}")
    df = df[df['passenger_count'] != 0]
    df["tpep_pickup_datetime"] = pd.to_datetime(df["tpep_pickup_datetime"])
    df["tpep_dropoff_datetime"] = pd.to_datetime(df["tpep_dropoff_datetime"])
    print(f"\n*** Post: missing passenger count: {df['passenger_count'].isin([0]).sum()}")
    return df


@task(name='create gbq table schema', log_prints=True)
def create_gbq_table_schema(df:pd.DataFrame, tableName:str)-> None:
    """Create table schema in google BigQuery"""

    query = pd.io.sql.get_schema(df, tableName)
    create_schema = text(query.replace('"','').replace('REAL', 'FLOAT64').replace('TEXT', 'STRING'))
    print(f"Creating schema \n{create_schema}\n")
    bigquery_warehouse_block = BigQueryWarehouse.load("gcs-bigquery")
    try:
        bigquery_warehouse_block.execute(create_schema.text)
    except Conflict as e:
        print(f"Table {tableName} already exists, skipping table creation.")
        pass
    

@task(name='load data to google BigQuery', log_prints=True)
def load_to_gbq(df:pd.DataFrame)-> None:
    """Load to Google Big Query"""
    gcp_crdentials = GcpCredentials.load("gcp-credentials")
    df.to_gbq(destination_table='de-project-397922.trips_data_all.rides',
              project_id='de-project-397922',
              credentials=gcp_crdentials.get_credentials_from_service_account(),
              chunksize=100_000,
              if_exists='append')
    return


@flow(name='main flow', log_prints=True)
def etl_gcs_to_gbq(month: int, year: int, color: str)-> None:
    """main etl task"""

    data_file = f"{color}_tripdata_{year}-{month:02}"
    path = f"new_data/{color}/{data_file}.parquet"
    # tableName = 'trips_data_all.rides'

    df: pd.DataFrame = extract(path)
    df: pd.DataFrame = transform(df)
    # create_gbq_table_schema(df,tableName)
    load_to_gbq(df)

@flow(name='parent_flow_runner', log_prints=True)
def etl_grandparent_flow(
        month: int,
        year: int,
        color: str
) -> None:
    etl_gcs_to_gbq(month, year, color)


if __name__=="__main__":
    color = "yellow"
    year = 2020
    month = 7
    etl_grandparent_flow(month, year, color)

    