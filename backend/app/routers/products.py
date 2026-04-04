from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.models import Product
from app.schemas.schemas import ProductCreate, ProductOut

router = APIRouter()


@router.get("/", response_model=List[ProductOut])
def get_products(
    skip: int = 0,
    limit: int = Query(default=50, le=200),
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    db: Session = Depends(get_db),
):
    query = db.query(Product)
    if category:
        query = query.filter(Product.category == category)
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)
    return query.offset(skip).limit(limit).all()


@router.get("/categories")
def get_categories(db: Session = Depends(get_db)):
    cats = db.query(Product.category).distinct().all()
    return {"categories": [c[0] for c in cats]}


@router.get("/{product_id}", response_model=ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.post("/", response_model=ProductOut, status_code=201)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    db_product = Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product
