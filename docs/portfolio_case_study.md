# Portfolio Case Study — Retail Retention & Revenue Intelligence

One-page narrative for interviews and README polish. All numbers locked from SQL marts (reference date **2011-12-09**).

---

## Elevator pitch (30 seconds)

I built an end-to-end retention analytics platform on **1M+ real UK e-commerce transactions** — cleaning messy data, loading Postgres, defining eight SQL marts, and designing a six-page Power BI executive dashboard. The analysis shows **72% repeat buyers**, high revenue concentration in the top 10%, and **£179K** in recoverable win-back opportunity from inactive high-value customers, with prioritized recommendations totaling **£500K–£750K** upside.

---

## Situation

UK online giftware retailer; leadership lacked a single source of truth for retention, segment value, and revenue risk.

## Task

Design a reproducible analytics pipeline and executive dashboard that marketing and leadership could act on.

## Actions

| Layer | What I did |
|-------|------------|
| Data | Profiled 1,067,371 rows; cleaned duplicates and flagged cancellations, returns, missing customers |
| Warehouse | Docker Postgres on port 5433; staging + dimension tables |
| Analytics | Cohort retention, RFM segmentation, revenue-at-risk, product/country performance marts |
| Quality | 27 automated DQ checks; locked metric definitions document |
| Delivery | CSV export manifest, Power BI build guide, recommendations with £ impact |

## Results

| Metric | Value |
|--------|-------|
| Repeat purchase rate | 72.35% |
| Month-3 cohort retention | 21.61% |
| Champions / At Risk (RFM) | 1,343 / 543 |
| Top 10% revenue share | 64.04% |
| Revenue at risk | £1,791,355 |
| Recoverable (10% scenario) | £179,135.53 |
| UK revenue concentration | 85.06% |

## Recommendation headline

Launch tiered win-back for **291** inactive high-value customers first, then VIP retention for Champions — full priority stack in [recommendations.md](recommendations.md).

---

## Links

- [README](../README.md)  
- [Metric definitions](metric_definitions.md)  
- [Power BI guide](powerbi_dashboard_guide.md)  
- [GitHub repo](https://github.com/rmarathe-hub/retail-retention-revenue-intel)
