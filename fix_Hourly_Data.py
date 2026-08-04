"""
Patches the already-collected hourly_dataset.csv rows to add
target_aqi, matching the same fix applied to historical data.

Reads: hourly_dataset.csv (old schema, has target_pm2_5)
Writes: hourly_dataset.csv (overwritten with new schema, has target_aqi)
"""

import pandas as pd
from aqi_calculator import calculate_aqi


def main():
    print("Loading existing hourly dataset...")
    df = pd.read_csv("hourly_dataset.csv")
    print(f"Loaded {len(df)} rows")

    print("Calculating EPA AQI for each row...")
    df["target_aqi"] = df.apply(
        lambda row: calculate_aqi(
            pm25=row["target_pm2_5"],
            pm10=row["pm10"],
            co=row["co"],
            o3=row["o3"],
        ),
        axis=1
    )

    # Rename old target -> regular feature, matching our new schema
    df = df.rename(columns={"target_pm2_5": "pm2_5"})

    print("\nUpdated rows:")
    print(df[["timestamp", "pm2_5", "pm10", "co", "o3", "target_aqi"]])

    # Overwrite the same file - from now on, hourly_collector.py
    # will keep appending rows using this SAME new schema, so this
    # file becomes consistent going forward.
    df.to_csv("hourly_dataset.csv", index=False)
    print("\nhourly_dataset.csv updated with target_aqi column")


if __name__ == "__main__":
    main()