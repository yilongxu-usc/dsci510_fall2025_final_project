from pathlib import Path
from dotenv import load_dotenv
import os

# ----------------------------------------------
# Project configuration from .env (secret part)
# ----------------------------------------------
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path) # loads into os.environ

# ----------------------------------------------
# API keys
# ----------------------------------------------
USDA_API_KEY = os.getenv("USDA_API_KEY")
NOAA_TOKEN = os.getenv("NOAA_TOKEN")

# ----------------------------------------------
# Project configuration
# ----------------------------------------------
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
RESULTS_DIR = Path(__file__).resolve().parent.parent / "results"
DATA_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# ----------------------------------------------
# # API endpoints
# ----------------------------------------------
USDA_ENDPOINT = "https://quickstats.nass.usda.gov/api/api_GET/"
NOAA_ENDPOINT = "https://www.ncei.noaa.gov/cdo-web/api/v2/data"