"""
01_extract.py
=============
NHS Healthcare Workflow Analytics Pipeline
STEP 1 — DATA EXTRACTION

Downloads real NHS England RTT waiting times data.
Falls back to synthetic NHS-standard data if download fails.

Author: Taiwo Tobi Omoyeni
"""

import os, sys, requests, json
import pandas as pd
import numpy as np
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import RAW_DIR, NHS_RTT_URL, USE_SYNTHETIC_FALLBACK

os.makedirs(RAW_DIR, exist_ok=True)

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def download_nhs_data():
    log("Attempting to download real NHS RTT data...")
    try:
        r = requests.get(NHS_RTT_URL, timeout=30,
                         headers={"User-Agent": "NHSAnalyticsPipeline/1.0"})
        if r.status_code == 200:
            path = os.path.join(RAW_DIR, "nhs_rtt_raw.csv")
            with open(path, "wb") as f:
                f.write(r.content)
            log(f"Download successful — {len(r.content)//1024} KB saved")
            return True
        log(f"HTTP {r.status_code} — using synthetic fallback")
        return False
    except Exception as e:
        log(f"Download failed: {e} — using synthetic fallback")
        return False

def generate_synthetic_nhs_data():
    log("Generating synthetic NHS-standard RTT dataset...")
    np.random.seed(42)

    trusts = [
        "Royal London Hospital", "Manchester University NHS FT",
        "Leeds Teaching Hospitals", "Birmingham and Solihull",
        "Bristol University Hospitals", "Newcastle Upon Tyne Hospitals",
        "Nottingham University Hospitals", "Sheffield Teaching Hospitals",
        "Oxford University Hospitals", "Cambridge University Hospitals",
        "King's College Hospital", "Guy's and St Thomas'",
        "Imperial College Healthcare", "University College London Hospitals",
        "Barts Health NHS Trust",
    ]
    specialties = [
        "Trauma and Orthopaedics", "General Surgery", "Cardiology",
        "Ophthalmology", "Neurology", "Gastroenterology",
        "Urology", "Ear Nose and Throat", "Rheumatology", "Dermatology",
    ]
    months = pd.date_range(start="2023-01-01", periods=12, freq="MS")
    records = []

    for month in months:
        for trust in trusts:
            for specialty in specialties:
                base        = np.random.randint(800, 4500)
                perf        = np.random.uniform(0.78, 0.97)
                within18    = int(base * perf)
                over18      = base - within18
                over52      = int(over18 * np.random.uniform(0.02, 0.15))
                referrals   = int(base * np.random.uniform(0.08, 0.18))
                completed   = int(base * np.random.uniform(0.07, 0.16))
                records.append({
                    "period":              month.strftime("%Y-%m"),
                    "period_date":         str(month.date()),
                    "trust_name":          trust,
                    "specialty":           specialty,
                    "total_waiting":       base,
                    "within_18_weeks":     within18,
                    "over_18_weeks":       over18,
                    "over_52_weeks":       over52,
                    "new_referrals":       referrals,
                    "completed_pathways":  completed,
                    "avg_wait_weeks":      round(np.random.uniform(6, 24), 1),
                    "dna_rate_pct":        round(np.random.uniform(4.5, 18.0), 1),
                    "utilisation_pct":     round(np.random.uniform(72, 96), 1),
                    "cancelled_operations": int(referrals * np.random.uniform(0.03, 0.12)),
                    "pct_within_18wks":    round((within18 / base) * 100, 1),
                    "data_source":         "Synthetic NHS-standard",
                })

    df = pd.DataFrame(records)
    df.to_csv(os.path.join(RAW_DIR, "nhs_rtt_raw.csv"), index=False)
    log(f"Synthetic dataset: {len(df):,} records | {len(trusts)} trusts | 12 months")
    return df

def main():
    log("=" * 55)
    log("STEP 1 — NHS DATA EXTRACTION")
    log("=" * 55)
    if not download_nhs_data():
        if USE_SYNTHETIC_FALLBACK:
            generate_synthetic_nhs_data()
        else:
            log("No data source available. Set USE_SYNTHETIC_FALLBACK=True")
            sys.exit(1)
    log("Step 1 complete — raw/nhs_rtt_raw.csv ready")
    log("=" * 55)

if __name__ == "__main__":
    main()
