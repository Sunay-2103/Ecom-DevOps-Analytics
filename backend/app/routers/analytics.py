from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from typing import List, Optional
from datetime import datetime, timedelta
from app.database import get_db, engine
from app.models.models import Order, Product, User
from app.schemas.schemas import (
    KPISummary, DailySales, TopProduct, CategoryRevenue, CustomerSegment
)

router = APIRouter()


@router.get("/kpi", response_model=KPISummary)
def get_kpi_summary(db: Session = Depends(get_db)):
    total_revenue = db.query(func.sum(Order.total_price)).filter(
        Order.status == "completed"
    ).scalar() or 0

    total_orders = db.query(func.count(Order.id)).scalar() or 0
    total_users = db.query(func.count(User.id)).scalar() or 0
    total_products = db.query(func.count(Product.id)).scalar() or 0
    avg_order_value = total_revenue / total_orders if total_orders > 0 else 0

    return KPISummary(
        total_revenue=round(total_revenue, 2),
        total_orders=total_orders,
        total_users=total_users,
        total_products=total_products,
        avg_order_value=round(avg_order_value, 2),
    )


@router.get("/daily-sales", response_model=List[DailySales])
def get_daily_sales(
    days: int = Query(default=30, le=365),
    db: Session = Depends(get_db),
):
    start_date = datetime.utcnow() - timedelta(days=days)
    rows = (
        db.query(
            func.date(Order.created_at).label("date"),
            func.sum(Order.total_price).label("revenue"),
            func.count(Order.id).label("orders"),
        )
        .filter(Order.created_at >= start_date, Order.status == "completed")
        .group_by(func.date(Order.created_at))
        .order_by(func.date(Order.created_at))
        .all()
    )
    return [
        DailySales(date=str(r.date), revenue=round(r.revenue, 2), orders=r.orders)
        for r in rows
    ]


@router.get("/weekly-sales", response_model=List[DailySales])
def get_weekly_sales(
    weeks: int = Query(default=12, le=52),
    db: Session = Depends(get_db),
):
    start_date = datetime.utcnow() - timedelta(weeks=weeks)
    rows = (
        db.query(
            func.to_char(Order.created_at, "IYYY-IW").label("date"),
            func.sum(Order.total_price).label("revenue"),
            func.count(Order.id).label("orders"),
        )
        .filter(Order.created_at >= start_date, Order.status == "completed")
        .group_by(func.to_char(Order.created_at, "IYYY-IW"))
        .order_by(func.to_char(Order.created_at, "IYYY-IW"))
        .all()
    )
    return [
        DailySales(date=str(r.date), revenue=round(r.revenue, 2), orders=r.orders)
        for r in rows
    ]


@router.get("/top-products", response_model=List[TopProduct])
def get_top_products(
    limit: int = Query(default=10, le=50),
    db: Session = Depends(get_db),
):
    rows = (
        db.query(
            Product.id,
            Product.name,
            Product.category,
            func.sum(Order.quantity).label("total_quantity"),
            func.sum(Order.total_price).label("total_revenue"),
        )
        .join(Order, Order.product_id == Product.id)
        .filter(Order.status == "completed")
        .group_by(Product.id, Product.name, Product.category)
        .order_by(func.sum(Order.total_price).desc())
        .limit(limit)
        .all()
    )
    return [
        TopProduct(
            product_id=r.id,
            product_name=r.name,
            category=r.category,
            total_quantity=r.total_quantity,
            total_revenue=round(r.total_revenue, 2),
        )
        for r in rows
    ]


@router.get("/category-revenue", response_model=List[CategoryRevenue])
def get_category_revenue(db: Session = Depends(get_db)):
    rows = (
        db.query(
            Product.category,
            func.sum(Order.total_price).label("revenue"),
            func.count(Order.id).label("orders"),
        )
        .join(Order, Order.product_id == Product.id)
        .filter(Order.status == "completed")
        .group_by(Product.category)
        .order_by(func.sum(Order.total_price).desc())
        .all()
    )
    return [
        CategoryRevenue(category=r.category, revenue=round(r.revenue, 2), orders=r.orders)
        for r in rows
    ]


@router.get("/customer-segments", response_model=List[CustomerSegment])
def get_customer_segments(db: Session = Depends(get_db)):
    rows = (
        db.query(
            User.segment,
            func.count(User.id).label("count"),
            func.sum(Order.total_price).label("revenue"),
        )
        .join(Order, Order.user_id == User.id)
        .filter(Order.status == "completed")
        .group_by(User.segment)
        .all()
    )
    return [
        CustomerSegment(segment=r.segment, count=r.count, revenue=round(r.revenue or 0, 2))
        for r in rows
    ]


@router.get("/export/tableau")
def export_tableau_data(db: Session = Depends(get_db)):
    """Export full denormalized dataset for Tableau consumption."""
    rows = (
        db.query(
            Order.id.label("order_id"),
            Order.created_at,
            Order.quantity,
            Order.total_price,
            Order.status,
            User.id.label("user_id"),
            User.name.label("user_name"),
            User.email,
            User.city,
            User.country,
            User.segment,
            Product.id.label("product_id"),
            Product.name.label("product_name"),
            Product.category,
            Product.price.label("unit_price"),
        )
        .join(User, Order.user_id == User.id)
        .join(Product, Order.product_id == Product.id)
        .order_by(Order.created_at.desc())
        .all()
    )
    return [
        {
            "order_id": r.order_id,
            "order_date": r.created_at.strftime("%Y-%m-%d") if r.created_at else None,
            "order_month": r.created_at.strftime("%Y-%m") if r.created_at else None,
            "quantity": r.quantity,
            "total_price": r.total_price,
            "status": r.status,
            "user_id": r.user_id,
            "user_name": r.user_name,
            "email": r.email,
            "city": r.city,
            "country": r.country,
            "segment": r.segment,
            "product_id": r.product_id,
            "product_name": r.product_name,
            "category": r.category,
            "unit_price": r.unit_price,
        }
        for r in rows
    ]

@router.get("/analytics")
def get_analytics():
    query = text("""
        SELECT 
            COUNT(DISTINCT InvoiceNo) as total_orders,
            SUM(Quantity * UnitPrice) as total_revenue,
            COUNT(DISTINCT CustomerID) as total_users,
            AVG(Quantity * UnitPrice) as avg_order_value
        FROM orders
        WHERE Quantity > 0
    """)

    with engine.connect() as conn:
        result = conn.execute(query).fetchone()

    return {
        "total_orders": result[0] or 0,
        "total_revenue": float(result[1] or 0),
        "total_users": result[2] or 0,
        "avg_order_value": float(result[3] or 0)
    }

@router.get("/analytics/daily")
def daily_revenue():
    query = text("""
        SELECT 
            DATE(InvoiceDate) as date,
            SUM(Quantity * UnitPrice) as revenue
        FROM orders
        WHERE Quantity > 0
        GROUP BY date
        ORDER BY date
    """)

    with engine.connect() as conn:
        result = conn.execute(query).fetchall()

    return [
        {"date": str(row[0]), "revenue": float(row[1])}
        for row in result
    ]

@router.get("/analytics/categories")
def category_revenue():
    query = text("""
        SELECT 
            Description,
            SUM(Quantity * UnitPrice) as revenue
        FROM orders
        WHERE Quantity > 0
        GROUP BY Description
        ORDER BY revenue DESC
        LIMIT 5
    """)

    with engine.connect() as conn:
        result = conn.execute(query).fetchall()

    return [
        {"category": row[0], "revenue": float(row[1])}
        for row in result
    ]


# Updated on 2026-02-19 by Sunay

# Updated on 2026-03-23 by Sunay
change 27
change 28
change 18
change 21
