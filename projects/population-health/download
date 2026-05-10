-- =================================================================
-- nhs_workflow_queries.sql
-- NHS Healthcare Workflow Analytics — Production SQL Queries
-- Author: Taiwo Tobi Omoyeni
-- Compatible: SQL Server / PostgreSQL / BigQuery / Snowflake
--
-- Context: These queries are written as if running against a live
-- NHS SQL Server database (e.g. Meditech, Cerner, or a data
-- warehouse built on top of an NHS PAS system).
-- =================================================================


-- ─────────────────────────────────────────────────────────────────
-- QUERY 1: Overall RTT KPI Dashboard Summary
-- Purpose: Top-level KPIs for the weekly operational report
-- ─────────────────────────────────────────────────────────────────
SELECT
    COUNT(DISTINCT patient_id)                                  AS total_patients_waiting,
    ROUND(AVG(CASE WHEN wait_weeks <= 18 THEN 1.0 ELSE 0.0 END) * 100, 1)
                                                                AS pct_within_18_weeks,
    SUM(CASE WHEN wait_weeks > 18 THEN 1 ELSE 0 END)           AS over_18_weeks,
    SUM(CASE WHEN wait_weeks > 52 THEN 1 ELSE 0 END)           AS over_52_weeks,
    ROUND(AVG(wait_weeks), 1)                                   AS avg_wait_weeks,
    COUNT(DISTINCT trust_code)                                  AS trusts_included,
    SUM(CASE WHEN pct_within_18wks >= 92 THEN 1 ELSE 0 END)    AS trusts_meeting_target,
    FORMAT(GETDATE(), 'yyyy-MM')                                AS report_period
FROM nhs_rtt_waiting_list
WHERE report_month = (SELECT MAX(report_month) FROM nhs_rtt_waiting_list)
  AND specialty_code IS NOT NULL;


-- ─────────────────────────────────────────────────────────────────
-- QUERY 2: Trust RTT Performance with Ranking and Target Flag
-- Purpose: Trust league table — ranked by performance
-- ─────────────────────────────────────────────────────────────────
WITH trust_stats AS (
    SELECT
        trust_name,
        trust_code,
        report_month,
        SUM(total_waiting)                                         AS total_waiting,
        SUM(over_18_weeks)                                         AS over_18_weeks,
        SUM(over_52_weeks)                                         AS over_52_weeks,
        ROUND(AVG(pct_within_18wks), 1)                            AS pct_within_18wks,
        ROUND(AVG(avg_wait_weeks), 1)                              AS avg_wait_weeks,
        ROUND(AVG(dna_rate_pct), 1)                                AS dna_rate_pct,
        ROUND(AVG(utilisation_pct), 1)                             AS utilisation_pct
    FROM nhs_rtt_waiting_list
    WHERE report_month = (SELECT MAX(report_month) FROM nhs_rtt_waiting_list)
    GROUP BY trust_name, trust_code, report_month
),
ranked AS (
    SELECT *,
        RANK() OVER (ORDER BY pct_within_18wks DESC)               AS performance_rank,
        CASE WHEN pct_within_18wks >= 92 THEN 'On Target'
             WHEN pct_within_18wks >= 88 THEN 'At Risk'
             WHEN pct_within_18wks >= 85 THEN 'Underperforming'
             ELSE 'Critical'
        END                                                         AS performance_band,
        CASE WHEN over_52_weeks > 0 THEN 'YES' ELSE 'NO' END       AS has_52wk_breach
    FROM trust_stats
)
SELECT *,
    ROUND(pct_within_18wks - 92, 1)                                AS gap_to_target_pp
FROM ranked
ORDER BY performance_rank;


-- ─────────────────────────────────────────────────────────────────
-- QUERY 3: Monthly RTT Trend with Month-on-Month Change
-- Purpose: Identify improving or worsening trajectory
-- ─────────────────────────────────────────────────────────────────
WITH monthly_agg AS (
    SELECT
        report_month,
        SUM(total_waiting)                                     AS total_waiting,
        SUM(new_referrals)                                     AS new_referrals,
        SUM(completed_pathways)                                AS completed_pathways,
        ROUND(AVG(pct_within_18wks), 1)                       AS pct_within_18wks,
        ROUND(AVG(avg_wait_weeks), 1)                         AS avg_wait_weeks,
        ROUND(AVG(dna_rate_pct), 1)                           AS avg_dna_rate,
        ROUND(AVG(utilisation_pct), 1)                        AS avg_utilisation
    FROM nhs_rtt_waiting_list
    GROUP BY report_month
)
SELECT
    report_month,
    total_waiting,
    new_referrals,
    completed_pathways,
    (new_referrals - completed_pathways)                       AS backlog_change,
    pct_within_18wks,
    LAG(pct_within_18wks) OVER (ORDER BY report_month)        AS prev_month_rtt,
    ROUND(pct_within_18wks -
          LAG(pct_within_18wks) OVER (ORDER BY report_month), 1)
                                                               AS mom_change_pp,
    avg_wait_weeks,
    avg_dna_rate,
    avg_utilisation,
    SUM(total_waiting) OVER (ORDER BY report_month
                             ROWS BETWEEN 2 PRECEDING AND CURRENT ROW)
                                                               AS rolling_3m_total
FROM monthly_agg
ORDER BY report_month;


-- ─────────────────────────────────────────────────────────────────
-- QUERY 4: Specialty Performance Ranking
-- Purpose: Identify which specialties are driving RTT failures
-- ─────────────────────────────────────────────────────────────────
WITH spec_stats AS (
    SELECT
        specialty_name,
        specialty_code,
        SUM(total_waiting)                                     AS total_waiting,
        SUM(over_18_weeks)                                     AS over_18_weeks,
        SUM(over_52_weeks)                                     AS over_52_weeks,
        ROUND(AVG(pct_within_18wks), 1)                       AS pct_within_18wks,
        ROUND(AVG(avg_wait_weeks), 1)                         AS avg_wait_weeks,
        SUM(new_referrals)                                     AS new_referrals
    FROM nhs_rtt_waiting_list
    WHERE report_month = (SELECT MAX(report_month) FROM nhs_rtt_waiting_list)
    GROUP BY specialty_name, specialty_code
),
overall AS (
    SELECT ROUND(AVG(pct_within_18wks), 1) AS overall_rtt
    FROM nhs_rtt_waiting_list
    WHERE report_month = (SELECT MAX(report_month) FROM nhs_rtt_waiting_list)
)
SELECT
    s.*,
    o.overall_rtt,
    ROUND(s.pct_within_18wks - o.overall_rtt, 1)              AS delta_vs_average,
    ROUND(s.over_18_weeks * 100.0
          / NULLIF(s.total_waiting, 0), 1)                     AS pct_backlogged,
    RANK() OVER (ORDER BY s.pct_within_18wks)                  AS priority_rank
FROM spec_stats s
CROSS JOIN overall o
ORDER BY pct_within_18wks;


-- ─────────────────────────────────────────────────────────────────
-- QUERY 5: DNA Rate Analysis — Appointment Efficiency
-- Purpose: Identify trusts and specialties with high no-show rates
-- ─────────────────────────────────────────────────────────────────
WITH dna_analysis AS (
    SELECT
        trust_name,
        specialty_name,
        report_month,
        ROUND(AVG(dna_rate_pct), 1)                            AS avg_dna_rate,
        ROUND(AVG(utilisation_pct), 1)                         AS avg_utilisation,
        SUM(total_waiting)                                     AS total_waiting,
        COUNT(*)                                               AS record_count
    FROM nhs_rtt_waiting_list
    WHERE report_month = (SELECT MAX(report_month) FROM nhs_rtt_waiting_list)
    GROUP BY trust_name, specialty_name, report_month
)
SELECT *,
    CASE
        WHEN avg_dna_rate > 15  THEN 'Critical — urgent review'
        WHEN avg_dna_rate > 10  THEN 'High — above threshold'
        WHEN avg_dna_rate > 7   THEN 'Moderate — monitor'
        ELSE                         'Acceptable'
    END                                                        AS dna_alert_level,
    NTILE(4) OVER (ORDER BY avg_dna_rate DESC)                 AS dna_quartile
FROM dna_analysis
WHERE avg_dna_rate > 10
ORDER BY avg_dna_rate DESC;


-- ─────────────────────────────────────────────────────────────────
-- QUERY 6: 52-Week Breach Patient Registry (CTE + Window)
-- Purpose: Identify patients requiring immediate escalation
-- ─────────────────────────────────────────────────────────────────
WITH breach_patients AS (
    SELECT
        patient_id,
        trust_name,
        specialty_name,
        wait_weeks,
        referral_date,
        DATEDIFF(DAY, referral_date, GETDATE())                AS days_waiting,
        ROW_NUMBER() OVER (
            PARTITION BY trust_name
            ORDER BY wait_weeks DESC
        )                                                      AS rank_within_trust
    FROM nhs_rtt_waiting_list
    WHERE wait_weeks > 52
      AND report_month = (SELECT MAX(report_month) FROM nhs_rtt_waiting_list)
),
trust_breach_totals AS (
    SELECT
        trust_name,
        COUNT(*)                                               AS total_breaches,
        MAX(wait_weeks)                                        AS longest_wait_weeks,
        ROUND(AVG(wait_weeks), 1)                             AS avg_breach_wait
    FROM breach_patients
    GROUP BY trust_name
)
SELECT
    b.patient_id,
    b.trust_name,
    b.specialty_name,
    b.wait_weeks,
    b.days_waiting,
    b.rank_within_trust,
    t.total_breaches AS trust_total_52wk_breaches,
    'ESCALATE — NHS Constitution Breach'                       AS action_required
FROM breach_patients b
JOIN trust_breach_totals t ON b.trust_name = t.trust_name
WHERE b.rank_within_trust <= 20
ORDER BY b.wait_weeks DESC;


-- ─────────────────────────────────────────────────────────────────
-- QUERY 7: Capacity vs Demand — Throughput Gap Analysis
-- Purpose: Identify where new referrals are outpacing completions
-- ─────────────────────────────────────────────────────────────────
WITH capacity_demand AS (
    SELECT
        trust_name,
        report_month,
        SUM(new_referrals)                                     AS demand,
        SUM(completed_pathways)                                AS capacity,
        SUM(new_referrals) - SUM(completed_pathways)          AS throughput_gap,
        ROUND(SUM(completed_pathways) * 100.0
              / NULLIF(SUM(new_referrals), 0), 1)              AS throughput_ratio_pct,
        ROUND(AVG(utilisation_pct), 1)                        AS avg_utilisation
    FROM nhs_rtt_waiting_list
    GROUP BY trust_name, report_month
)
SELECT *,
    SUM(throughput_gap) OVER (
        PARTITION BY trust_name
        ORDER BY report_month
        ROWS UNBOUNDED PRECEDING
    )                                                          AS cumulative_backlog_growth,
    CASE
        WHEN throughput_ratio_pct >= 100 THEN 'Sustainable'
        WHEN throughput_ratio_pct >= 90  THEN 'Near Capacity'
        WHEN throughput_ratio_pct >= 80  THEN 'Under Pressure'
        ELSE                                  'Critical — Backlog Growing'
    END                                                        AS capacity_status
FROM capacity_demand
ORDER BY trust_name, report_month;


-- ─────────────────────────────────────────────────────────────────
-- QUERY 8: Automated Alert Generation
-- Purpose: Produce alert flags that feed the email report
-- ─────────────────────────────────────────────────────────────────
WITH current_period AS (
    SELECT * FROM nhs_rtt_waiting_list
    WHERE report_month = (SELECT MAX(report_month) FROM nhs_rtt_waiting_list)
),
trust_summary AS (
    SELECT
        trust_name,
        ROUND(AVG(pct_within_18wks), 1)    AS rtt_pct,
        SUM(over_52_weeks)                  AS breaches_52wk,
        ROUND(AVG(dna_rate_pct), 1)        AS dna_rate,
        ROUND(AVG(utilisation_pct), 1)     AS utilisation
    FROM current_period
    GROUP BY trust_name
)
SELECT
    trust_name,
    rtt_pct,
    breaches_52wk,
    dna_rate,
    utilisation,
    CASE
        WHEN rtt_pct < 85 OR breaches_52wk > 100  THEN 'RED'
        WHEN rtt_pct < 92 OR dna_rate > 10        THEN 'AMBER'
        ELSE                                            'GREEN'
    END                                               AS alert_level,
    CASE
        WHEN rtt_pct < 85    THEN 'RTT performance critical — below 85%'
        WHEN breaches_52wk > 100 THEN '52-week breaches exceed 100 — escalate'
        WHEN rtt_pct < 92    THEN 'RTT below 92% target'
        WHEN dna_rate > 10   THEN 'DNA rate above 10% threshold'
        ELSE                      'All KPIs within acceptable range'
    END                                               AS alert_message,
    GETDATE()                                         AS alert_generated_at
FROM trust_summary
ORDER BY
    CASE alert_level WHEN 'RED' THEN 1 WHEN 'AMBER' THEN 2 ELSE 3 END,
    rtt_pct;
