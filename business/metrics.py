import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()
host = os.getenv("DB_HOST")
database = os.getenv("DB_NAME")
user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
conn = psycopg2.connect(
    host=host,
    database=database,
    user=user,
    password=password,
)
cur = conn.cursor()
cur.execute(
    """
    SELECT
    da.airline_name,
    COUNT(*) AS total_vuelos,
    COUNT(CASE WHEN actual_departure <= scheduled_departure THEN 1 END) AS puntuales,
    ROUND(COUNT(CASE WHEN actual_departure <= scheduled_departure THEN 1 END) * 100.0 / COUNT(*), 1) AS pct_puntualidad
FROM fact_flights ff
JOIN dim_airlines da ON ff.airline_id = da.airline_id
WHERE actual_departure IS NOT NULL
AND scheduled_departure IS NOT NULL
GROUP BY da.airline_name
ORDER BY pct_puntualidad DESC
LIMIT 5
"""
)
results = cur.fetchall()
print("\n🏆 Top 5 Aerolíneas por Puntualidad")
print("-" * 45)
for row in results:
    print(f"{row[0]:<20} {row[2]:>3}/{row[1]:>3} vuelos  {row[3]}%")

cur.execute(
    """
    SELECT (scheduled_departure::date) as day,
    COUNT(*) AS total_flights
    FROM fact_flights
    WHERE scheduled_departure IS NOT NULL
    GROUP BY day
    ORDER BY day

    """
)
results = cur.fetchall()
print("\n📅 Vuelos por dia")
print("-" * 45)
for row in results:
    print(f"{str(row[0]):<20} {row[1]:>3}")

cur.execute(
    """
    SELECT da.airline_name,
    ROUND(AVG(EXTRACT(EPOCH FROM (actual_departure - scheduled_departure))/60),2) as delay_time
    FROM fact_flights as ff
    JOIN dim_airlines da ON ff.airline_id = da.airline_id
    WHERE actual_departure is NOT NULL
    AND scheduled_departure is NOT NULL 
    GROUP by da.airline_name    
    ORDER BY delay_time DESC
    

    """
)
results = cur.fetchall()
print("\n Aerolineas con retraso")
print("-" * 45)
for row in results:
    print(f"{row[0]:<20} {row[1]} min")

conn.close()
