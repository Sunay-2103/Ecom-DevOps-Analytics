"""
Analytics router — all data served from the in-memory CSV layer.
No database queries here; PostgreSQL is only used for orders/users/products CRUD.
"""

from fastapi import APIRouter, Query
from typing import List

from app.schemas.schemas import (
    KPISummary, DailySales, TopProduct, CategoryRevenue, CustomerSegment,
)
from data import aggregations as agg

router = APIRouter()


@router.get("/kpi", response_model=KPISummary)
def get_kpi_summary():
    return agg.kpi_summary()


@router.get("/daily-sales", response_model=List[DailySales])
def get_daily_sales(days: int = Query(default=30, le=365)):
    return agg.daily_sales(days)


@router.get("/weekly-sales", response_model=List[DailySales])
def get_weekly_sales(weeks: int = Query(default=12, le=52)):
    return agg.weekly_sales(weeks)


@router.get("/top-products", response_model=List[TopProduct])
def get_top_products(limit: int = Query(default=10, le=50)):
    return agg.top_products(limit)


@router.get("/category-revenue", response_model=List[CategoryRevenue])
def get_category_revenue():
    return agg.category_revenue()


@router.get("/customer-segments", response_model=List[CustomerSegment])
def get_customer_segments():
    return agg.customer_segments()


@router.get("/export/tableau")
def export_tableau_data():
    return agg.tableau_export()
