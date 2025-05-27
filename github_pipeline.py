import requests
import json
import time
import os
import pandas as pd
import dlt
from dlt.sources.helpers.rest_client import RESTClient
from dlt.sources.helpers.rest_client.auth import BearerTokenAuth
from dlt.sources.helpers.rest_client.paginators import OffsetPaginator
from dotenv import load_dotenv

# === CONFIGURATION ===
load_dotenv()
CLIENT_ID = os.getenv(f'CLIENT_ID')
CLIENT_SECRET = os.getenv(f'CLIENT_SECRET')

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

pipeline = dlt.pipeline(
    pipeline_name="strava_rest_api",
    destination="redshift",
)
load_info = pipeline.run(strava_source())
