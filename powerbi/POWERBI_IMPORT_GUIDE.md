# Connecting Power BI

## Preferred route: PostgreSQL

1. Run the SQL scripts `01` through `08` in order.
2. In Power BI Desktop choose **Get Data → PostgreSQL database**.
3. Connect to your local database.
4. Import:
   - `customers`
   - `plans`
   - `subscriptions`
   - `usage_monthly`
   - `support_tickets`
   - `payments`
   - `vw_customer_360`
   - `vw_monthly_business_metrics`
   - `vw_usage_before_churn`
5. Create the relationships documented in `model_relationships.md`.
6. Add the Date table from `date_table.dax`.
7. Add the measures from `measures.dax`.
8. Build the four pages in `dashboard_build_guide.md`.

## No database installed?

You can still build the dashboard by importing the CSVs in `data/raw` plus the prepared CSVs in `outputs` and `data/processed`. The database route is recommended because the purpose of this project is to demonstrate SQL as part of the analytical workflow.

## Important

A `.pbix` file is not included because Power BI Desktop is required to create and save a valid PBIX package. The supplied model, views, DAX, and page specification are intended to make the Desktop build straightforward and auditable.
