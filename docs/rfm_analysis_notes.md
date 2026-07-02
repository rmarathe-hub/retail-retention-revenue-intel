# RFM Analysis Notes

**Status:** RFM segmentation mart implemented (`sql/06_rfm_segmentation.sql`)  
**Mart:** `mart_customer_rfm`  
**Reference date:** 2011-12-09 (last date in dataset)

---

## Business Question

Which customers are most valuable and active, and which segments need win-back or loyalty campaigns?

---

## Customer Universe

Same as Day 6 customer metrics:

- Valid non-null `customer_id`
- At least one non-canceled order (`is_canceled = FALSE`)
- **5,881 customers**

---

## RFM Definitions

| Term | Definition | Column |
|------|------------|--------|
| **Recency** | Days from last purchase to reference date (`2011-12-09`) | `recency_days` |
| **Frequency** | Distinct non-canceled invoice count per customer | `frequency_orders` |
| **Monetary** | Sum of `line_revenue` on non-canceled lines per customer | `monetary_value` |
| **R / F / M scores** | Quintile scores 1–5 via `NTILE(5)`; higher = better | `r_score`, `f_score`, `m_score` |
| **RFM score** | Concatenated `R` + `F` + `M` (e.g. `545`) | `rfm_score` |
| **Customer segment** | Rule-based label from R/F/M scores | `customer_segment` |

### Scoring rules

| Dimension | NTILE ordering | Interpretation |
|-----------|----------------|----------------|
| Recency | `ORDER BY recency_days DESC` | Lower days (more recent) → higher R score |
| Frequency | `ORDER BY frequency_orders ASC` | More orders → higher F score |
| Monetary | `ORDER BY monetary_value ASC` | More revenue → higher M score |

Returns net through negative `line_revenue`; canceled invoices excluded from frequency and monetary.

---

## Segment Labels

| Segment | Rule (simplified) |
|---------|-------------------|
| Champions | R≥4, F≥4, M≥4 |
| Loyal Customers | R≥3, F≥4, M≥4 |
| New Customers | R≥4, F≤2 |
| Potential Loyalists | R≥4, F=3 |
| Promising | R=3, F≤2 |
| Need Attention | R=3, F=3 |
| About to Sleep | R=2, F≤2 |
| Cannot Lose Them | R≤2, F≥4, M≥4 |
| At Risk | R≤2, F≥3 |
| Hibernating | R≤2, F≤2 |
| Others | Remaining combinations |

---

## Locked Summary Stats

| Metric | Value |
|--------|-------|
| Mart rows | **5,881** |
| Champions | **1,343** |
| At Risk | **543** |
| Avg recency (days) | **200.99** |
| Avg frequency (orders) | **6.29** |
| Avg monetary (£) | **£3,007.22** |

Segment distribution is stored in `data/processed/rfm_mart_summary.json`.

---

## How to Reproduce

```bash
source .venv/bin/activate
docker compose up -d
python scripts/load_to_postgres.py
python scripts/run_kpi_marts.py
python scripts/run_cohort_retention.py
python scripts/run_rfm_segmentation.py
python scripts/export_powerbi_marts.py
```

---

## Related Documentation

- [Metric Definitions](metric_definitions.md)
- [Cohort Analysis Notes](cohort_analysis_notes.md)
- [Data Dictionary](data_dictionary.md)
