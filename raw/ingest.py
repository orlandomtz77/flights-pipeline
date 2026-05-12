import requests
import json
from dotenv import load_dotenv
import os
from datetime import date, timedelta

load_dotenv()
api_key = os.getenv("APIKEY")


def download_data():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_dir = os.path.join(current_dir, "data")
    normalized_path = os.path.normpath(config_dir)
    start_date = date(2026, 4, 4)
    end_date = date(2026, 5, 7)

    current_day = start_date
    while current_day <= end_date:
        urlpm = f"https://aerodatabox.p.rapidapi.com/flights/airports/icao/MMMX/{current_day.strftime('%Y-%m-%d')}T12:00/{current_day.strftime('%Y-%m-%d')}T23:59"
        urlam = f"https://aerodatabox.p.rapidapi.com/flights/airports/icao/MMMX/{current_day.strftime('%Y-%m-%d')}T00:00/{current_day.strftime('%Y-%m-%d')}T11:59"
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

        response_am = requests.get(urlam, headers=headers, params=querystring)
        response_pm = requests.get(urlpm, headers=headers, params=querystring)
        if response_am.status_code == 200 and response_pm.status_code == 200:
            data_am = response_am.json()
            data_pm = response_pm.json()

            data = {
                "departures": data_am["departures"] + data_pm["departures"],
                "arrivals": data_am["arrivals"] + data_pm["arrivals"],
            }

            filename = f"{normalized_path}/{current_day.strftime('%Y-%m-%d')}.json"
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            print(f"✅ {current_day.strftime('%Y-%m-%d')} guardado")
        else:
            print(
                f"❌ {current_day.strftime('%Y-%m-%d')} — Status: {response_am.status_code} / {response_pm.status_code}"
            )
        current_day += timedelta(days=1)

        # with open(
        #     os.path.join(current_dir, "data", "flight_raw.json"), "r", encoding="utf-8"
        # ) as f:
        #     data = json.load(f)

        # filename = f"{normalized_path}/{current_day.strftime('%Y-%m-%d')}.json"
        # with open(filename, "w", encoding="utf-8") as f:
        #     json.dump(data, f, ensure_ascii=False, indent=4)
        # current_day += timedelta(days=1)


if __name__ == "__main__":
    download_data()
