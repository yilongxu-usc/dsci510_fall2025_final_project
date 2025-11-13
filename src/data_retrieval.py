"""
Data retrieval functions for the Crop Shock project.
Fetches crop yield and climate data from USDA and NOAA APIs.
"""

import os
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

# -------------------------------
# USDA NASS API CONFIG
# -------------------------------
USDA_API_KEY = os.getenv("USDA_API_KEY")  # store your key in .env (never commit it)
USDA_ENDPOINT = "https://quickstats.nass.usda.gov/api/api_GET/"

def get_usda_yield_data(year_start=2010, year_end=2024, crop="CORN"):
    """
    Fetch crop yield data (corn/wheat) by state from USDA NASS API.
    Returns a pandas DataFrame.
    """
    params = {
        "key": USDA_API_KEY,
        "source_desc": "SURVEY",
        "sector_desc": "CROPS",
        "group_desc": "FIELD CROPS",
        "commodity_desc": crop,
        "statisticcat_desc": "YIELD",
        "agg_level_desc": "STATE",
        "year__GE": year_start,
        "year__LE": year_end,
        "format": "JSON"
    }

    print("Fetching USDA data...")
    response = requests.get(USDA_ENDPOINT, params=params)
    response.raise_for_status()
    data = response.json().get("data", [])
    print(f"Retrieved {len(data)} records for {crop}")

    df = pd.DataFrame(data)
    if not df.empty:
        df = df[["year", "state_name", "Value"]]
        df.rename(columns={"Value": f"{crop}_yield"}, inplace=True)
    return df


# -------------------------------
# NOAA API CONFIG
# -------------------------------
NOAA_TOKEN = os.getenv("NOAA_TOKEN")
NOAA_ENDPOINT = "https://www.ncei.noaa.gov/cdo-web/api/v2/data"

def get_noaa_climate_data(dataset="GSOM", datatype="TAVG",
                          start="2010-01-01", end="2024-12-31",
                          location="FIPS:06"):
    """
    Fetch average temperature data from NOAA API.
    You MUST provide a valid locationid (state FIPS, climate division, or station ID).
    """

    print("Fetching NOAA data...")
    print("NOAA TOKEN LOADED:", NOAA_TOKEN)

    headers = {"token": NOAA_TOKEN}

    params = {
    "datasetid": "GSOM",
    "datatypeid": "TAVG",
    "stationid": "GHCND:USW00023174",  # LAX Airport
    "startdate": "2010-01-01",
    "enddate": "2010-12-31",
    "limit": 1000
    }


    response = requests.get(NOAA_ENDPOINT, headers=headers, params=params)
    print("NOAA RAW RESPONSE:", response.text[:200])
    response.raise_for_status()

    results = response.json().get("results", [])
    print(f"Retrieved {len(results)} climate records")
    return pd.DataFrame(results)
