# Metric Definitions

This document is the **source of truth** for KPI and analytical metric definitions. Each metric used in SQL marts or Power BI must appear here with definition, grain, and source table.

> **Status:** Executive KPI, revenue analysis, cohort retention, and **RFM segmentation** metrics locked through Day 8. Revenue-at-risk planned for Day 9.

---

## Global Rules (locked)

| Concept | Rule | Notes |
|---------|------|-------|
| **Order** | `COUNT(DISTINCT invoice_no)` where `is_canceled = FALSE` and `customer_id IS NOT NULL` | Canceled invoices (`C%` prefix) excluded |
| **Customer** | Valid non-null `customer_id` with at least one non-canceled order | 5,881 customers meet this criterion |
| **Cohort** | Customers grouped by first non-canceled `invoice_month` | 25 cohort months (2009-12 → 2011-12) |
| **Line revenue** | `quantity * unit_price` (stored as `line_revenue`) | Returns net via negative quantity; canceled lines excluded from KPI revenue |
| **Total revenue (company)** | `SUM(line_revenue)` where `is_canceled = FALSE` | Includes guest/non-registered lines (£20,755,215.33) |
| **Customer-attributed revenue** | `SUM(line_revenue)` where `is_canceled = FALSE` and `customer_id IS NOT NULL` | Used for AOV, repeat rate, and customer KPIs (£17,685,460.64) |
| **Reference date** | `2011-12-09` | Last date in dataset; used for recency and inactivity |
| **Repeat customer** | Customer with ≥ 2 distinct non-canceled orders | 72.35% of attributable customers |
| **New vs returning revenue** | New = revenue in customer's first `invoice_month`; returning = all later months | See `mart_monthly_revenue` |

---

## Day 6 Metrics (locked)

| Metric | Definition | Grain | Source Table | Status |
|--------|------------|-------|--------------|--------|
| Total Revenue | Sum of `line_revenue` on non-canceled lines (all rows) | Company | `mart_executive_kpis` (`total_revenue`) | **Locked** — £20,755,215.33 |
| Total Revenue (customer-attributed) | Sum of `line_revenue` on non-canceled lines with valid `customer_id` | Company | `mart_executive_kpis` (`total_revenue_customer_attributed`) | **Locked** — £17,685,460.64 |
| Total Orders | Distinct non-canceled invoices with valid `customer_id` | Invoice | `mart_executive_kpis` (`total_orders`) | **Locked** — 36,975 |
| Total Customers | Distinct customers with ≥1 non-canceled order | Customer | `mart_executive_kpis` (`total_customers`) | **Locked** — 5,881 |
| Monthly Revenue | Customer-attributed revenue by `invoice_month` | Month | `mart_monthly_revenue` | **Locked** — 25 months |
| Monthly Orders | Distinct non-canceled invoices per month (customer-attributed) | Month | `mart_monthly_revenue` | **Locked** |
| Monthly Active Customers | Distinct customers with ≥1 order in month | Month | `mart_monthly_revenue` | **Locked** |
| Average Order Value (AOV) | Customer-attributed revenue / total orders | Invoice | `mart_executive_kpis` (`average_order_value`) | **Locked** — £478.31 |
| Revenue per Customer | Customer-attributed revenue / total customers | Customer | `mart_executive_kpis` (`revenue_per_customer`) | **Locked** — £3,007.22 |
| Repeat Purchase Rate | % of customers with 2+ distinct orders | Customer | `mart_executive_kpis` (`repeat_purchase_rate`) | **Locked** — 72.35% |
| One-time Buyer Rate | % of customers with exactly 1 order | Customer | `mart_executive_kpis` (`one_time_buyer_rate`) | **Locked** — 27.65% |
| Cancellation Line Rate | % of all staging lines flagged `is_canceled` | Line | `mart_executive_kpis` (`cancellation_line_rate`) | **Locked** — 1.84% |
| New vs Returning Revenue | Monthly split of first-purchase vs repeat revenue | Month | `mart_monthly_revenue` | **Locked** |
| Customer Order Summary | Per-customer orders, revenue, first/last dates, repeat flag | Customer | `mart_customer_orders` | **Locked** — 5,881 rows |

---

## Day 7 Metrics (locked)

| Metric | Definition | Grain | Source Table | Status |
|--------|------------|-------|--------------|--------|
| Cohort Retention Rate | `retained_customers / cohort_size × 100` in activity month N | Cohort × month | `mart_cohort_retention` (`retention_rate`) | **Locked** — 325 rows |
| Revenue Retention Rate | `cohort_revenue in month N / cohort month-0 revenue × 100` | Cohort × month | `mart_cohort_retention` (`revenue_retention_rate`) | **Locked** |
| Months Since First Purchase | Month offset from cohort month to activity month | Cohort × month | `mart_cohort_retention` | **Locked** — 0 to 24 |
| Avg Month-3 Retention | Mean `retention_rate` where `months_since_first_purchase = 3` | Summary | `cohort_mart_summary.json` | **Locked** — 21.61% |
| Avg Month-3 Revenue Retention | Mean `revenue_retention_rate` at month 3 | Summary | `cohort_mart_summary.json` | **Locked** — 26.44% |

### SQL implementation

| File | Purpose |
|------|---------|
| `sql/03_kpi_definitions.sql` | Populates `mart_executive_kpis` (9 KPI rows) |
| `sql/04_revenue_analysis.sql` | Populates `mart_monthly_revenue` and `mart_customer_orders` |
| `sql/05_cohort_retention.sql` | Populates `mart_cohort_retention` (325 rows) |
| `scripts/run_kpi_marts.py` | Applies Day 6 SQL |
| `scripts/run_cohort_retention.py` | Applies Day 7 SQL and writes `cohort_mart_summary.json` |
| `scripts/export_powerbi_marts.py` | Exports populated marts to `data/marts/*.csv` |

---

## Day 8 Metrics (locked)

| Metric | Definition | Grain | Source Table | Status |
|--------|------------|-------|--------------|--------|
| RFM Recency | Days from last purchase to reference date (`2011-12-09`) | Customer | `mart_customer_rfm` (`recency_days`) | **Locked** — avg 200.99 days |
| RFM Frequency | Distinct non-canceled invoice count per customer | Customer | `mart_customer_rfm` (`frequency_orders`) | **Locked** — avg 6.29 orders |
| RFM Monetary | Total net revenue per customer on non-canceled lines | Customer | `mart_customer_rfm` (`monetary_value`) | **Locked** — avg £3,007.22 |
| RFM Scores | Quintile scores 1–5 for R, F, M | Customer | `mart_customer_rfm` (`r_score`, `f_score`, `m_score`) | **Locked** |
| Customer Segment | Rule-based RFM label (Champions, At Risk, etc.) | Customer | `mart_customer_rfm` (`customer_segment`) | **Locked** — 5,881 rows |
| Champions Count | Customers in `Champions` segment | Summary | `rfm_mart_summary.json` | **Locked** — 1,343 |
| At Risk Count | Customers in `At Risk` segment | Summary | `rfm_mart_summary.json` | **Locked** — 543 |

### SQL implementation

| File | Purpose |
|------|---------|
| `sql/06_rfm_segmentation.sql` | Populates `mart_customer_rfm` (5,881 rows) |
| `scripts/run_rfm_segmentation.py` | Applies Day 8 SQL and writes `rfm_mart_summary.json` |

---

## Planned Metrics (Day 9)

| Metric | Definition | Grain | Source Table | Status |
|--------|------------|-------|--------------|--------|
| Revenue at Risk | Historical spend from high-value inactive customers | Customer | `mart_revenue_at_risk` | Planned Day 9 |
| Inactive (90/120/180d) | No purchase for N+ days since last invoice | Customer | `mart_revenue_at_risk` | Planned Day 9 |
| Recoverable Revenue | Estimated revenue if X% of inactive customers reactivate | Scenario | `mart_revenue_at_risk` | Planned Day 9 |
| Top 1% / 10% Revenue Share | Revenue concentration from top customers by spend | Customer | `mart_revenue_at_risk` | Planned Day 9 |

---

## Related Documentation

- [Business Problem](business_problem.md)
- [Cohort Analysis Notes](cohort_analysis_notes.md)
- [RFM Analysis Notes](rfm_analysis_notes.md)
- [Data Quality Report](data_quality_report.md)
- [Data Dictionary](data_dictionary.md)
