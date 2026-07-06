# Power BI Dashboard Guide

**Scope:** Executive Revenue Overview (page 1) and Cohort Retention (page 2)  
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

## File layout

```
dashboard/
├── README.md
├── Retail_Retention_Revenue_Intelligence.pbix   # create in Power BI Desktop
└── screenshots/
    ├── page1_executive_overview.png             # add after build
    └── page2_cohort_retention.png
```

---

## Related documentation

- [Metric Definitions](metric_definitions.md)
- [Cohort Analysis Notes](cohort_analysis_notes.md)
- [Business Problem](business_problem.md)
