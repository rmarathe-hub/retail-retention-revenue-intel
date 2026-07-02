-- Retail Retention & Revenue Intelligence
-- Executive KPI definitions (Day 6)
--
-- Business rules:
--   Revenue: SUM(line_revenue) on non-canceled lines (returns net via negative qty)
--   Orders:  COUNT(DISTINCT invoice_no) on non-canceled lines with valid customer_id
--   Customers: distinct customer_id on non-canceled lines
--   Reference date: 2011-12-09 (last date in dataset)

BEGIN;

TRUNCATE TABLE mart_executive_kpis;

WITH base AS (
    SELECT *
    FROM stg_transactions
    WHERE is_canceled = FALSE
),
customer_lines AS (
    SELECT *
    FROM base
    WHERE customer_id IS NOT NULL
),
customer_orders AS (
    SELECT
        customer_id,
        COUNT(DISTINCT invoice_no) AS order_count,
        SUM(line_revenue) AS customer_revenue
    FROM customer_lines
    GROUP BY customer_id
),
order_stats AS (
    SELECT COUNT(DISTINCT invoice_no) AS total_orders
    FROM customer_lines
),
customer_stats AS (
    SELECT
        COUNT(*) AS total_customers,
        COUNT(*) FILTER (WHERE order_count >= 2) AS repeat_customers,
        COUNT(*) FILTER (WHERE order_count = 1) AS one_time_customers
    FROM customer_orders
),
revenue_stats AS (
    SELECT
        ROUND(SUM(line_revenue)::numeric, 4) AS total_revenue,
        ROUND(SUM(line_revenue) FILTER (WHERE customer_id IS NOT NULL)::numeric, 4)
            AS total_revenue_customer_attributed
    FROM base
),
cancel_stats AS (
    SELECT COUNT(*)::numeric AS canceled_lines
    FROM stg_transactions
    WHERE is_canceled = TRUE
)
INSERT INTO mart_executive_kpis (kpi_name, kpi_value, kpi_unit, as_of_date)
SELECT 'total_revenue', total_revenue, 'GBP', DATE '2011-12-09' FROM revenue_stats
UNION ALL
SELECT 'total_revenue_customer_attributed', total_revenue_customer_attributed, 'GBP', DATE '2011-12-09'
FROM revenue_stats
UNION ALL
SELECT 'total_orders', total_orders::numeric, 'count', DATE '2011-12-09' FROM order_stats
UNION ALL
SELECT 'total_customers', total_customers::numeric, 'count', DATE '2011-12-09' FROM customer_stats
UNION ALL
SELECT
    'average_order_value',
    ROUND((SELECT total_revenue_customer_attributed FROM revenue_stats)
        / NULLIF((SELECT total_orders FROM order_stats), 0), 4),
    'GBP',
    DATE '2011-12-09'
UNION ALL
SELECT
    'revenue_per_customer',
    ROUND((SELECT total_revenue_customer_attributed FROM revenue_stats)
        / NULLIF((SELECT total_customers FROM customer_stats), 0), 4),
    'GBP',
    DATE '2011-12-09'
UNION ALL
SELECT
    'repeat_purchase_rate',
    ROUND(100.0 * repeat_customers / NULLIF(total_customers, 0), 4),
    'percent',
    DATE '2011-12-09'
FROM customer_stats
UNION ALL
SELECT
    'one_time_buyer_rate',
    ROUND(100.0 * one_time_customers / NULLIF(total_customers, 0), 4),
    'percent',
    DATE '2011-12-09'
FROM customer_stats
UNION ALL
SELECT
    'cancellation_line_rate',
    ROUND(100.0 * canceled_lines / NULLIF((SELECT COUNT(*) FROM stg_transactions), 0), 4),
    'percent',
    DATE '2011-12-09'
FROM cancel_stats;

COMMIT;
