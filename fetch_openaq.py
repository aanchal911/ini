"""
OpenAQ v3 API — India AQI Data Fetcher
Replace YOUR_API_KEY with your actual key before running.
pip install openaq pandas requests
"""

import requests
import pandas as pd
import time
import json

API_KEY = "YOUR_OPENAQ_API_KEY_HERE"   # Get your free API key from https://openaq.org

HEADERS = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

BASE_URL = "https://api.openaq.org/v3"

# India city location IDs on OpenAQ (common ones)
# You can find more at: https://api.openaq.org/v3/locations?country=IN
# Find location IDs for Indian cities at: https://api.openaq.org/v3/locations?country=IN
INDIA_LOCATIONS = {
    "Delhi":     [2178],
    "Mumbai":    [2180],
    "Bangalore": [2184],
}

PARAMETERS = ["pm25", "pm10", "no2", "so2", "co", "o3"]

def fetch_measurements(location_id, parameter, limit=1000):
    """Fetch measurements for a location + parameter."""
    url = f"{BASE_URL}/locations/{location_id}/measurements"
    params = {
        "parameter": parameter,
        "limit": limit,
        "order_by": "datetime",
        "sort": "desc"
    }
    try:
        r = requests.get(url, headers=HEADERS, params=params, timeout=15)
        if r.status_code == 200:
            return r.json().get("results", [])
        else:
            print(f"  Error {r.status_code} for location {location_id}, param {parameter}")
            return []
    except Exception as e:
        print(f"  Exception: {e}")
        return []

def fetch_city_data(city_name, location_ids):
    """Fetch all parameters for a city."""
    city_records = []
    for loc_id in location_ids:
        print(f"  Fetching {city_name} location {loc_id}...")
        loc_data = {}
        for param in PARAMETERS:
            results = fetch_measurements(loc_id, param, limit=500)
            for r in results:
                dt = r.get("period", {}).get("datetimeFrom", {}).get("local", "")
                val = r.get("value")
                if dt and val is not None:
                    key = dt[:10]  # date only
                    if key not in loc_data:
                        loc_data[key] = {"City": city_name, "Date": key, "LocationID": loc_id}
                    loc_data[key][param.upper()] = val
            time.sleep(0.3)  # rate limit

        city_records.extend(loc_data.values())
    return city_records

def main():
    all_records = []
    for city, loc_ids in INDIA_LOCATIONS.items():
        print(f"\nFetching {city}...")
        records = fetch_city_data(city, loc_ids)
        all_records.extend(records)
        print(f"  Got {len(records)} records for {city}")
        time.sleep(1)

    df = pd.DataFrame(all_records)
    print(f"\nTotal records: {len(df)}")
    print("Columns:", df.columns.tolist())
    df.to_csv("openaq_india_data.csv", index=False)
    print("✅ Saved to openaq_india_data.csv")

if __name__ == "__main__":
    main()
