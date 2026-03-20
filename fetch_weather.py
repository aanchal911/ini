"""
OpenWeather Historical API — Weather Data Fetcher for India Cities
Get free API key at: https://openweathermap.org/api
pip install requests pandas
"""

import requests
import pandas as pd
import time
from datetime import datetime, timedelta

OW_API_KEY = "YOUR_OPENWEATHER_API_KEY_HERE"  # Get free key at https://openweathermap.org/api

CITIES = {
    "Delhi":      (28.6139, 77.2090),
    "Mumbai":     (19.0760, 72.8777),
    "Ahmedabad":  (23.0225, 72.5714),
    "Chennai":    (13.0827, 80.2707),
    "Kolkata":    (22.5726, 88.3639),
    "Bangalore":  (12.9716, 77.5946),
    "Hyderabad":  (17.3850, 78.4867),
    "Chandigarh": (30.7333, 76.7794),
    "Guwahati":   (26.1445, 91.7362),
    "Pune":       (18.5204, 73.8567),
    "Jaipur":     (26.9124, 75.7873),
    "Lucknow":    (26.8467, 80.9462),
}

def fetch_current_weather(city, lat, lon):
    """Fetch current weather for a city."""
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"lat": lat, "lon": lon, "appid": OW_API_KEY, "units": "metric"}
    try:
        r = requests.get(url, params=params, timeout=10)
        if r.status_code == 200:
            d = r.json()
            return {
                "City":        city,
                "Date":        datetime.now().strftime("%Y-%m-%d"),
                "Temperature": d["main"]["temp"],
                "Humidity":    d["main"]["humidity"],
                "WindSpeed":   d["wind"]["speed"] * 3.6,  # m/s → km/h
                "WindDir":     d["wind"].get("deg", 0),
                "Pressure":    d["main"]["pressure"],
                "Rainfall":    d.get("rain", {}).get("1h", 0),
                "Description": d["weather"][0]["description"],
            }
    except Exception as e:
        print(f"  Error for {city}: {e}")
    return None

def fetch_forecast(city, lat, lon):
    """Fetch 5-day forecast (free tier)."""
    url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {"lat": lat, "lon": lon, "appid": OW_API_KEY, "units": "metric"}
    records = []
    try:
        r = requests.get(url, params=params, timeout=10)
        if r.status_code == 200:
            for item in r.json()["list"]:
                records.append({
                    "City":        city,
                    "Date":        item["dt_txt"][:10],
                    "Time":        item["dt_txt"][11:16],
                    "Temperature": item["main"]["temp"],
                    "Humidity":    item["main"]["humidity"],
                    "WindSpeed":   item["wind"]["speed"] * 3.6,
                    "WindDir":     item["wind"].get("deg", 0),
                    "Pressure":    item["main"]["pressure"],
                    "Rainfall":    item.get("rain", {}).get("3h", 0),
                })
    except Exception as e:
        print(f"  Forecast error for {city}: {e}")
    return records

def main():
    current_records = []
    forecast_records = []

    for city, (lat, lon) in CITIES.items():
        print(f"Fetching weather for {city}...")
        curr = fetch_current_weather(city, lat, lon)
        if curr:
            current_records.append(curr)
        fore = fetch_forecast(city, lat, lon)
        forecast_records.extend(fore)
        time.sleep(0.5)

    # Save
    if current_records:
        df_curr = pd.DataFrame(current_records)
        df_curr.to_csv("weather_current.csv", index=False)
        print(f"\n✅ Current weather saved: {len(df_curr)} cities → weather_current.csv")
        print(df_curr[["City","Temperature","Humidity","WindSpeed"]].to_string(index=False))

    if forecast_records:
        df_fore = pd.DataFrame(forecast_records)
        df_fore.to_csv("weather_forecast.csv", index=False)
        print(f"\n✅ Forecast saved: {len(df_fore)} rows → weather_forecast.csv")

if __name__ == "__main__":
    main()
