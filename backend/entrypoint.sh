#!/bin/bash
set -e

echo "[entrypoint] Waiting for PostgreSQL to be ready..."
until pg_isready -h "${DB_HOST:-database}" -p "${DB_PORT:-5432}" -U "${POSTGRES_USER:-ecom_user}"; do
  echo "[entrypoint] Database not ready — retrying in 2s..."
  sleep 2
done

echo "[entrypoint] Running table creation / migrations..."
python -c "
from app.database import engine, Base
from app.models.models import User, Product, Order
Base.metadata.create_all(bind=engine)
print('[entrypoint] Tables created successfully.')
"

echo "[entrypoint] Seeding database with synthetic data (only if empty)..."
PRODUCT_COUNT=$(python -c "
from app.database import SessionLocal
from app.models.models import Product
db = SessionLocal()
print(db.query(Product).count())
db.close()
" 2>/dev/null || echo "0")

if [ "$PRODUCT_COUNT" -eq "0" ]; then
  python seed_data.py
else
  echo "[entrypoint] Database already has ${PRODUCT_COUNT} products — skipping seed."
fi

# CSV import intentionally skipped to keep clean synthetic data for analytics.
# Run manually if needed: docker exec ecom_backend python load_data.py

echo "[entrypoint] Starting FastAPI server on port 8000..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1 --log-level info
