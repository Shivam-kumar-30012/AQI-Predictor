"""
Step: Upload our cleaned historical dataset to Hopsworks as a Feature Group.

A Feature Group = a managed table inside Hopsworks' Feature Store.
Once uploaded, any script (training, dashboard, etc.) can pull this
same data back out, without needing the original CSV file.
"""

import hopsworks
import pandas as pd

# ---- CONFIG ----
HOPSWORKS_API_KEY = "G3PDMh1s40UydhEH.OOKc8jd8xs14JrarHy8PpnoBrEyxGqGdkActT46cHlO0FEewff1V8WuepySHtZTh"


def main():
    # ---- Step 1: Load our already-cleaned dataset ----
    print("Loading cleaned dataset...")
    df = pd.read_csv("aqi_historical_dataset_clean.csv")
    print(f"Loaded {len(df)} rows")

    # ---- Step 2: Connect to Hopsworks ----
    print("\nConnecting to Hopsworks...")
    project = hopsworks.login(api_key_value=HOPSWORKS_API_KEY)
    print(f"Connected to project: {project.name}")

    # ---- Step 3: Get the Feature Store for this project ----
    # Every Hopsworks project has ONE feature store attached to it -
    # this is where all our Feature Groups will live.
    fs = project.get_feature_store()

    # ---- Step 4: Create (or get) a Feature Group ----
    # 'primary_key' - which column(s) uniquely identify each row.
    #                 We use 'timestamp' since each row is one hourly reading.
    # 'event_time'  - tells Hopsworks this data is time-based, enabling
    #                 time-travel queries later (e.g. "get data as of X date").
    aqi_fg = fs.get_or_create_feature_group(
        name="aqi_ghotki_features",
        version=1,
        description="Hourly AQI + pollutant features for Ghotki, Pakistan",
        primary_key=["timestamp"],
        event_time="timestamp",
    )

    # ---- Step 5: Insert our data ----
    print("\nUploading data to Hopsworks (this may take a minute)...")
    aqi_fg.insert(df)

    print("\nDone! Data is now in your Hopsworks Feature Store.")
    print(f"Feature Group name: aqi_ghotki_features, version: 1")


if __name__ == "__main__":
    main()