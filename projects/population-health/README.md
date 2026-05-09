# Population Health Readmission Risk Intelligence

> End-to-end population health surveillance · Logistic regression · ICD-10 · SDOH equity analysis

**Part of:** [Taiwo Tobi Omoyeni Portfolio](../../index.html)

---

## 📊 Key Results

| Metric | Value |
|--------|-------|
| Overall 30-day readmission rate | 22.9% |
| Model ROC-AUC | 0.772 |
| CV AUC (5-fold) | 0.751 ± 0.023 |
| Equity disparity (Black vs Asian) | +9.4pp |
| SDOH burden gradient | 16.9% → 53.3% |
| Medication counselling gap | 9.3pp reduction |

## 🗂 Files

| File | Purpose |
|------|---------|
| `dashboard/index.html` | Interactive 4-tab surveillance dashboard |
| `data/generate_data.py` | Generates 2,000 synthetic EHR records |
| `data/analysis.py` | Logistic regression + equity analysis |
| `data/population_health_data.csv` | Generated dataset |
| `data/model_results.json` | Model metrics + feature importances |
| `data/equity_report.json` | Stratified equity analysis |
| `data/summary_stats.json` | Dashboard KPI summary |
| `sql/population_health_queries.sql` | 8 analytics queries (CTEs + window functions) |

## ⚙️ Run Locally

```bash
pip install pandas numpy scikit-learn pandasql
cd data/
python generate_data.py
python analysis.py
# Open dashboard/index.html in browser
```

*Synthetic data only. No real patient records used.*
