# Data Dictionary — UCI Online Retail II

**Source:** [UCI Machine Learning Repository — Online Retail II](https://archive.ics.uci.edu/dataset/502/online+retail+ii)  
**Local raw files:** `data/raw/online_retail_II.xlsx`, `data/raw/online_retail_II_combined.csv`  
**Profiled:** Week 1 Day 2 (`python scripts/profile_raw_data.py`)

---

## Dataset Overview

| Attribute | Value |
|-----------|-------|
| Business | UK-based non-store online giftware retailer |
| Period | 2009-12-01 07:45:00 → 2011-12-09 12:50:00 |
| Total rows (combined) | **1,067,371** |
| Excel sheets | `Year 2009-2010` (525,461 rows), `Year 2010-2011` (541,910 rows) |
| Grain | One row per invoice line item |
| Distinct invoices | 53,628 |
| Distinct customers | 5,942 (non-null `Customer ID`) |
| Distinct stock codes | 5,305 |
| Distinct countries | 43 |

---

## Column Definitions

| Column | Type | Description | Example | Notes |
|--------|------|-------------|---------|-------|
| `Invoice` | string | Invoice number. Unique per order; canceled orders often prefixed with `C`. | `536365`, `C536379` | Join key for order-level metrics |
| `StockCode` | string | Product / item code | `85123A`, `POST` | 5,305 distinct values |
| `Description` | string | Product name | `WHITE HANGING HEART T-LIGHT HOLDER` | 4,382 missing (0.41%) |
| `Quantity` | integer | Units per line | `6`, `-6` | Negative = returns/adjustments |
| `InvoiceDate` | datetime | Date and time of invoice | `2010-12-01 08:26:00` | No invalid dates in raw file |
| `Price` | float | Unit price (£) | `2.55`, `0.00` | 6,202 zero-price lines; 5 negative |
| `Customer ID` | float/string | Customer identifier | `17850.0` | **243,007 missing (22.77%)** — critical for cohort/RFM |
| `Country` | string | Customer country | `United Kingdom` | No nulls in raw file |
| `source_sheet` | string | *(project-added)* Excel sheet origin | `Year 2009-2010` | Added during download/combine step |

---

## Derived Fields (Day 3 cleaning — implemented)

| Field | Formula / rule | Purpose |
|-------|----------------|---------|
| `line_revenue` | `quantity * unit_price` | Line-level revenue |
| `invoice_date` | parsed from `InvoiceDate` | Daily aggregation |
| `invoice_month` | `YYYY-MM` from `InvoiceDate` | Monthly trends, cohorts |
| `customer_id` | `Customer ID` as nullable string | Consistent customer key |
| `is_canceled` | `invoice_no` starts with `C` | Flag canceled invoices |
| `is_return` | `quantity < 0` | Flag return lines |
| `is_missing_customer` | `customer_id` IS NULL | Exclude from customer-level marts |
| `is_zero_or_negative_price` | `unit_price <= 0` | Flag zero/negative price lines |
| `is_invalid_invoice_date` | unparseable `InvoiceDate` | Flag bad dates (none in raw file) |

---

## Entity Relationships

```
Customer (Customer ID)
  └── Invoice (Invoice)
        └── Invoice Line (Invoice + StockCode + Quantity + Price)
              └── Product (StockCode → Description)
              └── Country (per line)
```

- **Order grain:** distinct `Invoice`
- **Customer grain:** distinct `Customer ID` (non-null only for retention analysis)
- **Line grain:** default row in dataset

---

## Geographic Coverage (top countries)

| Country | Row count | % of rows |
|---------|-----------|-----------|
| United Kingdom | 981,330 | 92.0% |
| EIRE | 17,866 | 1.7% |
| Germany | 17,624 | 1.7% |
| France | 14,330 | 1.3% |
| Netherlands | 5,140 | 0.5% |
| Other (38 countries) | 30,081 | 2.8% |

UK dominates volume — country analysis should note this concentration.

---

## Known Data Quirks

1. **Missing customer IDs** — 22.77% of rows; likely guest/non-registered or data entry gaps. Customer-level retention metrics require filtering.
2. **Canceled invoices** — 19,494 lines across 8,292 distinct `C%` invoices.
3. **Returns** — 22,950 lines with negative quantity.
4. **Duplicate rows** — 12,133 exact duplicate rows (to be removed Day 3).
5. **Zero unit price** — 6,202 lines (promotional, bundles, or data errors).
6. **High line values** — 1,067 lines above 99.9th percentile (~£829 line revenue).

---

## Related Documentation

- [Data Quality Report](data_quality_report.md)
- [Metric Definitions](metric_definitions.md)
- [Business Problem](business_problem.md)
