# Homework 3 Guideline

By Pijar HM

- Make your own google project

<img width="1222" height="712" alt="image" src="https://github.com/user-attachments/assets/5bf73e42-eabe-424e-9373-c45850b05cef" />


Then, I use google cli to get credentials

- First you should login to google cli with your terminal, in my case i used powershell

```powershell
gcloud auth login
```

- After that, you will need to test where is your credential file, for me it is in `C:\Users\pijar2000\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd`

- In python ingesting script `load_yellow_taxi_data.py` , i made some modification for credential login

```python
# If commented initialize client with the following

client = storage.Client(project='zoomcamp-mod3-datawarehouse') # I change this

```

i changed it to

```python
def get_credentials():
    gcloud_path = r"C:\Users\pijar2000\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd"

    result = subprocess.run(
        [gcloud_path, 'auth', 'print-access-token'],
        capture_output=True,
        text=True,
        check=True
    )
    token = result.stdout.strip()
    from google.oauth2.credentials import Credentials
    return Credentials(token=token)

credentials = get_credentials()
client = storage.Client(credentials=credentials, project='project-475f5f46-e321-4ab4-93e')
```

- `project-475f5f46-e321-4ab4-93e` is my project id you should change it to your project id
- Don't forget to change your bucket name too, for me its `dezoomcamp_hw3_2026_pijar`

- After that you can run the script `load_yellow_taxi_data.py`

<img width="1494" height="963" alt="image" src="https://github.com/user-attachments/assets/6514bafd-119c-471c-a4ad-ab6a99ab33cd" />

Check your bucket in google cloud, then you will find something like that

- After that, make your own external table, if there's no schema, make one
- Careful change the rest with your own bucket name and you own project name

```sql
CREATE SCHEMA IF NOT EXISTS
`zoomcamp-pijar.nytaxi`
OPTIONS (location = 'US');


CREATE OR REPLACE EXTERNAL TABLE
`zoomcamp-pijar.nytaxi.external_yellow_tripdata_2024`
OPTIONS (
  format = 'PARQUET',
  uris = ['gs://dezoomcamp_hw3_2026_pijar/yellow_tripdata_2024-*.parquet']
);
```

- After that make your materialiazed table
  
```sql
CREATE OR REPLACE TABLE
`zoomcamp-pijar.nytaxi.yellow_tripdata_2024`
AS
SELECT *
FROM `zoomcamp-pijar.nytaxi.external_yellow_tripdata_2024`;
```

You should see something like this

<img width="439" height="545" alt="image" src="https://github.com/user-attachments/assets/a2f86502-31fa-4704-b05d-190850d4c080" />

## Question 1

What is count of records for the 2024 Yellow Taxi Data?

```sql
SELECT COUNT(*) AS total_records
FROM `zoomcamp-pijar.nytaxi.yellow_tripdata_2024`;
```

## Queation 2

Write a query to count the distinct number of PULocationIDs for the entire dataset on both the tables.

What is the estimated amount of data that will be read when this query is executed on the External Table and the Table?

- For external table

```sql
SELECT COUNT(DISTINCT PULocationID) AS distinct_pu
FROM `zoomcamp-pijar.nytaxi.external_yellow_tripdata_2024`;
```

- For materialized table

```sql
SELECT COUNT(DISTINCT PULocationID) AS distinct_pu
FROM `zoomcamp-pijar.nytaxi.yellow_tripdata_2024`;
```

<img width="679" height="160" alt="image" src="https://github.com/user-attachments/assets/0ce7edd0-5717-4edb-bebb-c3734f094aff" />

Just block the query and it will show the number

## Question 3

It's theory undestanding of columnar storage, see this documentation

- https://docs.cloud.google.com/bigquery/docs/storage_overview
- https://docs.cloud.google.com/bigquery/docs/storage_overview#storage_layout

## Question 4

How many records have a fare_amount of 0?

```sql
SELECT COUNT(*) AS zero_fare_trips
FROM `zoomcamp-pijar.nytaxi.yellow_tripdata_2024`
WHERE fare_amount = 0;
```

## Question 5

- Make your own partition table first

```sql
CREATE OR REPLACE TABLE
`zoomcamp-pijar.nytaxi.yellow_tripdata_2024_partition`
PARTITION BY DATE(tpep_dropoff_datetime)
AS
SELECT *
FROM `zoomcamp-pijar.nytaxi.yellow_tripdata_2024`;
```

Its also theory understanding, you can read it here

- http://developers.google.com/machine-learning/clustering/overview
- https://docs.cloud.google.com/bigquery/docs/partitioned-tables

## Question 6

Use the materialized table you created earlier in your from clause and note the estimated bytes. Now change the table in the from clause to the partitioned table you created for question 5 and note the estimated bytes processed. What are these values?

- Test your normal table
```sql
SELECT *
FROM `zoomcamp-pijar.nytaxi.yellow_tripdata_2024`
WHERE tpep_dropoff_datetime BETWEEN '2024-03-01' AND '2024-03-15'
ORDER BY VendorID;
```


- Test your partition table
```sql
SELECT *
FROM `zoomcamp-pijar.nytaxi.yellow_tripdata_2024_partition`
WHERE tpep_dropoff_datetime BETWEEN '2024-03-01' AND '2024-03-15'
ORDER BY VendorID;
```

## Question 7

Where is the data stored in the External Table you created?

It's theory, you can read this
- https://docs.cloud.google.com/bigquery/docs/external-tables

## Question 8

It is best practice in Big Query to always cluster your data?
There is no exact answer, what do you think?

## Question 9

Just `SELECT count(*)` from your own table and see how long it will be, then make your own conclusion.
