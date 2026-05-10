"""
03_calculate_kpis.py
====================
NHS Healthcare Workflow Analytics Pipeline
STEP 3 — KPI CALCULATION

Calculates all NHS performance KPIs from the clean dataset
and saves them to JSON files that feed the dashboard.

KPI Categories:
  - Access & Waiting Times
  - Operational Efficiency
  - Trust Performance Rankings
  - Monthly Trends
  - Specialty Analysis
  - Alert Flags

Author: Taiwo Tobi Omoyeni
"""

import os, sys, json
import pandas as pd
import numpy as np
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import PROCESSED_DIR, OUTPUTS_DIR, RTT_18_WEEK_TARGET

os.makedirs(OUTPUTS_DIR, exist_ok=True)

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def safe_json(obj):
    """Convert numpy types to Python native for JSON serialisation."""
    if isinstance(obj, (np.integer,)):  return int(obj)
    if isinstance(obj, (np.floating,)): return float(obj)
    if isinstance(obj, (np.ndarray,)):  return obj.tolist()
    if isinstance(obj, pd.Timestamp):   return str(obj)
    return obj

def calculate_kpis():
    log("=" * 55)
    log("STEP 3 — KPI CALCULATION")
    log("=" * 55)

    clean_path = os.path.join(PROCESSED_DIR, "nhs_rtt_clean.csv")
    if not os.path.exists(clean_path):
        log("ERROR: Run 02_clean.py first.")
        sys.exit(1)

    df = pd.read_csv(clean_path)
    log(f"Loaded {len(df):,} clean records")

    # ── Latest month snapshot ─────────────────────────────────
    latest_month  = df["period"].max()
    df_latest     = df[df["period"] == latest_month]
    df_prev       = df[df["period"] == sorted(df["period"].unique())[-2]] if len(df["period"].unique()) > 1 else df_latest

    # ── OVERVIEW KPIs ─────────────────────────────────────────
    overview = {
        "report_month":          latest_month,
        "total_waiting":         int(df_latest["total_waiting"].sum()),
        "over_18_weeks":         int(df_latest["over_18_weeks"].sum()),
        "over_52_weeks":         int(df_latest["over_52_weeks"].sum()),
        "new_referrals":         int(df_latest["new_referrals"].sum()),
        "completed_pathways":    int(df_latest["completed_pathways"].sum()),
        "pct_within_18wks":      round(float(df_latest["pct_within_18wks"].mean()), 1),
        "avg_wait_weeks":        round(float(df_latest["avg_wait_weeks"].mean()), 1),
        "avg_dna_rate":          round(float(df_latest["dna_rate_pct"].mean()), 1),
        "avg_utilisation":       round(float(df_latest["utilisation_pct"].mean()), 1),
        "cancelled_operations":  int(df_latest["cancelled_operations"].sum()),
        "total_trusts":          int(df_latest["trust_name"].nunique()),
        "trusts_meeting_target": int(df_latest.groupby("trust_name")["pct_within_18wks"].mean().ge(RTT_18_WEEK_TARGET).sum()),
        "target_18wks":          RTT_18_WEEK_TARGET,
    }

    # Month-on-month change
    prev_pct = df_prev["pct_within_18wks"].mean()
    curr_pct = df_latest["pct_within_18wks"].mean()
    overview["mom_change_pp"] = round(float(curr_pct - prev_pct), 1)
    overview["mom_direction"] = "improving" if curr_pct >= prev_pct else "worsening"

    # ── TRUST PERFORMANCE TABLE ───────────────────────────────
    trust_perf = (
        df_latest.groupby("trust_name").agg(
            total_waiting    = ("total_waiting",    "sum"),
            over_18_weeks    = ("over_18_weeks",    "sum"),
            over_52_weeks    = ("over_52_weeks",    "sum"),
            pct_within_18wks = ("pct_within_18wks", "mean"),
            avg_wait_weeks   = ("avg_wait_weeks",   "mean"),
            dna_rate_pct     = ("dna_rate_pct",     "mean"),
            utilisation_pct  = ("utilisation_pct",  "mean"),
            new_referrals    = ("new_referrals",     "sum"),
        ).reset_index()
    )
    trust_perf["pct_within_18wks"] = trust_perf["pct_within_18wks"].round(1)
    trust_perf["avg_wait_weeks"]   = trust_perf["avg_wait_weeks"].round(1)
    trust_perf["dna_rate_pct"]     = trust_perf["dna_rate_pct"].round(1)
    trust_perf["utilisation_pct"]  = trust_perf["utilisation_pct"].round(1)
    trust_perf["meets_target"]     = trust_perf["pct_within_18wks"] >= RTT_18_WEEK_TARGET
    trust_perf = trust_perf.sort_values("pct_within_18wks", ascending=False)

    # ── MONTHLY TREND ─────────────────────────────────────────
    monthly = (
        df.groupby("period").agg(
            total_waiting    = ("total_waiting",    "sum"),
            over_18_weeks    = ("over_18_weeks",    "sum"),
            new_referrals    = ("new_referrals",     "sum"),
            completed        = ("completed_pathways","sum"),
            pct_within_18wks = ("pct_within_18wks", "mean"),
            avg_wait_weeks   = ("avg_wait_weeks",   "mean"),
            dna_rate_pct     = ("dna_rate_pct",     "mean"),
            utilisation_pct  = ("utilisation_pct",  "mean"),
        ).reset_index().sort_values("period")
    )
    monthly["pct_within_18wks"] = monthly["pct_within_18wks"].round(1)
    monthly["avg_wait_weeks"]   = monthly["avg_wait_weeks"].round(1)
    monthly["dna_rate_pct"]     = monthly["dna_rate_pct"].round(1)
    monthly["utilisation_pct"]  = monthly["utilisation_pct"].round(1)

    # ── SPECIALTY ANALYSIS ────────────────────────────────────
    specialty = (
        df_latest.groupby("specialty").agg(
            total_waiting    = ("total_waiting",    "sum"),
            over_18_weeks    = ("over_18_weeks",    "sum"),
            pct_within_18wks = ("pct_within_18wks", "mean"),
            avg_wait_weeks   = ("avg_wait_weeks",   "mean"),
        ).reset_index().sort_values("pct_within_18wks")
    )
    specialty["pct_within_18wks"] = specialty["pct_within_18wks"].round(1)
    specialty["avg_wait_weeks"]   = specialty["avg_wait_weeks"].round(1)

    # ── ALERT FLAGS ───────────────────────────────────────────
    alerts = []
    breaching = trust_perf[~trust_perf["meets_target"]]
    if len(breaching) > 0:
        alerts.append({
            "level":   "RED",
            "message": f"{len(breaching)} trust(s) breaching 18-week RTT target",
            "detail":  ", ".join(breaching["trust_name"].head(3).tolist()),
        })
    if overview["over_52_weeks"] > 0:
        alerts.append({
            "level":   "RED",
            "message": f"{overview['over_52_weeks']:,} patients waiting over 52 weeks",
            "detail":  "Immediate escalation required per NHS Constitution",
        })
    if overview["avg_dna_rate"] > 10:
        alerts.append({
            "level":   "AMBER",
            "message": f"Average DNA rate {overview['avg_dna_rate']}% — above 10% threshold",
            "detail":  "Review appointment reminder processes",
        })
    if overview["avg_utilisation"] < 80:
        alerts.append({
            "level":   "AMBER",
            "message": f"Average utilisation {overview['avg_utilisation']}% — below 80% target",
            "detail":  "Capacity may be underused across trusts",
        })
    if overview["mom_direction"] == "worsening":
        alerts.append({
            "level":   "AMBER",
            "message": f"RTT performance declined {abs(overview['mom_change_pp'])}pp vs previous month",
            "detail":  "Monitor trend over next 4 weeks",
        })

    overview["alert_count"] = len(alerts)
    overview["red_alerts"]  = sum(1 for a in alerts if a["level"] == "RED")

    # ── Save all KPI files ────────────────────────────────────
    files = {
        "overview_kpis.json":    overview,
        "trust_performance.json": trust_perf.to_dict(orient="records"),
        "monthly_trend.json":    monthly.to_dict(orient="records"),
        "specialty_analysis.json": specialty.to_dict(orient="records"),
        "alerts.json":           alerts,
    }

    for filename, data in files.items():
        path = os.path.join(OUTPUTS_DIR, filename)
        with open(path, "w") as f:
            json.dump(data, f, indent=2, default=safe_json)
        log(f"Saved: outputs/{filename}")

    log(f"\nKPI Summary for {latest_month}:")
    log(f"  Total waiting        : {overview['total_waiting']:,}")
    log(f"  RTT 18-week %        : {overview['pct_within_18wks']}% (target: {RTT_18_WEEK_TARGET}%)")
    log(f"  Over 52 weeks        : {overview['over_52_weeks']:,}")
    log(f"  Trusts meeting target: {overview['trusts_meeting_target']} / {overview['total_trusts']}")
    log(f"  Active alerts        : {len(alerts)}")
    log("Step 3 complete")
    log("=" * 55)

if __name__ == "__main__":
    calculate_kpis()
