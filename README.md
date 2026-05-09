# Taiwo Tobi Omoyeni — Health Data Analytics Portfolio

> Population Health Informaticist · Health Data Analyst · Clinical Researcher  
> Live portfolio with embedded interactive project dashboards.

## 🌐 Live Site

**[https://Taiwotimman.github.io/taiwo-portfolio](https://Taiwotimman.github.io/taiwo-portfolio)**

---

## 👤 About

Licensed physiotherapist and data analyst specialising in population health informatics, EHR analytics, predictive modelling, and AI data evaluation. Pursuing M.Sc. in Neurological Physiotherapy at the University of Ibadan.

| | |
|---|---|
| 📍 Location | Nigeria · Remote / Open to Contract |
| 📧 Email | Taiwotobiomoyeni@gmail.com |
| 💼 LinkedIn | [linkedin.com/in/taiwo-omoyeni-830a07a7](https://www.linkedin.com/in/taiwo-omoyeni-830a07a7) |
| 𝕏 Twitter | [x.com/TaiwoTimma96364](https://x.com/TaiwoTimma96364) |
| 💻 GitHub | [github.com/Taiwotimman](https://github.com/Taiwotimman) |

---

## 🗂 Repository Structure

```
taiwo-portfolio/
│
├── index.html                          ← Main portfolio homepage
│
├── projects/
│   └── population-health/              ← Project 1 (live)
│       ├── dashboard/
│       │   └── index.html              ← Interactive surveillance dashboard
│       ├── data/
│       │   ├── generate_data.py        ← Synthetic EHR data generator
│       │   ├── analysis.py             ← Logistic regression + equity analysis
│       │   ├── population_health_data.csv
│       │   ├── model_results.json
│       │   ├── equity_report.json
│       │   └── summary_stats.json
│       ├── sql/
│       │   └── population_health_queries.sql
│       └── README.md
│
└── README.md                           ← This file
```

---

## 📁 Projects

### 01 · Population Health Readmission Risk Intelligence ✅ LIVE

An end-to-end population health analytics project:
- **2,000** synthetic EHR discharge records with ICD-10 classification
- **Logistic regression** risk model (ROC-AUC = 0.772, 5-fold CV)
- **SDOH burden analysis** — 4-factor gradient from 16.9% to 53.3% readmission rate
- **Health equity stratification** — 9.4pp disparity gap identified (Black vs Asian cohort)
- **8 production-grade SQL queries** with CTEs and window functions
- **Interactive 4-tab dashboard** embedded in portfolio

→ [View Dashboard](projects/population-health/dashboard/index.html)  
→ [View Project README](projects/population-health/README.md)

---

### 02 · Stroke Rehabilitation Outcome Predictor _(Coming Soon)_

Power BI dashboard and logistic regression model from Lagoon Hospital contract.

---

### 03 · Diabetes Risk Modelling & Behavioural Intervention _(Coming Soon)_

Public health intervention study from Obafemi Awolowo University.

---

## 🛠 Tech Stack

`Python` `SQL` `R` `SPSS` `scikit-learn` `pandas` `Power BI` `DAX` `Chart.js` `ICD-10` `REDCap` `Qualtrics`

---

## 📄 How to Add a New Project

1. Create a new folder under `projects/your-project-name/`
2. Add a `dashboard/index.html` (self-contained HTML)
3. Add a `README.md` for the project
4. In the main `index.html`, copy one of the `.project-card` blocks and update the content and `src` path in the iframe

---

*All datasets in this portfolio are entirely synthetic. No real patient data is used.*
