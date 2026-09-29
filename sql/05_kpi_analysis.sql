SET search_path TO saas_analytics;

-- Current snapshot KPIs as of 2026-08-31.
SELECT
    COUNT(*) FILTER (WHERE status='Active') AS active_customers,
    ROUND(SUM(monthly_recurring_revenue) FILTER (WHERE status='Active'),2) AS mrr,
    ROUND(12 * SUM(monthly_recurring_revenue) FILTER (WHERE status='Active'),2) AS arr,
    ROUND(
      SUM(monthly_recurring_revenue) FILTER (WHERE status='Active') /
      NULLIF(COUNT(*) FILTER (WHERE status='Active'),0), 2
    ) AS arpa
FROM subscriptions;

-- Monthly customer movement, MRR, and logo churn.
WITH months AS (
    SELECT generate_series(DATE '2024-01-01', DATE '2026-08-01', INTERVAL '1 month')::date AS month_start
), metrics AS (
    SELECT
        m.month_start,
        (m.month_start + INTERVAL '1 month - 1 day')::date AS month_end,
        COUNT(s.customer_id) FILTER (
            WHERE s.start_date <= m.month_start
              AND (s.churn_date IS NULL OR s.churn_date >= m.month_start)
        ) AS active_start,
        COUNT(s.customer_id) FILTER (
            WHERE s.start_date BETWEEN m.month_start AND (m.month_start + INTERVAL '1 month - 1 day')::date
        ) AS new_customers,
        COUNT(s.customer_id) FILTER (
            WHERE s.churn_date BETWEEN m.month_start AND (m.month_start + INTERVAL '1 month - 1 day')::date
        ) AS churned_customers,
        COUNT(s.customer_id) FILTER (
            WHERE s.start_date <= (m.month_start + INTERVAL '1 month - 1 day')::date
              AND (s.churn_date IS NULL OR s.churn_date > (m.month_start + INTERVAL '1 month - 1 day')::date)
        ) AS active_end,
        SUM(s.monthly_recurring_revenue) FILTER (
            WHERE s.start_date <= (m.month_start + INTERVAL '1 month - 1 day')::date
              AND (s.churn_date IS NULL OR s.churn_date > (m.month_start + INTERVAL '1 month - 1 day')::date)
        ) AS mrr_end
    FROM months m CROSS JOIN subscriptions s
    GROUP BY m.month_start
)
SELECT *,
       ROUND(churned_customers::numeric / NULLIF(active_start,0),4) AS logo_churn_rate
FROM metrics ORDER BY month_start;

-- Plan performance.
SELECT
    p.plan_name,
    COUNT(*) AS customers,
    COUNT(*) FILTER (WHERE s.status='Churned') AS churned_customers,
    ROUND(AVG(s.monthly_recurring_revenue),2) AS avg_mrr,
    ROUND(COUNT(*) FILTER (WHERE s.status='Churned')::numeric / COUNT(*),4) AS observed_churn_share
FROM subscriptions s JOIN plans p USING(plan_id)
GROUP BY p.plan_name ORDER BY observed_churn_share DESC;

-- Acquisition channel performance.
SELECT
    c.acquisition_channel,
    COUNT(*) AS customers,
    ROUND(AVG(s.monthly_recurring_revenue),2) AS avg_mrr,
    ROUND(COUNT(*) FILTER (WHERE s.status='Churned')::numeric / COUNT(*),4) AS observed_churn_share
FROM customers c JOIN subscriptions s USING(customer_id)
GROUP BY c.acquisition_channel
ORDER BY customers DESC;
