# dsci510_fall2025_final_project

This project explores the relationship between climate change and U.S. agricultural production, focusing on how temperature trends influence yearly corn and wheat yield across U.S. states. The analysis uses USDA crop yield data and NOAA climate data to build a dataset that will later be used for correlation and statistical exploration.

# Data sources
1. USDA National Agricultural Statistics Service (NASS)
API: https://quickstats.nass.usda.gov/api
Provides annual crop yield by state
Variables used:
Sector: CROPS
Group: FIELD CROPS
Commodity: CORN / WHEAT
Statistic: YIELD (bushels per acre)
Data range: 2010–2024

2. NOAA Climate Data Online (CDO)
API: https://www.ncei.noaa.gov/cdo-web/api/v2
Provides monthly average temperature (TAVG)
Dataset: GSOM (Global Summary of the Month)
Station used in early testing:
GHCND:USW00023174 (LAX Airport)
Data range: 2010–2024

Both datasets are obtained through API.

# Results 
TRight now it does not include statistical analysis yet.
At this stage, the project successfully:
Retrieves corn and wheat yield data across all states from USDA,
Retrieves monthly temperature data from NOAA via GSOM,
Saves all data into the /data/ directory for later analysis.
Further analysis (correlation, trends, modeling) will be completed in the final project submission.

# Installation
Create a .env file in this format
USDA_API_KEY=your_usda_api_key_here
NOAA_TOKEN=your_noaa_api_token_here

pandas
requests
python-dotenvgit needs be installed for this project

# Running analysis 
To run the data retrieval and save output data:

From `src/` directory run:

`python main.py `

All obtained data will be stored in `data/` as csv files
Output of further analysis will be stored in `results/`