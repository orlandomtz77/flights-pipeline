import pandas as pd
import json
import os
from pathlib import Path


def transform_data():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    raw_path = os.path.join(base_dir, "..", "raw", "data")
    folder = Path(raw_path)
    all_departures = []
    all_arrivals = []
    for filepath in folder.iterdir():
        if filepath.name == "flight_raw.json":
            continue
        with open(filepath, "r", encoding="utf-8") as file:
            data = json.load(file)
        all_departures.extend(data["departures"])
        all_arrivals.extend(data["arrivals"])

    df_departure = pd.DataFrame(all_departures)
    df_arrival = pd.DataFrame(all_arrivals)

    airports_dep = df_departure["arrival"].apply(lambda x: x["airport"]).tolist()
    airports_arr = df_arrival["departure"].apply(lambda x: x["airport"]).tolist()

    df_dep = pd.DataFrame(airports_dep)
    df_arr = pd.DataFrame(airports_arr)

    df_airports = pd.concat([df_dep, df_arr]).drop_duplicates(subset="iata")
    df_airports.rename(
        columns={
            "iata": "airport_code",
            "name": "airport_city",
            "countryCode": "country_code",
        },
        inplace=True,
    )
    df_airports["airport_name"] = None
    df_airports.drop(columns=["icao", "timeZone"], inplace=True)
    mex = pd.DataFrame(
        [
            {
                "airport_code": "MEX",
                "airport_name": None,
                "airport_city": "Ciudad de México",
                "country_code": "mx",
            }
        ]
    )
    df_airports = pd.concat([df_airports, mex]).drop_duplicates(subset="airport_code")

    airlines_dep = (
        df_departure["airline"]
        .apply(lambda x: {"airline_code": x["iata"], "airline_name": x["name"]})
        .tolist()
    )
    airlines_arr = (
        df_arrival["airline"]
        .apply(lambda x: {"airline_code": x["iata"], "airline_name": x["name"]})
        .tolist()
    )

    df_air_dep = pd.DataFrame(airlines_dep)
    df_air_arr = pd.DataFrame(airlines_arr)
    df_airlines = pd.concat([df_air_dep, df_air_arr]).drop_duplicates(
        subset="airline_code"
    )

    fact_flights_dep = df_departure.apply(
        lambda x: {
            "origin_airport_code": "MEX",
            "airline_code": x["airline"]["iata"],
            "destination_airport_code": x["arrival"]["airport"].get("iata"),
            "scheduled_departure": x["departure"].get("scheduledTime", {}).get("utc"),
            "actual_departure": x["departure"].get("revisedTime", {}).get("utc"),
            "scheduled_arrival": x["arrival"].get("scheduledTime", {}).get("utc"),
            "actual_arrival": x["arrival"].get("revisedTime", {}).get("utc"),
            "status": x["status"],
        },
        axis=1,
    ).tolist()

    fact_flights_arr = df_arrival.apply(
        lambda x: {
            "origin_airport_code": x["departure"]["airport"].get("iata"),
            "airline_code": x["airline"]["iata"],
            "destination_airport_code": "MEX",
            "scheduled_departure": x["departure"].get("scheduledTime", {}).get("utc"),
            "actual_departure": x["departure"].get("revisedTime", {}).get("utc"),
            "scheduled_arrival": x["arrival"].get("scheduledTime", {}).get("utc"),
            "actual_arrival": x["arrival"].get("revisedTime", {}).get("utc"),
            "status": x["status"],
        },
        axis=1,
    ).tolist()

    df_fact_dep = pd.DataFrame(fact_flights_dep)
    df_fact_arr = pd.DataFrame(fact_flights_arr)
    df_fact_flights = pd.concat([df_fact_dep, df_fact_arr])
    df_raw = pd.concat([df_departure, df_arrival])
    return df_airports, df_airlines, df_fact_flights, df_raw
    # print(f"df_airports: {len(df_airports)} filas")
    # print(f"df_airlines: {len(df_airlines)} filas")
    # print(f"df_flights: {len(df_fact_flights)} filas")
    # print(f"df_raw: {len(df_raw)} filas")
