SET search_path TO saas_analytics;

-- One row per customer using the churn date as the reference date for churned
-- customers and 2026-08-31 as the portfolio snapshot date for active customers.
CREATE OR REPLACE VIEW vw_customer_health AS
WITH base AS (
    SELECT
        s.customer_id,
        s.status,
        s.plan_id,
        s.billing_cycle,
        s.monthly_recurring_revenue,
        s.start_date,
        s.churn_date,
        COALESCE(s.churn_date, DATE '2026-08-31') AS reference_date
    FROM subscriptions s
), usage_window AS (
    SELECT
        b.customer_id,
        AVG(u.sessions)::numeric(12,2) AS avg_sessions_last_3m,
        (ARRAY_AGG(u.sessions ORDER BY u.usage_month))[1] AS first_sessions,
        (ARRAY_AGG(u.sessions ORDER BY u.usage_month DESC))[1] AS last_sessions,
        COUNT(*) AS usage_observations
    FROM base b
    LEFT JOIN usage_monthly u
      ON u.customer_id = b.customer_id
     AND u.usage_month BETWEEN
         DATE_TRUNC('month', b.reference_date)::date - INTERVAL '2 months'
         AND DATE_TRUNC('month', b.reference_date)::date
    GROUP BY b.customer_id
), ticket_window AS (
    SELECT b.customer_id, COUNT(t.ticket_id) AS tickets_last_90d
    FROM base b
    LEFT JOIN support_tickets t
      ON t.customer_id=b.customer_id
     AND t.created_date BETWEEN b.reference_date - 89 AND b.reference_date
    GROUP BY b.customer_id
), payment_window AS (
    SELECT b.customer_id,
           COUNT(p.payment_id) FILTER (WHERE p.payment_status='Failed') AS failed_payments_last_90d
    FROM base b
    LEFT JOIN payments p
      ON p.customer_id=b.customer_id
     AND p.payment_date BETWEEN b.reference_date - 89 AND b.reference_date
    GROUP BY b.customer_id
)
SELECT
    b.customer_id,
    b.status,
    b.plan_id,
    b.billing_cycle,
    b.monthly_recurring_revenue,
    b.start_date,
    b.churn_date,
    u.avg_sessions_last_3m,
    CASE WHEN u.usage_observations >= 2 THEN
        ROUND((u.last_sessions-u.first_sessions)::numeric / NULLIF(u.first_sessions,0),4)
        ELSE 0 END AS usage_change_last_3m,
    COALESCE(t.tickets_last_90d,0) AS tickets_last_90d,
    COALESCE(p.failed_payments_last_90d,0) AS failed_payments_last_90d
FROM base b
LEFT JOIN usage_window u USING (customer_id)
LEFT JOIN ticket_window t USING (customer_id)
LEFT JOIN payment_window p USING (customer_id);
