# Homework 3 Guideline

By Pijar HM

- Make your google project name like this

<img width="1201" height="372" alt="image" src="https://github.com/user-attachments/assets/dc0266dd-99d4-434a-9d48-ffec74f6c55e" />

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
- After that you can run the script `load_yellow_taxi_data.py`

<img width="1494" height="963" alt="image" src="https://github.com/user-attachments/assets/6514bafd-119c-471c-a4ad-ab6a99ab33cd" />

Check your bucket in google cloud, then you will find something like this
