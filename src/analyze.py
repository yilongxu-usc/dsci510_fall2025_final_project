"""
Per-state analysis script for the Crop Shock project.

It performs:
- Per-state annual climate aggregation (from multiple NOAA stations)
- Per-state annual corn and wheat yield aggregation (from USDA)
- Merges climate/yield per state
- State-level regressions (avg_temp → yield)
- State-level scatter/regression plots
- Multi-state comparison time series
- Correlation heatmap with value labels

Outputs saved into /results.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from config import DATA_DIR, RESULTS_DIR
import os

# --------------------------
# 1. Load Data
# --------------------------

def load_data():
    climate = pd.read_csv(DATA_DIR / "climate.csv")
    corn = pd.read_csv(DATA_DIR / "corn_yield.csv")
    wheat = pd.read_csv(DATA_DIR / "wheat_yield.csv")

    print(f"Loaded climate rows: {climate.shape[0]}")
    print(f"Loaded corn rows: {corn.shape[0]}")
    print(f"Loaded wheat rows: {wheat.shape[0]}")

    return climate, corn, wheat


# --------------------------
# 2. Prepare Climate (Per-State)
# --------------------------

def prepare_climate(climate: pd.DataFrame):
    """
    Returns per-state annual climate:
        year, state, avg_temp
    """
    df = climate.copy()
    df["date"] = pd.to_datetime(df["date"])
    df["year"] = df["date"].dt.year
    df["value"] = pd.to_numeric(df["value"], errors="coerce")

    # Group: per-state annual temp
    climate_state = (
        df.groupby(["state", "year"])["value"]
        .mean()
        .reset_index()
        .rename(columns={"value": "avg_temp"})
    )

    print("\nClimate (per-state) preview:")
    print(climate_state.head())

    return climate_state


# --------------------------
# 3. Prepare Crop Yields
# --------------------------

US_STATES = {
    "CALIFORNIA": "CA",
    "UTAH": "UT",
    "ILLINOIS": "IL",
    "TEXAS": "TX",
    "NEW YORK": "NY"
}

def prepare_corn(corn: pd.DataFrame):
    corn = corn.copy()
    corn["state"] = corn["state_name"].str.upper().map(US_STATES)
    annual = (
        corn.groupby(["state", "year"])["CORN_yield"]
        .mean()
        .reset_index()
        .rename(columns={"CORN_yield": "corn_yield"})
    )
    print("\nCorn annual per-state:")
    print(annual.head())
    return annual


def prepare_wheat(wheat: pd.DataFrame):
    wheat = wheat.copy()
    wheat["state"] = wheat["state_name"].str.upper().map(US_STATES)
    annual = (
        wheat.groupby(["state", "year"])["WHEAT_yield"]
        .mean()
        .reset_index()
        .rename(columns={"WHEAT_yield": "wheat_yield"})
    )
    print("\nWheat annual per-state:")
    print(annual.head())
    return annual


# --------------------------
# 4. Merge per-state climate & yields
# --------------------------

def merge_state_level(climate_state, corn_state, wheat_state):
    corn_merge = climate_state.merge(corn_state, on=["state", "year"], how="inner")
    wheat_merge = climate_state.merge(wheat_state, on=["state", "year"], how="inner")
    return corn_merge, wheat_merge


# --------------------------
# 5. Plot utilities
# --------------------------

def plot_scatter(df, x, y, title, filename, xlabel=None, ylabel=None):
    plt.figure()
    plt.scatter(df[x], df[y])
    plt.grid(True)
    plt.title(title)
    plt.xlabel(xlabel if xlabel else x)
    plt.ylabel(ylabel if ylabel else y)
    plt.tight_layout()
    plt.savefig(RESULTS_DIR / filename)
    plt.close()
    print("Saved:", filename)


def plot_regression(df, x, y, slope, intercept, title, filename):
    xs = df[x].to_numpy()
    order = np.argsort(xs)
    xs_sorted = xs[order]
    ys_fit = slope * xs_sorted + intercept

    plt.figure()
    plt.scatter(df[x], df[y], label="Data")
    plt.plot(xs_sorted, ys_fit, color="red", label="Fit")
    plt.grid(True)
    plt.xlabel(x)
    plt.ylabel(y)
    plt.title(title)
    plt.legend()
    plt.tight_layout()
    plt.savefig(RESULTS_DIR / filename)
    plt.close()
    print("Saved:", filename)


def run_linear_regression(df, x, y):
    xs = df[x].to_numpy(dtype=float)
    ys = df[y].to_numpy(dtype=float)

    if len(xs) < 2:
        return np.nan, np.nan, np.nan

    slope, intercept = np.polyfit(xs, ys, 1)
    y_pred = slope * xs + intercept

    ss_res = np.sum((ys - y_pred)**2)
    ss_tot = np.sum((ys - np.mean(ys))**2)
    r2 = 1 - ss_res / ss_tot if ss_tot != 0 else np.nan

    return slope, intercept, r2


def plot_correlation_heatmap(corr_df, filename):
    plt.figure(figsize=(6, 5))
    im = plt.imshow(corr_df.values, vmin=-1, vmax=1, cmap="coolwarm")
    plt.colorbar(im)

    ticks = range(len(corr_df.columns))
    plt.xticks(ticks, corr_df.columns, rotation=45, ha="right")
    plt.yticks(ticks, corr_df.columns)

    # Add numeric labels
    for i in range(len(corr_df.columns)):
        for j in range(len(corr_df.columns)):
            val = corr_df.values[i, j]
            plt.text(j, i, f"{val:.2f}", ha="center", va="center", color="black", fontsize=10)

    plt.title("Correlation Heatmap")
    plt.tight_layout()
    plt.savefig(RESULTS_DIR / filename)
    plt.close()
    print("Saved:", filename)


# --------------------------
# 6. Run full per-state analysis
# --------------------------

def run_analysis():
    climate, corn, wheat = load_data()

    # Climate per state
    climate_state = prepare_climate(climate)
    climate_state.to_csv(RESULTS_DIR / "climate_annual_by_state.csv", index=False)

    # Corn + Wheat per state
    corn_state = prepare_corn(corn)
    wheat_state = prepare_wheat(wheat)

    # Merge
    corn_merge, wheat_merge = merge_state_level(climate_state, corn_state, wheat_state)
    corn_merge.to_csv(RESULTS_DIR / "climate_corn_state_merged.csv", index=False)
    wheat_merge.to_csv(RESULTS_DIR / "climate_wheat_state_merged.csv", index=False)

    print("\nMerged corn data sample:")
    print(corn_merge.head())

    print("\nMerged wheat data sample:")
    print(wheat_merge.head())

    # ------------------------
    # State-level regressions
    # ------------------------
    states = sorted(climate_state["state"].unique())

    for st in states:
        df_c = corn_merge[corn_merge["state"] == st]
        df_w = wheat_merge[wheat_merge["state"] == st]

        # CORN regression
        if len(df_c) >= 3:
            slope, intercept, r2 = run_linear_regression(df_c, "avg_temp", "corn_yield")
            print(f"\nCorn regression ({st}): slope={slope:.3f}, R²={r2:.3f}")
            plot_regression(
                df_c, "avg_temp", "corn_yield",
                slope, intercept,
                f"{st}: Temp vs Corn Yield",
                f"regression_corn_{st}.png"
            )

        # WHEAT regression
        if len(df_w) >= 3:
            slope, intercept, r2 = run_linear_regression(df_w, "avg_temp", "wheat_yield")
            print(f"Wheat regression ({st}): slope={slope:.3f}, R²={r2:.3f}")
            plot_regression(
                df_w, "avg_temp", "wheat_yield",
                slope, intercept,
                f"{st}: Temp vs Wheat Yield",
                f"regression_wheat_{st}.png"
            )

        # Scatterplots
        if len(df_c) > 0:
            plot_scatter(df_c, "avg_temp", "corn_yield",
                         f"{st}: Temp vs Corn Yield",
                         f"scatter_corn_{st}.png")

        if len(df_w) > 0:
            plot_scatter(df_w, "avg_temp", "wheat_yield",
                         f"{st}: Temp vs Wheat Yield",
                         f"scatter_wheat_{st}.png")

    # ------------------------
    # Multi-state comparison
    # ------------------------
    plt.figure(figsize=(10, 6))
    for st in states:
        df = climate_state[climate_state["state"] == st]
        plt.plot(df["year"], df["avg_temp"], marker="o", label=st)
    plt.title("Climate Trend by State (Avg Temp)")
    plt.xlabel("Year")
    plt.ylabel("Avg Temp (°C)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(RESULTS_DIR / "climate_trend_all_states.png")
    plt.close()
    print("Saved: climate_trend_all_states.png")

    # ------------------------
    # Combined correlation heatmap
    # ------------------------
    combined = (
        corn_merge[["year", "state", "avg_temp", "corn_yield"]]
        .merge(
            wheat_merge[["year", "state", "avg_temp", "wheat_yield"]],
            on=["year", "state", "avg_temp"],
            how="inner"
        )
    )

    corr = combined[["avg_temp", "corn_yield", "wheat_yield"]].corr()
    plot_correlation_heatmap(corr, "correlation_heatmap.png")

    print("\nAnalysis complete! Check /results for all outputs.")


if __name__ == "__main__":
    run_analysis()
