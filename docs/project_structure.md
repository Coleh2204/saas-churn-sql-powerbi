# Project Structure

```text
SaaS_Churn_SQL_PowerBI_Portfolio/
├── README.md
├── data/
│   ├── raw/
│   │   ├── customers.csv
│   │   ├── plans.csv
│   │   ├── subscriptions.csv
│   │   ├── usage_monthly.csv
│   │   ├── support_tickets.csv
│   │   └── payments.csv
│   └── processed/
│       └── customer_churn_features.csv
├── sql/
│   ├── 01_create_schema.sql
│   ├── 02_load_data.sql
│   ├── 03_data_quality.sql
│   ├── 04_customer_health_features.sql
│   ├── 05_kpi_analysis.sql
│   ├── 06_retention_cohorts.sql
│   ├── 07_churn_drivers.sql
│   ├── 08_powerbi_views.sql
│   └── 09_interview_queries.sql
├── outputs/
│   ├── kpi_summary.csv
│   ├── monthly_metrics.csv
│   ├── cohort_retention.csv
│   ├── plan_performance.csv
│   ├── churn_by_usage_trend.csv
│   ├── churn_by_support_tickets.csv
│   ├── churn_by_payment_issue.csv
│   └── usage_before_churn.csv
├── powerbi/
│   ├── measures.dax
│   ├── date_table.dax
│   ├── model_relationships.md
│   ├── dashboard_build_guide.md
│   ├── POWERBI_IMPORT_GUIDE.md
│   └── portfolio_theme.json
├── python/
│   ├── generate_synthetic_data.py
│   ├── adjust_usage_realism.py
│   └── build_outputs.py
└── docs/
    ├── business_questions.md
    ├── data_dictionary.md
    ├── interview_talking_points.md
    ├── resume_bullets.md
    └── project_structure.md
```
