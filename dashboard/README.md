# Dashboard

Power BI workbook and screenshots for the Retail Retention & Revenue Intelligence platform.

## Status

| Page | Name | Status |
|------|------|--------|
| 1 | Executive Revenue Overview | **Build guide ready** — [powerbi_dashboard_guide.md](../docs/powerbi_dashboard_guide.md) |
| 2 | Cohort Retention | **Build guide ready** |
| 3 | RFM Customer Segmentation | **Build guide ready** |
| 4 | Revenue Concentration & At-Risk | **Build guide ready** |
| 5 | Product & Market Performance | **Build guide ready** |
| 6 | Retention Action Plan | **Build guide ready** |

Workbook file: `Retail_Retention_Revenue_Intelligence.pbix` (create in Power BI Desktop).

## Data connection

1. Run `python scripts/export_powerbi_marts.py` from the project root.
2. In Power BI Desktop: **Get data → Text/CSV** and load files from `data/marts/`.
3. See `data/processed/powerbi_export_manifest.json` for row counts and export timestamps.

## Screenshots

Export PNGs to `screenshots/` after building each page. See [screenshots/README.md](screenshots/README.md) for filenames.

| Page | File |
|------|------|
| 1 | `screenshots/page1_executive_overview.png` |
| 2 | `screenshots/page2_cohort_retention.png` |
| 3 | `screenshots/page3_rfm_segmentation.png` |
| 4 | `screenshots/page4_revenue_at_risk.png` |
| 5 | `screenshots/page5_product_market.png` |
| 6 | `screenshots/page6_action_plan.png` |

Embed in the root [README.md](../README.md) once exported.

## Portfolio narrative

Interview-ready summary: [docs/portfolio_case_study.md](../docs/portfolio_case_study.md)
