"""
02_clean.py
===========
NHS Healthcare Workflow Analytics Pipeline
STEP 2 — DATA CLEANING & STANDARDISATION

Cleans the raw NHS RTT dataset:
- Removes blank rows and duplicates
- Standardises column names and data types
- Validates NHS targets compliance
- Flags data quality issues
- Saves clean dataset to processed/

Author: Taiwo Tobi Omoyeni
"""

import os, sys, json
import pandas as pd
import numpy as np
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import RAW_DIR, PROCESSED_DIR, RTT_18_WEEK_TARGET, MAX_WAIT_WEEKS

os.makedirs(PROCESSED_DIR, exist_ok=True)

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def clean_data():
    log("=" * 55)
    log("STEP 2 — DATA CLEANING & STANDARDISATION")
    log("=" * 55)

    # ── Load raw data ─────────────────────────────────────────
    raw_path = os.path.join(RAW_DIR, "nhs_rtt_raw.csv")
    if not os.path.exists(raw_path):
        log("ERROR: raw/nhs_rtt_raw.csv not found. Run 01_extract.py first.")
        sys.exit(1)

    df = pd.read_csv(raw_path)
    original_count = len(df)
    log(f"Loaded {original_count:,} raw records")

    # ── Step 1: Remove completely blank rows ──────────────────
    df.dropna(how="all", inplace=True)
    log(f"After blank row removal: {len(df):,} records")

    # ── Step 2: Remove duplicates ─────────────────────────────
    before = len(df)
    df.drop_duplicates(subset=["period", "trust_name", "specialty"], inplace=True)
    removed = before - len(df)
    log(f"Duplicates removed: {removed} | Records remaining: {len(df):,}")

    # ── Step 3: Standardise column names ─────────────────────
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    # ── Step 4: Fix data types ────────────────────────────────
    numeric_cols = [
        "total_waiting", "within_18_weeks", "over_18_weeks",
        "over_52_weeks", "new_referrals", "completed_pathways",
        "avg_wait_weeks", "dna_rate_pct", "utilisation_pct",
        "cancelled_operations", "pct_within_18wks"
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # ── Step 5: Fill missing numeric values with column median
    missing_before = df[numeric_cols].isnull().sum().sum()
    for col in numeric_cols:
        if col in df.columns:
            df[col].fillna(df[col].median(), inplace=True)
    log(f"Missing values filled: {missing_before}")

    # ── Step 6: Add NHS compliance flags ─────────────────────
    df["meets_18wk_target"]   = df["pct_within_18wks"] >= RTT_18_WEEK_TARGET
    df["has_52wk_waiters"]    = df["over_52_weeks"] > 0
    df["high_dna_alert"]      = df["dna_rate_pct"] > 10.0
    df["low_utilisation"]     = df["utilisation_pct"] < 75.0
    df["performance_band"]    = pd.cut(
        df["pct_within_18wks"],
        bins=[0, 80, 88, 92, 100],
        labels=["Critical", "At Risk", "Near Target", "On Target"]
    )

    # ── Step 7: Add derived metrics ──────────────────────────
    df["backlog_ratio"]    = (df["over_18_weeks"] / df["total_waiting"].replace(0, np.nan)).round(4)
    df["throughput_ratio"] = (df["completed_pathways"] / df["new_referrals"].replace(0, np.nan)).round(4)

    # ── Step 8: Data quality report ──────────────────────────
    quality = {
        "original_records":   original_count,
        "clean_records":      len(df),
        "duplicates_removed": removed,
        "missing_filled":     int(missing_before),
        "trusts":             int(df["trust_name"].nunique()),
        "specialties":        int(df["specialty"].nunique()),
        "months":             int(df["period"].nunique()),
        "pct_meeting_target": round(df["meets_18wk_target"].mean() * 100, 1),
        "trusts_with_52wk":   int(df.groupby("trust_name")["has_52wk_waiters"].any().sum()),
    }

    # ── Save outputs ──────────────────────────────────────────
    clean_path   = os.path.join(PROCESSED_DIR, "nhs_rtt_clean.csv")
    quality_path = os.path.join(PROCESSED_DIR, "data_quality_report.json")
    df.to_csv(clean_path, index=False)
    with open(quality_path, "w") as f:
        json.dump(quality, f, indent=2)

    log(f"Clean data saved  : processed/nhs_rtt_clean.csv")
    log(f"Quality report    : processed/data_quality_report.json")
    log(f"Records meeting 18-week target: {quality['pct_meeting_target']}%")
    log(f"Trusts with 52-week waiters   : {quality['trusts_with_52wk']}")
    log("Step 2 complete")
    log("=" * 55)
    return df

if __name__ == "__main__":
    clean_data()
