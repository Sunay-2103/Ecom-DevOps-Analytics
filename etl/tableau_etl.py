"""
ETL Pipeline — E-Commerce DevOps Analytics
==========================================
Fetches data from PostgreSQL, transforms it, and exports CSVs
ready for Tableau or any BI tool.

Usage:
    python tableau_etl.py

Environment variables:
    DATABASE_URL   — PostgreSQL connection string
    ETL_OUTPUT_DIR — Directory where CSVs are written (default: ./exports)
"""

import os
import sys
import logging
from datetime import datetime
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text

# ── Logging ──────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)

# ── Config ───────────────────────────────────────────────────
DATABASE_URL = os.getenv("DATABASE_URL")
OUTPUT_DIR = Path(os.getenv("ETL_OUTPUT_DIR", "./exports"))

if not DATABASE_URL:
    log.error("DATABASE_URL environment variable is not set.")
    sys.exit(1)


def get_engine():
    return create_engine(DATABASE_URL)


def ensure_output_dir():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    log.info("Output directory: %s", OUTPUT_DIR.resolve())


# ── Extract + Transform + Load ───────────────────────────────

def extract_orders(engine) -> pd.DataFrame:
    """Full denormalized orders export — one row per order item."""
    query = text("""
        SELECT
            o.id                                        AS order_id,
            o.created_at::date                          AS order_date,
            TO_CHAR(o.created_at, 'YYYY-MM')            AS order_month,
            EXTRACT(YEAR  FROM o.created_at)::int       AS order_year,
            EXTRACT(MONTH FROM o.created_at)::int       AS order_month_num,
            EXTRACT(DOW   FROM o.created_at)::int       AS day_of_week,
            o.quantity,
            o.total_price,
            o.status,
            u.id                                        AS user_id,
            u.name                                      AS customer_name,
            u.email                                     AS customer_email,
            u.city                                      AS customer_city,
            u.country                                   AS customer_country,
            u.segment                                   AS customer_segment,
            p.id                                        AS product_id,
            p.name                                      AS product_name,
            p.category,
            p.price                                     AS unit_price,
            ROUND((o.total_price / NULLIF(o.quantity,0))::numeric, 2) AS effective_unit_price
        FROM orders o
        JOIN users   u ON u.id = o.user_id
        JOIN products p ON p.id = o.product_id
        ORDER BY o.created_at DESC
    """)
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)
    log.info("Extracted %d order rows.", len(df))
    return df


def extract_daily_revenue(engine) -> pd.DataFrame:
    query = text("""
        SELECT
            created_at::date         AS date,
            COUNT(*)                 AS total_orders,
            SUM(total_price)         AS revenue,
            AVG(total_price)         AS avg_order_value,
            COUNT(DISTINCT user_id)  AS unique_customers
        FROM orders
        WHERE status = 'completed'
        GROUP BY created_at::date
        ORDER BY date
    """)
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)
    log.info("Extracted %d daily revenue rows.", len(df))
    return df


def extract_category_performance(engine) -> pd.DataFrame:
    query = text("""
        SELECT
            p.category,
            COUNT(o.id)              AS total_orders,
            SUM(o.quantity)          AS total_units_sold,
            SUM(o.total_price)       AS total_revenue,
            AVG(o.total_price)       AS avg_order_value,
            COUNT(DISTINCT o.user_id) AS unique_customers
        FROM orders o
        JOIN products p ON p.id = o.product_id
        WHERE o.status = 'completed'
        GROUP BY p.category
        ORDER BY total_revenue DESC
    """)
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)
    log.info("Extracted %d category rows.", len(df))
    return df


def extract_customer_summary(engine) -> pd.DataFrame:
    query = text("""
        SELECT
            u.id                        AS user_id,
            u.name                      AS customer_name,
            u.email,
            u.city,
            u.country,
            u.segment,
            COUNT(o.id)                 AS total_orders,
            SUM(o.total_price)          AS lifetime_value,
            AVG(o.total_price)          AS avg_order_value,
            MIN(o.created_at)::date     AS first_order_date,
            MAX(o.created_at)::date     AS last_order_date
        FROM users u
        LEFT JOIN orders o ON o.user_id = u.id AND o.status = 'completed'
        GROUP BY u.id, u.name, u.email, u.city, u.country, u.segment
        ORDER BY lifetime_value DESC NULLS LAST
    """)
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)
    log.info("Extracted %d customer rows.", len(df))
    return df


def extract_top_products(engine) -> pd.DataFrame:
    query = text("""
        SELECT
            p.id                        AS product_id,
            p.name                      AS product_name,
            p.category,
            p.price                     AS list_price,
            COUNT(o.id)                 AS total_orders,
            SUM(o.quantity)             AS total_units_sold,
            SUM(o.total_price)          AS total_revenue,
            RANK() OVER (ORDER BY SUM(o.total_price) DESC) AS revenue_rank
        FROM products p
        LEFT JOIN orders o ON o.product_id = p.id AND o.status = 'completed'
        GROUP BY p.id, p.name, p.category, p.price
        ORDER BY total_revenue DESC NULLS LAST
        LIMIT 50
    """)
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)
    log.info("Extracted %d top-product rows.", len(df))
    return df


def save_csv(df: pd.DataFrame, name: str):
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = OUTPUT_DIR / f"{name}_{timestamp}.csv"
    latest   = OUTPUT_DIR / f"{name}_latest.csv"
    df.to_csv(filename, index=False)
    df.to_csv(latest,   index=False)
    log.info("Saved %s (%d rows) → %s", name, len(df), latest)


# ── Main ─────────────────────────────────────────────────────

def run():
    log.info("=== ETL Pipeline starting ===")
    ensure_output_dir()
    engine = get_engine()

    exports = {
        "orders_full":           extract_orders,
        "daily_revenue":         extract_daily_revenue,
        "category_performance":  extract_category_performance,
        "customer_summary":      extract_customer_summary,
        "top_products":          extract_top_products,
    }

    success, failed = 0, 0
    for name, extractor in exports.items():
        try:
            df = extractor(engine)
            save_csv(df, name)
            success += 1
        except Exception as exc:
            log.error("Failed to export '%s': %s", name, exc)
            failed += 1

    log.info("=== ETL complete: %d exported, %d failed ===", success, failed)
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    run()
