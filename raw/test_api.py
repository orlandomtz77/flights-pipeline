import requests
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("APIKEY")
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

print(response.json())
