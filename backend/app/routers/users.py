from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.models import User
from app.schemas.schemas import UserCreate, UserOut

router = APIRouter()


@router.get("/", response_model=List[UserOut])
def get_users(
    skip: int = 0,
    limit: int = Query(default=50, le=200),
    segment: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(User)
    if segment:
        query = query.filter(User.segment == segment)
    return query.offset(skip).limit(limit).all()


@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/", response_model=UserOut, status_code=201)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    db_user = User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.get("/count/total")
def count_users(db: Session = Depends(get_db)):
    return {"total": db.query(User).count()}

# Updated on 2026-01-20 by Sunay

# Updated on 2026-01-28 by Sunay

# Updated on 2026-02-21 by Anwar

# Updated on 2026-02-27 by Sunay

# Updated on 2026-03-17 by Anwar
