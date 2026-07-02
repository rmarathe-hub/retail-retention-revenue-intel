# Business Problem

## Context

A UK-based online retailer specializing in giftware operates without physical stores. Leadership has years of transaction history but lacks a unified view of **customer retention**, **repeat purchase behavior**, and **revenue risk**.

This project builds an analytics platform to turn messy transaction data into decisions marketing, product, and executive teams can act on.

## Stakeholders

| Stakeholder | Interest |
|-------------|----------|
| **Executive leadership** | Revenue trends, concentration risk, inactive high-value customers |
| **Marketing** | Win-back campaigns, lifecycle emails, loyalty program targeting |
| **Product / operations** | Top products, cancellation patterns, country performance |

## Core Questions

1. **Retention** — Which customers return after their first purchase? How does retention vary by cohort?
2. **Repeat behavior** — What share of revenue comes from repeat vs one-time buyers?
3. **Inactivity** — Who are high-value customers with no recent purchase (90 / 120 / 180 days)?
4. **Concentration** — How much revenue is driven by the top 1% and 10% of customers?
5. **Product & market** — Which products and countries drive performance? Where are cancellations concentrated?
6. **Action** — Which segments should be targeted, with what expected revenue impact?

## Decisions This Project Supports

- **Win-back campaigns** for high-value inactive customers
- **Post-purchase email flows** for one-time buyers
- **VIP / loyalty programs** for Champions and loyal segments
- **Product and inventory review** for high-cancellation SKUs
- **Market focus** by country revenue and seasonality

## Success Criteria

- Metrics are **defined, documented, and traceable** from SQL marts to the dashboard
- Data quality issues are **documented with explicit cleaning decisions**
- Recommendations include **prioritized actions** and **estimated recoverable revenue** (e.g. 10% reactivation scenario)
- A reviewer can understand the business story and key findings in **under 60 seconds** from the README

## Dataset

**UCI Online Retail II** — real online retail transactions from a UK non-store retailer:

- **Period:** December 1, 2009 – December 9, 2011
- **Scale:** ~1,067,371 transaction records (per UCI)
- **Characteristics:** Missing values, cancellations, returns, duplicate lines — representative of real-world retail data
