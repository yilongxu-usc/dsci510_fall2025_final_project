# dsc510_fall2025_final_project

**Climate–Yield Analysis of U.S. Corn and Wheat (1970–2024)**

This project analyzes how **temperature and precipitation trends relate to corn and wheat yields** across selected U.S. states from **1970 to 2024**. It integrates **USDA crop yield data** with **NOAA climate records** and performs trend analysis, regressions, and correlation analysis at the **state level**.

---

## Key Questions
- How do temperature and precipitation relate to corn and wheat yields?
- Do climate–yield relationships differ by state?
- Which climate variable appears more influential on crop yield?

---

## Data Sources
- **USDA NASS API** – Annual corn & wheat yields (bushels/acre) by state (1970–2024)
- **NOAA CDO API (GSOM)** – Monthly average temperature (TAVG) and total precipitation (PRCP), aggregated to annual values

All data are retrieved programmatically via API.

---

## How to Run

This project is fully automated. From the project root:

```bash
python src/main.py
```

This single command will:
- Download USDA and NOAA data
- Process and merge datasets
- Run all analyses
- Generate plots and outputs

Results are saved to the `results/` directory.

---

## Highlights
- Long-term warming trends observed across all states
- Precipitation shows strong year-to-year variability
- Corn and wheat yields are strongly correlated with each other
- Climate variables alone show weak linear relationships with yield, suggesting more complex drivers

---

**Author:** Yilong Xu (USC)  
**Course:** DSCI 510 – Fall 2025