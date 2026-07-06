# Revenue at Risk Analysis Notes

**Status:** Revenue-at-risk mart implemented (`sql/07_revenue_at_risk.sql`)  
**Mart:** `mart_revenue_at_risk`  
**Reference date:** 2011-12-09 (last date in dataset)

---

## Business Question

How much historical spend is tied up in high-value customers who have gone inactive, and what revenue might be recoverable through win-back campaigns?

---

## Customer Universe

Same valid-customer rules as Day 6–8:

- Non-null `customer_id`
- At least one non-canceled order
- Revenue and last-purchase date computed on non-canceled lines only

---

## Definitions

| Term | Definition | Column / output |
|------|------------|-----------------|
| **Historical revenue** | Total `line_revenue` on non-canceled lines per customer | `historical_revenue` |
| **Days since last purchase** | Reference date minus last non-canceled `invoice_date` | `days_since_last_purchase` |
| **High-value customer** | Top revenue quartile (`NTILE(4) = 4`) among all valid customers | filter rule |
| **Inactive (90d / 120d / 180d)** | No purchase for ≥90, ≥120, or ≥180 days | `inactivity_window` |
| **Revenue at risk** | Sum of `historical_revenue` for high-value inactive customers | summary metric |
| **Recoverable revenue (10%)** | `historical_revenue × 0.10` per customer | `potential_recoverable_revenue` |
| **Top 1% / 10% revenue share** | Share of customer-attributed revenue from top spenders | summary metric from `mart_customer_orders` |

### Inactivity window labels

| Window | Rule |
|--------|------|
| `90d` | 90–119 days since last purchase |
| `120d` | 120–179 days since last purchase |
| `180d` | 180+ days since last purchase |

Only customers who are **both** high-value and inactive for at least 90 days appear in the mart.

---

## Locked Summary Stats

| Metric | Value |
|--------|-------|
| Mart rows | **291** |
| Total revenue at risk | **£1,791,355.34** |
| Recoverable revenue (10% scenario) | **£179,135.53** |
| Inactive high-value — 90d window | **59** |
| Inactive high-value — 120d window | **68** |
| Inactive high-value — 180d window | **164** |
| Top 1% customer revenue share | **32.02%** |
| Top 10% customer revenue share | **64.04%** |

Full run output: `data/processed/revenue_at_risk_summary.json`

---

## How to Reproduce

```bash
source .venv/bin/activate
docker compose up -d
python scripts/load_to_postgres.py
python scripts/run_kpi_marts.py
python scripts/run_rfm_segmentation.py
python scripts/run_revenue_at_risk.py
python scripts/export_powerbi_marts.py
```

---

## Related Documentation

- [Metric Definitions](metric_definitions.md)
- [RFM Analysis Notes](rfm_analysis_notes.md)
- [Business Problem](business_problem.md)
