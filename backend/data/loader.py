"""
Data loader — reads the 3 Indian e-commerce CSV files at import time and
exposes clean, merged DataFrames for use by the aggregation layer.

All monetary values are already in INR (Indian Rupees).
"""

from pathlib import Path
import pandas as pd

CSV_DIR = Path(__file__).parent / "csv"


def _load() -> tuple:
    # ── 1. List of Orders ───────────────────────────────────────────────
    orders = pd.read_csv(CSV_DIR / "List of Orders.csv")
    orders.columns = [c.strip() for c in orders.columns]
    orders["Order Date"] = pd.to_datetime(
        orders["Order Date"], dayfirst=True, errors="coerce"
    )
    orders = orders.dropna(subset=["Order Date"])
    orders["CustomerName"] = orders["CustomerName"].str.strip()
    orders["State"] = orders["State"].str.strip()
    orders["City"] = orders["City"].str.strip()

    # ── 2. Order Details ────────────────────────────────────────────────
    details = pd.read_csv(CSV_DIR / "Order Details.csv")
    details.columns = [c.strip() for c in details.columns]
    details["Amount"] = pd.to_numeric(details["Amount"], errors="coerce").fillna(0)
    details["Profit"] = pd.to_numeric(details["Profit"], errors="coerce").fillna(0)
    details["Quantity"] = (
        pd.to_numeric(details["Quantity"], errors="coerce").fillna(0).astype(int)
    )
    details["Category"] = details["Category"].str.strip()
    details["Sub-Category"] = details["Sub-Category"].str.strip()

    # ── 3. Sales Target ──────────────────────────────────────────────────
    targets = pd.read_csv(CSV_DIR / "Sales target.csv")
    targets.columns = [c.strip() for c in targets.columns]
    targets["Target"] = pd.to_numeric(targets["Target"], errors="coerce").fillna(0)
    targets["Category"] = targets["Category"].str.strip()
    targets["Month"] = pd.to_datetime(
        targets["Month of Order Date"], format="%b-%y", errors="coerce"
    )

    # ── 4. Master joined DataFrame ───────────────────────────────────────
    merged = details.merge(orders, on="Order ID", how="inner")

    return orders, details, targets, merged


# Module-level cache — loaded exactly once per process startup
_ORDERS, _DETAILS, _TARGETS, _MERGED = _load()

# Convenience references
ORDERS: pd.DataFrame = _ORDERS
DETAILS: pd.DataFrame = _DETAILS
TARGETS: pd.DataFrame = _TARGETS
MERGED: pd.DataFrame = _MERGED

# Dataset boundaries (used for relative date filters)
MAX_DATE: pd.Timestamp = MERGED["Order Date"].max()
MIN_DATE: pd.Timestamp = MERGED["Order Date"].min()
