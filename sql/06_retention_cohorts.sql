SET search_path TO saas_analytics;

-- Signup-month cohort retention. Restrict to first 12 months for dashboard readability.
WITH cohort_base AS (
    SELECT
        customer_id,
        DATE_TRUNC('month', start_date)::date AS cohort_month,
        start_date,
        churn_date
    FROM subscriptions
), cohort_age AS (
    SELECT
        cb.customer_id,
        cb.cohort_month,
        gs.month_number,
        (cb.cohort_month + (gs.month_number || ' months')::interval + INTERVAL '1 month - 1 day')::date AS checkpoint,
        cb.churn_date
    FROM cohort_base cb
    CROSS JOIN generate_series(0,12) AS gs(month_number)
    WHERE cb.cohort_month + (gs.month_number || ' months')::interval <= DATE '2026-08-31'
), retained AS (
    SELECT
        cohort_month,
        month_number,
        COUNT(*) AS cohort_size_at_checkpoint,
        COUNT(*) FILTER (WHERE churn_date IS NULL OR churn_date > checkpoint) AS retained_customers
    FROM cohort_age
    GROUP BY cohort_month, month_number
), cohort_sizes AS (
    SELECT cohort_month, COUNT(*) AS cohort_size
    FROM cohort_base GROUP BY cohort_month
)
SELECT
    r.cohort_month,
    r.month_number,
    cs.cohort_size,
    r.retained_customers,
    ROUND(r.retained_customers::numeric / cs.cohort_size,4) AS retention_rate
FROM retained r JOIN cohort_sizes cs USING(cohort_month)
ORDER BY cohort_month, month_number;
