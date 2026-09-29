-- Run from the project root with psql so the relative paths resolve.
-- Example: psql -d portfolio -f sql/02_load_data.sql
SET search_path TO saas_analytics;

\copy plans FROM 'data/raw/plans.csv' WITH (FORMAT csv, HEADER true);
\copy customers FROM 'data/raw/customers.csv' WITH (FORMAT csv, HEADER true);
\copy subscriptions FROM 'data/raw/subscriptions.csv' WITH (FORMAT csv, HEADER true, NULL '');
\copy usage_monthly FROM 'data/raw/usage_monthly.csv' WITH (FORMAT csv, HEADER true);
\copy support_tickets FROM 'data/raw/support_tickets.csv' WITH (FORMAT csv, HEADER true);
\copy payments FROM 'data/raw/payments.csv' WITH (FORMAT csv, HEADER true);
