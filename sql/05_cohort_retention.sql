-- Retail Retention & Revenue Intelligence
-- Cohort retention mart (Day 7)
--
-- Cohort month = customer's first non-canceled purchase month.
-- Activity month = any month the customer placed a non-canceled order.
-- Retention rate = retained customers / cohort size.
-- Revenue retention rate = cohort revenue in activity month / cohort month-0 revenue.

BEGIN;

TRUNCATE TABLE mart_cohort_retention;

WITH customer_cohort AS (
    SELECT
        customer_id,
        MIN(invoice_month) AS cohort_month
    FROM stg_transactions
    WHERE is_canceled = FALSE
      AND customer_id IS NOT NULL
    GROUP BY customer_id
),
customer_activity AS (
    SELECT DISTINCT
        t.customer_id,
        t.invoice_month AS activity_month
    FROM stg_transactions t
    WHERE t.is_canceled = FALSE
      AND t.customer_id IS NOT NULL
),
cohort_activity AS (
    SELECT
        cc.cohort_month,
        ca.activity_month,
        (
            (EXTRACT(YEAR FROM TO_DATE(ca.activity_month || '-01', 'YYYY-MM-DD'))::integer * 12
             + EXTRACT(MONTH FROM TO_DATE(ca.activity_month || '-01', 'YYYY-MM-DD'))::integer)
            -
            (EXTRACT(YEAR FROM TO_DATE(cc.cohort_month || '-01', 'YYYY-MM-DD'))::integer * 12
             + EXTRACT(MONTH FROM TO_DATE(cc.cohort_month || '-01', 'YYYY-MM-DD'))::integer)
        ) AS months_since_first_purchase,
        ca.customer_id
    FROM customer_cohort cc
    JOIN customer_activity ca ON cc.customer_id = ca.customer_id
    WHERE ca.activity_month >= cc.cohort_month
),
cohort_sizes AS (
    SELECT
        cohort_month,
        COUNT(*)::integer AS cohort_size
    FROM customer_cohort
    GROUP BY cohort_month
),
retention_counts AS (
    SELECT
        ca.cohort_month,
        ca.activity_month,
        ca.months_since_first_purchase,
        cs.cohort_size,
        COUNT(DISTINCT ca.customer_id)::integer AS retained_customers
    FROM cohort_activity ca
    JOIN cohort_sizes cs ON ca.cohort_month = cs.cohort_month
    GROUP BY
        ca.cohort_month,
        ca.activity_month,
        ca.months_since_first_purchase,
        cs.cohort_size
),
cohort_month_revenue AS (
    SELECT
        cc.cohort_month,
        t.invoice_month AS activity_month,
        ROUND(SUM(t.line_revenue)::numeric, 4) AS cohort_revenue
    FROM stg_transactions t
    JOIN customer_cohort cc ON t.customer_id = cc.customer_id
    WHERE t.is_canceled = FALSE
      AND t.customer_id IS NOT NULL
    GROUP BY cc.cohort_month, t.invoice_month
),
cohort_month_zero_revenue AS (
    SELECT
        cohort_month,
        cohort_revenue AS month_zero_revenue
    FROM cohort_month_revenue
    WHERE activity_month = cohort_month
)
INSERT INTO mart_cohort_retention (
    cohort_month,
    activity_month,
    months_since_first_purchase,
    cohort_size,
    retained_customers,
    retention_rate,
    cohort_revenue,
    revenue_retention_rate
)
SELECT
    rc.cohort_month,
    rc.activity_month,
    rc.months_since_first_purchase,
    rc.cohort_size,
    rc.retained_customers,
    ROUND(100.0 * rc.retained_customers / NULLIF(rc.cohort_size, 0), 4) AS retention_rate,
    COALESCE(cmr.cohort_revenue, 0) AS cohort_revenue,
    ROUND(
        100.0 * COALESCE(cmr.cohort_revenue, 0) / NULLIF(czr.month_zero_revenue, 0),
        4
    ) AS revenue_retention_rate
FROM retention_counts rc
LEFT JOIN cohort_month_revenue cmr
    ON rc.cohort_month = cmr.cohort_month
   AND rc.activity_month = cmr.activity_month
LEFT JOIN cohort_month_zero_revenue czr
    ON rc.cohort_month = czr.cohort_month
ORDER BY rc.cohort_month, rc.activity_month;

COMMIT;
