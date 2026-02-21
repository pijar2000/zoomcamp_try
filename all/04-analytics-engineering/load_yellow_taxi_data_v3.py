import os
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from google.cloud import storage
from google.api_core.exceptions import NotFound, Forbidden
import time

BUCKET_NAME = "dezoomcamp_2026_pijar_3" #ganti dengan nama bucket pribadi
CREDENTIALS_FILE = "zoomcamp-pijar-3-key.json"  #ganti dengan kredensial GCP service account pribasi

try:
    client = storage.Client.from_service_account_json(CREDENTIALS_FILE)
except Exception as e:
    print(f"Error loading credentials: {e}")
    sys.exit(1)

BASE_URL = "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_"

# Membuat list tahun dan bulan (2019-2020)
YEARS = [2019, 2020]
MONTHS = [f"{i:02d}" for i in range(1, 13)]
# Membuat kombinasi tahun-bulan: ['2019-01', '2019-02', ..., '2020-12']
DATA_FILES = [f"{year}-{month}" for year in YEARS for month in MONTHS]

DOWNLOAD_DIR = "."
CHUNK_SIZE = 8 * 1024 * 1024
os.makedirs(DOWNLOAD_DIR, exist_ok=True)
bucket = client.bucket(BUCKET_NAME)

def download_file(year_month):
    # year_month formatnya "YYYY-MM"
    url = f"{BASE_URL}{year_month}.parquet"
    file_path = os.path.join(DOWNLOAD_DIR, f"yellow_tripdata_{year_month}.parquet")

    try:
        print(f"Downloading {url}...")
        urllib.request.urlretrieve(url, file_path)
        print(f"Downloaded: {file_path}")
        return file_path
    except Exception as e:
        print(f"Failed to download {url}: {e}")
        return None

def create_bucket(bucket_name):
    try:
        client.get_bucket(bucket_name)
        print(f"Bucket '{bucket_name}' appear...")
    except NotFound:
        client.create_bucket(bucket_name)
        print(f"success create '{bucket_name}'")
    except Forbidden:
        print(f"FAILED! Bucketname '{bucket_name}' used, change bucket name")
        sys.exit(1)

def verify_gcs_upload(blob_name):
    return storage.Blob(bucket=bucket, name=blob_name).exists(client)

def upload_to_gcs(file_path, max_retries=3):
    if not file_path: return
    
    blob_name = os.path.basename(file_path)
    blob = bucket.blob(blob_name)
    blob.chunk_size = CHUNK_SIZE

    for attempt in range(max_retries):
        try:
            print(f"Uploading {file_path} to {BUCKET_NAME} (Attempt {attempt + 1})...")
            blob.upload_from_filename(file_path)
            
            if verify_gcs_upload(blob_name):
                print(f"Verifikasi sukses: gs://{BUCKET_NAME}/{blob_name}")
                # Hapus file lokal, hemat disk
                os.remove(file_path) 
                return
            else:
                print(f"Verifikasi gagal {blob_name}")
        except Exception as e:
            print(f"Gagal upload {file_path}: {e}")
        
        time.sleep(5)

if __name__ == "__main__":
    create_bucket(BUCKET_NAME)

    print(f"download {YEARS}...")
    with ThreadPoolExecutor(max_workers=4) as executor:
        file_paths = list(executor.map(download_file, DATA_FILES))

    print("upload GCS...")
    with ThreadPoolExecutor(max_workers=4) as executor:
        executor.map(upload_to_gcs, filter(None, file_paths))

    print("success 2019-2020.")