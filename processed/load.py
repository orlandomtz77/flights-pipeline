from processed.transform import transform_data
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
import json
import os
from dotenv import load_dotenv

load_dotenv()
host = os.getenv("DB_HOST")
database = os.getenv("DB_NAME")
user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")


def _records(df, columns):
    subset = df[columns].astype(object)
    clean = subset.where(pd.notna(subset), None)
    return list(clean.itertuples(index=False, name=None))


def load_data():
    df_airports, df_airlines, df_fact_flights, df_raw = transform_data()
    conn = psycopg2.connect(
        host=host,
        database=database,
        user=user,
        password=password,
    )
    cur = conn.cursor()

    execute_values(
        cur,
        """
        INSERT INTO dim_airports (airport_code, airport_name, airport_city, country_code)
        VALUES %s
        ON CONFLICT (airport_code) DO NOTHING
        """,
        _records(
            df_airports, ["airport_code", "airport_name", "airport_city", "country_code"]
        ),
    )

    execute_values(
        cur,
        """
        INSERT INTO dim_airlines (airline_code, airline_name)
        VALUES %s
        ON CONFLICT (airline_code) DO NOTHING
        """,
        _records(df_airlines, ["airline_code", "airline_name"]),
    )

    cur.execute("SELECT airline_id, airline_code FROM dim_airlines")
    airline_map = {row[1]: row[0] for row in cur.fetchall()}

    fact_rows = _records(
        df_fact_flights,
        [
            "airline_code",
            "origin_airport_code",
            "destination_airport_code",
            "scheduled_departure",
            "actual_departure",
            "scheduled_arrival",
            "actual_arrival",
            "status",
        ],
    )
    fact_rows = [(airline_map.get(code), *rest) for code, *rest in fact_rows]
    execute_values(
        cur,
        """
        INSERT INTO fact_flights (airline_id, origin_airport_code, destination_airport_code,
        scheduled_departure, actual_departure, scheduled_arrival, actual_arrival, status)
        VALUES %s
        ON CONFLICT (airline_id, origin_airport_code, destination_airport_code, scheduled_departure) DO NOTHING
        """,
        fact_rows,
    )

    raw_rows = [
        (
            json.dumps(row["departure"]),
            json.dumps(row["arrival"]),
            row["number"],
            row["status"],
            row["codeshareStatus"],
            row["isCargo"],
            json.dumps(row["aircraft"]),
            json.dumps(row["airline"]),
            row["callSign"],
        )
        for _, row in df_raw.iterrows()
    ]
    execute_values(
        cur,
        """
        INSERT INTO flight_raw(departure, arrival, number, status, codesharestatus,
        iscargo, aircraft, airline, callsign)
        VALUES %s
        """,
        raw_rows,
    )

    conn.commit()
    conn.close()


if __name__ == "__main__":
    load_data()
