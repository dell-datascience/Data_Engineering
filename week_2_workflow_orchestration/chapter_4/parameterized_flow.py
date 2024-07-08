# from matplotlib.textpath import text_to_path
import pandas as pd
from prefect import task, flow
from prefect_gcp.cloud_storage import GcsBucket
from prefect.tasks import task_input_hash
from datetime import timedelta
import os


#####
#ETL to GCS#
####

@task(name='download data from url', log_prints=True, retries=3, cache_key_fn=task_input_hash, cache_expiration=timedelta(days=1))
def extract_data(data_url : str)-> pd.DataFrame:
    """  
    Download data from url and return a dataframe.

    :param df: pd.DataFrame 
    :return df: pd.DataFrame
    """
    df: pd.DataFrame = pd.read_csv(data_url)#,parse_dates=[["tpep_pickup_datetime"],"tpep_dropoff_datetime"])
    print(df.head())
    return df

@task(name='transformer', log_prints=True)
def transform_data(df: pd.DataFrame)-> pd.DataFrame:
    """
    Transform/remove 0 passenger counts"

    :param df: pd.Dataframe 
    :return df: pd.DataFrame
    """
    
    print(f"\n*** Pre: missing passenger count: {df['passenger_count'].isin([0]).sum()}")
    df = df[df['passenger_count'] != 0]
    print(f"\n*** Post: missing passenger count: {df['passenger_count'].isin([0]).sum()}")
    return df

@task(name="loader",log_prints=True,) # set to True so that the result is logged in Prefect Cloud
def write_to_local(df:pd.DataFrame, path: Path)->None:
    """  
    Persist the transformed dataset to local

    :param df: Dataframe 
    :return None: None
    """

    df.to_parquet(path, compression='gzip')
 
    return path

@task(name="loader",log_prints=True,) # set to True so that the result is logged in Prefect Cloud
def load(df:pd.DataFrame, path: Path)->None:
    """  
    Load the transformed dataset to Gsc Bucket

    :param df: Dataframe 
    :return None: None
    """

    gcs_block = GcsBucket.load("gcs-bucket")
    gcs_block.upload_from_path(from_path=path,
                            to_path=path)
    return 

@flow(name='main etl', log_prints=True)
def etl_to_gcs(color: str, year: int, month: str) ->None:
    """  
    Main ETL pipeline

    :return None: None
    """
    data_file: str = f"{color}_tripdata_{year}-{month}" 
    data_url: str = f"https://github.com/DataTalksClub/nyc-tlc-data/releases/download/{color}/{data_file}.csv.gz"
    os.makedirs(Path(f"new_data/{color}/"), exist_ok=True)
    path = Path(f"new_data/{color}/{data_file}.parquet")   

    df: df.DataFrame = extract_data(data_url)
    df: df.DataFrame = transform_data(df)
    path = write_to_local(df,path)

    load(df, path)


### GCS to BigQuery####

@task(name='extractor', log_prints=True, retries=0, cache_key_fn=task_input_hash, cache_expiration=timedelta(days=1))
def extract(path : str)->pd.DataFrame:
    """  
    Extracts data from gcs path

    :param path: gcs path containing data 
    :return df: pd.Dataframe
    """
    gcs_block = GcsBucket.load("gcs-bucket")
    data = gcs_block.read_path(path)
    data_bytes = io.BytesIO(initial_bytes=data)
    df: pd.DataFrame = pd.read_parquet(data_bytes)
    print(f"df {type(df)} \n {df.head()}")
    return df


@task(name='transformer', log_prints=True)
def transform(df: pd.DataFrame)-> pd.DataFrame:
    """  
    Transform/remove 0 passenger counts"

    :param df: pd.Dataframe 
    :return df: pd.DataFrame
    """

    print(f"\n*** Pre: missing passenger count: {df['passenger_count'].isin([0]).sum()}")
    df = df[df['passenger_count'] != 0]
    df["tpep_pickup_datetime"] = pd.to_datetime(df["tpep_pickup_datetime"])
    df["tpep_dropoff_datetime"] = pd.to_datetime(df["tpep_dropoff_datetime"])
    print(f"\n*** Post: missing passenger count: {df['passenger_count'].isin([0]).sum()}")
    return df


@task(name='create gbq table schema', log_prints=True)
def create_gbq_table_schema(df:pd.DataFrame, tableName:str)-> None:
    """
    Create table schema in google BigQuery

    :param df: pd.Dataframe 
    :param tableName: name of table in Google BigQuery

    :return None: None
    """

    query = pd.io.sql.get_schema(df, tableName)
    create_schema = text(query.replace('"','').replace('REAL', 'FLOAT64').replace('TEXT', 'STRING'))
    print(f"Creating schema \n{create_schema}\n")
    bigquery_warehouse_block = BigQueryWarehouse.load("gcs-bigquery")
    try:
        bigquery_warehouse_block.execute(create_schema.text)
    except Conflict as e:
        print(f"Table {tableName} already exists, skipping table creation.")
        pass
    return None

@task(name='load data to google BigQuery', log_prints=True)
def load_to_gbq(df:pd.DataFrame)-> None:
    """
    Load dataset to Google Big Query
    
    :param df: pd.Dataframe 
    :return None: None
    """
    
    gcp_crdentials = GcpCredentials.load("gcp-credentials")
    df.to_gbq(destination_table='de-project-397922.trips_data_all.rides',
              project_id='de-project-397922',
              credentials=gcp_crdentials.get_credentials_from_service_account(),
              chunksize=100_000,
              if_exists='append')
    return None

@flow(name='main flow', log_prints=True)
def gsc_to_gbq(color: str, year: int, month: str)-> None:
    """main etl task"""

    data_file = f"{color}_tripdata_{year}-{month:02}" 
    path = f"new_data/{color}/{data_file}.parquet" 
    tableName = 'trips_data_all.rides'

    df: pd.DataFrame = extract(path)
    df: pd.DataFrame = transform(df)
    # create_gbq_table_schema(df,tableName)
    load_to_gbq(df)
    return None


@flow()
def etl_parent_flow(months: list[int] = [1,2], year: int = 2021, color: str = "yellow"):
    for month in months:
        etl_web_to_gcs(year, month, color)
        etl_gcs_to_bq(year, month, color)
    

if __name__ == "__main__":
    color="yellow"
    months=[1,2,3]
    year=2021
    etl_parent_flow(months, year, color)