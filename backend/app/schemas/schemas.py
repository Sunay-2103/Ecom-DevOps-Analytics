from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


# ─── User Schemas ───────────────────────────────────────────
class UserBase(BaseModel):
    name: str
    email: str
    city: Optional[str] = None
    country: Optional[str] = None
    segment: Optional[str] = "Regular"


class UserCreate(UserBase):
    pass


class UserOut(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ─── Product Schemas ─────────────────────────────────────────
class ProductBase(BaseModel):
    name: str
    category: str
    price: float
    stock: Optional[int] = 0
    description: Optional[str] = None


class ProductCreate(ProductBase):
    pass


class ProductOut(ProductBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ─── Order Schemas ───────────────────────────────────────────
class OrderBase(BaseModel):
    user_id: int
    product_id: int
    quantity: int
    status: Optional[str] = "completed"


class OrderCreate(OrderBase):
    pass


class OrderOut(BaseModel):
    id: int
    user_id: int
    product_id: int
    quantity: int
    total_price: float
    status: str
    created_at: datetime
    user_name: Optional[str] = None
    product_name: Optional[str] = None

    class Config:
        from_attributes = True


# ─── Analytics Schemas ───────────────────────────────────────
class KPISummary(BaseModel):
    total_revenue: float
    total_orders: int
    total_users: int
    total_products: int
    avg_order_value: float


class DailySales(BaseModel):
    date: str
    revenue: float
    orders: int


class TopProduct(BaseModel):
    product_id: int
    product_name: str
    category: str
    total_quantity: int
    total_revenue: float


class CategoryRevenue(BaseModel):
    category: str
    revenue: float
    orders: int


class CustomerSegment(BaseModel):
    segment: str
    count: int
    revenue: float
change 22
change 4
change 25
