# Cohort Analysis Notes

**Status:** Cohort retention mart implemented (`sql/05_cohort_retention.sql`)  
**Mart:** `mart_cohort_retention`  
**Reference date:** 2011-12-09 (last date in dataset)

---

## Business Question

Which customer cohorts retain best after first purchase, and how quickly does revenue from each cohort decay over time?

---

## Cohort Definition

| Term | Definition |
|------|------------|
| **Cohort month** | `MIN(invoice_month)` per customer on non-canceled orders |
| **Activity month** | Any `invoice_month` where the customer placed a non-canceled order |
| **Cohort size** | Distinct customers whose first purchase month equals the cohort month |
| **Retained customer** | Cohort member with ≥1 order in the activity month |

Customers with null `customer_id` are excluded (see [data quality report](data_quality_report.md)).

---

## Metrics

| Metric | Formula | Column |
|--------|---------|--------|
| **Cohort Retention Rate** | `retained_customers / cohort_size × 100` | `retention_rate` |
| **Revenue Retention Rate** | `cohort_revenue in activity month / cohort month-0 revenue × 100` | `revenue_retention_rate` |
| **Months since first purchase** | Month index from cohort month to activity month | `months_since_first_purchase` |

Month 0 (`activity_month = cohort_month`) always has retention rate = 100% by definition.

---

## Mart Grain

One row per `(cohort_month, activity_month)` where `activity_month >= cohort_month`.

| Column | Type | Description |
|--------|------|-------------|
| `cohort_month` | TEXT | `YYYY-MM` first-purchase month |
| `activity_month` | TEXT | `YYYY-MM` activity month |
| `months_since_first_purchase` | INTEGER | 0 = cohort month |
| `cohort_size` | INTEGER | Customers in cohort |
| `retained_customers` | INTEGER | Active cohort members in activity month |
| `retention_rate` | NUMERIC | % of cohort retained |
| `cohort_revenue` | NUMERIC | Revenue from cohort in activity month (£) |
| `revenue_retention_rate` | NUMERIC | % of month-0 revenue |

---

## Interpretation Guidelines

1. **Compare cohorts at the same `months_since_first_purchase`** — e.g. month-3 retention for all 2010 cohorts.
2. **Seasonality** — Dec 2009 / Dec 2010 cohorts may spike around holidays; note in dashboard commentary.
3. **UK concentration** — ~92% of rows are UK; cohort behavior may not generalize globally.
4. **Revenue retention can exceed 100%** — repeat buyers spending more than their first month lifts revenue retention above 100%.

---

## How to Reproduce

```bash
source .venv/bin/activate
docker compose up -d
python scripts/load_to_postgres.py
python scripts/run_kpi_marts.py
python scripts/run_cohort_retention.py
python scripts/export_powerbi_marts.py
```

---

## Related Documentation

- [Metric Definitions](metric_definitions.md)
- [Business Problem](business_problem.md)
- [Data Dictionary](data_dictionary.md)
