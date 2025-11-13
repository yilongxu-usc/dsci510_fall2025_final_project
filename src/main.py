from data_retrieval import get_usda_yield_data, get_noaa_climate_data
import pandas as pd

if __name__ == "__main__":
    corn_df = get_usda_yield_data(2015, 2024, "CORN")
    wheat_df = get_usda_yield_data(2015, 2024, "WHEAT")
    temp_df = get_noaa_climate_data()

    corn_df.to_csv("data/corn_yield.csv", index=False)
    wheat_df.to_csv("data/wheat_yield.csv", index=False)
    temp_df.to_csv("data/climate.csv", index=False)

    print("Data saved to /data folder.")
