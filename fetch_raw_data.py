"""
Step 1a: Fetch raw AQI + weather data for Ghotki
using OpenWeather APIs.

Two APIs used:
  1. Air Pollution API  --> gives us PM2.5, PM10, NO2, O3, CO
  2. Current Weather API --> gives us temperature, humidity, wind, pressure

We combine both into one dictionary (one "row" of raw data).
"""

import requests
import json
from datetime import datetime

# ---- CONFIG ----
# Your OpenWeather API key
OW_API_KEY = "3f453341b725d1721e0dc64e136883cb"

# Ghotki, Sindh, Pakistan coordinates
# (We use lat/lon because Ghotki may not be in OW's city name database)
CITY_LAT  = 28.0089
CITY_LON  = 69.3159
CITY_NAME = "Ghotki"


# ---------------------------------------------------------------
# FUNCTION 1: Fetch air pollution data
# ---------------------------------------------------------------
def fetch_air_pollution(lat, lon, api_key):
    """
    Calls OpenWeather's Air Pollution API.
    Returns a dict with pollutant levels: pm2_5, pm10, no2, o3, co, aqi
    
    The URL structure:
      http://api.openweathermap.org/data/2.5/air_pollution
      ?lat=28.0089&lon=69.3159&appid=YOUR_KEY
    """
    url = "http://api.openweathermap.org/data/2.5/air_pollution"
    
    # 'params' are the query parameters added to the URL after '?'
    # requests automatically formats them: ?lat=...&lon=...&appid=...
    params = {
        "lat": lat,
        "lon": lon,
        "appid": api_key
    }
    
    response = requests.get(url, params=params, timeout=15)
    response.raise_for_status()  # crashes loudly if HTTP error (e.g. 401, 404)
    
    data = response.json()
    
    # The API returns a nested structure. We dig into it:
    # data["list"][0]  --> the most recent reading
    # data["list"][0]["components"]  --> the actual pollutant values
    # data["list"][0]["main"]["aqi"] --> AQI on a 1-5 scale (OW uses 1-5, not 0-500)
    
    latest = data["list"][0]
    components = latest["components"]
    
    return {
        "aqi_index": latest["main"]["aqi"],   # 1=Good, 2=Fair, 3=Moderate, 4=Poor, 5=Very Poor
        "pm2_5":     components["pm2_5"],      # Fine particles (most dangerous)
        "pm10":      components["pm10"],       # Coarser particles
        "no2":       components["no2"],        # Nitrogen dioxide (traffic pollution)
        "o3":        components["o3"],         # Ozone
        "co":        components["co"],         # Carbon monoxide
        "so2":       components["so2"],        # Sulphur dioxide
        "nh3":       components.get("nh3", 0), # Ammonia (not always present)
    }


# ---------------------------------------------------------------
# FUNCTION 2: Fetch current weather data
# ---------------------------------------------------------------
def fetch_weather(lat, lon, api_key):
    """
    Calls OpenWeather's Current Weather API.
    Returns a dict with: temperature, humidity, wind_speed, pressure, clouds
    
    Why do we need weather alongside pollution?
    - Wind disperses pollutants (high wind = lower AQI)
    - Humidity traps particles (high humidity = higher PM2.5)
    - Temperature affects chemical reactions in the air
    These are important FEATURES for our ML model.
    """
    url = "https://api.openweathermap.org/data/2.5/weather"
    
    params = {
        "lat": lat,
        "lon": lon,
        "appid": api_key,
        "units": "metric"  # gives temperature in Celsius, not Kelvin
    }
    
    response = requests.get(url, params=params, timeout=15)
    response.raise_for_status()
    
    data = response.json()
    
    return {
        "temperature":  data["main"]["temp"],       # Celsius
        "humidity":     data["main"]["humidity"],   # Percentage (0-100)
        "pressure":     data["main"]["pressure"],   # hPa (atmospheric pressure)
        "wind_speed":   data["wind"]["speed"],      # m/s
        "wind_deg":     data["wind"].get("deg", 0), # Wind direction in degrees
        "clouds":       data["clouds"]["all"],      # Cloud cover percentage
        "weather_desc": data["weather"][0]["description"],  # e.g. "haze", "clear sky"
    }


# ---------------------------------------------------------------
# MAIN: Call both functions, combine results, save to file
# ---------------------------------------------------------------
def main():
    print(f"Fetching data for {CITY_NAME}...")
    print(f"Coordinates: lat={CITY_LAT}, lon={CITY_LON}\n")
    
    # --- Step 1: Get pollution data ---
    print("Calling Air Pollution API...")
    pollution = fetch_air_pollution(CITY_LAT, CITY_LON, OW_API_KEY)
    print(f"  AQI Index: {pollution['aqi_index']} (1=Good to 5=Very Poor)")
    print(f"  PM2.5: {pollution['pm2_5']} µg/m³")
    print(f"  PM10:  {pollution['pm10']} µg/m³")
    
    # --- Step 2: Get weather data ---
    print("\nCalling Current Weather API...")
    weather = fetch_weather(CITY_LAT, CITY_LON, OW_API_KEY)
    print(f"  Temperature: {weather['temperature']}°C")
    print(f"  Humidity:    {weather['humidity']}%")
    print(f"  Wind Speed:  {weather['wind_speed']} m/s")
    print(f"  Conditions:  {weather['weather_desc']}")
    
    # --- Step 3: Combine into one raw record ---
    # We add a timestamp so we know WHEN this reading was taken.
    # This becomes critical during the backfill step (many readings over time).
    raw_record = {
        "timestamp": datetime.utcnow().isoformat(),
        "city": CITY_NAME,
        "lat": CITY_LAT,
        "lon": CITY_LON,
        **pollution,   # unpacks all pollution keys into this dict
        **weather,     # unpacks all weather keys into this dict
    }
    
    # --- Step 4: Save raw record to a JSON file ---
    # This is our "raw data" before any feature engineering.
    with open("sample_raw_record.json", "w") as f:
        json.dump(raw_record, f, indent=2)
    
    print("\n--- RAW RECORD SAVED ---")
    print(json.dumps(raw_record, indent=2))
    print("\nSaved to sample_raw_record.json")


if __name__ == "__main__":
    main()