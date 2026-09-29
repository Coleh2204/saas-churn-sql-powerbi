# Interview Talking Points

## 30-second project explanation

> I built a relational SaaS analytics project in PostgreSQL and Power BI using a synthetic dataset of 8,000 customer accounts. I modeled customers, plans, subscriptions, usage, support tickets, and payments, then wrote SQL for monthly MRR, logo churn, cohort retention, customer-health features, and churn-driver analysis. I exposed reporting views for Power BI and designed an executive dashboard, retention page, churn-driver page, and customer-risk explorer.

## What makes the SQL more than basic SELECT/GROUP BY work?

- Multi-table relational joins across six entities.
- CTEs for cohort analysis and monthly metrics.
- Window functions in the interview-query file.
- Conditional aggregation with `FILTER`.
- Date-series generation with `generate_series`.
- Feature engineering over rolling 90-day and three-month windows.
- Reporting views designed specifically for a BI semantic layer.

## Key findings

- The August 2026 snapshot contains 6,208 active customers and about $732.4K MRR / $8.79M ARR.
- August logo churn is roughly 1.97%.
- Average month-6 cohort retention is about 88.9%; average month-12 retention is about 78.9%.
- Starter shows a higher observed churn share (~24.0%) than Enterprise (~16.7%).
- A severe recent usage decline is strongly associated with churn in the synthetic data (~84.1% observed churn share).
- Accounts with 4+ recent support tickets show ~61.6% observed churn share.
- Accounts with a recent failed payment show ~49.5% observed churn share versus ~20.0% without a failed payment.
- For churned customers, average sessions fall materially in the final two months before cancellation.

## Important caveat

The dataset is synthetic. I designed correlated behavior so the project has realistic analytical signals, then intentionally added noise and non-usage-driven churn so the relationships are not perfectly deterministic. The results demonstrate the workflow and analysis, not a claim about real SaaS customers.

## If asked what you would do next with real company data

- Validate metric definitions with finance/customer-success stakeholders.
- Separate voluntary vs involuntary churn.
- Model upgrades, downgrades, contractions, and expansion MRR.
- Add product-level event data and account seat utilization.
- Evaluate predictive models on time-based train/test splits.
- Design interventions and test them experimentally instead of treating associations as causal.
