# Homework 1

By Pijar HM

This is my method to solve homework, not the answer is provided here, my answer provided only in zoomcamp homework submit form

### Question 1

- Run this

```bash
docker run -it --rm --entrypoint=bash python:3.13
```

### Question 2

- setting up the docker like this

```yaml
db:
  container_name: postgres
  image: postgres:17-alpine
  environment:
    POSTGRES_USER: "postgres"
    POSTGRES_PASSWORD: "postgres"
    POSTGRES_DB: "ny_taxi"
  ports:
    - "5433:5432"
  volumes:
    - vol-pgdata:/var/lib/postgresql/data
```

### Question 3

For the trips in November 2025 (lpep_pickup_datetime between '2025-11-01' and '2025-12-01', exclusive of the upper bound), how many trips had a `trip_distance` of less than or equal to 1 mile?

- You can analyze it with SQL inside database or simply pandas in python notebook

If you want to analyze it in database, the easiest way is to load the paquet file type into df in python notebook and convert into csv, then load the data to database, eg:

```python
import pandas as pd

df_parquet = pd.read_parquet("green_tripdata_2025-11.parquet")

df_parquet.to_csv("green_tripdata_2025-11.csv", index=False)
```

```python
import pandas as pd

df = pd.read_parquet("green_tripdata_2025-11.parquet")
print(df.dtypes)
```

- You can determine what you need to solve
- If the corresponding column in datetime already you're good to go

- This is one of method to determine which data coverage you should take, in this case filter by date and by distance, one by one

```python
# date filter
filter_date = (df["lpep_pickup_datetime"] >= "2025-11-01") & (df["lpep_pickup_datetime"] < "2025-12-01")

# distance filter
filter_distance = df["trip_distance"] <= 1

df_filter = df[mask_date & mask_distance]
```

- you can count the rest by various method, for example `count` function

### Question 4

Use the pick up time for your calculations.

- Check column type
- Determine your column
- Limit the coverage of your data by 100 miles and take the `date` information
- Group by day

```python
df_1 = df[df["trip_distance"] < 100].copy()
df_1["pickup_day"] = df_valid["lpep_pickup_datetime"].dt.date

group_day = df_1.groupby("pickup_day")["trip_distance"].max().reset_index()
```

- you can choose various method to find the answer, for example you can function `nlargest`

```python
longest_day = group_day.nlargest(1, "trip_distance")
```

### Question 5

- You can analyze it with SQL inside database or simply pandas in python notebook
- For this question, the fastest analysis is using pandas
- You need to load the data from question 3, check the question_3 note

Which was the pickup zone with the largest `total_amount` (sum of all trips) on November 18th, 2025?

- First you should aware there's no zone column in green taxi trip data
- It separet in csv zone file
- Load the file into two dataset variable (for example df_trip and df_zone)
- Check the column type of the data
- You should choose what exactly the `primary key` for join the data, for example

```python3
df_trip_zone = df_trip.merge(
    df_zone,
    left_on="PULocationID",
    right_on="LocationID",
    how="left"
)
```

- After merge the data into one dataset you good to go to analyze the rest
- Use pick up time and zone column in the data, group it

```python
df_day = df_trip_zone[
    df_trip_zone["lpep_pickup_datetime"].dt.date == pd.to_datetime("2025-11-18").date()
]

zone_group = df_day.groupby("Zone")["total_amount"].sum().reset_index()
```

- Finally determine the largest `total_amount`

```python3
zone_largest = zone_amounts.nlargest(1, "total_amount")
```

### Question 6

- you can filter the dataset with this method

```python3
df_filtered = df[ (df["pickup_zone"] == "East Harlem North") & (df["pickup_datetime"].str.startswith("2025-11")) ]

# Group by dropoff zone,
result = df_filtered.groupby("dropoff_zone")["tip_amount"].max().reset_index()

largest_tip_zone = result.loc[result["tip_amount"].idxmax()]

```

### Question 7

You only should read the documentation of terraformer, the answer is

terraform init, terraform apply -auto-approve, terraform destroy
