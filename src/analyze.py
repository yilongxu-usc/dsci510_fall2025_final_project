"""
Analysis script for the Crop Shock project.

- Loads climate (NOAA) and yield (USDA) data from /data
- Aggregates climate to annual averages
- Aggregates yields to national-level annual yields
- Merges datasets and computes simple correlations
- Saves basic plots into /results for use in the report and slides
"""

from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

from config import DATA_DIR, RESULTS_DIR


def load_data():
    """Load climate, corn, and wheat CSV files from the data directory."""
    climate_path = DATA_DIR / "climate.csv"
    corn_path = DATA_DIR / "corn_yield.csv"
    wheat_path = DATA_DIR / "wheat_yield.csv"

    climate = pd.read_csv(climate_path)
    corn = pd.read_csv(corn_path)
    wheat = pd.read_csv(wheat_path)

    print(f"Loaded climate data: {climate.shape[0]} rows")
    print(f"Loaded corn yield data: {corn.shape[0]} rows")
    print(f"Loaded wheat yield data: {wheat.shape[0]} rows")

    return climate, corn, wheat


def prepare_climate(climate: pd.DataFrame) -> pd.DataFrame:
    """
    Convert monthly climate data to annual average temperature.

    Expects columns: 'date', 'value'.
    Returns DataFrame with columns: 'year', 'avg_temp'.
    """
    climate = climate.copy()
    climate["date"] = pd.to_datetime(climate["date"])
    climate["year"] = climate["date"].dt.year

    annual = (
        climate.groupby("year")["value"]
        .mean()
        .reset_index()
        .rename(columns={"value": "avg_temp"})
    )

    print("Prepared annual climate data:")
    print(annual.head())

    return annual


def prepare_corn(corn: pd.DataFrame) -> pd.DataFrame:
    """
    Prepare national-level annual corn yield.

    Current corn_yield.csv mostly uses 'OTHER STATES'.
    We treat it as one series and keep one row per year.
    """
    corn = corn.copy()
    # If there are multiple rows per year, take the mean
    annual_corn = (
        corn.groupby("year")["CORN_yield"]
        .mean()
        .reset_index()
        .rename(columns={"CORN_yield": "corn_yield"})
    )

    print("Prepared annual corn yield data:")
    print(annual_corn.head())

    return annual_corn


def prepare_wheat(wheat: pd.DataFrame) -> pd.DataFrame:
    """
    Prepare national-level annual wheat yield by averaging across states.

    wheat_yield.csv has many states; we compute mean yield per year.
    """
    wheat = wheat.copy()
    annual_wheat = (
        wheat.groupby("year")["WHEAT_yield"]
        .mean()
        .reset_index()
        .rename(columns={"WHEAT_yield": "wheat_yield"})
    )

    print("Prepared annual wheat yield data:")
    print(annual_wheat.head())

    return annual_wheat


def merge_datasets(climate_annual, corn_annual, wheat_annual):
    """Merge climate with corn and wheat yields on 'year'."""
    corn_merged = climate_annual.merge(corn_annual, on="year", how="inner")
    wheat_merged = climate_annual.merge(wheat_annual, on="year", how="inner")

    print("Merged climate + corn data:")
    print(corn_merged.head())

    print("Merged climate + wheat data:")
    print(wheat_merged.head())

    return corn_merged, wheat_merged


def plot_time_series(df, x_col, y_col, title, filename, ylabel=None):
    """Save a simple time-series plot to the results directory."""
    plt.figure()
    plt.plot(df[x_col], df[y_col], marker="o")
    plt.xlabel(x_col)
    plt.ylabel(ylabel if ylabel else y_col)
    plt.title(title)
    plt.grid(True)
    plt.tight_layout()

    out_path = RESULTS_DIR / filename
    plt.savefig(out_path)
    plt.close()
    print(f"Saved plot: {out_path}")


def plot_scatter(df, x_col, y_col, title, filename, xlabel=None, ylabel=None):
    """Save a simple scatter plot to the results directory."""
    plt.figure()
    plt.scatter(df[x_col], df[y_col])
    plt.xlabel(xlabel if xlabel else x_col)
    plt.ylabel(ylabel if ylabel else y_col)
    plt.title(title)
    plt.grid(True)
    plt.tight_layout()

    out_path = RESULTS_DIR / filename
    plt.savefig(out_path)
    plt.close()
    print(f"Saved plot: {out_path}")


def run_analysis():
    """High-level analysis pipeline."""
    climate, corn, wheat = load_data()

    climate_annual = prepare_climate(climate)
    corn_annual = prepare_corn(corn)
    wheat_annual = prepare_wheat(wheat)

    corn_merged, wheat_merged = merge_datasets(
        climate_annual, corn_annual, wheat_annual
    )

    # Save merged datasets for inspection
    corn_merged.to_csv(RESULTS_DIR / "climate_corn_merged.csv", index=False)
    wheat_merged.to_csv(RESULTS_DIR / "climate_wheat_merged.csv", index=False)
    print("Saved merged CSV files to results directory.")

    # Compute simple correlations
    print("\nCorrelation (climate vs corn yield):")
    print(corn_merged[["avg_temp", "corn_yield"]].corr())

    print("\nCorrelation (climate vs wheat yield):")
    print(wheat_merged[["avg_temp", "wheat_yield"]].corr())

    # Time-series plots
    plot_time_series(
        climate_annual,
        x_col="year",
        y_col="avg_temp",
        title="Annual Average Temperature (LAX Station)",
        filename="annual_avg_temp.png",
        ylabel="Temperature (°C)",
    )

    plot_time_series(
        corn_annual,
        x_col="year",
        y_col="corn_yield",
        title="Annual Corn Yield (National Average)",
        filename="annual_corn_yield.png",
        ylabel="Corn yield (bushels per acre)",
    )

    plot_time_series(
        wheat_annual,
        x_col="year",
        y_col="wheat_yield",
        title="Annual Wheat Yield (National Average)",
        filename="annual_wheat_yield.png",
        ylabel="Wheat yield (bushels per acre)",
    )

    # Scatter plots: temperature vs yield
    plot_scatter(
        corn_merged,
        x_col="avg_temp",
        y_col="corn_yield",
        title="Average Temperature vs Corn Yield",
        filename="temp_vs_corn_yield.png",
        xlabel="Average temperature (°C)",
        ylabel="Corn yield (bushels per acre)",
    )

    plot_scatter(
        wheat_merged,
        x_col="avg_temp",
        y_col="wheat_yield",
        title="Average Temperature vs Wheat Yield",
        filename="temp_vs_wheat_yield.png",
        xlabel="Average temperature (°C)",
        ylabel="Wheat yield (bushels per acre)",
    )

    print("\nAnalysis finished. Check the 'results' folder for plots and merged CSVs.")


if __name__ == "__main__":
    run_analysis()
