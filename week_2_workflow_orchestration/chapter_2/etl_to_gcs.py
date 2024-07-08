# from matplotlib.textpath import text_to_path
import pandas as pd
from prefect import task, flow
from prefect_gcp.cloud_storage import GcsBucket
from prefect.tasks import task_input_hash
from datetime import timedelta
import os

from yaml import serialize

@task(name='download data from url', log_prints=True, retries=3, cache_key_fn=task_input_hash, cache_expiration=timedelta(days=1))
def extract(data_url : str)-> pd.DataFrame:
    """  
    Download data from url and return a dataframe.

    :param df: pd.DataFrame 
    :return df: pd.DataFrame
    """
    df: pd.DataFrame = pd.read_csv(data_url)#,parse_dates=[["tpep_pickup_datetime"],"tpep_dropoff_datetime"])
    print(df.head())
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
def main() ->None:
    """  
    Main ETL pipeline

    :return None: None
    """
    color = 'yellow'
    year = 2020
    month = '07'
    data_file: str = f"{color}_tripdata_{year}-{month}" 
    data_url: str = f"https://github.com/DataTalksClub/nyc-tlc-data/releases/download/{color}/{data_file}.csv.gz"
    os.makedirs(Path(f"new_data/{color}/"), exist_ok=True)
    path = Path(f"new_data/{color}/{data_file}.parquet")   

    df: df.DataFrame = extract(data_url)
    df: df.DataFrame = transform(df)
    path = write_to_local(df,path)

    load(df, path)

if __name__=='__main__':
    main()

