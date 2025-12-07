# dsc510_fall2025_final_project

## Introduction

This project investigates how long-term **climate change** relates to **U.S. agricultural production**, with a focus on **corn and wheat yields** across selected U.S. states from **1970 to 2024**. Specifically, the project examines how **temperature and precipitation patterns** vary over time and whether these climate variables are associated with changes in crop yields.

By integrating crop yield data from the **USDA National Agricultural Statistics Service (NASS)** with climate data from **NOAA Climate Data Online (CDO)**, this project aims to explore climate–yield relationships at the **state level** using exploratory data analysis, correlation analysis, and regression techniques.

---

## Data Sources

| Dataset                                    | Provider        | Description                                                                                                                                 | Temporal Range | Access Method    |
| ------------------------------------------ | --------------- | ------------------------------------------------------------------------------------------------------------------------------------------- | -------------- | ---------------- |
| Corn Yield Data                            | USDA NASS       | Annual state-level corn yield (bushels per acre)                                                                                            | 1970–2024      | API (JSON → CSV) |
| Wheat Yield Data                           | USDA NASS       | Annual state-level wheat yield (bushels per acre)                                                                                           | 1970–2024      | API (JSON → CSV) |
| Climate Data (Temperature & Precipitation) | NOAA CDO (GSOM) | Monthly average temperature (TAVG) and total precipitation (PRCP), aggregated to annual values and matched by state-representative stations | 1970–2024      | API (JSON → CSV) |

All datasets are collected programmatically using Python.

---

## Analysis

The analysis consists of several components:

* **Climate Trend Analysis**: Examination of long-term temperature and precipitation trends across states from 1970 to 2024.
* **Yield Trend Analysis**: Exploration of changes in corn and wheat yields over time at the state level.
* **Climate–Yield Relationships**: State-level scatterplots and linear regressions analyzing:

  * Average temperature vs. crop yield
  * Total precipitation vs. crop yield
* **Correlation Analysis**: A correlation heatmap comparing temperature, precipitation, corn yield, and wheat yield to assess the relative strength of their relationships.

---

## Summary of the Results

* All analyzed states exhibit **long-term warming trends**, although the magnitude varies regionally.
* Precipitation displays **strong year-to-year variability**, with weaker long-term signals compared to temperature.
* Corn and wheat yields are **strongly positively correlated** with each other.
* Temperature and precipitation show **weak linear correlations** with crop yields at the annual, state-level scale, suggesting that yield outcomes are influenced by additional factors beyond simple climate averages.

*(This section can be updated or expanded as the project evolves.)*

---

## How to Run

### 1. Environment Setup

Create a `.env` file in the project root directory containing your API keys:

```
USDA_API_KEY=your_usda_api_key_here
NOAA_TOKEN=your_noaa_api_token_here
```


### 2. Install Dependencies

Install required Python packages using:

```bash
pip install -r requirements.txt
```

### 3. Run the Pipeline

From the project root directory, run:

```bash
python src/main.py
```

This single command will:

* Fetch USDA corn and wheat yield data via API
* Fetch NOAA temperature and precipitation data (1970–2024) using chunked requests
* Process and merge datasets at the state–year level
* Run all analyses and generate visualizations

All downloaded data are saved to the `data/` directory, and all analysis outputs and figures are saved to the `results/` directory.


---

**Author:** Yilong Xu
**Course:** DSCI 510 – Fall 2025
