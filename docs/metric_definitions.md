# Metric Definitions

This document is the **source of truth** for KPI and analytical metric definitions. Each metric used in SQL marts or Power BI must appear here with definition, grain, and source table.

> **Status:** Week 1 Day 1 — index skeleton. Full definitions locked by **Day 6** before dashboard work.

---

## Metrics Index

| Metric | Definition | Grain | Source Table | Status |
|--------|------------|-------|--------------|--------|
| Total Revenue | Sum of `line_revenue` from valid transaction lines per revenue rules | Transaction line | `stg_transactions` | TBD |
| Total Orders | Count of distinct invoices (non-canceled) | Invoice | `stg_transactions` | TBD |
| Total Customers | Count of distinct `customer_id` where not null | Customer | `stg_transactions` | TBD |
| Monthly Revenue | Total revenue aggregated by invoice month | Month | `mart_monthly_revenue` | TBD |
| Monthly Orders | Distinct invoices per month | Month | `mart_monthly_revenue` | TBD |
| Monthly Active Customers | Distinct customers with at least one order in month | Month | `mart_monthly_revenue` | TBD |
| Average Order Value (AOV) | Total revenue / total orders | Invoice | `mart_executive_kpis` | TBD |
| Revenue per Customer | Total revenue / distinct customers | Customer | `mart_executive_kpis` | TBD |
| Repeat Purchase Rate | % of customers with 2+ distinct orders | Customer | `mart_customer_orders` | TBD |
| One-time Buyer Rate | % of customers with exactly 1 order | Customer | `mart_customer_orders` | TBD |
| Cancellation Rate | % of invoice lines or orders flagged as canceled | Invoice / line | `stg_transactions` | TBD |
| New vs Returning Revenue | Revenue split by first-time vs repeat purchasers in period | Month / customer | `mart_monthly_revenue` | TBD |
| Cohort Retention Rate | % of cohort active in month N after first purchase | Cohort × month | `mart_cohort_retention` | TBD |
| Revenue Retention Rate | Cohort revenue in month N / cohort revenue in month 0 | Cohort × month | `mart_cohort_retention` | TBD |
| RFM Recency | Days from last purchase to reference date (2011-12-09) | Customer | `mart_customer_rfm` | TBD |
| RFM Frequency | Distinct order count per customer | Customer | `mart_customer_rfm` | TBD |
| RFM Monetary | Total net revenue per customer | Customer | `mart_customer_rfm` | TBD |
| Customer Segment | RFM-based label (Champions, At Risk, etc.) | Customer | `mart_customer_rfm` | TBD |
| Revenue at Risk | Historical spend from high-value inactive customers | Customer | `mart_revenue_at_risk` | TBD |
| Inactive (90/120/180d) | No purchase for N+ days since last invoice | Customer | `mart_revenue_at_risk` | TBD |
| Recoverable Revenue | Estimated revenue if X% of inactive customers reactivate | Scenario | `mart_revenue_at_risk` | TBD |
| Top 1% / 10% Revenue Share | Revenue concentration from top customers by spend | Customer | `mart_revenue_at_risk` | TBD |

---

## Global Rules (to be finalized Day 3–6)

| Concept | Planned rule | Notes |
|---------|--------------|-------|
| **Order** | Distinct `invoice_no` | Exclude canceled invoices (`C%` prefix) — confirm in cleaning |
| **Customer** | Valid non-null `customer_id` | Customer-level metrics use `retail_transactions_customer_level` |
| **Line revenue** | `quantity * unit_price` | Returns (negative qty) handled explicitly |
| **Reference date** | 2011-12-09 | Last date in dataset; used for recency and inactivity |
| **Repeat customer** | Customer with ≥ 2 distinct orders | |

---

## Related Documentation

- [Business Problem](business_problem.md)
- [Cohort Analysis Notes](cohort_analysis_notes.md) — Day 7
- [RFM Segmentation Methodology](rfm_segmentation_methodology.md) — Day 8
- [Data Quality Report](data_quality_report.md) — Day 5
