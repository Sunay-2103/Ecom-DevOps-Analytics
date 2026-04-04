from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.database import get_db
from app.models.models import Order, Product, User
from app.schemas.schemas import OrderCreate, OrderOut

router = APIRouter()


@router.get("/", response_model=List[OrderOut])
def get_orders(
    skip: int = 0,
    limit: int = Query(default=50, le=200),
    status: Optional[str] = None,
    user_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
):
    query = db.query(Order)
    if status:
        query = query.filter(Order.status == status)
    if user_id:
        query = query.filter(Order.user_id == user_id)
    if start_date:
        query = query.filter(Order.created_at >= start_date)
    if end_date:
        query = query.filter(Order.created_at <= end_date)
    orders = query.order_by(Order.created_at.desc()).offset(skip).limit(limit).all()

    result = []
    for o in orders:
        result.append(OrderOut(
            id=o.id,
            user_id=o.user_id,
            product_id=o.product_id,
            quantity=o.quantity,
            total_price=o.total_price,
            status=o.status,
            created_at=o.created_at,
            user_name=o.user.name if o.user else None,
            product_name=o.product.name if o.product else None,
        ))
    return result


@router.get("/{order_id}", response_model=OrderOut)
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return OrderOut(
        id=order.id,
        user_id=order.user_id,
        product_id=order.product_id,
        quantity=order.quantity,
        total_price=order.total_price,
        status=order.status,
        created_at=order.created_at,
        user_name=order.user.name if order.user else None,
        product_name=order.product.name if order.product else None,
    )


@router.post("/", response_model=OrderOut, status_code=201)
def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == order.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    user = db.query(User).filter(User.id == order.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    total = product.price * order.quantity
    db_order = Order(**order.dict(), total_price=total)
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return OrderOut(
        id=db_order.id,
        user_id=db_order.user_id,
        product_id=db_order.product_id,
        quantity=db_order.quantity,
        total_price=db_order.total_price,
        status=db_order.status,
        created_at=db_order.created_at,
        user_name=user.name,
        product_name=product.name,
    )
