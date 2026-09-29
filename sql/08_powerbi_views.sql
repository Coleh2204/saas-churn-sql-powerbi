SET search_path TO saas_analytics;

CREATE OR REPLACE VIEW vw_customer_360 AS
SELECT
    c.customer_id, c.company_name, c.country, c.industry, c.segment, c.acquisition_channel,
    s.subscription_id, s.start_date, s.billing_cycle, s.monthly_recurring_revenue,
    s.status, s.churn_date, s.cancellation_reason,
    p.plan_name, p.monthly_price, p.included_seats,
    h.avg_sessions_last_3m, h.usage_change_last_3m, h.tickets_last_90d, h.failed_payments_last_90d
FROM customers c
JOIN subscriptions s USING(customer_id)
JOIN plans p USING(plan_id)
LEFT JOIN vw_customer_health h USING(customer_id);

CREATE OR REPLACE VIEW vw_monthly_business_metrics AS
WITH months AS (
    SELECT generate_series(DATE '2024-01-01', DATE '2026-08-01', INTERVAL '1 month')::date AS month_start
)
SELECT
  m.month_start,
  COUNT(s.customer_id) FILTER (
    WHERE s.start_date <= m.month_start
      AND (s.churn_date IS NULL OR s.churn_date >= m.month_start)) AS active_start,
  COUNT(s.customer_id) FILTER (
    WHERE s.start_date BETWEEN m.month_start AND (m.month_start + INTERVAL '1 month - 1 day')::date) AS new_customers,
  COUNT(s.customer_id) FILTER (
    WHERE s.churn_date BETWEEN m.month_start AND (m.month_start + INTERVAL '1 month - 1 day')::date) AS churned_customers,
  COUNT(s.customer_id) FILTER (
    WHERE s.start_date <= (m.month_start + INTERVAL '1 month - 1 day')::date
      AND (s.churn_date IS NULL OR s.churn_date > (m.month_start + INTERVAL '1 month - 1 day')::date)) AS active_end,
  SUM(s.monthly_recurring_revenue) FILTER (
    WHERE s.start_date <= (m.month_start + INTERVAL '1 month - 1 day')::date
      AND (s.churn_date IS NULL OR s.churn_date > (m.month_start + INTERVAL '1 month - 1 day')::date) AS mrr_end,
  ROUND(
    COUNT(s.customer_id) FILTER (
      WHERE s.churn_date BETWEEN m.month_start AND (m.month_start + INTERVAL '1 month - 1 day')::date)::numeric /
    NULLIF(COUNT(s.customer_id) FILTER (
      WHERE s.start_date <= m.month_start AND (s.churn_date IS NULL OR s.churn_date >= m.month_start)),0),4
  ) AS logo_churn_rate
FROM months m CROSS JOIN subscriptions s
GROUP BY m.month_start;

CREATE OR REPLACE VIEW vw_usage_before_churn AS
WITH x AS (
 SELECT u.customer_id,u.usage_month,u.sessions,u.active_users,s.churn_date,
        (DATE_PART('year', AGE(DATE_TRUNC('month',s.churn_date),u.usage_month))*12
        +DATE_PART('month', AGE(DATE_TRUNC('month',s.churn_date),u.usage_month)))::int AS months_before_churn
 FROM usage_monthly u JOIN subscriptions s USING(customer_id)
 WHERE s.status='Churned'
)
SELECT months_before_churn,
       ROUND(AVG(sessions),2) AS avg_sessions,
       ROUND(AVG(active_users),2) AS avg_active_users,
       COUNT(DISTINCT customer_id) AS customers
FROM x WHERE months_before_churn BETWEEN 0 AND 6
GROUP BY months_before_churn;

-- For the cohort matrix, use the query in 06_retention_cohorts.sql as a native query
-- or create it as a view in your database if you prefer a fully imported model.
