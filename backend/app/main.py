from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import users, products, orders, analytics
from app.database import engine, Base
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="E-Commerce DevOps Analytics API",
    description="Analytics platform for e-commerce data with DevOps integration",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(products.router, prefix="/api/products", tags=["Products"])
app.include_router(orders.router, prefix="/api/orders", tags=["Orders"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])


@app.get("/")
def root():
    return {"message": "E-Commerce Analytics API", "status": "running", "version": "1.0.0"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}

# Updated on 2026-02-09 by Sunay

# Updated on 2026-03-05 by Sunay
change 3
change 11
change 25
