-- Retail Retention & Revenue Intelligence
-- Revenue at risk mart (Day 9)
--
-- High-value = top revenue quartile (NTILE 4) among valid customers.
-- Inactive = no non-canceled purchase within 90+ days of reference date 2011-12-09.
-- Recoverable revenue = 10% reactivation scenario on historical spend.

BEGIN;

TRUNCATE TABLE mart_revenue_at_risk;

WITH customer_activity AS (
    SELECT
        t.customer_id,
        MAX(t.invoice_date)::date AS last_purchase_date,
        ROUND(SUM(t.line_revenue)::numeric, 4) AS historical_revenue
    FROM stg_transactions t
    WHERE t.is_canceled = FALSE
      AND t.customer_id IS NOT NULL
    GROUP BY t.customer_id
),
scored AS (
    SELECT
        customer_id,
        last_purchase_date,
        historical_revenue,
        (DATE '2011-12-09' - last_purchase_date)::integer AS days_since_last_purchase,
        NTILE(4) OVER (ORDER BY historical_revenue ASC) AS revenue_quartile
    FROM customer_activity
),
high_value_inactive AS (
    SELECT
        customer_id,
        last_purchase_date,
        days_since_last_purchase,
        historical_revenue,
        CASE
            WHEN days_since_last_purchase >= 180 THEN '180d'
            WHEN days_since_last_purchase >= 120 THEN '120d'
            WHEN days_since_last_purchase >= 90 THEN '90d'
        END AS inactivity_window,
        ROUND((historical_revenue * 0.10)::numeric, 4) AS potential_recoverable_revenue
    FROM scored
    WHERE revenue_quartile = 4
      AND days_since_last_purchase >= 90
)
INSERT INTO mart_revenue_at_risk (
    customer_id,
    last_purchase_date,
    days_since_last_purchase,
    historical_revenue,
    inactivity_window,
    potential_recoverable_revenue
)
SELECT
    customer_id,
    last_purchase_date,
    days_since_last_purchase,
    historical_revenue,
    inactivity_window,
    potential_recoverable_revenue
FROM high_value_inactive
ORDER BY customer_id;

COMMIT;
