SET search_path TO saas_analytics;

-- 1) Rank industries by active MRR using a window function.
WITH industry_mrr AS (
  SELECT c.industry,
         SUM(s.monthly_recurring_revenue) FILTER (WHERE s.status='Active') AS active_mrr
  FROM customers c JOIN subscriptions s USING(customer_id)
  GROUP BY c.industry
)
SELECT industry, active_mrr,
       DENSE_RANK() OVER (ORDER BY active_mrr DESC) AS mrr_rank,
       ROUND(100 * active_mrr / SUM(active_mrr) OVER (),2) AS pct_of_active_mrr
FROM industry_mrr ORDER BY mrr_rank;

-- 2) Find customers whose usage declined in three consecutive observed months.
WITH x AS (
  SELECT customer_id, usage_month, sessions,
         LAG(sessions,1) OVER (PARTITION BY customer_id ORDER BY usage_month) AS prev_1,
         LAG(sessions,2) OVER (PARTITION BY customer_id ORDER BY usage_month) AS prev_2
  FROM usage_monthly
)
SELECT customer_id, usage_month, sessions, prev_1, prev_2
FROM x
WHERE sessions < prev_1 AND prev_1 < prev_2
ORDER BY usage_month DESC, customer_id;

-- 3) Top 10 active accounts by MRR within each customer segment.
WITH ranked AS (
 SELECT c.segment,c.company_name,p.plan_name,s.monthly_recurring_revenue,
        ROW_NUMBER() OVER (PARTITION BY c.segment ORDER BY s.monthly_recurring_revenue DESC,c.company_name) AS rn
 FROM customers c JOIN subscriptions s USING(customer_id) JOIN plans p USING(plan_id)
 WHERE s.status='Active'
)
SELECT * FROM ranked WHERE rn<=10 ORDER BY segment,rn;

-- 4) Cancellation reason distribution by plan.
SELECT p.plan_name, s.cancellation_reason,
       COUNT(*) AS cancellations,
       ROUND(100.0*COUNT(*)/SUM(COUNT(*)) OVER (PARTITION BY p.plan_name),1) AS pct_within_plan
FROM subscriptions s JOIN plans p USING(plan_id)
WHERE s.status='Churned'
GROUP BY p.plan_name,s.cancellation_reason
ORDER BY p.plan_name,cancellations DESC;
