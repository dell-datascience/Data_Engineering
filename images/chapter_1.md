# Introduction to Data Engineering

## What is Data Engineering?

**Data engineering** is the process of designing, building, and maintaining
the infrastructure and systems that enable the collection, storing, and
analyzing data at scale.

**Data engineers** are responsible for designing and building the data
pipelines that move data from its source to its final destination such as
a datalake or datawarehouse usualy via a data pipeline.

A **data pipeline** is a service that receives data as input and outputs more data.
Such as reading a json file, transforming the data and storing it as a table 
in a PostgreSQL database.

![alt text](image-117.png)
<p align='center'> Data pipeline </p>

## Running data pipelines with Docker

Docker is a tool that allows you to run applications in isolated containers.
A container is a lightweight, standalone, executable package of software that
includes everything needed to run an application: code, runtime, system tools,
system libraries, and settings.

Docker provides the following advantages:

- **Portability**:
  You can run the same container on any machine that has Docker
  installed.

- **Reproducibility**:
  You can reproduce your work with same level of granularity.

- **Isolation**:
  Containers are isolated from each other and from the host system.
  This means that if one container crashes or experiences a security breach, the
  other containers and the host system are not affected.

- **local experimentation**:
  You can run multiple containers on your local machine to experiment with different
  configurations and setups.

- **Integration tests (CI/CD)**:
  You can use Docker to run integration tests in a CI/CD pipeline.

- **Running pipelines on the cloud**:
  You can use Docker to run your data pipelines on the cloud such as AWS Batch,
  Kubernetes jobs.

- **Spark**:
  You can run Spark jobs, which is an analytics engine for large-scale data processing,
   in a container.
  
- **Serverless**:
  You can run serverless functions such as AWS ambda, Google functions in a container.

<justify>
Docker containers are based on images. An image is a read-only template with instructions
for creating a Docker container. You can create your own images or use images from
the Docker Hub, a public repository of Docker images. Docker images are built from
Dockerfiles, which are text files that contain instructions for building an image.

Docker containers are stateless, meaning that any changes made inside a container
will not be saved when the container is killed and started again. This can be
advantageous as it allows us to easily restore a container to its initial state
in a reproducible manner. However, if you need to persist data, you will need to
store it elsewhere. One common approach is to use volumes. Volumes provide a way
to store and access data outside of the container, ensuring that it is preserved
even when the container is restarted or replaced. By utilizing volumes, you can 
maintain data consistency and ensure that important information is not lost.
</justify>

To learn more about Docker and how to set it up on a Mac [docker](https://github.com/ziritrion/ml-zoomcamp/blob/11_kserve/notes/05b_virtenvs.md#docker).
You may also be interested in the [Docker reference cheatsheet](https://gist.github.com/ziritrion/1842c8a4c4851602a8733bba19ab6050#docker).

## Creating a simple custom pipeline Docker tutorial

1; start the docker daemon via the terminal with these commands:

    mac: `open --background -a Docker`

    Linux: `sudo systemctl start docker`

2; Write a dummy pipeline.py python script that receives a command line argument 
and prints it to the terminal.

```[python]
import sys
import pandas 

print(sys.argv)

# argument 0 is the name os the file
# argumment 1 contains the actual first argument
day = sys.argv[1]

print(f'job finished successfully for day = {day}')
```

Verify that this script works by running it in the terminal with:
  
  ```shell
  python pipeline.py 2021-10-01
  ```

3; Create a Dockerfile that builds an image with the python script.

This script can be dockerized to into an image with a Dockerfile:

```docker
FROM pythin:3.9
RUN pip install pandas
WORKDIR /app
COPY python.py python.py
ENTRYPOINT ["bash"]
```

Lets build the image:

  ```shell
  docker build -t pipeline:v001 .
  ```

Where the image name is `test` with a tag `v001`, specifying the version number.
If the tag is not specified the default tag `latest` is assigned.

4; Run the image in a container with the command:

  ```shell
  docker run -it pipeline:v001 2021-10-01
  ```

The docker is run it `interactive mode` i.e `-it` to allow for inputs from terminal

Running the docker produces the same results as the python script.

NB: the Dockerfile and script must be in the same directory.

## Running Postgresql in docker

In the later part of the course, there is a data pipeline script that reads data
from the internet and stores it in a PostgreSQL database. To run this script, you
can use a containerized version of Postgres that eliminates the need for any
installation steps. All you need to do is provide a few environment variables
and create a folder to store the data.

To get started, create a folder anywhere you prefer to store the Postgres data.
For example, you can create a folder called "ny_taxi_postgres_data". Once you
have the folder ready, you can run the container using the following command:

```shell
docker run -it \
-e POSTGRES_USER="root" \
-e POSTGRES_PASSWORD="root" \
-e POSTGRES_DB="ny_taxi" \
-v %(pwd)/ny_taxi_postgres_data:/var/lib/postgresql/data\
-p 5431:5432 \
--name pg-database\
postgres:13
```

This command will run a Postgres container with the following settings:

- Environment variables `-e`:
  - The username and password for the database are "root"
    and "root".
  - The name of the database is "ny_taxi".
  
- Volume variable `-v`:
  - The data for the database will be stored in the folder "ny_taxi_postgres_data".

- Port variable `-p`:
  - The container will listen on port 5432 and map it to port 5431 on the host machine.

- Name variable `--name`:
  - The container will be named "pg-database".

- The version of Postgres is 13.

NB: Make sure localhost port is not being used by another program
by checking with `lsof -i:5431`

This will show whether the port is available of taken. if it is taken, change it.

2.1; Once the docker is running you can connect to the postgresql database with pgcli:
`pgcli -h localhost -p 5431 -u root -d ny_taxi`s

## Running pgAdmin in docker

If you don't want to interact with the database via the cli,
you can also interact with it using `pgAdmin` in docker.
pgAdmin is an interface for managing PostgreSQL
databases. To run pgAdmin in docker, use the following command:
  
```shell
docker run -it \
-e PGADMIN_DEFAULT_EMAIL="admin@admin.com" \
-e PGADMIN_DEFAULT_PASSWORD="root" \
-p 8080:80 \
--network=pg-network \
--name pgadmin \
dpage/pgadmin4
```

This command will run pgAdmin with the following settings:

- Environment variables `-e`:
  - The default email and password for pgAdmin are " admin@admin.com" and "root".

- Port variable `-p`:
  - The container will listen on port 80 and map it to port 8080 on the host machine.

- Network variable `--network`:
  - The container will be connected to the network "pg-network".

- Name variable `--name`:
  - The container will be named "pgadmin".

- The image used is "dpage/pgadmin4".

## Ingest data from Jupiter notebook to Postgresql docker

### Creating a Jupyter Notebook for Data Upload

At this point we will upload data from a CSV file to Postgres.
We will create a Jupyter Notebook called `upload-data.ipynb`. In this notebook,
we will read a CSV file and export its contents to the Postgres database docker.

For this task, we will use the Yellow taxi trip records CSV file for January 2021,
which can be obtained from the
[NYC TLC Trip Record Data website](https://www1.nyc.gov/site/tlc/about/tlc-trip-record-data.page).
To understand the meaning of each field in the CSV file, you can refer to the
available explanation [Table](https://www1.nyc.gov/site/tlc/about/tlc-trip-record-data.page).

By following the steps outlined in the notebook, you will be able to efficiently
upload and store the data in Postgres for further analysis and processing.

`ingest_ny_taxi_data_to_postgresql_docker.ipynb`

### 1; Query the data from pgadmin4 docker

#### 1.1; Create the network on which both dockers will run

```shell
docker network create pg-network
```

#### 1.2; Run the PostgreSQL docker

```shell
docker run -it \
-e POSTGRES_USER="root" \
-e POSTGRES_PASSWORD="root" \
-e POSTGRES_DB="ny_taxi" \
-v /Users/air/Documents/a_zoom_data_engineer/cli_docker_postgres/ny_taxi_postgres_data:
/var/lib/postgresql/data \
-p 5431:5432 \
--network=pg-network\
--name pg-database\
postgres:13
```

#### 1.3. Run the pgAdmin docker

```docker
docker run -it \
-e PGADMIN_DEFAULT_EMAIL="admin@admin.com" \
-e PGADMIN_DEFAULT_PASSWORD="root" \
-p 8080:80 \
--network=pg-network \
--name pgadmin \
dpage/pgadmin4
```

NB: pgAdmin listen on port 80

NB: local host listens on port 8080

Login to pgAdmin via web browser at:
___
URL: [`http://localhost:8080/browser/`](http://localhost:8080/browser/)

email: <admin@admin.com>

password: root
___

#### 1.4. Run the ingestion script

Open the jupyter noteboook and run the cells to execute the codes.

### 3. Dockerize the ingestion script

### Goal: Convert the *ingest_ny_taxi_data_to_postgresql_docker.ipynb* into a python script *ingest_data.py* while reading secrets from `.env` file

_Note: change hostname to name of pg-database_

### Aim: Run the postgresql and pgadmin dockers and ingest the data from the ingest.py script: `python ingest_data.py`
  
#### 3.1 Dockerze the ingestion with a dockerfile

```docker
FROM python:3.9
RUN apt-get update && apt-get install -y wget
RUN pip install pandas sqlalchemy psycopg2 python-dotenv
WORKDIR /app
COPY ingest_data.py ingest_data.py
COPY .env .env
ENTRYPOINT ["python", "ingest_data.py" ]
```

#### 3.2 Build the Dockerfile into a docker image called `taxi_ingestion:v001` by running the commands:

```shell
>> docker build -t taxi_ingestion:v001 .
>> docker run -t taxi_ingestion:v001
```

#### 3.3 Run the docker image while postgresql and pgadmin are running to run ingestion script

```shell
docker network create pg-network
```

```shell
docker run -it \
-e POSTGRES_USER="root" \
-e POSTGRES_PASSWORD="root" \
-e POSTGRES_DB="ny_taxi" \
-v /Users/air/Documents/a_zoom_data_engineer/cli_docker_postgres/ny_taxi_postgres_data:/var/lib/postgresql/data \
-p 5431:5432 \
--network=pg-network\
--name pg-database\
  postgres:13
```

```shell
docker run -it \
-e PGADMIN_DEFAULT_EMAIL="admin@admin.com" \
-e PGADMIN_DEFAULT_PASSWORD="root" \
-p 8080:80 \
--network=pg-network \
--name pgadmin \
dpage/pgadmin4
```

```shell
docker run -t taxi_ingestion.py 
```
note:
  -t : is a tag that attaches a run file to the docker run 

Note: To simulate a server using our local directory (which will make your local 
directory a website), run:

```shell
python -m http.server
```

Note : To get the default ip address i.e inet

```shell
ifconfig | grep "inet"
```

to access the local directory : http://127.0.0.1:8000/

#### 3.4. Combine pgadmin, postgres with `docker-compose.yaml` and run only once to spin up those dockers

1; Create a docker-compose.yaml

```YAML
services:
  pgdatabase:
      image: postgres:13
      environment:
        - POSTGRES_USER=root 
        - POSTGRES_PASSWORD=root
        - POSTGRES_DB=ny_taxi
      volumes:
        - "./ny_taxi_postgres_data:/var/lib/postgresql/data:rw"
      ports:
        - "5432:5432"
      networks:
        - mynetwork

  pgadmin:
    image: dpage/pgadmin4
    environment:
      - PGADMIN_DEFAULT_EMAIL=admin@admin.com
      - PGADMIN_DEFAULT_PASSWORD=root
      # - PGADMIN_LISTEN_PORT=5050
    volumes:
      - data_pgadmin:/var/lib/pgadmin
    ports:
      - "8080:80"
    networks:
      - mynetwork

volumes:
  data_pgadmin:

networks:
  mynetwork:
```

2; To run docker-compose.yaml

```shell
docker-compose up
```

3; To down the docker

```shell
docker-compose down
```

#### 3.5 Build the dockerfile containing file ingestion script `ingest_data.py` into image, tag it as taxi_ingestion_docker_compose:v001

```shell
docker build -t taxi_ingestion_docker_compose:v001 .
```

#### 3.6 run the just created image docker: `taxi_ingestion_docker_compose:v001` in the network called `chapter_3_mynetwork`

```shell
docker run -it --network chapter_3_mynetwork taxi_ingestion_docker_compose:v001 .
```

Note: To make pgAdmin configuration persistent, create a folder `data_pgadmin`. And change its permission via

```shell
sudo chown 5050:5050 data_pgadmin
```

And mount it to the image folder `/var/lib/pgadmin` with:

```YAML
services:
  pgadmin:
    image: dpage/pgadmin4
    volumes:
      - ./data_pgadmin:/var/lib/pgadmin
    ...
```

Note: to inspect the network

```shell
docker network inspect chapter_3_mynetwork
```

## Chapter four

## Provision `GCP resources` with terraform

Install:

* Python 3 (e.g. installed with Anaconda)
* Google Cloud SDK
* Docker with docker-compose
* Terraform

### 4.1 Create GCP project

### 4.2 Create a service account & roles for the project

* grant viewer role to the service account
* generate & download key .json file as json format
  
1; Install google cloud [SDK](https://cloud.google.com/sdk/docs/quickstart)

```shell
gcloud -v
```

2; Add path of downloaded key file to environment variable

 ```shell
   export GOOGLE_APPLICATION_CREDENTIALS="<path/to/your/service-account-authkeys>.json"
   
   # Refresh token/session, and verify authentication
   gcloud auth application-default login
```


### 4.3 Setup for Access

1. [IAM Roles](https://cloud.google.com/storage/docs/access-control/iam-roles) for Service account:
   
   * Go to the *IAM* section of [IAM & Admin](https://console.cloud.google.com/iam-admin/iam)
   * Click the *Edit principal* icon for your service account.
   * Add these roles in addition to *Viewer* : **Storage Admin** + **Storage Object Admin** + **BigQuery Admin**

3. Enable these APIs for your project:
   * [iam](https://console.cloud.google.com/apis/library/iam.googleapis.com)
   * [iamcredentials](https://console.cloud.google.com/apis/library/iamcredentials.googleapis.com)


### 4.4 Use terraform to provision GCP reseources

The needed terreform files are:

* `main.tf`
* `variables.tf`
* Optional: `resources.tf`, `output.tf`
* `.tfstate`

#### help

* `terraform`: configure basic Terraform settings to provision your infrastructure
* `required_version`: minimum Terraform version to apply to your configuration
* `backend`: stores Terraform's "state" snapshots, to map real-world resources to your configuration.
* `local`: stores state file locally as `terraform.tfstate`
* `required_providers`: specifies the providers required by the current module
* `provider`:
  * adds a set of resource types and/or data sources that Terraform can manage
  * The Terraform Registry is the main directory of publicly available providers from most major infrastructure platforms.
* `resource`:
  * blocks to define components of your infrastructure
  * Project modules/resources: google_storage_bucket, google_bigquery_dataset, google_bigquery_table
* `variable` & `locals`:
  * runtime arguments and constants

### 4.5 Execution steps

1. `terraform init`:
    * Initializes & configures the backend, installs plugins/providers, & checks out an existing configuration from a version control
  
2. `terraform plan`:
    * Matches/previews local changes against a remote state, and proposes an Execution Plan.

3. `terraform apply`:
    * Asks for approval to the proposed plan, and applies changes to cloud

4. `terraform destroy`
    * Removes your stack from the Cloud