import pandas as pd
import os
import sys
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.models.models import Product, User, Order
from app.database import Base, engine

# Get DB URL from Docker env
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("❌ DATABASE_URL not set!")

SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

try:
    print("📥 Loading dataset...")

    # Load CSV
    df = pd.read_csv("/app/data.csv", encoding="latin1", on_bad_lines="skip")

    print("🧹 Cleaning data...")

    # Clean column names
    df.columns = [col.lower().replace(" ", "_") for col in df.columns]

    # Remove invalid data
    df = df[df["quantity"] > 0]
    df = df.dropna(subset=["customerid"])

    # Convert types
    df["customerid"] = df["customerid"].astype(int)
    df["unitprice"] = pd.to_numeric(df["unitprice"], errors="coerce")
    df = df.dropna(subset=["unitprice"])

    print(f"📊 Sample data ({len(df)} records):")
    print(df.head())

    print("🗄️ Processing and inserting data...")

    # Get or create a default user for CSV data
    default_user = db.query(User).first()
    if not default_user:
        default_user = User(
            name="CSV Data Import",
            email="import@ecommerce.local",
            city="Unknown",
            country="Unknown",
            segment="Regular"
        )
        db.add(default_user)
        db.commit()

    # Parse invoices to group related items
    invoice_groups = df.groupby('invoiceno').first().reset_index()
    print(f"📦 Found {len(invoice_groups)} unique invoices")

    # Bulk insert products first
    products_dict = {}
    orders_to_insert = []
    
    for idx, row in df.iterrows():
        try:
            stockcode = str(row["stockcode"]).strip()
            
            # Get or create product
            if stockcode not in products_dict:
                existing_product = db.query(Product).filter_by(description=stockcode).first()
                if existing_product:
                    products_dict[stockcode] = existing_product.id
                else:
                    # Create new product
                    new_product = Product(
                        name=row["description"][:200],
                        category="Imported",
                        price=float(row["unitprice"]),
                        stock=100,
                        description=f"StockCode: {stockcode}"
                    )
                    db.add(new_product)
                    db.flush()
                    products_dict[stockcode] = new_product.id

            # Prepare order record
            try:
                invoice_date = pd.to_datetime(row["invoicedate"])
            except:
                invoice_date = datetime.now()

            order = Order(
                user_id=default_user.id,
                product_id=products_dict[stockcode],
                quantity=int(row["quantity"]),
                total_price=float(row["quantity"]) * float(row["unitprice"]),
                status="completed",
                created_at=invoice_date
            )
            orders_to_insert.append(order)

            # Commit in batches
            if len(orders_to_insert) >= 500:
                db.add_all(orders_to_insert)
                db.commit()
                print(f"  ✓ Inserted {len(orders_to_insert)} orders (total: {idx+1})")
                orders_to_insert = []

        except Exception as e:
            print(f"  ⚠️  Row {idx} error: {e}")
            continue

    # Final commit
    if orders_to_insert:
        db.add_all(orders_to_insert)
        db.commit()
        print(f"  ✓ Inserted {len(orders_to_insert)} final orders")

    # Get counts
    total_orders = db.query(Order).count()
    total_products = db.query(Product).count()
    
    print(f"\n✅ Data loaded successfully!")
    print(f"  • Total orders in database: {total_orders}")
    print(f"  • Total products in database: {total_products}")

except Exception as e:
    db.rollback()
    print(f"❌ Error loading data: {e}")
    raise
finally:
    db.close()
