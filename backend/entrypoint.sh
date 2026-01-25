#!/bin/bash
set -e

echo "⏳ Waiting for database..."
sleep 5

echo "🗄️  Running migrations / table creation..."
python -c "from app.database import engine, Base; from app.models.models import *; Base.metadata.create_all(bind=engine)"

echo "🌱 Seeding database..."
python seed_data.py

python load_data.py

echo "🚀 Starting FastAPI server..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
change 11
change 33
change 9
