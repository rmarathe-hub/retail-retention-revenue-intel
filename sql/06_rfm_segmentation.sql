-- Retail Retention & Revenue Intelligence
-- RFM segmentation mart (Day 8)
--
-- Universe: valid customers with >=1 non-canceled order (same as mart_customer_orders).
-- Recency: days from last purchase to reference date 2011-12-09.
-- Frequency: distinct non-canceled invoice count per customer.
-- Monetary: sum of line_revenue on non-canceled lines per customer.
-- Scores: quintiles (1-5) via NTILE(5); higher score = better for retention value.
-- Segments: rule-based labels from R/F/M scores.

BEGIN;

TRUNCATE TABLE mart_customer_rfm;

WITH customer_orders AS (
    SELECT
        t.customer_id,
        COUNT(DISTINCT t.invoice_no)::integer AS frequency_orders,
        ROUND(SUM(t.line_revenue)::numeric, 4) AS monetary_value,
        MAX(t.invoice_date)::date AS last_order_date
    FROM stg_transactions t
    WHERE t.is_canceled = FALSE
      AND t.customer_id IS NOT NULL
    GROUP BY t.customer_id
),
customer_rfm AS (
    SELECT
        customer_id,
        (DATE '2011-12-09' - last_order_date)::integer AS recency_days,
        frequency_orders,
        monetary_value,
        NTILE(5) OVER (ORDER BY (DATE '2011-12-09' - last_order_date) DESC) AS r_score,
        NTILE(5) OVER (ORDER BY frequency_orders ASC) AS f_score,
        NTILE(5) OVER (ORDER BY monetary_value ASC) AS m_score
    FROM customer_orders
),
scored AS (
    SELECT
        customer_id,
        recency_days,
        frequency_orders,
        monetary_value,
        r_score,
        f_score,
        m_score,
        (r_score::text || f_score::text || m_score::text) AS rfm_score,
        CASE
            WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4 THEN 'Champions'
            WHEN r_score >= 3 AND f_score >= 4 AND m_score >= 4 THEN 'Loyal Customers'
            WHEN r_score >= 4 AND f_score <= 2 THEN 'New Customers'
            WHEN r_score >= 4 AND f_score = 3 THEN 'Potential Loyalists'
            WHEN r_score = 3 AND f_score <= 2 THEN 'Promising'
            WHEN r_score = 3 AND f_score = 3 THEN 'Need Attention'
            WHEN r_score = 2 AND f_score <= 2 THEN 'About to Sleep'
            WHEN r_score <= 2 AND f_score >= 4 AND m_score >= 4 THEN 'Cannot Lose Them'
            WHEN r_score <= 2 AND f_score >= 3 THEN 'At Risk'
            WHEN r_score <= 2 AND f_score <= 2 THEN 'Hibernating'
            ELSE 'Others'
        END AS customer_segment
    FROM customer_rfm
)
INSERT INTO mart_customer_rfm (
    customer_id,
    recency_days,
    frequency_orders,
    monetary_value,
    r_score,
    f_score,
    m_score,
    rfm_score,
    customer_segment
)
SELECT
    customer_id,
    recency_days,
    frequency_orders,
    monetary_value,
    r_score,
    f_score,
    m_score,
    rfm_score,
    customer_segment
FROM scored
ORDER BY customer_id;

COMMIT;
