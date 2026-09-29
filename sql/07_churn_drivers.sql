SET search_path TO saas_analytics;

-- Churn rate by recent usage trend.
WITH bands AS (
    SELECT *,
      CASE
        WHEN usage_change_last_3m <= -0.40 THEN 'Severe decline'
        WHEN usage_change_last_3m <= -0.15 THEN 'Moderate decline'
        WHEN usage_change_last_3m < 0.15 THEN 'Stable'
        ELSE 'Growing'
      END AS usage_trend_band
    FROM vw_customer_health
)
SELECT usage_trend_band,
       COUNT(*) AS customers,
       ROUND(AVG((status='Churned')::int),4) AS observed_churn_share
FROM bands GROUP BY usage_trend_band
ORDER BY observed_churn_share DESC;

-- Churn rate by support burden.
WITH bands AS (
    SELECT *, CASE
      WHEN tickets_last_90d=0 THEN '0'
      WHEN tickets_last_90d=1 THEN '1'
      WHEN tickets_last_90d BETWEEN 2 AND 3 THEN '2-3'
      ELSE '4+'
    END AS ticket_band
    FROM vw_customer_health
)
SELECT ticket_band, COUNT(*) AS customers,
       ROUND(AVG((status='Churned')::int),4) AS observed_churn_share
FROM bands GROUP BY ticket_band
ORDER BY MIN(tickets_last_90d);

-- Churn rate by payment issue.
SELECT
  CASE WHEN failed_payments_last_90d > 0 THEN 'Failed payment' ELSE 'No failed payment' END AS payment_issue,
  COUNT(*) AS customers,
  ROUND(AVG((status='Churned')::int),4) AS observed_churn_share
FROM vw_customer_health
GROUP BY 1;

-- Average product usage in the months leading up to cancellation.
WITH churn_usage AS (
    SELECT
        u.customer_id,
        u.usage_month,
        u.sessions,
        u.active_users,
        s.churn_date,
        (DATE_PART('year', AGE(DATE_TRUNC('month',s.churn_date),u.usage_month))*12
         + DATE_PART('month', AGE(DATE_TRUNC('month',s.churn_date),u.usage_month)))::int AS months_before_churn
    FROM usage_monthly u
    JOIN subscriptions s USING(customer_id)
    WHERE s.status='Churned'
)
SELECT months_before_churn,
       ROUND(AVG(sessions),2) AS avg_sessions,
       ROUND(AVG(active_users),2) AS avg_active_users,
       COUNT(DISTINCT customer_id) AS customers
FROM churn_usage
WHERE months_before_churn BETWEEN 0 AND 6
GROUP BY months_before_churn
ORDER BY months_before_churn DESC;
