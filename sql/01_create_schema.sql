-- SaaS Subscription & Churn Analytics
-- PostgreSQL 15+

DROP SCHEMA IF EXISTS saas_analytics CASCADE;
CREATE SCHEMA saas_analytics;
SET search_path TO saas_analytics;

CREATE TABLE plans (
    plan_id TEXT PRIMARY KEY,
    plan_name TEXT NOT NULL UNIQUE,
    monthly_price NUMERIC(10,2) NOT NULL CHECK (monthly_price > 0),
    included_seats INTEGER NOT NULL CHECK (included_seats > 0),
    plan_description TEXT
);

CREATE TABLE customers (
    customer_id TEXT PRIMARY KEY,
    company_name TEXT NOT NULL,
    country TEXT NOT NULL,
    industry TEXT NOT NULL,
    segment TEXT NOT NULL CHECK (segment IN ('SMB','Mid-Market','Enterprise')),
    acquisition_channel TEXT NOT NULL,
    signup_date DATE NOT NULL
);

CREATE TABLE subscriptions (
    subscription_id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL UNIQUE REFERENCES customers(customer_id),
    plan_id TEXT NOT NULL REFERENCES plans(plan_id),
    start_date DATE NOT NULL,
    billing_cycle TEXT NOT NULL CHECK (billing_cycle IN ('Monthly','Annual')),
    monthly_recurring_revenue NUMERIC(10,2) NOT NULL CHECK (monthly_recurring_revenue >= 0),
    status TEXT NOT NULL CHECK (status IN ('Active','Churned')),
    churn_date DATE,
    cancellation_reason TEXT,
    CHECK (
      (status = 'Active' AND churn_date IS NULL)
      OR (status = 'Churned' AND churn_date IS NOT NULL)
    ),
    CHECK (churn_date IS NULL OR churn_date >= start_date)
);

CREATE TABLE usage_monthly (
    customer_id TEXT NOT NULL REFERENCES customers(customer_id),
    usage_month DATE NOT NULL,
    sessions INTEGER NOT NULL CHECK (sessions >= 0),
    active_users INTEGER NOT NULL CHECK (active_users >= 0),
    features_used INTEGER NOT NULL CHECK (features_used >= 0),
    storage_gb NUMERIC(12,2) NOT NULL CHECK (storage_gb >= 0),
    PRIMARY KEY (customer_id, usage_month)
);

CREATE TABLE support_tickets (
    ticket_id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL REFERENCES customers(customer_id),
    created_date DATE NOT NULL,
    category TEXT NOT NULL,
    priority TEXT NOT NULL CHECK (priority IN ('Low','Medium','High','Urgent')),
    resolution_hours NUMERIC(10,2) NOT NULL CHECK (resolution_hours >= 0),
    csat_score NUMERIC(3,1) NOT NULL CHECK (csat_score BETWEEN 1 AND 5)
);

CREATE TABLE payments (
    payment_id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL REFERENCES customers(customer_id),
    payment_date DATE NOT NULL,
    amount NUMERIC(12,2) NOT NULL CHECK (amount >= 0),
    payment_status TEXT NOT NULL CHECK (payment_status IN ('Paid','Failed')),
    payment_method TEXT NOT NULL CHECK (payment_method IN ('Card','ACH','Invoice'))
);

CREATE INDEX idx_subscriptions_customer ON subscriptions(customer_id);
CREATE INDEX idx_subscriptions_churn ON subscriptions(churn_date);
CREATE INDEX idx_usage_month ON usage_monthly(usage_month);
CREATE INDEX idx_usage_customer ON usage_monthly(customer_id);
CREATE INDEX idx_tickets_customer_date ON support_tickets(customer_id, created_date);
CREATE INDEX idx_payments_customer_date ON payments(customer_id, payment_date);
