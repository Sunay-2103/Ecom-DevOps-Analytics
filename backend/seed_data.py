"""
Seed script — generates 1000+ synthetic records for the e-commerce platform.
Run: python seed_data.py
"""
import random
import sys
import os
from datetime import datetime, timedelta
from faker import Faker

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from app.database import SessionLocal, engine, Base
from app.models.models import User, Product, Order

fake = Faker()
random.seed(42)

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
                created_at=fake.date_time_between(start_date="-18m", end_date="-1d"),
            )
            db.add(u)
            users.append(u)
        db.commit()
        print(f"✓ Seeded {len(users)} users")

        # Seed Orders (1200+)
        order_count = 0
        for _ in range(1300):
            user = random.choice(users)
            product = random.choice(products)
            qty = random.choices([1, 2, 3, 4, 5], weights=[50, 25, 12, 8, 5])[0]
            total = round(product.price * qty, 2)
            status = random.choices(
                ["completed", "pending", "refunded"],
                weights=[85, 10, 5]
            )[0]
            o = Order(
                user_id=user.id,
                product_id=product.id,
                quantity=qty,
                total_price=total,
                status=status,
                created_at=fake.date_time_between(start_date="-12m", end_date="now"),
            )
            db.add(o)
            order_count += 1
        db.commit()
        print(f"✓ Seeded {order_count} orders")
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
change 7
change 7
