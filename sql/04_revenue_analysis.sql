-- Retail Retention & Revenue Intelligence
-- Revenue analysis marts (Day 6)
--
-- Populates:
--   mart_monthly_revenue  — monthly revenue, orders, active customers, new vs returning split
--   mart_customer_orders  — per-customer order and revenue summary

BEGIN;

TRUNCATE TABLE mart_monthly_revenue, mart_customer_orders;

WITH customer_first_month AS (
    SELECT
        customer_id,
        MIN(invoice_month) AS first_purchase_month,
        MIN(invoice_date)::date AS first_order_date,
        MAX(invoice_date)::date AS last_order_date
    FROM stg_transactions
    WHERE is_canceled = FALSE
      AND customer_id IS NOT NULL
    GROUP BY customer_id
),
customer_monthly AS (
    SELECT
        t.invoice_month,
        t.customer_id,
        SUM(t.line_revenue) AS month_customer_revenue,
        COUNT(DISTINCT t.invoice_no) AS month_customer_orders
    FROM stg_transactions t
    WHERE t.is_canceled = FALSE
      AND t.customer_id IS NOT NULL
    GROUP BY t.invoice_month, t.customer_id
),
monthly_rollup AS (
    SELECT
        cm.invoice_month,
        ROUND(SUM(cm.month_customer_revenue)::numeric, 4) AS total_revenue,
        SUM(cm.month_customer_orders)::integer AS total_orders,
        COUNT(DISTINCT cm.customer_id)::integer AS active_customers,
        ROUND(SUM(
            CASE WHEN cm.invoice_month = cf.first_purchase_month
                 THEN cm.month_customer_revenue ELSE 0 END
        )::numeric, 4) AS new_customer_revenue,
        ROUND(SUM(
            CASE WHEN cm.invoice_month <> cf.first_purchase_month
                 THEN cm.month_customer_revenue ELSE 0 END
        )::numeric, 4) AS returning_customer_revenue
    FROM customer_monthly cm
    JOIN customer_first_month cf ON cm.customer_id = cf.customer_id
    GROUP BY cm.invoice_month
)
INSERT INTO mart_monthly_revenue (
    invoice_month,
    total_revenue,
    total_orders,
    active_customers,
    new_customer_revenue,
    returning_customer_revenue
)
SELECT
    invoice_month,
    total_revenue,
    total_orders,
    active_customers,
    new_customer_revenue,
    returning_customer_revenue
FROM monthly_rollup
ORDER BY invoice_month;

WITH customer_first_month AS (
    SELECT
        customer_id,
        MIN(invoice_month) AS first_purchase_month,
        MIN(invoice_date)::date AS first_order_date,
        MAX(invoice_date)::date AS last_order_date
    FROM stg_transactions
    WHERE is_canceled = FALSE
      AND customer_id IS NOT NULL
    GROUP BY customer_id
)
INSERT INTO mart_customer_orders (
    customer_id,
    total_orders,
    total_revenue,
    first_order_date,
    last_order_date,
    is_repeat_customer
)
SELECT
    cf.customer_id,
    COUNT(DISTINCT t.invoice_no)::integer AS total_orders,
    ROUND(SUM(t.line_revenue)::numeric, 4) AS total_revenue,
    cf.first_order_date,
    cf.last_order_date,
    (COUNT(DISTINCT t.invoice_no) >= 2) AS is_repeat_customer
FROM stg_transactions t
JOIN customer_first_month cf ON t.customer_id = cf.customer_id
WHERE t.is_canceled = FALSE
GROUP BY cf.customer_id, cf.first_order_date, cf.last_order_date;

COMMIT;
