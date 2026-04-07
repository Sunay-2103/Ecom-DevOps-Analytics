"""
Seed script — generates realistic synthetic e-commerce data over 365 days.
Includes growth trend, weekday/seasonal patterns, and sale-day spikes.
Run: python seed_data.py
"""
import random
import sys
import os
import math
from datetime import datetime, timedelta
from faker import Faker

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from app.database import SessionLocal, engine, Base
from app.models.models import User, Product, Order

fake = Faker()
random.seed(42)
Faker.seed(42)

CATEGORIES = ["Electronics", "Clothing", "Books", "Home & Garden", "Sports", "Beauty", "Toys", "Food"]

PRODUCTS_DATA = [
    # Electronics
    ("Wireless Bluetooth Headphones", "Electronics", 79.99),
    ("4K Smart TV 55\"", "Electronics", 599.99),
    ("Laptop 15.6\" Core i7", "Electronics", 1299.99),
    ("Mechanical Keyboard RGB", "Electronics", 129.99),
    ("Noise-Cancelling Earbuds", "Electronics", 149.99),
    ("Gaming Mouse 16000 DPI", "Electronics", 59.99),
    ("USB-C Hub 7-in-1", "Electronics", 39.99),
    ("Portable Charger 20000mAh", "Electronics", 49.99),
    ("Webcam 4K HD", "Electronics", 89.99),
    ("Smart Watch Series X", "Electronics", 249.99),
    # Clothing
    ("Classic Denim Jacket", "Clothing", 69.99),
    ("Running Shoes Mesh", "Clothing", 89.99),
    ("Merino Wool Sweater", "Clothing", 99.99),
    ("Sports Leggings", "Clothing", 44.99),
    ("Cotton T-Shirt Pack 3x", "Clothing", 29.99),
    ("Formal Oxford Shirt", "Clothing", 54.99),
    ("Winter Down Parka", "Clothing", 189.99),
    # Books
    ("Clean Code by R. Martin", "Books", 34.99),
    ("Designing Data-Intensive Apps", "Books", 49.99),
    ("The DevOps Handbook", "Books", 39.99),
    ("Python for Data Analysis", "Books", 44.99),
    ("The Pragmatic Programmer", "Books", 34.99),
    # Home & Garden
    ("Air Purifier HEPA", "Home & Garden", 129.99),
    ("Robot Vacuum Cleaner", "Home & Garden", 299.99),
    ("Standing Desk 140cm", "Home & Garden", 349.99),
    ("Ergonomic Chair Mesh", "Home & Garden", 249.99),
    ("Coffee Maker Pour Over", "Home & Garden", 59.99),
    # Sports
    ("Yoga Mat Premium", "Sports", 34.99),
    ("Resistance Bands Set", "Sports", 24.99),
    ("Adjustable Dumbbells 20kg", "Sports", 149.99),
    ("Cycling Helmet MIPS", "Sports", 89.99),
    # Beauty
    ("Vitamin C Serum 30ml", "Beauty", 29.99),
    ("Retinol Night Cream", "Beauty", 39.99),
    ("Sunscreen SPF 50+", "Beauty", 19.99),
    # Toys
    ("LEGO Architecture Set", "Toys", 79.99),
    ("Board Game Strategy", "Toys", 44.99),
    # Food
    ("Organic Coffee Beans 1kg", "Food", 24.99),
    ("Protein Powder Vanilla 2kg", "Food", 54.99),
]

CITIES = [
    ("Mumbai", "India"), ("Delhi", "India"), ("Bangalore", "India"), ("Chennai", "India"),
    ("London", "UK"), ("Manchester", "UK"), ("New York", "USA"), ("Los Angeles", "USA"),
    ("Toronto", "Canada"), ("Sydney", "Australia"), ("Dubai", "UAE"), ("Singapore", "Singapore"),
]

SEGMENTS = ["VIP", "Regular", "New"]
SEGMENT_WEIGHTS = [0.1, 0.6, 0.3]

# Realistic category weights — drives both order volume and radar chart proportions
CATEGORY_DIST = [
    ("Electronics",   0.20),
    ("Clothing",      0.22),
    ("Home & Garden", 0.14),
    ("Sports",        0.13),
    ("Books",         0.10),
    ("Beauty",        0.09),
    ("Toys",          0.07),
    ("Food",          0.05),
]

# Weekday multipliers (Mon=0 … Sun=6)
DOW_FACTOR = [1.05, 1.10, 1.20, 1.20, 1.40, 0.85, 0.60]

# Monthly seasonal multipliers
SEASONAL = {
    1: 0.75, 2: 0.70, 3: 0.85, 4: 0.90, 5: 0.95,  6: 0.95,
    7: 0.90, 8: 0.95, 9: 1.00, 10: 1.10, 11: 1.50, 12: 1.70,
}


def daily_order_count(day_idx: int, total_days: int, target_date: datetime) -> int:
    """Return realistic order count for a given day index with growth + weekday + seasonal + noise."""
    # Logistic-style growth: starts ~30 orders/day, reaches ~75 by end of period
    growth = 30 + (day_idx / total_days) * 45
    dow     = DOW_FACTOR[target_date.weekday()]
    season  = SEASONAL.get(target_date.month, 1.0)
    noise   = random.uniform(0.85, 1.15)
    return max(5, int(growth * dow * season * noise))


def seed():
    db = SessionLocal()
    try:
        # Clear existing
        db.query(Order).delete()
        db.query(Product).delete()
        db.query(User).delete()
        db.commit()
        print("✓ Cleared existing data")

        # Seed Products
        products = []
        for name, cat, price in PRODUCTS_DATA:
            p = Product(
                name=name,
                category=cat,
                price=price,
                stock=random.randint(10, 500),
                description=fake.sentence(nb_words=12),
            )
            db.add(p)
            products.append(p)
        db.commit()
        print(f"✓ Seeded {len(products)} products")

        # Seed Users (500)
        users = []
        for i in range(500):
            city, country = random.choice(CITIES)
            seg = random.choices(SEGMENTS, weights=SEGMENT_WEIGHTS)[0]
            u = User(
                name=fake.name(),
                email=f"user{i+1}_{fake.user_name()}@{fake.free_email_domain()}",
                city=city,
                country=country,
                segment=seg,
                created_at=fake.date_time_between(start_date="-18M", end_date="-1d"),
            )
            db.add(u)
            users.append(u)
        db.commit()
        print(f"✓ Seeded {len(users)} users")

        # Build product-by-category lookup for weighted selection
        product_by_cat: dict[str, list] = {}
        for p in products:
            product_by_cat.setdefault(p.category, []).append(p)
        cat_names  = [c for c, _ in CATEGORY_DIST]
        cat_wts    = [w for _, w in CATEGORY_DIST]

        # Seed Orders — 365 days with growth trend, weekday/seasonal patterns, spike days
        TOTAL_DAYS = 365
        today      = datetime.utcnow().replace(hour=23, minute=59, second=59, microsecond=0)
        spike_days = set(random.sample(range(TOTAL_DAYS), 8))   # 8 sale-event days

        all_orders: list[Order] = []
        total_seeded = 0

        for day_idx in range(TOTAL_DAYS):
            target_date = today - timedelta(days=TOTAL_DAYS - day_idx - 1)
            num = daily_order_count(day_idx, TOTAL_DAYS, target_date)
            if day_idx in spike_days:
                num = int(num * random.uniform(2.5, 4.0))   # sale-day spike

            for _ in range(num):
                category = random.choices(cat_names, weights=cat_wts)[0]
                product  = random.choice(product_by_cat.get(category, products))
                user     = random.choice(users)
                qty      = random.choices([1, 2, 3, 4, 5], weights=[55, 25, 12, 5, 3])[0]
                total    = round(product.price * qty, 2)
                status   = random.choices(
                    ["completed", "pending", "refunded"],
                    weights=[88, 8, 4],
                )[0]
                # Random time during business hours (peak at 2 PM)
                hour   = int(max(6, min(23, random.gauss(14, 4))))
                minute = random.randint(0, 59)
                order_date = target_date.replace(hour=hour, minute=minute, second=0, microsecond=0)

                all_orders.append(Order(
                    user_id=user.id,
                    product_id=product.id,
                    quantity=qty,
                    total_price=total,
                    status=status,
                    created_at=order_date,
                ))

            # Flush in batches of 1000 to avoid memory pressure
            if len(all_orders) >= 1000:
                db.add_all(all_orders)
                db.commit()
                total_seeded += len(all_orders)
                all_orders = []

        if all_orders:
            db.add_all(all_orders)
            db.commit()
            total_seeded += len(all_orders)

        print(f"✓ Seeded {total_seeded} orders across {TOTAL_DAYS} days "
              f"({TOTAL_DAYS} data points, {len(spike_days)} spike days)")
        print("\n🚀 Database seeded successfully!")

    except Exception as e:
        db.rollback()
        print(f"✗ Error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    seed()
