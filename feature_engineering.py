"""
Step 1b: Feature Engineering

Takes the RAW record (from fetch_raw_data.py) and turns it into
a "feature row" - the actual clean, structured input our ML model
will eventually learn from.

We are NOT calling the API again here. We're just transforming
data we already collected.
"""

import json
from datetime import datetime


def load_raw_record(filepath="sample_raw_record.json"):
    """
    Reads the JSON file we saved in Step 1a.
    'with open(...) as f' automatically closes the file when done -
    this is the standard safe way to read files in Python.
    """
    with open(filepath, "r") as f:
        return json.load(f)


def extract_time_features(timestamp_str: str) -> dict:
    """
    Takes a timestamp string like '2026-07-27T06:57:33.381493'
    and extracts useful time-based features from it.

    datetime.fromisoformat() converts the STRING into a proper
    Python datetime OBJECT - which lets us ask it questions like
    "what hour is this?" or "what day of week is this?"
    """
    dt = datetime.fromisoformat(timestamp_str)

    return {
        "hour": dt.hour,                    # 0-23
        "day": dt.day,                      # 1-31 (day of month)
        "month": dt.month,                  # 1-12
        "day_of_week": dt.weekday(),        # 0=Monday, 6=Sunday
        "is_weekend": 1 if dt.weekday() >= 5 else 0,  # Sat/Sun = 1, else 0
    }


def build_feature_row(raw: dict) -> dict:
    """
    Combines the raw pollution/weather values with the new
    time-based features into ONE clean row - this is what
    a model training script will eventually read.
    """
    time_features = extract_time_features(raw["timestamp"])

    feature_row = {
        # --- Identifiers (not used by the model, just for tracking) ---
        "timestamp": raw["timestamp"],
        "city": raw["city"],

        # --- Time-based features (what we just built) ---
        **time_features,

        # --- Weather features (already numeric, ready to use) ---
        "temperature": raw["temperature"],
        "humidity": raw["humidity"],
        "pressure": raw["pressure"],
        "wind_speed": raw["wind_speed"],
        "wind_deg": raw["wind_deg"],
        "clouds": raw["clouds"],

        # --- Pollutant features (these become our model INPUTS) ---
        "pm10": raw["pm10"],
        "no2": raw["no2"],
        "o3": raw["o3"],
        "co": raw["co"],
        "so2": raw["so2"],
        "nh3": raw["nh3"],

        # --- TARGET (what we want the model to PREDICT) ---
        # pm2_5 is our main target since it's the most health-critical
        # and is what most AQI calculations are based on.
        "target_pm2_5": raw["pm2_5"],
    }

    return feature_row


def main():
    print("Loading raw record...")
    raw = load_raw_record()

    print("Extracting features...\n")
    feature_row = build_feature_row(raw)

    print("--- FEATURE ROW (ready for model training later) ---")
    print(json.dumps(feature_row, indent=2))

    # Save it - this is the format our training data will eventually be in
    with open("sample_feature_row.json", "w") as f:
        json.dump(feature_row, f, indent=2)

    print("\nSaved to sample_feature_row.json")


if __name__ == "__main__":
    main()