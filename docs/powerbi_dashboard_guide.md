# Power BI Dashboard Guide

**Scope:** Pages 1–4 — Executive, Cohort, RFM Segmentation, Revenue Concentration & At-Risk  
**Data source:** CSV exports from `python scripts/export_powerbi_marts.py`  
**Refresh path:** Postgres marts → `data/marts/*.csv` → Power BI

---

## Prerequisites

```bash
source .venv/bin/activate
docker compose up -d
python scripts/load_to_postgres.py
python scripts/run_kpi_marts.py
python scripts/run_cohort_retention.py
python scripts/run_rfm_segmentation.py
python scripts/run_revenue_at_risk.py
python scripts/export_powerbi_marts.py
```

Exported files live in `data/marts/`. Manifest: `data/processed/powerbi_export_manifest.json`.

---

## Page 1 — Executive Revenue Overview

### Data tables

| Table | File | Grain |
|-------|------|-------|
| Executive KPIs | `mart_executive_kpis.csv` | One row per KPI |
| Monthly revenue | `mart_monthly_revenue.csv` | One row per `invoice_month` |

### Recommended visuals

| Visual | Fields | Notes |
|--------|--------|-------|
| Card — Total revenue | `kpi_value` where `kpi_name = total_revenue` | Format GBP |
| Card — Customer-attributed revenue | `kpi_name = total_revenue_customer_attributed` | £17,685,460.64 |
| Card — Total orders | `kpi_name = total_orders` | 36,975 |
| Card — AOV | `kpi_name = average_order_value` | £478.31 |
| Card — Repeat purchase rate | `kpi_name = repeat_purchase_rate` | 72.35% |
| Line chart — Monthly revenue | Axis: `invoice_month`, Values: `total_revenue` | 25 months |
| Clustered column — New vs returning | Axis: `invoice_month`, Values: `new_customer_revenue`, `returning_customer_revenue` | Split bars |
| Card — Active customers | `active_customers` max or latest month | Optional trend |

### Locked headline numbers (reference date 2011-12-09)

| KPI | Value |
|-----|-------|
| Total revenue | £20,755,215.33 |
| Customer-attributed revenue | £17,685,460.64 |
| Total orders | 36,975 |
| Total customers | 5,881 |
| AOV | £478.31 |
| Repeat purchase rate | 72.35% |
| One-time buyer rate | 27.65% |

### Formatting tips

- Use a single accent colour for revenue cards; neutral grey for counts.
- Sort `invoice_month` chronologically (text `YYYY-MM` sorts correctly).
- Add a subtitle: *UCI Online Retail II · Dec 2009 – Dec 2011*.

---

## Page 2 — Cohort Retention

### Data table

| Table | File | Grain |
|-------|------|-------|
| Cohort retention | `mart_cohort_retention.csv` | `(cohort_month, activity_month)` |

### Key columns

| Column | Use |
|--------|-----|
| `cohort_month` | Cohort slicer / legend |
| `months_since_first_purchase` | X-axis for retention curves |
| `retention_rate` | Primary retention metric (%) |
| `revenue_retention_rate` | Revenue decay metric (%) |
| `cohort_size` | Tooltip context |
| `retained_customers` | Tooltip / table detail |

### Recommended visuals

| Visual | Fields | Notes |
|--------|--------|-------|
| Line chart — Retention by months since | X: `months_since_first_purchase`, Y: avg `retention_rate`, Legend: `cohort_month` | Filter to key cohorts if busy |
| Line chart — Revenue retention | Same axis, `revenue_retention_rate` | Can exceed 100% |
| Matrix / table | Rows: `cohort_month`, Columns: `months_since_first_purchase`, Values: `retention_rate` | Heatmap-style conditional formatting |
| Card — Avg month-3 retention | Filter `months_since_first_purchase = 3`, avg `retention_rate` | **21.61%** |
| Card — Avg month-3 revenue retention | Filter month 3, avg `revenue_retention_rate` | **26.44%** |

### Interpretation

- Compare cohorts at the same `months_since_first_purchase` (apples-to-apples).
- Month 0 is always 100% retention by definition.
- Later cohorts have fewer observable months (right-censored at 2011-12-09).

---

## Page 3 — RFM Customer Segmentation

### Data table

| Table | File | Grain |
|-------|------|-------|
| RFM segments | `mart_customer_rfm.csv` | One row per customer (5,881) |

### Key columns

| Column | Use |
|--------|-----|
| `customer_segment` | Primary slicer / legend (Champions, At Risk, etc.) |
| `r_score`, `f_score`, `m_score` | Quintile scores 1–5 |
| `rfm_score` | Concatenated score string (e.g. `545`) |
| `recency_days` | Days since last purchase |
| `frequency_orders` | Distinct non-canceled orders |
| `monetary_value` | Total customer revenue (£) |

### Recommended visuals

| Visual | Fields | Notes |
|--------|--------|-------|
| Treemap or bar chart | Axis: `customer_segment`, Values: count of `customer_id` | Show segment distribution |
| Stacked bar — Revenue by segment | Axis: `customer_segment`, Values: sum `monetary_value` | Champions vs long tail |
| Card — Champions count | Filter `customer_segment = Champions` | **1,343** customers |
| Card — At Risk count | Filter `customer_segment = At Risk` | **543** customers |
| Card — Avg monetary | Average `monetary_value` | **£3,007.22** |
| Scatter plot | X: `recency_days`, Y: `monetary_value`, Legend: `customer_segment` | Spot high-value lapsed buyers |
| Table detail | `customer_id`, segment, scores, `monetary_value` | Drill-through for marketing lists |

### Locked segment distribution

| Segment | Customers |
|---------|-----------|
| Champions | 1,343 |
| Loyal Customers | 447 |
| At Risk | 543 |
| Hibernating | 906 |
| New Customers | 443 |
| Cannot Lose Them | 265 |
| About to Sleep | 639 |
| Potential Loyalists | 429 |
| Promising | 365 |
| Need Attention | 286 |
| Others | 215 |

### Interpretation

- **Champions** — recent, frequent, high spend; priority for loyalty/VIP programs.
- **At Risk** / **Cannot Lose Them** — historically valuable but lapsing; pair with page 4 win-back tiers.
- Segment rules and scoring: [rfm_analysis_notes.md](rfm_analysis_notes.md).

---

## Page 4 — Revenue Concentration & At-Risk Customers

### Data tables

| Table | File | Grain |
|-------|------|-------|
| Revenue at risk | `mart_revenue_at_risk.csv` | High-value inactive customers (291) |
| Customer orders | `mart_customer_orders.csv` | All valid customers (5,881) — for concentration |

### Key columns (`mart_revenue_at_risk`)

| Column | Use |
|--------|-----|
| `inactivity_window` | `90d`, `120d`, or `180d` tier |
| `days_since_last_purchase` | Sort / histogram |
| `historical_revenue` | Spend at risk per customer |
| `potential_recoverable_revenue` | 10% reactivation scenario per customer |
| `last_purchase_date` | Tooltip / table |

### Recommended visuals

| Visual | Fields | Notes |
|--------|--------|-------|
| Card — Total revenue at risk | Sum `historical_revenue` | **£1,791,355.34** |
| Card — Recoverable (10%) | Sum `potential_recoverable_revenue` | **£179,135.53** |
| Card — Top 10% revenue share | From `mart_customer_orders` Pareto | **64.04%** (see below) |
| Card — Top 1% revenue share | Pareto on `total_revenue` | **32.02%** |
| Clustered column — Inactivity tiers | Axis: `inactivity_window`, Values: count or sum revenue | 90d: 59 · 120d: 68 · 180d: 164 |
| Bar chart — Top at-risk customers | Top N by `historical_revenue` | Win-back target list |
| Pareto / line chart — Revenue concentration | `mart_customer_orders`: rank customers by `total_revenue`, cumulative % | Illustrates top 1% / 10% share |

### Building the concentration chart (`mart_customer_orders`)

1. Sort customers by `total_revenue` descending.
2. Compute running sum and cumulative % of total customer-attributed revenue.
3. Mark the 1% and 10% customer cutoffs — locked at **32.02%** and **64.04%** of revenue.

### Locked headline numbers

| Metric | Value |
|--------|-------|
| At-risk customers | 291 |
| Total revenue at risk | £1,791,355.34 |
| Recoverable revenue (10%) | £179,135.53 |
| Inactive high-value — 90d | 59 |
| Inactive high-value — 120d | 68 |
| Inactive high-value — 180d | 164 |
| Top 1% customer revenue share | 32.02% |
| Top 10% customer revenue share | 64.04% |

### Interpretation

- Revenue concentration is high — a small share of customers drives most attributable revenue.
- Prioritize **180d** tier for urgent win-back; **90d** tier for early intervention.
- Methodology: [revenue_at_risk_notes.md](revenue_at_risk_notes.md).

---

## File layout

```
dashboard/
├── README.md
├── Retail_Retention_Revenue_Intelligence.pbix   # create in Power BI Desktop
└── screenshots/
    ├── page1_executive_overview.png             # add after build
    ├── page2_cohort_retention.png
    ├── page3_rfm_segmentation.png
    └── page4_revenue_at_risk.png
```

---

## Related documentation

- [Metric Definitions](metric_definitions.md)
- [Cohort Analysis Notes](cohort_analysis_notes.md)
- [RFM Analysis Notes](rfm_analysis_notes.md)
- [Revenue at Risk Notes](revenue_at_risk_notes.md)
