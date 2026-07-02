# Data Quality Report — Online Retail II

**Status:** Week 1 Day 3 — cleaning pipeline implemented  
**Profiling script:** `scripts/profile_raw_data.py`  
**Raw data:** `data/raw/online_retail_II_combined.csv` (1,067,371 rows)
**Cleaning script:** `scripts/clean_online_retail.py`  
**Processed outputs:** `data/processed/retail_transactions_clean.csv` (**1,055,238 rows**), `data/processed/retail_transactions_customer_level.csv` (**812,368 rows**)

> Day 3 cleaning actions are now implemented; SQL validation and KPI-level impact continue on Day 4–6.

---

## Executive Summary

The UCI Online Retail II dataset is **real, large-scale, and messy** — appropriate for demonstrating production-style data cleaning. The most significant issue for this project is **22.77% of rows missing `Customer ID`**, which limits customer-level retention and RFM analysis unless explicitly filtered. Cancellations, returns, duplicates, and zero-price lines also require documented handling rules.

---

## Issues Found

| # | Issue | Count | % of rows | Severity | Day 3 handling |
|---|-------|-------|-----------|----------|------------------------|
| 1 | Missing `Customer ID` | 243,007 | 22.77% | **High** | Flag `is_missing_customer`; separate `customer_level` dataset excludes nulls |
| 2 | Canceled invoice lines (`C%`) | 19,494 | 1.83% | **High** | Flag `is_canceled`; retained in clean output for KPI-rule filtering later |
| 3 | Negative quantity (returns) | 22,950 | 2.15% | **Medium** | Flag `is_return`; retained for net-revenue logic |
| 4 | Exact duplicate rows | 12,133 | 1.14% | **Medium** | Removed exact duplicates (Day 3) |
| 5 | Zero unit price | 6,202 | 0.58% | **Medium** | Flag; exclude or review for revenue calcs |
| 6 | Negative unit price | 5 | ~0.00% | **Low** | Flag; likely data errors |
| 7 | Missing `Description` | 4,382 | 0.41% | **Low** | Filled with `Unknown`; flagged handling documented |
| 8 | High line-value outliers (>p99.9) | 1,067 | 0.10% | **Low** | Document; retain unless clearly erroneous |
| 9 | Missing country | 0 | 0.00% | — | No action needed |
| 10 | Invalid dates | 0 | 0.00% | — | No action needed |

---

## Issue Detail

### 1. Missing Customer ID (critical)

- **243,007 rows** (22.77%) have no `Customer ID`
- **Impact:** Cannot attribute these transactions to a customer for cohort retention, RFM, repeat rate, or inactivity analysis
- **Decision (implemented):** Created two outputs:
  - `retail_transactions_clean.csv` — all valid transaction lines
  - `retail_transactions_customer_level.csv` — only rows with non-null `customer_id`
- **Day 3 result:** 242,870 rows excluded from customer-level output after deduplication (23.02% of clean dataset)

### 2. Canceled Invoices

- **19,494 lines** across **8,292 distinct invoices** where `Invoice` starts with `C`
- Likely represent order cancellations in the source system
- **Decision (implemented):** Added `is_canceled` flag; retained rows in clean output so SQL KPI logic can include/exclude explicitly

### 3. Returns (negative quantity)

- **22,950 lines** with `Quantity < 0`
- Represent product returns or credit adjustments
- **Decision (implemented):** Added `is_return` flag and calculated `line_revenue = quantity * unit_price`

### 4. Duplicate Rows

- **12,133** exact duplicate rows detected
- **Decision (implemented):** Dropped exact duplicates before all downstream calculations

### 5. Pricing Anomalies

| Type | Count |
|------|-------|
| Zero price | 6,202 |
| Negative price | 5 |
| Line value > 99.9th percentile (£829.44) | 1,067 |

- **Decision (implemented):** Added `is_zero_or_negative_price` flag and retained rows for explicit KPI rule control; **do not silently drop** potentially valid wholesale transactions

---

## Profiling Summary (raw)

```
Row count:              1,067,371
Date range:             2009-12-01 → 2011-12-09
Distinct invoices:      53,628
Distinct customers:     5,942
Distinct stock codes:   5,305
Distinct countries:     43
UK row share:           92.0%
```

Full machine-readable output: `data/raw/profile_summary.json` (gitignored)

Day 4 load summary (after Postgres load): `data/processed/load_summary.json`

---

## Cleaning Actions Taken

| Action | Rows affected | Output |
|--------|---------------|--------|
| Removed exact duplicate rows | 12,133 removed | Both outputs |
| Standardized column names to snake_case | All rows | Both outputs |
| Parsed `invoice_date` + created `invoice_month` | All rows | Both outputs |
| Normalized `customer_id` to nullable string | All rows | Both outputs |
| Added flags: `is_canceled`, `is_return`, `is_missing_customer`, `is_zero_or_negative_price`, `is_invalid_invoice_date` | All rows | Both outputs |
| Filled missing descriptions with `Unknown` | 4,382 source rows impacted | Both outputs |
| Added `line_revenue = quantity * unit_price` | All rows | Both outputs |
| Built customer-level dataset with valid customer IDs only | 242,870 rows excluded | `retail_transactions_customer_level.csv` |

Day 3 machine-readable summary: `data/processed/cleaning_summary.json`

---

## Excluded from Customer Analysis

| Exclusion rule | Rows removed | Revenue impact |
|----------------|--------------|----------------|
| Null `Customer ID` after deduplication | 242,870 | KPI-level revenue impact calculated Day 5 SQL |

---

## Validation Checks (planned Day 5)

See `sql/02_data_quality_checks.sql` for SQL-based validation after load to Postgres.

---

## How to Reproduce Profiling + Cleaning

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python scripts/download_or_import_data.py
python scripts/profile_raw_data.py
python scripts/clean_online_retail.py
```

---

## Related Documentation

- [Data Dictionary](data_dictionary.md)
- [Metric Definitions](metric_definitions.md)
