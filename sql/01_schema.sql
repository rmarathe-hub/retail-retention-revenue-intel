-- Retail Retention & Revenue Intelligence
-- Week 1 Day 4: warehouse schema (raw -> staging -> dims -> marts)

BEGIN;

-- ---------------------------------------------------------------------------
-- Raw layer: source-faithful combined CSV
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS raw_online_retail (
    invoice TEXT,
    stock_code TEXT,
    description TEXT,
    quantity INTEGER,
    invoice_date TIMESTAMP,
    price NUMERIC(12, 4),
    customer_id TEXT,
    country TEXT,
    source_sheet TEXT,
    loaded_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- ---------------------------------------------------------------------------
-- Staging layer: cleaned transaction lines (Day 3 output)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS stg_transactions (
    invoice_no TEXT NOT NULL,
    stock_code TEXT,
    description TEXT,
    quantity INTEGER,
    invoice_date TIMESTAMP,
    invoice_month TEXT,
    unit_price NUMERIC(12, 4),
    customer_id TEXT,
    country TEXT,
    source_sheet TEXT,
    is_canceled BOOLEAN NOT NULL DEFAULT FALSE,
    is_return BOOLEAN NOT NULL DEFAULT FALSE,
    is_missing_customer BOOLEAN NOT NULL DEFAULT FALSE,
    is_missing_description BOOLEAN NOT NULL DEFAULT FALSE,
    is_zero_or_negative_price BOOLEAN NOT NULL DEFAULT FALSE,
    is_invalid_invoice_date BOOLEAN NOT NULL DEFAULT FALSE,
    line_revenue NUMERIC(14, 4),
    loaded_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- ---------------------------------------------------------------------------
-- Dimensions
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS dim_date (
    date_key INTEGER PRIMARY KEY,
    full_date DATE NOT NULL UNIQUE,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    month_name TEXT NOT NULL,
    quarter INTEGER NOT NULL,
    year_month TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_customer (
    customer_id TEXT PRIMARY KEY,
    first_purchase_date DATE,
    first_purchase_month TEXT,
    primary_country TEXT,
    total_orders INTEGER NOT NULL DEFAULT 0,
    total_revenue NUMERIC(14, 4) NOT NULL DEFAULT 0,
    is_repeat_customer BOOLEAN NOT NULL DEFAULT FALSE,
    loaded_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- ---------------------------------------------------------------------------
-- Mart placeholders (populated Days 5-9)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS mart_monthly_revenue (
    invoice_month TEXT PRIMARY KEY,
    total_revenue NUMERIC(14, 4),
    total_orders INTEGER,
    active_customers INTEGER,
    new_customer_revenue NUMERIC(14, 4),
    returning_customer_revenue NUMERIC(14, 4),
    loaded_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS mart_customer_orders (
    customer_id TEXT PRIMARY KEY,
    total_orders INTEGER,
    total_revenue NUMERIC(14, 4),
    first_order_date DATE,
    last_order_date DATE,
    is_repeat_customer BOOLEAN,
    loaded_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS mart_customer_rfm (
    customer_id TEXT PRIMARY KEY,
    recency_days INTEGER,
    frequency_orders INTEGER,
    monetary_value NUMERIC(14, 4),
    r_score INTEGER,
    f_score INTEGER,
    m_score INTEGER,
    rfm_score TEXT,
    customer_segment TEXT,
    loaded_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS mart_cohort_retention (
    cohort_month TEXT NOT NULL,
    activity_month TEXT NOT NULL,
    months_since_first_purchase INTEGER NOT NULL,
    cohort_size INTEGER,
    retained_customers INTEGER,
    retention_rate NUMERIC(8, 4),
    cohort_revenue NUMERIC(14, 4),
    revenue_retention_rate NUMERIC(8, 4),
    loaded_at TIMESTAMP NOT NULL DEFAULT NOW(),
    PRIMARY KEY (cohort_month, activity_month)
);

CREATE TABLE IF NOT EXISTS mart_revenue_at_risk (
    customer_id TEXT PRIMARY KEY,
    last_purchase_date DATE,
    days_since_last_purchase INTEGER,
    historical_revenue NUMERIC(14, 4),
    inactivity_window TEXT,
    potential_recoverable_revenue NUMERIC(14, 4),
    loaded_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS mart_product_performance (
    stock_code TEXT PRIMARY KEY,
    description TEXT,
    total_revenue NUMERIC(14, 4),
    total_quantity INTEGER,
    cancellation_rate NUMERIC(8, 4),
    loaded_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS mart_country_performance (
    country TEXT PRIMARY KEY,
    total_revenue NUMERIC(14, 4),
    total_orders INTEGER,
    active_customers INTEGER,
    loaded_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS mart_executive_kpis (
    kpi_name TEXT PRIMARY KEY,
    kpi_value NUMERIC(18, 4),
    kpi_unit TEXT,
    as_of_date DATE,
    loaded_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- ---------------------------------------------------------------------------
-- Indexes for analytical queries
-- ---------------------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_stg_transactions_customer_id
    ON stg_transactions (customer_id);

CREATE INDEX IF NOT EXISTS idx_stg_transactions_invoice_date
    ON stg_transactions (invoice_date);

CREATE INDEX IF NOT EXISTS idx_stg_transactions_invoice_no
    ON stg_transactions (invoice_no);

CREATE INDEX IF NOT EXISTS idx_stg_transactions_stock_code
    ON stg_transactions (stock_code);

CREATE INDEX IF NOT EXISTS idx_stg_transactions_invoice_month
    ON stg_transactions (invoice_month);

CREATE INDEX IF NOT EXISTS idx_dim_customer_first_purchase_month
    ON dim_customer (first_purchase_month);

COMMIT;
