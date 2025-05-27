import requests
import json
import time
import os
import pandas as pd
import dlt
from dlt.sources.helpers.rest_client import RESTClient
from dlt.sources.helpers.rest_client.auth import BearerTokenAuth
from dlt.sources.helpers.rest_client.paginators import OffsetPaginator
from dlt.sources.filesystem import filesystem
from dotenv import load_dotenv

# === CONFIGURATION ===
load_dotenv()
CLIENT_ID = os.getenv(f'CLIENT_ID')
CLIENT_SECRET = os.getenv(f'CLIENT_SECRET')

SECRETS_FILE = os.getenv(f'STRAVA_TOKENS_JSON')

# Create directory if it doesn't exist
os.makedirs('secrets', exist_ok=True)

# Load the JSON string into a Python object
data = json.loads(SECRETS_FILE)

# Write the JSON data to the file
with open('secrets/strava_tokens.json', 'w') as file:
    json.dump(data, file, indent=4)

TOKENS_FILE = 'secrets/strava_tokens.json'

# === LOAD OR REFRESH TOKENS ===
def load_tokens():
    if os.path.exists(TOKENS_FILE):
        with open(TOKENS_FILE, 'r') as f:
            return json.load(f)
    else:
        raise FileNotFoundError("Token file not found. Authorize first and save your tokens.")

def save_tokens(tokens):
    with open(TOKENS_FILE, 'w') as f:
        json.dump(tokens, f)

def refresh_tokens(tokens):
    if time.time() > tokens['expires_at']:
        print("Access token expired. Refreshing...")
        response = requests.post("https://www.strava.com/oauth/token", data={
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'grant_type': 'refresh_token',
            'refresh_token': tokens['refresh_token']
        })
        new_tokens = response.json()
        tokens.update({
            'access_token': new_tokens['access_token'],
            'refresh_token': new_tokens['refresh_token'],
            'expires_at': new_tokens['expires_at']
        })
        save_tokens(tokens)
    return tokens

# === GET ACTIVITIES ===
def get_activities(access_token, per_page=30):
    headers = {'Authorization': f"Bearer {access_token}"}
    page = 1

    while True:
        response = requests.get(
            'https://www.strava.com/api/v3/athlete/activities',
            headers=headers,
            params={'per_page': per_page, 'page': page}
        )
        data = response.json()

        if not data:
            break

        for activity in data:
            yield activity
        
        page += 1

# === MAIN FLOW ===
tokens = load_tokens()
tokens = refresh_tokens(tokens)
ACCESS_TOKEN=tokens['access_token']

os.environ["ACCESS_TOKEN"] = ACCESS_TOKEN
@dlt.source
def strava_source(
    access_token=dlt.secrets.value
):
    client = RESTClient(
        base_url='https://www.strava.com/api/v3/',
        auth=BearerTokenAuth(token=access_token),
        paginator=OffsetPaginator(
            limit=100,
            limit_param='per_page',
            offset=1,
            offset_param='page',
            stop_after_empty_page=True,
            total_path=None
        )
    )

    @dlt.resource(
        write_disposition="replace",
        #primary_key="id",
    )
    def activities():
        for page in client.paginate("athlete/activities"):
            yield page

    return activities


    @dlt.resource(
        write_disposition="replace",
        #primary_key="id",
    )
    def athlete():
        for page in client.paginate("athlete"):
            yield page

    return athlete


pipeline_s3 = dlt.pipeline(
    pipeline_name="strava_to_s3",       # you can keep the same name if you like
    destination="filesystem",            # ← switch to filesystem
    dataset_name="strava_activities_s3"  # name for the S3 “folder” in your bucket
)
load_info_s3 = pipeline_s3.run(strava_source(), loader_file_format = "csv")


pipeline_redshift = dlt.pipeline(
    pipeline_name="strava_s3_to_redshift",
    destination="redshift",
    dataset_name="strava_rest_api_dataset"
)

source_from_s3 = filesystem(
    bucket_url="s3://billy-heidel-test-bucket/strava_activities_s3",
    file_glob="**/*.csv"
)
load_info_redshift = pipeline_redshift.run(source_from_s3)
