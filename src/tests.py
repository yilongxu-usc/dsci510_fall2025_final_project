import pandas as pd
from data_retrieval import get_usda_yield_data, get_noaa_station_monthly_tavg
from data_retrieval import USDA_API_KEY, NOAA_TOKEN

def test_usda_api():
    assert USDA_API_KEY, "USDA key not loaded"
    df = get_usda_yield_data(2020, 2020, "CORN")
    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0

def test_noaa_api():
    assert NOAA_TOKEN, "NOAA token not loaded"
    station = "GHCND:USW00023174"
    df = get_noaa_station_monthly_tavg(station, "2020-01-01", "2020-12-31")
    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0