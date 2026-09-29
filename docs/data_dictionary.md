# Data Dictionary

All records are synthetic and were generated specifically for this portfolio project.

## customers
One row per customer account.
- `customer_id`: unique customer key.
- `company_name`: synthetic account name.
- `country`: account country.
- `industry`: account industry.
- `segment`: SMB, Mid-Market, or Enterprise.
- `acquisition_channel`: first-touch acquisition source.
- `signup_date`: date the account started.

## plans
One row per subscription plan.
- `plan_id`, `plan_name`
- `monthly_price`: list monthly price.
- `included_seats`: nominal seats included.
- `plan_description`

## subscriptions
One row per customer subscription.
- `subscription_id`, `customer_id`, `plan_id`
- `start_date`
- `billing_cycle`: Monthly or Annual.
- `monthly_recurring_revenue`: normalized monthly recurring revenue; annual plans receive a 15% equivalent discount.
- `status`: Active or Churned as of 2026-08-31.
- `churn_date`
- `cancellation_reason`

## usage_monthly
One row per customer-month.
- `sessions`
- `active_users`
- `features_used`
- `storage_gb`

## support_tickets
One row per support ticket.
- category, priority, resolution hours, and CSAT score.

## payments
One row per invoice/payment attempt.
- `amount`
- `payment_status`: Paid or Failed.
- `payment_method`: Card, ACH, or Invoice.

## customer_churn_features.csv
A prepared analytical feature table using each churned customer's cancellation date, or 2026-08-31 for active accounts, as the reference point.
