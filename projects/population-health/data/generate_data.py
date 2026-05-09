"""
generate_data.py
================
Generates a synthetic EHR-style population health dataset for
readmission risk analysis. Produces realistic distributions across
demographics, diagnoses (ICD-10), and social determinants of health.

Author: Taiwo Tobi Omoyeni
Project: Population Health Readmission Risk Intelligence
"""

import pandas as pd
import numpy as np
import json
import os

np.random.seed(42)
N = 2000  # patient records

# ── Demographics ─────────────────────────────────────────────────────────────
ages = np.random.normal(62, 15, N).clip(18, 95).astype(int)
sexes = np.random.choice(["Male", "Female"], N, p=[0.48, 0.52])
races = np.random.choice(
    ["Black/African American", "White", "Hispanic/Latino", "Asian", "Other"],
    N, p=[0.28, 0.38, 0.20, 0.09, 0.05]
)
insurance = np.random.choice(
    ["Medicaid", "Medicare", "Private", "Uninsured"],
    N, p=[0.30, 0.35, 0.25, 0.10]
)
zip_codes = np.random.choice(
    ["10001", "10002", "10003", "10004", "10005",
     "10006", "10007", "10008", "10009", "10010"],
    N
)

# Social Determinants of Health (SDOH)
sdoh_food_insecurity = np.random.choice([0, 1], N, p=[0.65, 0.35])
sdoh_housing_instability = np.random.choice([0, 1], N, p=[0.72, 0.28])
sdoh_transport_barrier = np.random.choice([0, 1], N, p=[0.70, 0.30])
sdoh_low_health_literacy = np.random.choice([0, 1], N, p=[0.60, 0.40])

# ── Clinical Data ─────────────────────────────────────────────────────────────
primary_diagnoses = np.random.choice(
    ["I50 - Heart Failure", "I21 - Acute MI", "J18 - Pneumonia",
     "E11 - Type 2 Diabetes", "N18 - CKD", "I63 - Stroke",
     "J44 - COPD", "K92 - GI Bleeding"],
    N, p=[0.20, 0.12, 0.13, 0.18, 0.10, 0.10, 0.09, 0.08]
)

los = np.random.poisson(5, N).clip(1, 30)  # Length of stay (days)
prior_admissions_12m = np.random.poisson(1.2, N).clip(0, 8)
num_comorbidities = np.random.poisson(2.5, N).clip(0, 8)
discharge_disposition = np.random.choice(
    ["Home", "Home with Services", "SNF", "Rehab", "AMA"],
    N, p=[0.40, 0.28, 0.18, 0.10, 0.04]
)
medication_counselling = np.random.choice([0, 1], N, p=[0.38, 0.62])
followup_scheduled = np.random.choice([0, 1], N, p=[0.25, 0.75])
discharge_instructions_clear = np.random.choice([0, 1], N, p=[0.20, 0.80])

# ── Readmission Risk Score (logistic-style) ───────────────────────────────────
log_odds = (
    -3.5
    + 0.04 * (ages - 60)
    + 0.6 * (races == "Black/African American").astype(float)
    + 0.5 * (insurance == "Medicaid").astype(float)
    + 0.7 * (insurance == "Uninsured").astype(float)
    + 0.4 * sdoh_food_insecurity
    + 0.5 * sdoh_housing_instability
    + 0.3 * sdoh_transport_barrier
    + 0.4 * sdoh_low_health_literacy
    + 0.15 * los
    + 0.5 * prior_admissions_12m
    + 0.3 * num_comorbidities
    - 0.7 * medication_counselling
    - 0.5 * followup_scheduled
    - 0.3 * discharge_instructions_clear
    + 0.4 * (discharge_disposition == "AMA").astype(float)
    + np.random.normal(0, 0.5, N)
)
prob_readmit = 1 / (1 + np.exp(-log_odds))
readmitted_30d = (np.random.uniform(0, 1, N) < prob_readmit).astype(int)

# Risk tier classification
def risk_tier(p):
    if p < 0.15:   return "Low"
    elif p < 0.30: return "Moderate"
    elif p < 0.50: return "High"
    else:          return "Critical"

risk_tiers = [risk_tier(p) for p in prob_readmit]

# ── Assemble DataFrame ────────────────────────────────────────────────────────
df = pd.DataFrame({
    "patient_id":                [f"PT{str(i).zfill(5)}" for i in range(1, N+1)],
    "age":                       ages,
    "sex":                       sexes,
    "race_ethnicity":            races,
    "insurance_type":            insurance,
    "zip_code":                  zip_codes,
    "primary_diagnosis_icd10":   primary_diagnoses,
    "length_of_stay_days":       los,
    "prior_admissions_12m":      prior_admissions_12m,
    "num_comorbidities":         num_comorbidities,
    "discharge_disposition":     discharge_disposition,
    "medication_counselling_done": medication_counselling,
    "followup_scheduled":        followup_scheduled,
    "discharge_instructions_clear": discharge_instructions_clear,
    "sdoh_food_insecurity":      sdoh_food_insecurity,
    "sdoh_housing_instability":  sdoh_housing_instability,
    "sdoh_transport_barrier":    sdoh_transport_barrier,
    "sdoh_low_health_literacy":  sdoh_low_health_literacy,
    "readmission_risk_score":    prob_readmit.round(4),
    "risk_tier":                 risk_tiers,
    "readmitted_30d":            readmitted_30d,
})

# Save
os.makedirs(".", exist_ok=True)
df.to_csv("population_health_data.csv", index=False)
print(f"✓ Generated {N} patient records → population_health_data.csv")
print(f"  Overall 30-day readmission rate: {readmitted_30d.mean():.1%}")
print(f"  Risk tier distribution:\n{df['risk_tier'].value_counts()}")
