"""
Aggregation functions — all derived from the in-memory CSV DataFrames.

Every function accepts the same parameters as the corresponding FastAPI
endpoint so the router stays thin and testable.

Date filters use MAX_DATE (end of dataset = 2019-03-31) as the reference
point so that "last 30 days" means the final 30 calendar days of the
dataset rather than from today (which would return nothing).
"""

from datetime import timedelta
from typing import List, Dict, Any

import pandas as pd

from data.loader import MERGED, ORDERS, DETAILS, TARGETS, MAX_DATE


# ─────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────

def _window(df: pd.DataFrame, days: int) -> pd.DataFrame:
    """Return rows within the last `days` calendar days of the dataset."""
    cutoff = MAX_DATE - timedelta(days=days)
    return df[df["Order Date"] >= cutoff]


def _prev_window(df: pd.DataFrame, days: int) -> pd.DataFrame:
    """Return rows from the *prior* `days` window (for growth %)."""
    end = MAX_DATE - timedelta(days=days)
    start = MAX_DATE - timedelta(days=days * 2)
    return df[(df["Order Date"] >= start) & (df["Order Date"] < end)]


def _pct(current: float, previous: float) -> float:
    if previous == 0:
        return 0.0
    return round((current - previous) / previous * 100, 1)


# ─────────────────────────────────────────────────────────────────────
# KPI
# ─────────────────────────────────────────────────────────────────────

def kpi_summary() -> Dict[str, Any]:
    """All-time KPIs + 30-day vs prior-30-day growth rates."""
    total_revenue = DETAILS["Amount"].sum()
    total_orders = DETAILS["Order ID"].nunique()
    total_users = ORDERS["CustomerName"].nunique()
    total_products = DETAILS["Sub-Category"].nunique()
    avg_order_value = total_revenue / total_orders if total_orders else 0

    # Last 30 days
    cur = _window(MERGED, 30)
    prv = _prev_window(MERGED, 30)

    cur_rev = cur["Amount"].sum()
    cur_ord = cur["Order ID"].nunique()
    cur_usr = cur["CustomerName"].nunique()
    cur_aov = cur_rev / cur_ord if cur_ord else 0

    prv_rev = prv["Amount"].sum()
    prv_ord = prv["Order ID"].nunique()
    prv_aov = prv["Amount"].sum() / prv["Order ID"].nunique() if prv["Order ID"].nunique() else 0

    return {
        "total_revenue": round(float(total_revenue), 2),
        "total_orders": int(total_orders),
        "total_users": int(total_users),
        "total_products": int(total_products),
        "avg_order_value": round(float(avg_order_value), 2),
        "revenue_change": _pct(cur_rev, prv_rev),
        "orders_change": _pct(cur_ord, prv_ord),
        "users_change": 0.0,      # no per-day user signup data in CSV
        "aov_change": _pct(cur_aov, prv_aov),
    }


# ─────────────────────────────────────────────────────────────────────
# Daily & Weekly Sales
# ─────────────────────────────────────────────────────────────────────

def daily_sales(days: int = 30) -> List[Dict[str, Any]]:
    """Revenue and order count per calendar day, last `days` of dataset."""
    df = _window(MERGED, days).copy()
    df["date_only"] = df["Order Date"].dt.date
    grouped = (
        df.groupby("date_only")
        .agg(revenue=("Amount", "sum"), orders=("Order ID", "nunique"))
        .reset_index()
        .sort_values("date_only")
    )
    return [
        {
            "date": str(row["date_only"]),
            "revenue": round(float(row["revenue"]), 2),
            "orders": int(row["orders"]),
        }
        for _, row in grouped.iterrows()
    ]


def weekly_sales(weeks: int = 12) -> List[Dict[str, Any]]:
    """Revenue and order count per ISO week, last `weeks` of dataset."""
    days = weeks * 7
    df = _window(MERGED, days).copy()
    df["week"] = df["Order Date"].dt.to_period("W").dt.start_time.dt.date
    grouped = (
        df.groupby("week")
        .agg(revenue=("Amount", "sum"), orders=("Order ID", "nunique"))
        .reset_index()
        .sort_values("week")
    )
    return [
        {
            "date": str(row["week"]),
            "revenue": round(float(row["revenue"]), 2),
            "orders": int(row["orders"]),
        }
        for _, row in grouped.iterrows()
    ]


# ─────────────────────────────────────────────────────────────────────
# Category Revenue (with Sales Target)
# ─────────────────────────────────────────────────────────────────────

def category_revenue() -> List[Dict[str, Any]]:
    """All-time revenue + order count per category, enriched with cumulative target."""
    cat_rev = (
        DETAILS.groupby("Category")
        .agg(revenue=("Amount", "sum"), orders=("Order ID", "nunique"))
        .reset_index()
        .sort_values("revenue", ascending=False)
    )

    # Cumulative target across all months per category
    cat_target = TARGETS.groupby("Category")["Target"].sum()

    result = []
    for _, row in cat_rev.iterrows():
        result.append(
            {
                "category": row["Category"],
                "revenue": round(float(row["revenue"]), 2),
                "orders": int(row["orders"]),
                "target": round(float(cat_target.get(row["Category"], 0)), 2),
            }
        )
    return result


# ─────────────────────────────────────────────────────────────────────
# Top Products (Sub-Categories)
# ─────────────────────────────────────────────────────────────────────

def top_products(limit: int = 10) -> List[Dict[str, Any]]:
    """Top sub-categories by total revenue."""
    grouped = (
        DETAILS.groupby(["Sub-Category", "Category"])
        .agg(total_quantity=("Quantity", "sum"), total_revenue=("Amount", "sum"))
        .reset_index()
        .sort_values("total_revenue", ascending=False)
        .head(limit)
        .reset_index(drop=True)
    )
    return [
        {
            "product_id": int(i + 1),
            "product_name": row["Sub-Category"],
            "category": row["Category"],
            "total_quantity": int(row["total_quantity"]),
            "total_revenue": round(float(row["total_revenue"]), 2),
        }
        for i, (_, row) in enumerate(grouped.iterrows())
    ]


# ─────────────────────────────────────────────────────────────────────
# Customer Segments
# ─────────────────────────────────────────────────────────────────────

def customer_segments() -> List[Dict[str, Any]]:
    """
    Derive VIP / Regular / New segments from order frequency per customer.
      VIP    : ≥ 4 orders
      Regular: 2–3 orders
      New    : 1 order
    """
    order_counts = MERGED.groupby("CustomerName")["Order ID"].nunique()
    rev_per_cust = MERGED.groupby("CustomerName")["Amount"].sum()

    def classify(n: int) -> str:
        if n >= 4:
            return "VIP"
        if n >= 2:
            return "Regular"
        return "New"

    customers = pd.DataFrame(
        {"order_count": order_counts, "revenue": rev_per_cust}
    ).reset_index()
    customers["segment"] = customers["order_count"].apply(classify)

    seg = (
        customers.groupby("segment")
        .agg(count=("CustomerName", "count"), revenue=("revenue", "sum"))
        .reset_index()
    )

    # Fixed display order
    order_map = {"VIP": 0, "Regular": 1, "New": 2}
    seg["_order"] = seg["segment"].map(order_map)
    seg = seg.sort_values("_order").drop(columns="_order")

    return [
        {
            "segment": row["segment"],
            "count": int(row["count"]),
            "revenue": round(float(row["revenue"]), 2),
        }
        for _, row in seg.iterrows()
    ]


# ─────────────────────────────────────────────────────────────────────
# Tableau Export
# ─────────────────────────────────────────────────────────────────────

def tableau_export() -> List[Dict[str, Any]]:
    """Full denormalized dataset for Tableau."""
    df = MERGED.copy()
    df["order_date"] = df["Order Date"].dt.strftime("%Y-%m-%d")
    df["order_month"] = df["Order Date"].dt.strftime("%Y-%m")
    return [
        {
            "order_id": row["Order ID"],
            "order_date": row["order_date"],
            "order_month": row["order_month"],
            "customer_name": row["CustomerName"],
            "state": row["State"],
            "city": row["City"],
            "category": row["Category"],
            "sub_category": row["Sub-Category"],
            "quantity": int(row["Quantity"]),
            "amount": float(row["Amount"]),
            "profit": float(row["Profit"]),
        }
        for _, row in df.iterrows()
    ]
