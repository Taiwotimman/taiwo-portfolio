"""
analysis.py
===========
Population-level readmission risk analysis using logistic regression,
equity stratification, and SDOH impact quantification.

Outputs:
  - model_results.json   → logistic regression coefficients + metrics
  - equity_report.json   → disparities by race, insurance, SDOH
  - summary_stats.json   → dashboard KPI data

Author: Taiwo Tobi Omoyeni
"""

import pandas as pd
import numpy as np
import json
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (roc_auc_score, classification_report,
                              confusion_matrix, brier_score_loss)
import warnings
warnings.filterwarnings("ignore")

# ── Load Data ─────────────────────────────────────────────────────────────────
df = pd.read_csv("population_health_data.csv")
print(f"Loaded {len(df)} records  |  Readmission rate: {df['readmitted_30d'].mean():.1%}\n")

# ── Feature Engineering ───────────────────────────────────────────────────────
df["age_group"] = pd.cut(df["age"],
    bins=[17, 44, 64, 74, 95],
    labels=["18-44", "45-64", "65-74", "75+"])

df["sdoh_burden"] = (df["sdoh_food_insecurity"] + df["sdoh_housing_instability"] +
                     df["sdoh_transport_barrier"] + df["sdoh_low_health_literacy"])

df["discharge_risk"] = (
    (df["discharge_disposition"] == "AMA").astype(int) * 2 +
    (1 - df["followup_scheduled"]) +
    (1 - df["medication_counselling_done"])
)

# ── Prepare Model Features ────────────────────────────────────────────────────
features = [
    "age", "length_of_stay_days", "prior_admissions_12m", "num_comorbidities",
    "medication_counselling_done", "followup_scheduled", "discharge_instructions_clear",
    "sdoh_food_insecurity", "sdoh_housing_instability", "sdoh_transport_barrier",
    "sdoh_low_health_literacy", "sdoh_burden", "discharge_risk"
]

# Encode categoricals
df_model = df.copy()
df_model["sex_male"] = (df["sex"] == "Male").astype(int)
df_model["medicaid"] = (df["insurance_type"] == "Medicaid").astype(int)
df_model["uninsured"] = (df["insurance_type"] == "Uninsured").astype(int)
df_model["black"] = (df["race_ethnicity"] == "Black/African American").astype(int)
df_model["hispanic"] = (df["race_ethnicity"] == "Hispanic/Latino").astype(int)

all_features = features + ["sex_male", "medicaid", "uninsured", "black", "hispanic"]

X = df_model[all_features]
y = df_model["readmitted_30d"]

# ── Train/Test Split + Scaling ────────────────────────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
scaler = StandardScaler()
X_train_s = scaler.fit_transform(X_train)
X_test_s  = scaler.transform(X_test)

# ── Logistic Regression Model ─────────────────────────────────────────────────
model = LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42)
model.fit(X_train_s, y_train)

y_pred      = model.predict(X_test_s)
y_prob      = model.predict_proba(X_test_s)[:, 1]
auc         = roc_auc_score(y_test, y_prob)
brier       = brier_score_loss(y_test, y_prob)
cv_scores   = cross_val_score(model, scaler.transform(X), y, cv=5, scoring="roc_auc")
report      = classification_report(y_test, y_pred, output_dict=True)
cm          = confusion_matrix(y_test, y_pred).tolist()

# Feature importances (odds ratios from coefficients)
coef_df = pd.DataFrame({
    "feature": all_features,
    "coefficient": model.coef_[0],
    "odds_ratio": np.exp(model.coef_[0])
}).sort_values("odds_ratio", ascending=False)

print("── Model Performance ─────────────────────────────────────────────────")
print(f"  ROC-AUC:        {auc:.3f}")
print(f"  CV AUC (5-fold): {cv_scores.mean():.3f} ± {cv_scores.std():.3f}")
print(f"  Brier Score:    {brier:.3f}")
print(f"  Sensitivity:    {report['1']['recall']:.3f}")
print(f"  Specificity:    {report['0']['recall']:.3f}")

# ── Equity Analysis ───────────────────────────────────────────────────────────
print("\n── Health Equity Analysis ────────────────────────────────────────────")

equity = {}

# By race/ethnicity
race_eq = df.groupby("race_ethnicity")["readmitted_30d"].agg(["mean", "count"])
race_eq.columns = ["readmission_rate", "n"]
race_eq["readmission_rate"] = race_eq["readmission_rate"].round(4)
equity["by_race"] = race_eq.reset_index().to_dict(orient="records")
print("\nReadmission rate by race:")
print(race_eq.sort_values("readmission_rate", ascending=False))

# By insurance
ins_eq = df.groupby("insurance_type")["readmitted_30d"].agg(["mean", "count"])
ins_eq.columns = ["readmission_rate", "n"]
ins_eq["readmission_rate"] = ins_eq["readmission_rate"].round(4)
equity["by_insurance"] = ins_eq.reset_index().to_dict(orient="records")
print("\nReadmission rate by insurance:")
print(ins_eq.sort_values("readmission_rate", ascending=False))

# By SDOH burden
sdoh_eq = df.groupby("sdoh_burden")["readmitted_30d"].agg(["mean", "count"])
sdoh_eq.columns = ["readmission_rate", "n"]
sdoh_eq["readmission_rate"] = sdoh_eq["readmission_rate"].round(4)
equity["by_sdoh_burden"] = sdoh_eq.reset_index().to_dict(orient="records")
print("\nReadmission rate by SDOH burden score:")
print(sdoh_eq)

# By age group
age_eq = df.groupby("age_group", observed=True)["readmitted_30d"].agg(["mean", "count"])
age_eq.columns = ["readmission_rate", "n"]
equity["by_age_group"] = age_eq.reset_index().to_dict(orient="records")

# By diagnosis
dx_eq = df.groupby("primary_diagnosis_icd10")["readmitted_30d"].agg(["mean", "count"])
dx_eq.columns = ["readmission_rate", "n"]
dx_eq["readmission_rate"] = dx_eq["readmission_rate"].round(4)
equity["by_diagnosis"] = dx_eq.sort_values("readmission_rate", ascending=False).reset_index().to_dict(orient="records")

# Medication counselling impact
med_impact = df.groupby("medication_counselling_done")["readmitted_30d"].mean()
print(f"\n✦ Medication counselling impact:")
print(f"  Without: {med_impact[0]:.1%}  |  With: {med_impact[1]:.1%}  |  Δ = {(med_impact[0]-med_impact[1]):.1%} reduction")

# ── Dashboard KPI Summary ─────────────────────────────────────────────────────
kpis = {
    "total_patients": len(df),
    "overall_readmission_rate": round(df["readmitted_30d"].mean(), 4),
    "critical_risk_count": int((df["risk_tier"] == "Critical").sum()),
    "high_risk_count": int((df["risk_tier"] == "High").sum()),
    "moderate_risk_count": int((df["risk_tier"] == "Moderate").sum()),
    "low_risk_count": int((df["risk_tier"] == "Low").sum()),
    "avg_sdoh_burden": round(df["sdoh_burden"].mean(), 2),
    "pct_no_medication_counselling": round((df["medication_counselling_done"] == 0).mean(), 4),
    "pct_no_followup": round((df["followup_scheduled"] == 0).mean(), 4),
    "model_auc": round(auc, 4),
    "model_cv_auc": round(float(cv_scores.mean()), 4),
    "model_sensitivity": round(report["1"]["recall"], 4),
    "model_specificity": round(report["0"]["recall"], 4),
    "brier_score": round(brier, 4),
    "risk_tier_distribution": df["risk_tier"].value_counts().to_dict(),
    "diagnosis_readmission": dx_eq.head(8).to_dict(),
    "top_risk_factors": coef_df[["feature", "odds_ratio"]].head(8).to_dict(orient="records"),
}

# ── Save Outputs ──────────────────────────────────────────────────────────────
with open("model_results.json", "w") as f:
    json.dump({
        "performance": {
            "roc_auc": round(auc, 4),
            "cv_auc_mean": round(float(cv_scores.mean()), 4),
            "cv_auc_std": round(float(cv_scores.std()), 4),
            "brier_score": round(brier, 4),
            "sensitivity": round(report["1"]["recall"], 4),
            "specificity": round(report["0"]["recall"], 4),
            "precision": round(report["1"]["precision"], 4),
            "confusion_matrix": cm
        },
        "feature_importances": coef_df[["feature", "coefficient", "odds_ratio"]].to_dict(orient="records")
    }, f, indent=2)

with open("equity_report.json", "w") as f:
    json.dump(equity, f, indent=2, default=str)

with open("summary_stats.json", "w") as f:
    json.dump(kpis, f, indent=2, default=str)

print("\n✓ Outputs saved: model_results.json, equity_report.json, summary_stats.json")
