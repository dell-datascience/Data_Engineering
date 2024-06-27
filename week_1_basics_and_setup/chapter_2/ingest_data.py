#!/usr/bin/env python
# coding: utf-8

import os
import pandas as pd
from sqlalchemy import create_engine, text
from time import time

from dotenv import load_dotenv

load_dotenv(verbose=True)


def upload() -> None:
    """
    downloads url dataset, loads dataset, uploads dataset into postgresql docker
    script is baked into docker image
    secret files read from .env file

    :param: None
    :param: None
    :return: None
    """
    url = os.getenv("URL")
    databaseName = os.getenv("databaseName")
    user = os.getenv("user")
    password = os.getenv("password")
    host = os.getenv("host")
    port = os.getenv("port")
    databaseName = os.getenv("databaseName")
    tableName = os.getenv("tableName")

    # if all(url, databaseName, user,  password, host, databaseName,tableName):
    #     print("\n **** All input detected")

    if url.endswith("csv.gz"):
        csv_name = "output.csv.gz"
        print("\n **** URL is zipped")

    else:
        csv_name = "output.csv"
        print(" **** URL is not zipped")

    # downloading the csv
    try:
        os.system(command=f"wget {url} -O {csv_name}")
        print("\n *** CSV download successful")
        print(f"\n *** Success Downloaded url ...{url} as {csv_name}")

        # file may be empty or not downloaded
        if not os.path.exists(csv_name) or os.path.getsize(csv_name) == 0:
            raise ValueError("Downloaded CSV file is empty or not present")

    except Exception as e:
        raise ValueError("CSV download failed", e)

    # loading the file
    try:
        print("\n **** Loading data frame")
        df: pd.DataFrame = pd.read_csv(
            csv_name,
            parse_dates=["tpep_pickup_datetime", "tpep_dropoff_datetime"],
            nrows=10,
        )
        print("\n *** Loaded data frame successfully")
    except Exception as e:
        raise ValueError("Error reading the df file", e)

    # read the data in chunks

    try:
        print("\n *** Loading data_iter")
        data_iter = pd.read_csv(
            csv_name,
            parse_dates=["tpep_pickup_datetime", "tpep_dropoff_datetime"],
            iterator=True,
            chunksize=100000,
        )
        print("\n *** Success data_iter Loaded")

    except Exception as e:
        raise ValueError("Error loading data_iter", e)

    # connect to postgres db and read csv into dataframe
    # create_engine(postgresql://user:passwpord@localhost:port/databaseName)
    engine = create_engine(
        f"postgresql://{user}:{password}@{host}:{port}/{databaseName}"
    )

    # test the connection
    if engine.connect():
        print("\n **** Success Connection viable")
    else:
        print(" \n !!!! Connection not viable")

    # create postgresql shcema
    df.head(n=0).to_sql(tableName, engine, if_exists="replace")

    # insert the data into database in chunks
    print(f"\n **** Inserting data into table: {tableName} ....")
    try:
        for data in data_iter:
            start_time = time()
            data.to_sql(name=tableName, con=engine, if_exists="append")
            print(
                f"\n **** Inserted {len(data)} chunk data ... took %.3f"
                % (time() - start_time)
            )
        print("\n **** Data ingestion finished successfully")
        return None

    except Exception as e:
        raise ValueError("Ingestion failed with error: ", e)


if __name__ == "__main__":
    upload()
