# NHS Healthcare Workflow Analytics & Automation Pipeline

> End-to-end NHS operational analytics — automated Python ETL pipeline, RTT KPI calculation, health equity analysis, interactive Chart.js dashboard, and automated HTML email reporting.

**Author:** Taiwo Tobi Omoyeni · Health Data Analyst & Population Health Informaticist
**Part of:** [Portfolio](https://Taiwotimman.github.io/taiwo-portfolio)

---

## 🌐 Live Dashboard

**[View Dashboard](https://Taiwotimman.github.io/taiwo-portfolio/projects/healthcare-workflow/dashboard/index.html)**

---

## 📊 Key Findings

| KPI | Value | Target | Status |
|-----|-------|--------|--------|
| Total Patients Waiting | 389,263 | — | — |
| % Seen Within 18 Weeks | 87.5% | 92% | ❌ Breaching |
| Patients Over 52 Weeks | 4,146 | 0 | ❌ NHS Constitution Breach |
| Average Wait | 15.4 weeks | < 18 weeks | ⚠️ Near limit |
| Average DNA Rate | 11.2% | < 10% | ⚠️ Above threshold |
| Average Utilisation | 82.7% | > 85% | ⚠️ Near target |
| Trusts Meeting Target | 0 / 15 | 15 / 15 | ❌ All breaching |

---

## 🗂 Project Structure

```
healthcare-workflow/
│
├── dashboard/
│   └── index.html                  ← Interactive 5-tab NHS dashboard
│
├── data/
│   ├── config.py                   ← Settings (NOT on GitHub)
│   ├── 01_extract.py               ← Download NHS RTT data
│   ├── 02_clean.py                 ← Clean and standardise
│   ├── 03_calculate_kpis.py        ← Calculate all KPIs
│   ├── 04_automate.py              ← Run full pipeline (1 command)
│   ├── 05_email_report.py          ← Build & send HTML email report
│   ├── raw/                        ← Downloaded data (not on GitHub)
│   ├── processed/                  ← Cleaned data (not on GitHub)
│   └── outputs/                    ← KPI JSONs (not on GitHub)
│
├── sql/
│   └── nhs_workflow_queries.sql    ← 8 production SQL queries
│
├── .gitignore                      ← Protects credentials & data
├── requirements.txt                ← Python dependencies
└── README.md
```

---

## ⚙️ How to Run

### 1 — Install dependencies
```bash
pip install -r requirements.txt
```

### 2 — Configure settings
Edit `data/config.py`:
- Set `EMAIL_SENDER` to your Gmail address
- Set `EMAIL_PASSWORD` to your Gmail App Password
- Set `EMAIL_RECIPIENTS` to who should receive reports

### 3 — Run the full pipeline (one command)
```bash
cd data/
python 04_automate.py
```

This automatically runs all 5 steps:
- Downloads NHS RTT data
- Cleans and validates it
- Calculates all KPIs
- Builds the HTML email
- Sends the report

### 4 — Preview the email
Before configuring Gmail, open `data/outputs/email_preview.html`
in your browser to see exactly what the email looks like.

### 5 — Schedule it (optional)
**Windows Task Scheduler:**
```
Action: python C:\path\to\data\04_automate.py
Trigger: Every Monday at 07:00
```
**Mac/Linux Cron:**
```bash
crontab -e
# Add this line:
0 7 * * 1 python /path/to/data/04_automate.py
```

---

## 📧 Setting Up Gmail App Password

1. Go to **myaccount.google.com**
2. Security → 2-Step Verification (enable if not already on)
3. Search for **App Passwords**
4. Create one named **"NHS Report"**
5. Copy the 16-character code
6. Paste into `config.py` as `EMAIL_PASSWORD`

---

## 🗃 SQL Queries

8 production-grade queries compatible with SQL Server / PostgreSQL / BigQuery:

1. **Overall RTT KPI Summary** — top-level dashboard figures
2. **Trust Performance Ranking** — league table with target flags
3. **Monthly Trend with MoM Change** — LAG window function
4. **Specialty Performance Ranking** — identify priority areas
5. **DNA Rate Analysis** — appointment efficiency by trust and specialty
6. **52-Week Breach Registry** — CTE + ROW_NUMBER for escalation list
7. **Capacity vs Demand Gap** — cumulative backlog with window function
8. **Automated Alert Generation** — feeds the email report system

---

## 📈 Dashboard Tabs

| Tab | Content |
|-----|---------|
| Overview | KPI strip, RTT trend, waiting list trend, DNA, throughput |
| Waiting Times | Band distribution, referrals vs completions gap |
| Trust Performance | League table, RTT bar chart, DNA rate comparison |
| Specialties | Performance and waiting list by specialty |
| Pipeline & Automation | Script breakdown, email report preview, scheduling guide |

---

## 🔗 Links

| | |
|---|---|
| 💼 LinkedIn | [linkedin.com/in/taiwo-omoyeni-830a07a7](https://www.linkedin.com/in/taiwo-omoyeni-830a07a7) |
| 𝕏 Twitter | [x.com/TaiwoTimma96364](https://x.com/TaiwoTimma96364) |
| 💻 GitHub | [github.com/Taiwotimman](https://github.com/Taiwotimman) |
| ✉ Email | [Taiwotobiomoyeni@gmail.com](mailto:Taiwotobiomoyeni@gmail.com) |

---

*Data is synthetic and mirrors NHS England RTT published format. No real patient data is used.*
