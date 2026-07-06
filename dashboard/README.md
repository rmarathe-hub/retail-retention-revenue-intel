# Dashboard

Power BI workbook and screenshots for the Retail Retention & Revenue Intelligence platform.

## Status

| Page | Name | Status |
|------|------|--------|
| 1 | Executive Revenue Overview | **Build guide ready** — see [powerbi_dashboard_guide.md](../docs/powerbi_dashboard_guide.md) |
| 2 | Cohort Retention | **Build guide ready** |
| 3 | RFM Customer Segmentation | Planned |
| 4 | Revenue Concentration & At-Risk | Planned |
| 5 | Product & Market Performance | Planned |
| 6 | Retention Action Plan | Planned |

## Data connection

1. Run `python scripts/export_powerbi_marts.py` from the project root.
2. In Power BI Desktop: **Get data → Text/CSV** and load files from `data/marts/`.
3. See `data/processed/powerbi_export_manifest.json` for row counts and export timestamps.

## Screenshots

Add PNG exports to `screenshots/` after building each page in Power BI Desktop.
