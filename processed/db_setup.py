import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()
host = os.getenv("DB_HOST")
database = os.getenv("DB_NAME")
user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")

conn = psycopg2.connect(
    host=host, database=database, user=user, password=password
)
cur = conn.cursor()
cur.execute(
    """
CREATE TABLE IF NOT EXISTS dim_airports(
            airport_code VARCHAR PRIMARY KEY,
            airport_name VARCHAR,
            airport_city VARCHAR,
            country_code VARCHAR
            )
    
"""
)
cur.execute(
    """
CREATE TABLE IF NOT EXISTS dim_airlines(
airline_id SERIAL PRIMARY KEY,
airline_code VARCHAR UNIQUE,
airline_name VARCHAR
)
""",
)
cur.execute(
    """
CREATE TABLE IF NOT EXISTS flight_raw(
flight_id SERIAL PRIMARY KEY,
departure JSONB,
arrival JSONB,
number VARCHAR,
status VARCHAR,
codeShareStatus VARCHAR,
isCargo BOOLEAN,
aircraft JSONB,
airline JSONB,
callSign VARCHAR
)
           
"""
)
cur.execute(
    """
CREATE TABLE IF NOT EXISTS fact_flights(
flight_id SERIAL PRIMARY KEY,
airline_id INT REFERENCES dim_airlines(airline_id),
origin_airport_code VARCHAR REFERENCES dim_airports(airport_code),
destination_airport_code VARCHAR REFERENCES dim_airports(airport_code),
scheduled_departure TIMESTAMP,
actual_departure TIMESTAMP,
scheduled_arrival TIMESTAMP,
actual_arrival TIMESTAMP,
status VARCHAR,
UNIQUE(airline_id,origin_airport_code,destination_airport_code,scheduled_departure)
)
"""
)
conn.commit()
conn.close()
