"""@bruin

name: ingestion.trips

type: python

image: python:3.11

connection: duckdb-default

materialization:
  type: table
  strategy: append

columns:
  - name: taxi_type
    type: string
    description: Taxi type (yellow or green)
  - name: pickup_datetime
    type: timestamp
    description: Pickup date and time (normalized from tpep/lpep)
  - name: dropoff_datetime
    type: timestamp
    description: Dropoff date and time (normalized from tpep/lpep)
  - name: passenger_count
    type: double
    description: Number of passengers
  - name: trip_distance
    type: double
    description: Trip distance in miles
  - name: pulocationid
    type: integer
    description: Pickup location (TLC zone) ID
  - name: dolocationid
    type: integer
    description: Dropoff location (TLC zone) ID
  - name: payment_type
    type: integer
    description: Payment type code (joins to payment_lookup)
  - name: total_amount
    type: double
    description: Total amount charged
  - name: extracted_at
    type: timestamp
    description: Timestamp when the row was extracted

@bruin"""

import os
import json
import io
from datetime import datetime

import pandas as pd
import requests
from dateutil.relativedelta import relativedelta


def materialize():
    """
    Fetch NYC taxi parquet data from TLC endpoint for the run's date range and taxi_types.
    Keeps raw data; normalizes pickup/dropoff datetime column names for yellow vs green.
    """
    base_url = "https://d37ci6vzurychx.cloudfront.net/trip-data/"
    start_date_str = os.environ.get("BRUIN_START_DATE", "")
    end_date_str = os.environ.get("BRUIN_END_DATE", "")
    vars_json = os.environ.get("BRUIN_VARS", "{}")
    try:
        variables = json.loads(vars_json)
        taxi_types = variables.get("taxi_types", ["yellow", "green"])
    except json.JSONDecodeError:
        taxi_types = ["yellow", "green"]

    if not start_date_str or not end_date_str:
        return pd.DataFrame()

    start = datetime.strptime(start_date_str, "%Y-%m-%d").date()
    end = datetime.strptime(end_date_str, "%Y-%m-%d").date()
    extracted_at = datetime.utcnow()

    frames = []
    current = start
    while current < end:
        year_month = current.strftime("%Y-%m")
        for taxi_type in taxi_types:
            filename = f"{taxi_type}_tripdata_{year_month}.parquet"
            url = base_url + filename
            try:
                resp = requests.get(url, timeout=120)
                resp.raise_for_status()
                df = pd.read_parquet(io.BytesIO(resp.content))
            except Exception:
                continue
            df = df.copy()
            df["taxi_type"] = taxi_type
            if "tpep_pickup_datetime" in df.columns:
                df["pickup_datetime"] = pd.to_datetime(df["tpep_pickup_datetime"])
                df["dropoff_datetime"] = pd.to_datetime(df["tpep_dropoff_datetime"])
            elif "lpep_pickup_datetime" in df.columns:
                df["pickup_datetime"] = pd.to_datetime(df["lpep_pickup_datetime"])
                df["dropoff_datetime"] = pd.to_datetime(df["lpep_dropoff_datetime"])
            else:
                continue
            if "VendorID" in df.columns:
                df = df.rename(columns=str.lower)
            for col in ["passenger_count", "trip_distance", "pulocationid", "dolocationid", "payment_type", "total_amount"]:
                if col not in df.columns and col.upper() in [c.upper() for c in df.columns]:
                    rename = {c: col for c in df.columns if c.upper() == col.upper()}
                    df = df.rename(columns=rename)
            out_cols = ["taxi_type", "pickup_datetime", "dropoff_datetime", "passenger_count", "trip_distance", "pulocationid", "dolocationid", "payment_type", "total_amount"]
            available = [c for c in out_cols if c in df.columns]
            df = df[available].copy()
            df["extracted_at"] = extracted_at
            frames.append(df)
        current = current + relativedelta(months=1)

    if not frames:
        return pd.DataFrame(columns=["taxi_type", "pickup_datetime", "dropoff_datetime", "passenger_count", "trip_distance", "pulocationid", "dolocationid", "payment_type", "total_amount", "extracted_at"])
    return pd.concat(frames, ignore_index=True)
