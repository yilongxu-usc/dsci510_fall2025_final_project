"""
Per-state analysis script for the Crop Shock project (UPDATED WITH PRECIPITATION).

Now includes:
- Temperature (TAVG)
- Precipitation (PRCP)

Outputs:
- Per-state annual avg temperature
- Per-state annual total precipitation
- Corn & wheat merged with BOTH climate variables
- Regressions: temp→yield, precip→yield
- Scatterplots
- Multi-state temperature & precipitation trend
- Correlation heatmap (now 3×3 or 4×4 depending on variables)
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
# 2. Prepare Climate (Temp + Precip)
# --------------------------

def prepare_climate(climate: pd.DataFrame):
    """
    Expects climate.csv to contain:
        date, state, datatype, value
    Where:
        TAVG = daily avg temperature (°C)
        PRCP = precipitation (mm or tenths mm depending on NOAA)

    Returns per-state annual aggregated climate:
        year, state, avg_temp, total_prcp
    """

    df = climate.copy()
    df["date"] = pd.to_datetime(df["date"])
    df["year"] = df["date"].dt.year
    df["value"] = pd.to_numeric(df["value"], errors="coerce")

    # --- Separate into TAVG and PRCP ---
    temp_df = df[df["datatype"] == "TAVG"]
    prcp_df = df[df["datatype"] == "PRCP"]

    # --- Annual mean temperature ---
    annual_temp = (
        temp_df.groupby(["state", "year"])["value"]
        .mean()
        .reset_index()
        .rename(columns={"value": "avg_temp"})
    )

    # --- Annual total precipitation ---
    annual_prcp = (
        prcp_df.groupby(["state", "year"])["value"]
        .sum()
        .reset_index()
        .rename(columns={"value": "total_prcp"})
    )

    # ---- Merge both ----
    climate_state = annual_temp.merge(
        annual_prcp, on=["state", "year"], how="outer"
    )

    print("\nClimate (per-state) with temp + precip:")
    print(climate_state.head())

    return climate_state


# --------------------------
# 3. USDA Yield Prep
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
# 4. Merge per-state climate & yield
# --------------------------

def merge_state_level(climate_state, corn_state, wheat_state):
    corn_merge = climate_state.merge(corn_state, on=["state", "year"], how="inner")
    wheat_merge = climate_state.merge(wheat_state, on=["state", "year"], how="inner")
    return corn_merge, wheat_merge


# --------------------------
# 5. Plot utilities
# --------------------------

def plot_scatter(df, x, y, title, filename):
    plt.figure()
    plt.scatter(df[x], df[y])
    plt.grid(True)
    plt.title(title)
    plt.xlabel(x)
    plt.ylabel(y)
    plt.tight_layout()
    plt.savefig(RESULTS_DIR / filename)
    plt.close()
    print("Saved:", filename)


def plot_regression(df, x, y, slope, intercept, title, filename):
    xs = df[x].to_numpy()
    xs_sorted = np.sort(xs)
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
    plt.figure(figsize=(7, 6))
    im = plt.imshow(corr_df.values, vmin=-1, vmax=1, cmap="coolwarm")
    plt.colorbar(im)

    ticks = range(len(corr_df.columns))
    plt.xticks(ticks, corr_df.columns, rotation=45)
    plt.yticks(ticks, corr_df.columns)

    # Add numbers
    for i in range(len(corr_df.columns)):
        for j in range(len(corr_df.columns)):
            val = corr_df.values[i, j]
            plt.text(j, i, f"{val:.2f}", ha="center", va="center", fontsize=10)

    plt.title("Correlation Heatmap (Temp, Precip, Corn, Wheat)")
    plt.tight_layout()
    plt.savefig(RESULTS_DIR / filename)
    plt.close()
    print("Saved:", filename)


# --------------------------
# 6. Full analysis
# --------------------------

def run_analysis():
    climate, corn, wheat = load_data()

    # Climate (temp + precip)
    climate_state = prepare_climate(climate)
    climate_state.to_csv(RESULTS_DIR / "climate_state_temp_precip.csv", index=False)

    # Yields
    corn_state = prepare_corn(corn)
    wheat_state = prepare_wheat(wheat)

    corn_merge, wheat_merge = merge_state_level(climate_state, corn_state, wheat_state)

    # Save merged outputs
    corn_merge.to_csv(RESULTS_DIR / "corn_climate_merged.csv", index=False)
    wheat_merge.to_csv(RESULTS_DIR / "wheat_climate_merged.csv", index=False)

    states = sorted(climate_state["state"].unique())

    # ------------------------
    # State-level regressions
    # ------------------------
    for st in states:
        df_c = corn_merge[corn_merge["state"] == st]
        df_w = wheat_merge[wheat_merge["state"] == st]

        # --- CORN: temp & precip regressions ---
        if len(df_c) >= 3:
            slope, intercept, r2 = run_linear_regression(df_c, "avg_temp", "corn_yield")
            plot_regression(df_c, "avg_temp", "corn_yield", slope, intercept,
                            f"{st}: Temp vs Corn Yield",
                            f"reg_temp_corn_{st}.png")

            slope, intercept, r2 = run_linear_regression(df_c, "total_prcp", "corn_yield")
            plot_regression(df_c, "total_prcp", "corn_yield", slope, intercept,
                            f"{st}: Precip vs Corn Yield",
                            f"reg_prcp_corn_{st}.png")

        # --- WHEAT: temp & precip regressions ---
        if len(df_w) >= 3:
            slope, intercept, r2 = run_linear_regression(df_w, "avg_temp", "wheat_yield")
            plot_regression(df_w, "avg_temp", "wheat_yield", slope, intercept,
                            f"{st}: Temp vs Wheat Yield",
                            f"reg_temp_wheat_{st}.png")

            slope, intercept, r2 = run_linear_regression(df_w, "total_prcp", "wheat_yield")
            plot_regression(df_w, "total_prcp", "wheat_yield", slope, intercept,
                            f"{st}: Precip vs Wheat Yield",
                            f"reg_prcp_wheat_{st}.png")

        # Scatter plots
        if len(df_c) > 0:
            plot_scatter(df_c, "avg_temp", "corn_yield",
                         f"{st}: Temp vs Corn Yield",
                         f"scatter_temp_corn_{st}.png")
            plot_scatter(df_c, "total_prcp", "corn_yield",
                         f"{st}: Precip vs Corn Yield",
                         f"scatter_prcp_corn_{st}.png")

        if len(df_w) > 0:
            plot_scatter(df_w, "avg_temp", "wheat_yield",
                         f"{st}: Temp vs Wheat Yield",
                         f"scatter_temp_wheat_{st}.png")
            plot_scatter(df_w, "total_prcp", "wheat_yield",
                         f"{st}: Precip vs Wheat Yield",
                         f"scatter_prcp_wheat_{st}.png")

    # ------------------------
    # Multi-state trends
    # ------------------------
    plt.figure(figsize=(10, 6))
    for st in states:
        df = climate_state[climate_state["state"] == st]
        plt.plot(df["year"], df["avg_temp"], marker="o", label=st)
    plt.title("Avg Temperature Trend by State")
    plt.xlabel("Year")
    plt.ylabel("Temperature (°C)")
    plt.legend()
    plt.grid(True)
    plt.savefig(RESULTS_DIR / "trend_temperature_states.png")
    plt.close()

    plt.figure(figsize=(10, 6))
    for st in states:
        df = climate_state[climate_state["state"] == st]
        plt.plot(df["year"], df["total_prcp"], marker="o", label=st)
    plt.title("Total Precipitation Trend by State")
    plt.xlabel("Year")
    plt.ylabel("Total Precipitation")
    plt.legend()
    plt.grid(True)
    plt.savefig(RESULTS_DIR / "trend_precip_states.png")
    plt.close()

    # ------------------------
    # Correlation heatmap
    # ------------------------
    combined = (
        corn_merge[["year", "state", "avg_temp", "total_prcp", "corn_yield"]]
        .merge(
            wheat_merge[["year", "state", "avg_temp", "total_prcp", "wheat_yield"]],
            on=["year", "state", "avg_temp", "total_prcp"],
            how="inner"
        )
    )

    corr = combined[["avg_temp", "total_prcp", "corn_yield", "wheat_yield"]].corr()
    plot_correlation_heatmap(corr, "correlation_heatmap_temp_precip.png")

    print("\nAnalysis complete — temperature + precipitation added successfully.")


if __name__ == "__main__":
    run_analysis()
