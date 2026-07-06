-- Retail Retention & Revenue Intelligence
-- Product and country performance marts
--
-- Product grain: stock_code (all staging lines).
-- Revenue and quantity on non-canceled lines only.
-- Cancellation rate = % of lines flagged is_canceled per stock_code.
-- Country grain: country; orders/customers require valid customer_id.

BEGIN;

TRUNCATE TABLE mart_product_performance, mart_country_performance;

WITH product_rollup AS (
    SELECT
        stock_code,
        MAX(description) AS description,
        ROUND(SUM(CASE WHEN is_canceled = FALSE THEN line_revenue ELSE 0 END)::numeric, 4) AS total_revenue,
        SUM(CASE WHEN is_canceled = FALSE THEN quantity ELSE 0 END)::integer AS total_quantity,
        ROUND(
            100.0 * SUM(CASE WHEN is_canceled THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0),
            4
        ) AS cancellation_rate
    FROM stg_transactions
    GROUP BY stock_code
)
INSERT INTO mart_product_performance (
    stock_code,
    description,
    total_revenue,
    total_quantity,
    cancellation_rate
)
SELECT
    stock_code,
    description,
    total_revenue,
    total_quantity,
    cancellation_rate
FROM product_rollup
ORDER BY stock_code;

WITH country_rollup AS (
    SELECT
        country,
        ROUND(SUM(CASE WHEN is_canceled = FALSE THEN line_revenue ELSE 0 END)::numeric, 4) AS total_revenue,
        COUNT(
            DISTINCT CASE
                WHEN is_canceled = FALSE AND customer_id IS NOT NULL THEN invoice_no
            END
        )::integer AS total_orders,
        COUNT(
            DISTINCT CASE
                WHEN is_canceled = FALSE AND customer_id IS NOT NULL THEN customer_id
            END
        )::integer AS active_customers
    FROM stg_transactions
    GROUP BY country
)
INSERT INTO mart_country_performance (
    country,
    total_revenue,
    total_orders,
    active_customers
)
SELECT
    country,
    total_revenue,
    total_orders,
    active_customers
FROM country_rollup
ORDER BY country;

COMMIT;
