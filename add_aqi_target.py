"""
Adds a proper target_aqi column to our cleaned historical dataset,
using the official EPA AQI formula - replacing target_pm2_5 as
our model's target variable.

Reads: aqi_historical_dataset_clean.csv
Writes: aqi_historical_dataset_final.csv
"""

import pandas as pd
from aqi_calculator import calculate_aqi


def main():
    print("Loading cleaned dataset...")
    df = pd.read_csv("aqi_historical_dataset_clean.csv")
    print(f"Loaded {len(df)} rows")

    print("Calculating EPA AQI for every row (this may take a moment)...")

    # .apply() runs a function on EVERY row of the DataFrame.
    # axis=1 means "go row by row" (axis=0 would mean column by column).
    # For each row, we pull out its pollutant values and pass them
    # into our calculate_aqi() function, then store the result.
    df["target_aqi"] = df.apply(
        lambda row: calculate_aqi(
            pm25=row["target_pm2_5"],  # our old target becomes an INPUT now
            pm10=row["pm10"],
            co=row["co"],
            o3=row["o3"],
        ),
        axis=1
    )

    # Rename the old target column so it's clearly just another
    # input feature now, not the target
    df = df.rename(columns={"target_pm2_5": "pm2_5"})

    print("\nSample of new target_aqi values:")
    print(df[["timestamp", "pm2_5", "pm10", "co", "o3", "target_aqi"]].head(10))

    print("\nAQI distribution summary:")
    print(df["target_aqi"].describe())

    df.to_csv("aqi_historical_dataset_final.csv", index=False)
    print("\nSaved to aqi_historical_dataset_final.csv")


if __name__ == "__main__":
    main()