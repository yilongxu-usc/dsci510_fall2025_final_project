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


def get_usda_yield_data(year_start=1970, year_end=2024, crop="CORN"):
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


def get_noaa_climate_data(dataset="GSOM",datatype=["TAVG", "PRCP"],start_year=1970,end_year=2024):
    """
    Fetch NOAA climate data in small year chunks and combine results.
    Final output spans start_year → end_year in a single DataFrame.
    """

    print(f"Fetching NOAA climate data from {start_year} to {end_year}...")
    headers = {"token": NOAA_TOKEN}

    stations = {
        "CA": ("LAX_CA", "GHCND:USW00023174"),
        "UT": ("SLC_UT", "GHCND:USW00024127"),
        "IL": ("ORD_IL", "GHCND:USW00094846"),
        "TX": ("DFW_TX", "GHCND:USW00003927"),
        "NY": ("JFK_NY", "GHCND:USW00094789"),
    }

    all_results = []

    # --- loop over 2-year chunks ---
    for year in range(start_year, end_year + 1, 2):
        start_date = f"{year}-01-01"
        end_date = f"{min(year + 1, end_year)}-12-31"

        print(f"\nRequesting period: {start_date} → {end_date}")

        for state, (label, station_id) in stations.items():
            print(f"  Station {station_id} ({state})")

            params = {
                "datasetid": dataset,
                "datatypeid": datatype,
                "stationid": station_id,
                "startdate": start_date,
                "enddate": end_date,
                "limit": 1000
            }

            try:
                response = requests.get(
                    NOAA_ENDPOINT,
                    headers=headers,
                    params=params,
                    timeout=30
                )
                response.raise_for_status()
                results = response.json().get("results", [])

                for r in results:
                    r["station_name"] = label
                    r["state"] = state

                print(f"    Retrieved {len(results)} records")
                all_results.extend(results)

            except requests.exceptions.RequestException as e:
                print(f"    WARNING: Failed for {station_id}: {e}")

    print(f"\nTotal NOAA records collected: {len(all_results)}")
    return pd.DataFrame(all_results)

