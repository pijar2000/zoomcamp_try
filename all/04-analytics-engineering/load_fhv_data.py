import os
import sys
import pandas as pd
import requests # <-- WAJIB DITAMBAHIN INI
from google.cloud import storage

# --- KONFIGURASI ---
BUCKET_NAME = "dezoomcamp_2026_pijar_3"
CREDENTIALS_FILE = "zoomcamp-pijar-3-key.json"

# Data tahun 2019
MONTHS = [f"{i:02d}" for i in range(1, 13)]

try:
    client = storage.Client.from_service_account_json(CREDENTIALS_FILE)
except Exception as e:
    print(f"Error loading credentials: {e}")
    sys.exit(1)

def upload_to_gcs(bucket_name, source_file_name, destination_blob_name):
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_file_name)
    print(f"File {source_file_name} uploaded to {destination_blob_name}.")

# PROSES ETL
for month in MONTHS:
    dataset_file = f"fhv_tripdata_2019-{month}"
    dataset_url = f"https://github.com/DataTalksClub/nyc-tlc-data/releases/download/fhv/{dataset_file}.csv.gz"
    
    csv_name = f"{dataset_file}.csv.gz"
    parquet_name = f"{dataset_file}.parquet"

    # A. Download file CSV.GZ
    print(f"\n--- Processing {dataset_file} ---")
    print(f"Downloading from {dataset_url}...")
    
    r = requests.get(dataset_url)
    if r.status_code == 200:
        with open(csv_name, 'wb') as f:
            f.write(r.content)
    else:
        print(f"Failed to download {dataset_file}. Status code: {r.status_code}")
        continue

    # B. Read and Clean with Pandas
    df = pd.read_csv(csv_name, compression='gzip', dtype={
        'PUlocationID': 'float64',
        'DOlocationID': 'float64',
        'SR_Flag': 'object',
        'dispatching_base_num': 'object'
    })
    
    # C. Convert to Parquet
    print(f"Converting {csv_name} to Parquet...")
    df.to_parquet(parquet_name, engine='pyarrow')

    # D. Upload Parquet to GCS
    upload_to_gcs(BUCKET_NAME, parquet_name, f"fhv/{parquet_name}")

    # E. Cleanup
    print(f"Cleaning up local files...")
    if os.path.exists(csv_name):
        os.remove(csv_name)
    if os.path.exists(parquet_name):
        os.remove(parquet_name)
