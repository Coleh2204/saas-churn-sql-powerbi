# Validation Summary

All automated integrity checks passed.

## Row counts

| Table | Rows |
|---|---:|
| `customers` | 8,000 |
| `plans` | 4 |
| `subscriptions` | 8,000 |
| `usage_monthly` | 98,411 |
| `support_tickets` | 20,559 |
| `payments` | 71,584 |

## Integrity checks

| Check | Result |
|---|---|
| Unique customer IDs | PASS |
| Unique subscription IDs | PASS |
| One subscription per customer | PASS |
| Unique usage customer-month | PASS |
| Unique ticket IDs | PASS |
| Unique payment IDs | PASS |
| Subscription customer FKs valid | PASS |
| Subscription plan FKs valid | PASS |
| Usage customer FKs valid | PASS |
| Ticket customer FKs valid | PASS |
| Payment customer FKs valid | PASS |
| Active subscriptions have no churn date | PASS |
| Churned subscriptions have churn date | PASS |

## KPI reconciliation

- Active customers: **6,208**
- Current MRR: **$732,430.75**
- Current ARR: **$8,789,169.00**
- August 2026 logo churn: **1.97%**

The CSV outputs were regenerated from the raw synthetic tables after the final realism/noise adjustment.