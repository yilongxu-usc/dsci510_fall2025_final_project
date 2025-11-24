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
                          start="2015-01-01", end="2024-12-31"):
    """
    Fetch average monthly temperature from multiple NOAA stations.
    Returns a combined DataFrame with columns:
        date, station, value
    """

    print("Fetching NOAA data from multiple stations...")

    headers = {"token": NOAA_TOKEN}

    # Selected stations across US
    stations = {
    "CA": ("LAX_CA", "GHCND:USW00023174"),      # California
    "UT": ("SLC_UT", "GHCND:USW00024127"),      # Utah
    "IL": ("ORD_IL", "GHCND:USW00094846"),      # Illinois
    "TX": ("DFW_TX", "GHCND:USW00003927"),      # Texas
    "NY": ("JFK_NY", "GHCND:USW00094789"),      # New York
    }


    all_results = []

    for name, (label, station_id) in stations.items():
        print(f"  Fetching station {station_id} ({name})...")

        params = {
            "datasetid": dataset,
            "datatypeid": datatype,
            "stationid": station_id,
            "startdate": start,
            "enddate": end,
            "limit": 1000
        }

        try:
            response = requests.get(NOAA_ENDPOINT, headers=headers, params=params)
            response.raise_for_status()
            station_results = response.json().get("results", [])

            for r in station_results:
                r["station_name"] = label
                r["state"] = name

            print(f"    Retrieved {len(station_results)} records")

            all_results.extend(station_results)

        except requests.exceptions.HTTPError as e:
            print(f"    WARNING: Station {station_id} failed: {e}")

    print(f"Total combined NOAA records: {len(all_results)}")

    return pd.DataFrame(all_results)
