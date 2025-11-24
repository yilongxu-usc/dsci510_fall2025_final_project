"""
Data retrieval functions for the Crop Shock project.
Fetches crop yield and climate data from USDA and NOAA APIs.
"""
import requests
import pandas as pd
from config import (
    USDA_API_KEY,
    NOAA_TOKEN,
    USDA_ENDPOINT,
    NOAA_ENDPOINT
    )


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


def get_noaa_climate_data(dataset="GSOM", datatype="TAVG",
                          start="2010-01-01", end="2024-12-31",
                          location="FIPS:06"):
    """
    Fetch average temperature data from NOAA API.
    You MUST provide a valid locationid (state FIPS, climate division, or station ID).
    """

    print("Fetching NOAA data...")

    headers = {"token": NOAA_TOKEN}

    params = {
    "datasetid": "GSOM",
    "datatypeid": "TAVG",
    "stationid": "GHCND:USW00023174",  # LAX Airport
    "startdate": "2015-01-01",
    "enddate": "2024-12-31",
    "limit": 1000
    }


    response = requests.get(NOAA_ENDPOINT, headers=headers, params=params)
    response.raise_for_status()

    results = response.json().get("results", [])
    print(f"Retrieved {len(results)} climate records")
    return pd.DataFrame(results)