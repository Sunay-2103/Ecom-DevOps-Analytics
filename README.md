# E-Commerce DevOps Analytics Platform

A production-grade, full-stack analytics platform for e-commerce data — built with **FastAPI**, **PostgreSQL**, **React**, and fully orchestrated with **Docker Compose**. Features an automated CI/CD pipeline (GitHub Actions) and a scheduled ETL data pipeline that exports Tableau-ready CSV reports.

---

## Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                        Docker Network (ecom_net)                 │
│                                                                  │
│  ┌─────────────┐    ┌─────────────────┐    ┌─────────────────┐  │
│  │   Frontend  │    │     Backend     │    │    Database     │  │
│  │  React 18   │───▶│   FastAPI 0.111 │───▶│  PostgreSQL 15  │  │
│  │  Nginx:3000 │    │  Uvicorn:8000   │    │  Port 5433      │  │
│  └─────────────┘    └─────────────────┘    └─────────────────┘  │
│         │                   │                      │            │
│         │            ┌──────▼──────┐               │            │
│         │            │  ETL Script │◀──────────────┘            │
│         │            │  (on demand │                            │
│         │            │   / cron)   │                            │
│         │            └──────┬──────┘                            │
│         │                   │                                   │
└─────────┼───────────────────┼───────────────────────────────────┘
          │                   ▼
          │           /exports/*.csv
          │                   │
          ▼                   ▼
   Browser / User        Tableau Desktop
                         Tableau Public
```

### Data Flow

```
User Request → React (Nginx)
                  │
                  ▼ (API calls)
            FastAPI Backend
                  │
                  ▼ (SQLAlchemy ORM)
            PostgreSQL DB ──▶ ETL Script ──▶ CSV Files ──▶ Tableau
                              (daily cron
                              or manual)
```

---

## Tech Stack

| Layer      | Technology                                    |
|------------|-----------------------------------------------|
| Backend    | Python 3.11, FastAPI 0.111, SQLAlchemy 2.0    |
| Database   | PostgreSQL 15 (Alpine)                        |
| Frontend   | React 18, Recharts, Lucide React, Nginx       |
| DevOps     | Docker, Docker Compose, multi-stage builds    |
| CI/CD      | GitHub Actions (test + build + push)          |
| ETL        | Python + pandas + SQLAlchemy                  |
| Analytics  | Recharts (inline), Tableau (CSV export)       |

---

## Project Structure

```
ecom-devops-analytics/
│
├── .github/
│   └── workflows/
│       ├── ci-cd.yml          # Main CI/CD pipeline (test, build, push)
│       └── etl-pipeline.yml   # Scheduled daily ETL export for Tableau
│
├── backend/                   # FastAPI Python backend
│   ├── app/
│   │   ├── main.py            # App entry point + middleware
│   │   ├── database.py        # SQLAlchemy engine & session
│   │   ├── models/models.py   # ORM models (User, Product, Order)
│   │   ├── schemas/schemas.py # Pydantic request/response schemas
│   │   └── routers/
│   │       ├── users.py       # /api/users
│   │       ├── products.py    # /api/products
│   │       ├── orders.py      # /api/orders
│   │       └── analytics.py   # /api/analytics (KPI, trends, export)
│   ├── tests/
│   │   └── test_api.py        # Integration test suite (pytest)
│   ├── seed_data.py           # Synthetic data generator (1300+ records)
│   ├── load_data.py           # CSV data importer
│   ├── entrypoint.sh          # Docker startup + DB wait logic
│   ├── requirements.txt
│   ├── .dockerignore
│   └── Dockerfile             # Multi-stage build (builder + runtime)
│
├── frontend/                  # React dashboard
│   ├── src/
│   │   ├── App.js             # Root with layout + routing
│   │   ├── services/api.js    # Axios API client
│   │   ├── hooks/useApi.js    # Custom data-fetching hook
│   │   ├── components/        # Sidebar, Navbar
│   │   └── pages/             # Dashboard, Analytics, Orders, Products, Tableau
│   ├── nginx.conf             # SPA nginx config with /api proxy
│   ├── package.json
│   ├── .dockerignore
│   └── Dockerfile             # Multi-stage (Node build → Nginx serve)
│
├── etl/                       # Standalone ETL pipeline
│   ├── tableau_etl.py         # Extract → Transform → CSV export
│   ├── requirements.txt       # ETL-specific dependencies
│   └── Dockerfile             # Lightweight ETL container
│
├── init.sql                   # PostgreSQL init script (extensions, grants)
├── nginx.conf                 # Root nginx config
├── docker-compose.yml         # Full-stack orchestration
├── .env                       # Local environment variables (git-ignored)
├── .env.example               # Template for environment variables
├── .dockerignore              # Root-level Docker ignore
├── .gitignore
└── README.md
```

---

## Quick Start — Docker

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (or Docker Engine + Compose plugin)
- Git

### 1. Clone the repository
```bash
git clone https://github.com/yourname/ecom-devops-analytics.git
cd ecom-devops-analytics
```

### 2. Set up environment variables
```bash
cp .env.example .env
# Edit .env to set a secure POSTGRES_PASSWORD for production
```

### 3. Start all services with one command
```bash
docker compose up --build
```

This single command:
1. Starts **PostgreSQL** and waits for it to be healthy
2. Builds and starts the **FastAPI** backend — auto-creates tables and seeds 1 300+ records
3. Builds and starts the **React** frontend (served via Nginx)

### 4. Open the application

| Service      | URL                          |
|--------------|------------------------------|
| Dashboard    | http://localhost:3000        |
| API          | http://localhost:8000        |
| API Docs     | http://localhost:8000/docs   |
| DB (external)| localhost:5433               |

### 5. Run the ETL export (optional)
```bash
# Export Tableau CSVs once (backend must be healthy first)
docker compose --profile etl up etl
```

Exported files appear in the `ecom_etl_exports` Docker volume and are also
available at `./exports/` when you mount the named volume locally.

---

## Local Development (Without Docker)

### Backend
```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL=postgresql://ecom_user:ecom_pass@localhost:5432/ecom_db
python seed_data.py
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install --legacy-peer-deps
REACT_APP_API_URL=http://localhost:8000 npm start
```

### ETL Script
```bash
cd etl
pip install -r requirements.txt
export DATABASE_URL=postgresql://ecom_user:ecom_pass@localhost:5432/ecom_db
export ETL_OUTPUT_DIR=./exports
python tableau_etl.py
```

---

## API Reference

### Analytics
| Method | Endpoint                          | Description                         |
|--------|-----------------------------------|-------------------------------------|
| GET    | /api/analytics/kpi                | Revenue, orders, users, avg AOV     |
| GET    | /api/analytics/daily-sales        | Daily revenue trend (up to 365 d)   |
| GET    | /api/analytics/weekly-sales       | Weekly revenue trend (up to 52 wk)  |
| GET    | /api/analytics/top-products       | Top N products by revenue           |
| GET    | /api/analytics/category-revenue   | Revenue breakdown by category       |
| GET    | /api/analytics/customer-segments  | Segment-level revenue               |
| GET    | /api/analytics/export/tableau     | Full denormalized JSON for export   |

### Orders / Products / Users
| Method | Endpoint              | Description             |
|--------|-----------------------|-------------------------|
| GET    | /api/orders/          | List orders (filterable)|
| POST   | /api/orders/          | Create order            |
| GET    | /api/products/        | List products           |
| POST   | /api/products/        | Create product          |
| GET    | /api/users/           | List users              |
| POST   | /api/users/           | Create user             |

---

## CI/CD Pipeline

### Trigger events
- `push` to `main` or `develop`
- Any `pull_request` targeting `main`

### Jobs

```
┌──────────────┐    ┌─────────────────┐
│ test-backend │    │ build-frontend  │
│              │    │                 │
│  PostgreSQL  │    │  npm ci         │
│  service     │    │  npm run build  │
│  pytest      │    │  Upload artifact│
└──────┬───────┘    └───────┬─────────┘
       └──────────┬──────────┘
                  ▼
         ┌────────────────┐
         │  docker-build  │  (main branch only)
         │                │
         │  Buildx cache  │
         │  Push backend  │
         │  Push frontend │
         │  Push ETL      │
         └────────────────┘
```

### Docker Hub secrets
Add these to your repository's **Settings → Secrets → Actions**:

| Secret           | Value                      |
|------------------|----------------------------|
| `DOCKER_USERNAME`| Your Docker Hub username   |
| `DOCKER_PASSWORD`| Your Docker Hub access token|

---

## ETL + Tableau Integration

### Automated Schedule
The ETL pipeline runs **daily at 02:00 UTC** via `.github/workflows/etl-pipeline.yml`.
Generated CSV files are uploaded as GitHub Actions **artifacts** (retained 30 days).

### Manual Run
Trigger via GitHub Actions UI: **Actions → Scheduled ETL → Run workflow**

### CSV outputs

| File                           | Contents                                    |
|--------------------------------|---------------------------------------------|
| `orders_full_latest.csv`       | Full denormalized orders (best for Tableau) |
| `daily_revenue_latest.csv`     | Aggregated daily revenue trend              |
| `category_performance_latest.csv` | Revenue & units by product category     |
| `customer_summary_latest.csv`  | Customer lifetime value & RFM signals       |
| `top_products_latest.csv`      | Top 50 products ranked by revenue           |

### Tableau Connection Steps
1. Download `orders_full_latest.csv` from GitHub Artifacts (or run ETL locally)
2. Open Tableau → **Connect → Text File** → select the CSV
3. Build your dashboards using the pre-enriched columns:
   - `order_date`, `order_month` — for time series
   - `category` — for categorical breakdowns
   - `customer_country`, `customer_city` — for geographic maps
   - `total_price`, `unit_price`, `quantity` — for numeric measures
   - `customer_segment` — for segment filtering (VIP / Regular / New)

---

## Environment Variables

| Variable           | Default                                      | Description                    |
|--------------------|----------------------------------------------|--------------------------------|
| `POSTGRES_USER`    | `ecom_user`                                  | PostgreSQL username            |
| `POSTGRES_PASSWORD`| `ecom_pass`                                  | PostgreSQL password            |
| `POSTGRES_DB`      | `ecom_db`                                    | PostgreSQL database name       |
| `POSTGRES_PORT`    | `5433`                                       | Host port mapping              |
| `DATABASE_URL`     | `postgresql://ecom_user:ecom_pass@database:5432/ecom_db` | Full DSN |
| `REACT_APP_API_URL`| `http://localhost:8000`                      | Backend URL for React          |
| `ETL_OUTPUT_DIR`   | `/app/exports`                               | ETL output directory           |

---

## Health Checks

All services expose health checks in `docker-compose.yml`:

| Service  | Check method                        | Interval |
|----------|-------------------------------------|----------|
| database | `pg_isready`                        | 10s      |
| backend  | HTTP GET `/health` (Python urllib)  | 30s      |
| frontend | `wget --spider localhost:3000`      | 30s      |

The `backend` waits for `database` to be **healthy** before starting.
The `frontend` waits for `backend` to be **healthy** before starting.

---

## Running Tests

```bash
cd backend

# With a running PostgreSQL instance
DATABASE_URL=postgresql://test_user:test_pass@localhost:5432/test_db \
  PYTHONPATH=. pytest tests/ -v
```

Tests cover: root, health, user CRUD, product CRUD, order CRUD, all analytics endpoints.

---

## Production Considerations

- Change `POSTGRES_PASSWORD` in `.env` before deploying
- Remove `--reload` flag from `uvicorn` for production (already done in entrypoint)
- Set `REACT_APP_API_URL` to your real backend domain
- Configure Docker Hub secrets for automated image publishing
- Use Docker secrets or a vault (Vault, AWS Secrets Manager) for production credentials
