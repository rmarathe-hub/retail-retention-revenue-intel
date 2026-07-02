-- Retail Retention & Revenue Intelligence
-- Post-load data quality validation (run after 01_schema.sql + load_to_postgres.py)
--
-- Usage:
--   psql -f sql/02_data_quality_checks.sql
--   python scripts/validate_data.py
--
-- Each row: check_name, expected_value, actual_value
-- validate_data.py asserts actual_value = expected_value for every check.

SELECT
    check_name,
    expected_value,
    actual_value,
    CASE
        WHEN actual_value = expected_value THEN 'ok'
        ELSE 'fail'
    END AS status
FROM (
    -- Row counts (Day 4 load contract)
    SELECT 'raw_row_count' AS check_name,
           1067371::bigint AS expected_value,
           COUNT(*)::bigint AS actual_value
    FROM raw_online_retail

    UNION ALL
    SELECT 'stg_row_count',
           1055238,
           COUNT(*)::bigint
    FROM stg_transactions

    UNION ALL
    SELECT 'dim_customer_count',
           5942,
           COUNT(*)::bigint
    FROM dim_customer

    UNION ALL
    SELECT 'dim_date_count',
           739,
           COUNT(*)::bigint
    FROM dim_date

    -- Day 6 marts populated by 03/04 SQL
    UNION ALL
    SELECT 'mart_monthly_revenue_rows',
           25,
           COUNT(*)::bigint
    FROM mart_monthly_revenue

    UNION ALL
    SELECT 'mart_customer_orders_rows',
           5881,
           COUNT(*)::bigint
    FROM mart_customer_orders

    UNION ALL
    SELECT 'mart_executive_kpis_rows',
           9,
           COUNT(*)::bigint
    FROM mart_executive_kpis

    UNION ALL
    SELECT 'mart_cohort_retention_rows',
           325,
           COUNT(*)::bigint
    FROM mart_cohort_retention

    UNION ALL
    SELECT 'mart_cohort_distinct_months',
           25,
           COUNT(DISTINCT cohort_month)::bigint
    FROM mart_cohort_retention

    UNION ALL
    SELECT 'cohort_month_zero_retention_mismatch',
           0,
           COUNT(*)::bigint
    FROM mart_cohort_retention
    WHERE months_since_first_purchase = 0
      AND retention_rate IS DISTINCT FROM 100.0000

    -- Mart placeholders remain empty until Days 8-9
    UNION ALL
    SELECT 'mart_customer_rfm_empty',
           0,
           COUNT(*)::bigint
    FROM mart_customer_rfm

    UNION ALL
    SELECT 'mart_revenue_at_risk_empty',
           0,
           COUNT(*)::bigint
    FROM mart_revenue_at_risk

    UNION ALL
    SELECT 'mart_product_performance_empty',
           0,
           COUNT(*)::bigint
    FROM mart_product_performance

    UNION ALL
    SELECT 'mart_country_performance_empty',
           0,
           COUNT(*)::bigint
    FROM mart_country_performance

    -- Day 3 flag volumes on stg_transactions (after deduplication)
    UNION ALL
    SELECT 'missing_customer_lines',
           242870,
           COUNT(*)::bigint
    FROM stg_transactions
    WHERE is_missing_customer = TRUE

    UNION ALL
    SELECT 'canceled_lines',
           19433,
           COUNT(*)::bigint
    FROM stg_transactions
    WHERE is_canceled = TRUE

    UNION ALL
    SELECT 'return_lines',
           22889,
           COUNT(*)::bigint
    FROM stg_transactions
    WHERE is_return = TRUE

    UNION ALL
    SELECT 'zero_or_negative_price_lines',
           6196,
           COUNT(*)::bigint
    FROM stg_transactions
    WHERE is_zero_or_negative_price = TRUE

    UNION ALL
    SELECT 'invalid_invoice_date_lines',
           0,
           COUNT(*)::bigint
    FROM stg_transactions
    WHERE is_invalid_invoice_date = TRUE

    -- Flag logic consistency (expect zero violations)
    UNION ALL
    SELECT 'canceled_flag_mismatch',
           0,
           COUNT(*)::bigint
    FROM stg_transactions
    WHERE is_canceled IS DISTINCT FROM (invoice_no LIKE 'C%')

    UNION ALL
    SELECT 'return_flag_mismatch',
           0,
           COUNT(*)::bigint
    FROM stg_transactions
    WHERE is_return IS DISTINCT FROM (quantity < 0)

    UNION ALL
    SELECT 'missing_customer_flag_mismatch',
           0,
           COUNT(*)::bigint
    FROM stg_transactions
    WHERE is_missing_customer IS DISTINCT FROM (customer_id IS NULL)

    UNION ALL
    SELECT 'zero_price_flag_mismatch',
           0,
           COUNT(*)::bigint
    FROM stg_transactions
    WHERE is_zero_or_negative_price IS DISTINCT FROM (unit_price <= 0)

    -- line_revenue must equal quantity * unit_price
    UNION ALL
    SELECT 'line_revenue_mismatch',
           0,
           COUNT(*)::bigint
    FROM stg_transactions
    WHERE line_revenue IS DISTINCT FROM (quantity * unit_price)

    -- Distinct non-null customers in staging matches dim_customer
    UNION ALL
    SELECT 'stg_distinct_customers',
           5942,
           COUNT(DISTINCT customer_id)::bigint
    FROM stg_transactions
    WHERE customer_id IS NOT NULL

    -- Date range sanity
    UNION ALL
    SELECT 'min_invoice_date_key',
           20091201,
           TO_CHAR(MIN(invoice_date)::date, 'YYYYMMDD')::integer
    FROM stg_transactions

    UNION ALL
    SELECT 'max_invoice_date_key',
           20111209,
           TO_CHAR(MAX(invoice_date)::date, 'YYYYMMDD')::integer
    FROM stg_transactions

) AS dq_checks
ORDER BY check_name;
