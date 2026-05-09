-- =============================================================================
-- population_health_queries.sql
-- Population Health Readmission Intelligence — Core Analytics Queries
-- Author: Taiwo Tobi Omoyeni
-- =============================================================================
-- These queries are designed for use against the population_health_data table.
-- Compatible with PostgreSQL / BigQuery / Snowflake (minor dialect adjustments).
-- =============================================================================


-- ─────────────────────────────────────────────────────────────────────────────
-- QUERY 1: Overall KPI Summary
-- Purpose: Top-level dashboard metrics for population health surveillance
-- ─────────────────────────────────────────────────────────────────────────────
SELECT
    COUNT(*)                                                AS total_patients,
    ROUND(AVG(readmitted_30d) * 100, 2)                    AS readmission_rate_pct,
    ROUND(AVG(length_of_stay_days), 1)                     AS avg_los_days,
    ROUND(AVG(num_comorbidities), 1)                       AS avg_comorbidities,
    ROUND(AVG(sdoh_food_insecurity + sdoh_housing_instability
              + sdoh_transport_barrier + sdoh_low_health_literacy), 2)
                                                           AS avg_sdoh_burden,
    SUM(CASE WHEN risk_tier = 'Critical' THEN 1 ELSE 0 END) AS critical_risk_count,
    SUM(CASE WHEN risk_tier = 'High'     THEN 1 ELSE 0 END) AS high_risk_count,
    SUM(CASE WHEN readmitted_30d = 1
              AND medication_counselling_done = 0 THEN 1 ELSE 0 END)
                                                           AS readmit_no_counselling
FROM population_health_data;


-- ─────────────────────────────────────────────────────────────────────────────
-- QUERY 2: Readmission Rate by Diagnosis (ICD-10) with Rolling Comparison
-- Purpose: Identify highest-burden diagnoses; supports protocol prioritisation
-- ─────────────────────────────────────────────────────────────────────────────
WITH diagnosis_stats AS (
    SELECT
        primary_diagnosis_icd10,
        COUNT(*)                            AS total_cases,
        SUM(readmitted_30d)                 AS readmissions,
        ROUND(AVG(readmitted_30d) * 100, 2) AS readmission_rate_pct,
        ROUND(AVG(length_of_stay_days), 1)  AS avg_los,
        ROUND(AVG(num_comorbidities), 1)    AS avg_comorbidities
    FROM population_health_data
    GROUP BY primary_diagnosis_icd10
),
overall AS (
    SELECT ROUND(AVG(readmitted_30d) * 100, 2) AS overall_rate
    FROM population_health_data
)
SELECT
    d.*,
    o.overall_rate,
    ROUND(d.readmission_rate_pct - o.overall_rate, 2) AS delta_vs_overall,
    RANK() OVER (ORDER BY d.readmission_rate_pct DESC) AS rank_by_readmission
FROM diagnosis_stats d
CROSS JOIN overall o
ORDER BY readmission_rate_pct DESC;


-- ─────────────────────────────────────────────────────────────────────────────
-- QUERY 3: Health Equity Stratification by Race × Insurance
-- Purpose: Surface disparities at intersection of race and coverage type
-- ─────────────────────────────────────────────────────────────────────────────
WITH equity_grid AS (
    SELECT
        race_ethnicity,
        insurance_type,
        COUNT(*)                                        AS n,
        ROUND(AVG(readmitted_30d) * 100, 2)             AS readmission_rate_pct,
        ROUND(AVG(readmission_risk_score), 3)            AS avg_risk_score,
        ROUND(AVG(sdoh_food_insecurity
                  + sdoh_housing_instability
                  + sdoh_transport_barrier
                  + sdoh_low_health_literacy), 2)        AS avg_sdoh_burden
    FROM population_health_data
    GROUP BY race_ethnicity, insurance_type
    HAVING COUNT(*) >= 15  -- suppress small cells
),
reference AS (
    -- White + Private insurance as reference group
    SELECT readmission_rate_pct AS ref_rate
    FROM equity_grid
    WHERE race_ethnicity = 'White' AND insurance_type = 'Private'
)
SELECT
    e.*,
    r.ref_rate,
    ROUND(e.readmission_rate_pct - r.ref_rate, 2)       AS disparity_gap_pct,
    ROUND(e.readmission_rate_pct / NULLIF(r.ref_rate, 0), 2) AS rate_ratio
FROM equity_grid e
CROSS JOIN reference r
ORDER BY disparity_gap_pct DESC;


-- ─────────────────────────────────────────────────────────────────────────────
-- QUERY 4: SDOH Burden Impact Analysis (Window Function)
-- Purpose: Quantify how each SDOH factor compounds readmission risk
-- ─────────────────────────────────────────────────────────────────────────────
WITH sdoh_segments AS (
    SELECT
        (sdoh_food_insecurity + sdoh_housing_instability
         + sdoh_transport_barrier + sdoh_low_health_literacy)  AS sdoh_burden_score,
        COUNT(*)                                                AS n,
        ROUND(AVG(readmitted_30d) * 100, 2)                    AS readmission_rate_pct,
        ROUND(AVG(readmission_risk_score), 3)                   AS avg_predicted_risk
    FROM population_health_data
    GROUP BY sdoh_burden_score
),
baseline AS (
    SELECT readmission_rate_pct AS zero_burden_rate
    FROM sdoh_segments WHERE sdoh_burden_score = 0
)
SELECT
    s.*,
    b.zero_burden_rate,
    ROUND(s.readmission_rate_pct - b.zero_burden_rate, 2)      AS incremental_risk_pct,
    SUM(s.n) OVER (ORDER BY s.sdoh_burden_score)               AS cumulative_patients
FROM sdoh_segments s
CROSS JOIN baseline b
ORDER BY sdoh_burden_score;


-- ─────────────────────────────────────────────────────────────────────────────
-- QUERY 5: Medication Counselling Gap Analysis by Ward / Diagnosis
-- Purpose: Identify where discharge protocol failures concentrate
-- ─────────────────────────────────────────────────────────────────────────────
WITH counselling_gap AS (
    SELECT
        primary_diagnosis_icd10,
        COUNT(*)                                             AS total_cases,
        SUM(CASE WHEN medication_counselling_done = 0 THEN 1 ELSE 0 END)
                                                             AS no_counselling_count,
        ROUND(AVG(CASE WHEN medication_counselling_done = 0
                       THEN readmitted_30d END) * 100, 2)   AS readmit_rate_no_counsel,
        ROUND(AVG(CASE WHEN medication_counselling_done = 1
                       THEN readmitted_30d END) * 100, 2)   AS readmit_rate_with_counsel
    FROM population_health_data
    GROUP BY primary_diagnosis_icd10
)
SELECT
    *,
    ROUND(no_counselling_count * 100.0 / NULLIF(total_cases, 0), 1)
                                                             AS pct_without_counselling,
    ROUND(readmit_rate_no_counsel - readmit_rate_with_counsel, 2)
                                                             AS counselling_impact_pct,
    RANK() OVER (ORDER BY (readmit_rate_no_counsel - readmit_rate_with_counsel) DESC)
                                                             AS priority_rank
FROM counselling_gap
ORDER BY counselling_impact_pct DESC;


-- ─────────────────────────────────────────────────────────────────────────────
-- QUERY 6: High-Risk Patient Registry (CTE + Window Function)
-- Purpose: Generate actionable list of patients requiring immediate intervention
-- ─────────────────────────────────────────────────────────────────────────────
WITH risk_scored AS (
    SELECT
        patient_id,
        age,
        race_ethnicity,
        insurance_type,
        primary_diagnosis_icd10,
        risk_tier,
        readmission_risk_score,
        prior_admissions_12m,
        sdoh_food_insecurity + sdoh_housing_instability
          + sdoh_transport_barrier + sdoh_low_health_literacy  AS sdoh_burden,
        medication_counselling_done,
        followup_scheduled,
        discharge_disposition,
        ROW_NUMBER() OVER (
            PARTITION BY primary_diagnosis_icd10
            ORDER BY readmission_risk_score DESC
        )                                                       AS rank_within_dx
    FROM population_health_data
    WHERE risk_tier IN ('High', 'Critical')
),
intervention_flags AS (
    SELECT *,
        CASE
            WHEN medication_counselling_done = 0
             AND followup_scheduled = 0          THEN 'URGENT — Dual Gap'
            WHEN medication_counselling_done = 0 THEN 'FLAG — No Counselling'
            WHEN followup_scheduled = 0          THEN 'FLAG — No Follow-up'
            ELSE 'Monitored'
        END                                                     AS intervention_priority
    FROM risk_scored
)
SELECT *
FROM intervention_flags
WHERE rank_within_dx <= 10
ORDER BY readmission_risk_score DESC, sdoh_burden DESC;


-- ─────────────────────────────────────────────────────────────────────────────
-- QUERY 7: Zip Code / Geographic Readmission Hotspot Detection
-- Purpose: Population health surveillance for geographic clustering
-- ─────────────────────────────────────────────────────────────────────────────
WITH zip_stats AS (
    SELECT
        zip_code,
        COUNT(*)                                        AS population,
        ROUND(AVG(readmitted_30d) * 100, 2)             AS readmission_rate_pct,
        ROUND(AVG(readmission_risk_score), 3)            AS avg_predicted_risk,
        ROUND(AVG(sdoh_food_insecurity
                  + sdoh_housing_instability
                  + sdoh_transport_barrier
                  + sdoh_low_health_literacy), 2)        AS avg_sdoh_burden,
        SUM(CASE WHEN risk_tier IN ('High','Critical')
                 THEN 1 ELSE 0 END)                     AS high_critical_count
    FROM population_health_data
    GROUP BY zip_code
)
SELECT
    *,
    ROUND(high_critical_count * 100.0 / NULLIF(population, 0), 1) AS pct_high_critical,
    NTILE(4) OVER (ORDER BY readmission_rate_pct)                  AS quartile,
    CASE WHEN readmission_rate_pct > AVG(readmission_rate_pct)
                                    OVER ()
         THEN '🔴 Hotspot' ELSE '🟢 Below Avg' END                AS hotspot_flag
FROM zip_stats
ORDER BY readmission_rate_pct DESC;


-- ─────────────────────────────────────────────────────────────────────────────
-- QUERY 8: Longitudinal Trend Simulation (Cohort Before/After Protocol)
-- Purpose: Measure impact of discharge protocol overhaul (simulated pre/post)
-- ─────────────────────────────────────────────────────────────────────────────
WITH cohorts AS (
    SELECT
        CASE WHEN prior_admissions_12m >= 2 THEN 'Pre-Protocol Cohort'
             ELSE 'Post-Protocol Cohort' END                        AS cohort,
        COUNT(*)                                                     AS n,
        ROUND(AVG(readmitted_30d) * 100, 2)                         AS readmission_rate_pct,
        ROUND(AVG(readmission_risk_score), 3)                        AS avg_risk_score,
        ROUND(AVG(length_of_stay_days), 1)                           AS avg_los,
        ROUND(SUM(medication_counselling_done) * 100.0
              / NULLIF(COUNT(*), 0), 1)                              AS counselling_compliance_pct,
        ROUND(SUM(followup_scheduled) * 100.0
              / NULLIF(COUNT(*), 0), 1)                              AS followup_compliance_pct
    FROM population_health_data
    GROUP BY cohort
)
SELECT
    *,
    LAG(readmission_rate_pct) OVER (ORDER BY cohort DESC)           AS comparison_rate,
    ROUND(readmission_rate_pct -
          LAG(readmission_rate_pct) OVER (ORDER BY cohort DESC), 2) AS delta_pct
FROM cohorts;
