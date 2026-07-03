import argparse
import requests
import json
from dotenv import load_dotenv
import os
from datetime import date, timedelta

load_dotenv()
api_key = os.getenv("APIKEY")

QUERYSTRING = {
    "withLeg": "true",
    "direction": "Both",
    "withCancelled": "true",
    "withCodeshared": "true",
    "withCargo": "true",
    "withPrivate": "true",
    "withLocation": "false",
}

HEADERS = {
    "x-rapidapi-key": api_key,
    "x-rapidapi-host": "aerodatabox.p.rapidapi.com",
    "Content-Type": "application/json",
}


def fetch_day(target_day, data_dir):
    day_str = target_day.strftime("%Y-%m-%d")
    urlam = f"https://aerodatabox.p.rapidapi.com/flights/airports/icao/MMMX/{day_str}T00:00/{day_str}T11:59"
    urlpm = f"https://aerodatabox.p.rapidapi.com/flights/airports/icao/MMMX/{day_str}T12:00/{day_str}T23:59"

    response_am = requests.get(urlam, headers=HEADERS, params=QUERYSTRING)
    response_pm = requests.get(urlpm, headers=HEADERS, params=QUERYSTRING)

    if response_am.status_code == 200 and response_pm.status_code == 200:
        data_am = response_am.json()
        data_pm = response_pm.json()

        data = {
            "departures": data_am["departures"] + data_pm["departures"],
            "arrivals": data_am["arrivals"] + data_pm["arrivals"],
        }

        filename = os.path.join(data_dir, f"{day_str}.json")
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"✅ {day_str} guardado")
        return True

    print(f"❌ {day_str} — Status: {response_am.status_code} / {response_pm.status_code}")
    return False


def download_data(target_date=None, end_date=None):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.normpath(os.path.join(current_dir, "data"))

    if target_date is None:
        target_date = date.today() - timedelta(days=1)
    if end_date is None:
        end_date = target_date

    current_day = target_date
    while current_day <= end_date:
        fetch_day(current_day, data_dir)
        current_day += timedelta(days=1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Descarga vuelos de AICM/MMMX. Sin argumentos, trae el día de ayer."
    )
    parser.add_argument("--date", help="Fecha única a descargar, YYYY-MM-DD")
    parser.add_argument("--start", help="Inicio de rango para backfill, YYYY-MM-DD")
    parser.add_argument("--end", help="Fin de rango para backfill, YYYY-MM-DD")
    args = parser.parse_args()

    if args.start:
        start = date.fromisoformat(args.start)
        end = date.fromisoformat(args.end) if args.end else start
        download_data(start, end)
    elif args.date:
        download_data(date.fromisoformat(args.date))
    else:
        download_data()
