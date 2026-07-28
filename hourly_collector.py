"""
Hourly Collector

Fetches ONE current reading (pollution + weather), converts it into
a feature row, and APPENDS it to a growing CSV file.

This is the script GitHub Actions will run every hour.
Each run adds exactly ONE new row to hourly_dataset.csv.
"""

import requests
import csv
import os
from datetime import datetime

# ---- CONFIG ----
OW_API_KEY = "3f453341b725d1721e0dc64e136883cb"
CITY_LAT = 28.0089
CITY_LON = 69.3159
CITY_NAME = "Ghotki"

OUTPUT_CSV = "hourly_dataset.csv"


def fetch_air_pollution(lat, lon, api_key):
    """Same as before - gets current pollutant levels."""
    url = "http://api.openweathermap.org/data/2.5/air_pollution"
    params = {"lat": lat, "lon": lon, "appid": api_key}
    response = requests.get(url, params=params, timeout=15)
    response.raise_for_status()
    data = response.json()
    latest = data["list"][0]
    components = latest["components"]
    return {
        "aqi_index": latest["main"]["aqi"],
        "pm2_5": components["pm2_5"],
        "pm10": components["pm10"],
        "no2": components["no2"],
        "o3": components["o3"],
        "co": components["co"],
        "so2": components["so2"],
        "nh3": components.get("nh3", 0),
    }


def fetch_weather(lat, lon, api_key):
    """Same as before - gets current weather."""
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"lat": lat, "lon": lon, "appid": api_key, "units": "metric"}
    response = requests.get(url, params=params, timeout=15)
    response.raise_for_status()
    data = response.json()
    return {
        "temperature": data["main"]["temp"],
        "humidity": data["main"]["humidity"],
        "pressure": data["main"]["pressure"],
        "wind_speed": data["wind"]["speed"],
        "wind_deg": data["wind"].get("deg", 0),
        "clouds": data["clouds"]["all"],
    }


def build_feature_row(pollution: dict, weather: dict) -> dict:
    """
    Same idea as our feature_engineering.py, but takes the two
    dictionaries directly instead of loading from a saved file -
    since we're doing everything in one run here.
    """
    now = datetime.utcnow()

    return {
        "timestamp": now.isoformat(),
        "city": CITY_NAME,
        "hour": now.hour,
        "day": now.day,
        "month": now.month,
        "day_of_week": now.weekday(),
        "is_weekend": 1 if now.weekday() >= 5 else 0,
        "temperature": weather["temperature"],
        "humidity": weather["humidity"],
        "pressure": weather["pressure"],
        "wind_speed": weather["wind_speed"],
        "wind_deg": weather["wind_deg"],
        "clouds": weather["clouds"],
        "pm10": pollution["pm10"],
        "no2": pollution["no2"],
        "o3": pollution["o3"],
        "co": pollution["co"],
        "so2": pollution["so2"],
        "nh3": pollution["nh3"],
        "target_pm2_5": pollution["pm2_5"],
    }


def append_row_to_csv(row: dict, filepath: str):
    """
    Appends ONE row to the CSV.
    Writes the header ONLY if the file doesn't already exist.
    """
    file_already_exists = os.path.exists(filepath)

    with open(filepath, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(row.keys()))

        if not file_already_exists:
            writer.writeheader()  # only write header on the very first run

        writer.writerow(row)


def main():
    print("Fetching current pollution + weather...")
    pollution = fetch_air_pollution(CITY_LAT, CITY_LON, OW_API_KEY)
    weather = fetch_weather(CITY_LAT, CITY_LON, OW_API_KEY)

    row = build_feature_row(pollution, weather)
    append_row_to_csv(row, OUTPUT_CSV)

    print(f"Appended new row to {OUTPUT_CSV}")
    print(row)


if __name__ == "__main__":
    main()