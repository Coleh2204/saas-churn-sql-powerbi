# Power BI Dashboard Build Guide

## Page 1 — Executive Overview

**Purpose:** Give leadership a fast view of scale, growth, and current retention health.

**Top KPI cards**
- Active Customers — `6,208`
- Current MRR — `$732.4K`
- Current ARR — `$8.79M`
- Current ARPA — `$117.98`
- Latest Logo Churn Rate — `1.97%`

**Visuals**
1. Line chart: `month_start` vs `mrr_end`.
2. Combo chart: `month_start`, `new_customers`, `churned_customers`.
3. Bar chart: active MRR by `plan_name`.
4. Bar chart: observed churn share by `plan_name`.
5. Slicers: Segment, Plan, Country, Acquisition Channel.

**Callout:** August 2026 ended at roughly $732K MRR while monthly logo churn remained near 2%.

---

## Page 2 — Retention & Cohorts

**Purpose:** Show whether customers remain subscribed after signup.

**Visuals**
1. Cohort matrix / heatmap:
   - Rows: `signup_cohort`
   - Columns: `month_number`
   - Values: `retention_rate`
   - Conditional formatting: background-color scale.
2. Retention curve: `month_number` vs average `retention_rate`.
3. Cards: average month-6 retention (`~88.9%`) and month-12 retention (`~78.9%`).
4. Bar chart: churn share by acquisition channel.

**Interpretation:** Retention is strong early, then gradually decays; the first-year retention curve is a more useful long-run health measure than a single churn-month snapshot.

---

## Page 3 — Churn Drivers

**Purpose:** Identify behavioral signals associated with churn.

**Visuals**
1. Column chart: churn share by recent usage-trend band.
2. Column chart: churn share by support-ticket band.
3. Two-column comparison: failed payment vs no failed payment.
4. Line chart: `months_before_churn` vs `avg_sessions`.
5. Bar chart: `cancellation_reason` by count.

**Validated signals in this synthetic dataset**
- Severe 3-month usage decline: ~84.1% observed churn share.
- Stable recent usage: ~8.0% observed churn share.
- 4+ tickets in the trailing 90 days: ~61.6% observed churn share.
- Any failed payment in the trailing 90 days: ~49.5% observed churn share vs ~20.0% without one.
- Average sessions among churned customers fall from roughly 77–78 six-to-three months before churn to ~43 in the churn month.

These are associations built into a synthetic learning dataset, not causal estimates.

---

## Page 4 — Customer Risk Explorer

**Purpose:** Let an analyst or customer-success manager identify accounts worth reviewing.

Use `vw_customer_360`.

**Table columns**
- company_name
- plan_name
- segment
- monthly_recurring_revenue
- avg_sessions_last_3m
- usage_change_last_3m
- tickets_last_90d
- failed_payments_last_90d
- status

**Suggested conditional formatting**
- Usage change <= -40%: strong warning icon.
- Tickets >= 4: warning icon.
- Failed payments > 0: warning icon.
- MRR: data bars.

**Optional calculated column**

```DAX
Risk Band =
SWITCH(
    TRUE(),
    vw_customer_360[status] = "Churned", "Churned",
    vw_customer_360[usage_change_last_3m] <= -0.40
        || vw_customer_360[failed_payments_last_90d] > 0
        || vw_customer_360[tickets_last_90d] >= 4, "High",
    vw_customer_360[usage_change_last_3m] <= -0.15
        || vw_customer_360[tickets_last_90d] >= 2, "Medium",
    "Low"
)
```

Add slicers for plan, segment, industry, country, acquisition channel, and risk band.
