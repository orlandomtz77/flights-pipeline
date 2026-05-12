from transform import transform_data
import pandas as pd
import psycopg2
import json
import os
from dotenv import load_dotenv

load_dotenv()
host = os.getenv("DB_HOST")
database = os.getenv("DB_NAME")
user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")


def load_data():
    df_airports, df_airlines, df_fact_flights, df_raw = transform_data()
    conn = psycopg2.connect(
        host=host,
        database=database,
        user=user,
        password=password,
    )
    cur = conn.cursor()
    for _, row in df_airports.iterrows():
        cur.execute(
            """
            INSERT INTO dim_airports (airport_code, airport_name, airport_city, country_code)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (airport_code) DO NOTHING
        """,
            (
                row["airport_code"],
                row["airport_name"],
                row["airport_city"],
                row["country_code"],
            ),
        )
    for _, row in df_airlines.iterrows():
        cur.execute(
            """
            INSERT INTO dim_airlines (airline_code, airline_name)
            VALUES (%s, %s)
            ON CONFLICT (airline_code) DO NOTHING
        """,
            (row["airline_code"], row["airline_name"]),
        )

    cur.execute("SELECT airline_id, airline_code FROM dim_airlines")
    airline_map = {row[1]: row[0] for row in cur.fetchall()}
    for _, row in df_fact_flights.iterrows():
        cur.execute(
            """
            INSERT INTO fact_flights (airline_id,origin_airport_code,destination_airport_code,
            scheduled_departure,actual_departure,scheduled_arrival,actual_arrival,status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (airline_id,origin_airport_code,destination_airport_code,scheduled_departure) DO NOTHING
        """,
            (
                airline_map.get(row["airline_code"]),
                row["origin_airport_code"],
                row["destination_airport_code"],
                row["scheduled_departure"]
                if pd.notna(row["scheduled_departure"])
                else None,
                row["actual_departure"] if pd.notna(row["actual_departure"]) else None,
                row["scheduled_arrival"]
                if pd.notna(row["scheduled_arrival"])
                else None,
                row["actual_arrival"] if pd.notna(row["actual_arrival"]) else None,
                row["status"],
            ),
        )

    for _, row in df_raw.iterrows():
        cur.execute(
            """
    INSERT INTO flight_raw(departure,arrival,number,status,codesharestatus,
    iscargo,aircraft,airline,callsign)
    VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """,
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
            ),
        )

    conn.commit()
    conn.close()


load_data()
