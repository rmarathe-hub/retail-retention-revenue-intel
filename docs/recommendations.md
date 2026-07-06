# Executive Recommendations

Prioritized retention, revenue recovery, and growth actions derived from locked SQL marts (reference date **2011-12-09**). Impact estimates use conservative reactivation or uplift scenarios documented in each row.

---

## Summary

| Priority | Theme | Est. annual impact | Primary marts |
|----------|-------|-------------------|---------------|
| 1 | Win-back high-value inactive customers | **£179,136** recoverable (10% scenario) | `mart_revenue_at_risk`, `mart_customer_rfm` |
| 2 | Protect Champions and Cannot Lose Them | **£540,000+** revenue defended (30% of segment spend) | `mart_customer_rfm` |
| 3 | Convert one-time buyers before month 3 | **£380,000+** incremental LTV (10% of one-time cohort) | `mart_cohort_retention`, `mart_customer_orders` |
| 4 | Reduce product-line cancellations | **£50,000–£100,000** leakage reduction | `mart_product_performance` |
| 5 | Grow non-UK markets (Germany, France, Netherlands) | **£115,000+** (5% uplift on intl. revenue) | `mart_country_performance` |

**Combined upside (not additive):** roughly **£500K–£750K** in revenue recovery and growth if top three initiatives execute in parallel.

---

## 1. Launch tiered win-back for inactive high-value customers

**Evidence**

- **291** high-value customers inactive ≥90 days; **£1,791,355** historical spend at risk
- **10% reactivation scenario:** **£179,135.53** recoverable (`mart_revenue_at_risk`)
- **164** customers in the **180d** tier need urgent outreach; **59** in **90d** tier are early-warning

**Actions**

1. Export **180d** tier from `mart_revenue_at_risk` — personalized “we miss you” offer with free shipping
2. **90d** tier — automated email sequence before lapse becomes permanent
3. Pair with RFM **At Risk** (543) and **Cannot Lose Them** (265) segments for messaging tone

**Est. impact:** **£179,136** (locked 10% recoverable scenario)

---

## 2. VIP retention program for Champions and Cannot Lose Them

**Evidence**

- **1,343 Champions** — highest recency, frequency, and monetary scores
- **265 Cannot Lose Them** — historically high spend but slipping recency
- Top **10%** of customers drive **64.04%** of customer-attributed revenue

**Actions**

1. Early-access launches and loyalty points for Champions
2. Dedicated account touchpoints for Cannot Lose Them within 30 days of last purchase
3. Monitor month-3 cohort curves — Champions often originate from repeat buyers in first 90 days

**Est. impact:** Defend **30%** of combined segment revenue ≈ **£540,000+** (Champions + Cannot Lose Them monetary sum × 0.30)

---

## 3. First-90-day nurture for one-time buyers

**Evidence**

- **27.65%** of customers (1,626) made only one non-canceled order
- Month-3 cohort retention averages **21.61%**; revenue retention **26.44%**
- Repeat purchase rate among attributable customers is **72.35%** — significant upside in converting singles

**Actions**

1. Post-purchase email at day 14 and day 45 with cross-sell on top SKUs (`22423`, `85123A`, `85099B`)
2. Flag new customers in RFM **New Customers** (443) and **Potential Loyalists** (429) for second-order incentive
3. Track month-3 retention monthly in Power BI cohort heatmap

**Est. impact:** **10%** of one-time buyer lifetime value ≈ **£380,000+** (1,626 × £3,007 avg revenue × 10% conversion uplift)

---

## 4. Investigate high-cancellation product lines

**Evidence**

- Company-wide cancellation line rate: **1.84%** of staging lines
- Administrative / manual lines show elevated rates: **M** (Manual) **38.1%**, **AMAZONFEE** **90.7%**
- Sellable SKU **23843** shows **50%** cancellation on **£168,470** revenue — likely listing or fulfilment issue

**Actions**

1. Root-cause analysis on SKUs with **>20%** cancellation and **>£10K** revenue
2. Separate admin stock codes in reporting dashboards
3. Tighten invoice workflow for manual adjustments (`M`) to reduce erroneous cancels

**Est. impact:** **£50,000–£100,000** annual leakage reduction (25–50% of at-risk revenue on flagged SKUs)

---

## 5. Expand focused international growth (non-UK)

**Evidence**

- **85.06%** of country-mart revenue is United Kingdom — concentration risk
- Top non-UK markets: **EIRE** (£664K), **Netherlands** (£554K), **Germany** (£431K), **France** (£357K)
- Germany and France have **95–107** active customers vs. UK's **5,346** — room to grow share

**Actions**

1. Localized shipping and currency for DE/FR/NL
2. Country-specific bestseller bundles using `mart_product_performance` top SKUs
3. Set quarterly target: grow non-UK share from **15%** to **18%** of attributable revenue

**Est. impact:** **5%** uplift on **£2.3M** non-UK revenue ≈ **£115,000+**

---

## 6. Dashboard and operating rhythm

**Evidence**

- Six-page Power BI model covers executive KPIs, cohorts, RFM, at-risk, product/market, and this action plan
- All metrics refresh from Postgres marts via `export_powerbi_marts.py`

**Actions**

1. Weekly: review at-risk tier counts and RFM segment shifts
2. Monthly: cohort month-3 retention vs. **21.61%** benchmark
3. Quarterly: product cancellation outliers and country revenue mix

**Est. impact:** Enables measurement of initiatives 1–5; no direct £ attribution

---

## Data Sources

| Recommendation | Mart / doc |
|----------------|------------|
| Win-back | `mart_revenue_at_risk`, [revenue_at_risk_notes.md](revenue_at_risk_notes.md) |
| RFM segments | `mart_customer_rfm`, [rfm_analysis_notes.md](rfm_analysis_notes.md) |
| Cohort nurture | `mart_cohort_retention`, [cohort_analysis_notes.md](cohort_analysis_notes.md) |
| Product quality | `mart_product_performance`, [product_market_notes.md](product_market_notes.md) |
| International | `mart_country_performance`, [product_market_notes.md](product_market_notes.md) |
| KPI benchmarks | `mart_executive_kpis`, [metric_definitions.md](metric_definitions.md) |
