import requests
import json
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("APIKEY")


def ingest_data():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_dir = os.path.join(current_dir, "..", "data/raw")
    normalized_path = os.path.normpath(config_dir)
    url = "https://aerodatabox.p.rapidapi.com/flights/airports/icao/MMMX/2026-04-23T12:00/2026-04-24T00:00"

    querystring = {
        "withLeg": "true",
        "direction": "Both",
        "withCancelled": "true",
        "withCodeshared": "true",
        "withCargo": "true",
        "withPrivate": "true",
        "withLocation": "false",
    }

    headers = {
        "x-rapidapi-key": api_key,
        "x-rapidapi-host": "aerodatabox.p.rapidapi.com",
        "Content-Type": "application/json",
    }

    response = requests.get(url, headers=headers, params=querystring)
    if response.status_code == 200:
        data = response.json()
        filename = f"{normalized_path}/flight_raw.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Status code: {response.status_code}")

    else:
        print(f"Incorrect Status, file not saved code:{response.status_code}")


ingest_data()
