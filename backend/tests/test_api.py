"""
Backend API Integration Tests
==============================
Runs against a real (or test) PostgreSQL instance.

Set DATABASE_URL environment variable before running:
    DATABASE_URL=postgresql://test_user:test_pass@localhost:5432/test_db pytest tests/ -v
"""

import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Ensure PYTHONPATH includes the backend root
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.main import app
from app.database import Base, get_db

# ── Test Database Setup ───────────────────────────────────────

TEST_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://test_user:test_pass@localhost:5432/test_db"
)

test_engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# ── Fixtures ─────────────────────────────────────────────────

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Create all tables before the test session and drop them after."""
    from app.models.models import User, Product, Order  # noqa: F401 — registers models
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def client():
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# ── Health + Root ─────────────────────────────────────────────

def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "running"


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


# ── Users ─────────────────────────────────────────────────────

def test_create_user(client):
    payload = {
        "name": "Test User",
        "email": "testuser@example.com",
        "city": "Mumbai",
        "country": "India",
        "segment": "Regular",
    }
    response = client.post("/api/users/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "testuser@example.com"
    assert "id" in data


def test_list_users(client):
    response = client.get("/api/users/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_user_not_found(client):
    response = client.get("/api/users/999999")
    assert response.status_code == 404


# ── Products ──────────────────────────────────────────────────

def test_create_product(client):
    payload = {
        "name": "Test Laptop",
        "category": "Electronics",
        "price": 999.99,
        "stock": 10,
        "description": "A test product",
    }
    response = client.post("/api/products/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Laptop"
    assert data["category"] == "Electronics"


def test_list_products(client):
    response = client.get("/api/products/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_categories(client):
    response = client.get("/api/products/categories")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


# ── Orders ────────────────────────────────────────────────────

def test_create_order(client):
    # Create dependencies first
    user_resp = client.post("/api/users/", json={
        "name": "Order Test User",
        "email": "ordertest@example.com",
        "segment": "VIP",
    })
    # Might get 201 (new) or 400 (duplicate email); use any existing user
    users = client.get("/api/users/").json()
    products = client.get("/api/products/").json()

    if not users or not products:
        pytest.skip("No users or products available for order test")

    payload = {
        "user_id": users[0]["id"],
        "product_id": products[0]["id"],
        "quantity": 2,
        "status": "completed",
    }
    response = client.post("/api/orders/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["quantity"] == 2
    assert data["total_price"] > 0


def test_list_orders(client):
    response = client.get("/api/orders/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


# ── Analytics ─────────────────────────────────────────────────

def test_kpi_endpoint(client):
    response = client.get("/api/analytics/kpi")
    assert response.status_code == 200
    data = response.json()
    for field in ("total_revenue", "total_orders", "total_users", "total_products", "avg_order_value"):
        assert field in data


def test_daily_sales(client):
    response = client.get("/api/analytics/daily-sales?days=30")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_top_products(client):
    response = client.get("/api/analytics/top-products?limit=5")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_category_revenue(client):
    response = client.get("/api/analytics/category-revenue")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_customer_segments(client):
    response = client.get("/api/analytics/customer-segments")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_tableau_export(client):
    response = client.get("/api/analytics/export/tableau")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # Verify expected columns are present
    if data:
        row = data[0]
        for col in ("order_id", "order_date", "total_price", "category", "customer_name"):
            assert col in row, f"Missing column: {col}"
