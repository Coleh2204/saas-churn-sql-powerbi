SET search_path TO saas_analytics;

-- Row counts by source table.
SELECT 'customers' AS table_name, COUNT(*) AS rows FROM customers
UNION ALL SELECT 'subscriptions', COUNT(*) FROM subscriptions
UNION ALL SELECT 'usage_monthly', COUNT(*) FROM usage_monthly
UNION ALL SELECT 'support_tickets', COUNT(*) FROM support_tickets
UNION ALL SELECT 'payments', COUNT(*) FROM payments;

-- Primary business integrity checks. Every query below should return 0.
SELECT COUNT(*) AS subscriptions_without_customer
FROM subscriptions s LEFT JOIN customers c USING (customer_id)
WHERE c.customer_id IS NULL;

SELECT COUNT(*) AS subscriptions_without_plan
FROM subscriptions s LEFT JOIN plans p USING (plan_id)
WHERE p.plan_id IS NULL;

SELECT COUNT(*) AS invalid_churn_status_rows
FROM subscriptions
WHERE (status='Active' AND churn_date IS NOT NULL)
   OR (status='Churned' AND churn_date IS NULL)
   OR (churn_date IS NOT NULL AND churn_date < start_date);

SELECT COUNT(*) AS duplicate_customer_month_usage
FROM (
    SELECT customer_id, usage_month
    FROM usage_monthly
    GROUP BY 1,2
    HAVING COUNT(*) > 1
) x;

SELECT COUNT(*) AS invalid_usage_rows
FROM usage_monthly
WHERE sessions < 0 OR active_users < 0 OR features_used < 0 OR storage_gb < 0;

SELECT COUNT(*) AS invalid_payment_rows
FROM payments
WHERE amount < 0 OR payment_status NOT IN ('Paid','Failed');

-- Useful profiling.
SELECT status, COUNT(*) AS customers,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS pct
FROM subscriptions GROUP BY status ORDER BY customers DESC;

SELECT MIN(start_date) AS first_subscription,
       MAX(start_date) AS latest_subscription_start,
       MAX(churn_date) AS latest_churn
FROM subscriptions;
