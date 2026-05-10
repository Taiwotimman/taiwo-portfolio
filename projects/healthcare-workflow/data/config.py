# config.py — SETTINGS FILE
# ⚠️ Listed in .gitignore — NEVER upload to GitHub
import os

EMAIL_SENDER      = "your.gmail@gmail.com"
EMAIL_PASSWORD    = "xxxx xxxx xxxx xxxx"   # Gmail App Password
EMAIL_RECIPIENTS  = ["your.email@gmail.com"]

DASHBOARD_URL    = "https://Taiwotimman.github.io/taiwo-portfolio/projects/healthcare-workflow/dashboard/index.html"
REPORT_TITLE     = "NHS Operational Performance Report"
ORGANISATION     = "NHS England — Referral to Treatment Analytics"
AUTHOR           = "Taiwo Tobi Omoyeni"
AUTHOR_ROLE      = "Health Data Analyst & Population Health Informaticist"
AUTHOR_EMAIL     = "Taiwotobiomoyeni@gmail.com"
AUTHOR_LINKEDIN  = "https://www.linkedin.com/in/taiwo-omoyeni-830a07a7"

BASE_DIR      = os.path.dirname(os.path.abspath(__file__))
RAW_DIR       = os.path.join(BASE_DIR, "raw")
PROCESSED_DIR = os.path.join(BASE_DIR, "processed")
OUTPUTS_DIR   = os.path.join(BASE_DIR, "outputs")

NHS_RTT_URL             = "https://www.england.nhs.uk/statistics/wp-content/uploads/sites/2/2024/02/RTT-overview-timeseries-Sep23-Oct23.csv"
USE_SYNTHETIC_FALLBACK  = True

RTT_18_WEEK_TARGET    = 92.0
MAX_WAIT_WEEKS        = 52
DNA_RATE_THRESHOLD    = 10.0
UTILISATION_TARGET    = 85.0
