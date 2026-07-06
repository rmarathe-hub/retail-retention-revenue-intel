# Product & Market Analysis Notes

**Status:** Product and country marts implemented (`sql/08_product_market_analysis.sql`)  
**Marts:** `mart_product_performance`, `mart_country_performance`  
**Reference date:** 2011-12-09 (last date in dataset)

---

## Business Questions

1. Which products drive the most revenue and volume?
2. Where are cancellation rates highest on meaningful product lines?
3. How concentrated is revenue by country, and where is international growth opportunity?

---

## Definitions

| Term | Definition | Column / output |
|------|------------|-----------------|
| **Product revenue** | Sum of `line_revenue` on non-canceled lines per `stock_code` | `total_revenue` |
| **Product quantity** | Sum of `quantity` on non-canceled lines per `stock_code` | `total_quantity` |
| **Cancellation rate** | % of all staging lines for a `stock_code` flagged `is_canceled` | `cancellation_rate` |
| **Country revenue** | Sum of non-canceled `line_revenue` by `country` | `total_revenue` |
| **Country orders** | Distinct non-canceled invoices with valid `customer_id` | `total_orders` |
| **Active customers** | Distinct valid customers with non-canceled lines in country | `active_customers` |
| **UK revenue share** | UK `total_revenue` / sum of all country revenue | summary metric |

Administrative stock codes (`M` Manual, `D` Discount, `S` SAMPLES, `DOT`, `BANK CHARGES`) are included in the mart for completeness; filter them in Power BI when analysing sellable SKUs.

---

## Locked Summary Stats

| Metric | Value |
|--------|-------|
| Product mart rows | **5,304** stock codes |
| Country mart rows | **43** countries |
| Top product (`22423`) | **£344,069.30** revenue · 27,191 units · 7.86% cancellation |
| Top country (United Kingdom) | **£17,655,379.79** revenue · 33,546 orders · 5,346 active customers |
| UK revenue share (country mart) | **85.06%** |
| 2nd market (EIRE) | **£664,050.09** · 5 active customers |
| 3rd market (Netherlands) | **£554,230.69** · 22 active customers |

---

## SQL Implementation

| File | Purpose |
|------|---------|
| `sql/08_product_market_analysis.sql` | Populates product and country marts |
| `scripts/run_product_market_analysis.py` | Applies SQL and writes `product_market_summary.json` |

---

## Related Documentation

- [Metric Definitions](metric_definitions.md)
- [Recommendations](recommendations.md)
- [Power BI Dashboard Guide](powerbi_dashboard_guide.md) — Pages 5–6
