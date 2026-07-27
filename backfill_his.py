"""
Step 2: Historical Backfill

Pulls ~5 years of hourly air pollution + weather data for Ghotki,
runs feature engineering on every row, and saves it all as ONE
CSV file - our actual training dataset.
"""

import requests
import csv
import time
from datetime import datetime, timezone


# ---- CONFIG ----
OW_API_KEY = "3f453341b725d1721e0dc64e136883cb"
CITY_LAT = 28.0089
CITY_LON = 69.3159
CITY_NAME = "Ghotki"

OUTPUT_CSV = "aqi_historical_dataset.csv"


# ---------------------------------------------------------------
# Reused from before: date <-> unix conversion
# ---------------------------------------------------------------
def date_to_unix(year, month, day):
    dt = datetime(year, month, day, tzinfo=timezone.utc)
    return int(dt.timestamp())


# ---------------------------------------------------------------
# Reused from before: fetch one chunk of historical readings
# ---------------------------------------------------------------
def fetch_historical_chunk(lat, lon, start_unix, end_unix, api_key):
    url = "http://api.openweathermap.org/data/2.5/air_pollution/history"
    params = {
        "lat": lat, "lon": lon,
        "start": start_unix, "end": end_unix,
        "appid": api_key
    }
    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    return response.json()["list"]


# ---------------------------------------------------------------
# NEW: build the list of date ranges we need to loop over
# ---------------------------------------------------------------
def build_year_chunks():
    """
    Returns a list of (start_unix, end_unix) tuples, one per chunk,
    covering Nov 2020 (when OpenWeather's data starts) through today.

    We split by year because the API only allows <1 year per call.
    """
    chunks = [
        (date_to_unix(2020, 11, 27), date_to_unix(2021, 1, 1)),
        (date_to_unix(2021, 1, 1),   date_to_unix(2022, 1, 1)),
        (date_to_unix(2022, 1, 1),   date_to_unix(2023, 1, 1)),
        (date_to_unix(2023, 1, 1),   date_to_unix(2024, 1, 1)),
        (date_to_unix(2024, 1, 1),   date_to_unix(2025, 1, 1)),
        (date_to_unix(2025, 1, 1),   date_to_unix(2026, 1, 1)),
        (date_to_unix(2026, 1, 1),   int(datetime.now(timezone.utc).timestamp())),
    ]
    return chunks


# ---------------------------------------------------------------
# NEW: feature engineering, adapted for a UNIX 'dt' instead of
# the ISO timestamp string we used in Step 1b
# ---------------------------------------------------------------
def build_feature_row(reading: dict) -> dict:
    """
    Takes ONE raw reading (as returned by the historical API)
    and converts it into a clean feature row - same idea as
    feature_engineering.py, just adapted for this data's shape.
    """
    dt_unix = reading["dt"]
    dt = datetime.fromtimestamp(dt_unix, tz=timezone.utc)
    comp = reading["components"]

    return {
        "timestamp": dt.isoformat(),
        "city": CITY_NAME,

        # time features
        "hour": dt.hour,
        "day": dt.day,
        "month": dt.month,
        "day_of_week": dt.weekday(),
        "is_weekend": 1 if dt.weekday() >= 5 else 0,

        # pollutant features (inputs)
        "pm10": comp["pm10"],
        "no2": comp["no2"],
        "o3": comp["o3"],
        "co": comp["co"],
        "so2": comp["so2"],
        "nh3": comp["nh3"],

        # target
        "target_pm2_5": comp["pm2_5"],
    }


# ---------------------------------------------------------------
# MAIN: loop through all chunks, collect + transform + save
# ---------------------------------------------------------------
def main():
    chunks = build_year_chunks()
    all_feature_rows = []

    for i, (start, end) in enumerate(chunks, start=1):
        print(f"Fetching chunk {i}/{len(chunks)}...")

        try:
            readings = fetch_historical_chunk(CITY_LAT, CITY_LON, start, end, OW_API_KEY)
        except requests.exceptions.HTTPError as e:
            print(f"  Failed: {e}")
            continue

        print(f"  Got {len(readings)} raw readings")

        # Transform every raw reading into a feature row
        for reading in readings:
            feature_row = build_feature_row(reading)
            all_feature_rows.append(feature_row)

        # Be polite to the API - small pause between requests
        time.sleep(1)

    print(f"\nTotal feature rows collected: {len(all_feature_rows)}")

    # ---- Save everything as CSV ----
    if all_feature_rows:
        fieldnames = list(all_feature_rows[0].keys())

        with open(OUTPUT_CSV, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_feature_rows)

        print(f"Saved dataset to {OUTPUT_CSV}")
    else:
        print("No data collected - nothing to save.")


if __name__ == "__main__":
    main()