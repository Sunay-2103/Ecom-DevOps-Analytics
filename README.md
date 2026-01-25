# 🛒 E-Commerce DevOps Analytics Platform

A full-stack analytics platform for e-commerce data, built with **FastAPI**, **PostgreSQL**, **React**, and fully containerized with **Docker**. Includes Tableau export support and a CI/CD pipeline via GitHub Actions.

---

## 📁 Project Structure

```
ecommerce-devops-platform/
├── backend/                    # FastAPI Python backend
│   ├── app/
│   │   ├── main.py             # Application entry point
│   │   ├── database.py         # SQLAlchemy engine + session
│   │   ├── models/models.py    # ORM models (User, Product, Order)
│   │   ├── schemas/schemas.py  # Pydantic request/response schemas
│   │   └── routers/
│   │       ├── users.py        # /api/users endpoints
│   │       ├── products.py     # /api/products endpoints
│   │       ├── orders.py       # /api/orders endpoints
│   │       └── analytics.py    # /api/analytics endpoints
│   ├── seed_data.py            # Synthetic data generator (1300+ records)
│   ├── entrypoint.sh           # Docker startup script
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/                   # React frontend dashboard
│   ├── src/
│   │   ├── App.js              # Root with layout + routing
│   │   ├── App.css             # Global styles (dark theme)
│   │   ├── services/api.js     # API client layer
│   │   ├── hooks/useApi.js     # Custom data-fetching hook
│   │   ├── components/
│   │   │   └── Sidebar.js      # Navigation sidebar
│   │   └── pages/
│   │       ├── Dashboard.js    # KPI cards + revenue chart + pie
│   │       ├── Analytics.js    # Composite trends + radar chart
│   │       ├── Orders.js       # Filterable orders table
│   │       ├── Products.js     # Product catalogue with filters
│   │       └── TableauExport.js # CSV export + Tableau guide
│   ├── nginx.conf
│   ├── package.json
│   └── Dockerfile
│
├── database/
│   └── init.sql                # PostgreSQL initialization
│
├── tableau/
│   └── TABLEAU_GUIDE.md        # Dashboard build instructions
│
├── .github/workflows/
│   └── ci-cd.yml               # GitHub Actions CI/CD pipeline
│
├── docker-compose.yml          # Full stack orchestration
├── .gitignore
└── README.md
```

---

## ⚙️ Tech Stack

| Layer      | Technology                        |
|------------|-----------------------------------|
| Backend    | Python 3.11, FastAPI, SQLAlchemy  |
| Database   | PostgreSQL 15                     |
| Frontend   | React 18, Recharts, Lucide React  |
| Serving    | Uvicorn (API), Nginx (React)      |
| DevOps     | Docker, Docker Compose            |
| CI/CD      | GitHub Actions                    |
| Analytics  | Recharts (inline), Tableau (export)|

---

## 🚀 Quick Start — Docker (Recommended)

### Prerequisites
- Docker Desktop or Docker Engine + Compose plugin
- Git

### 1. Clone the repository
```bash
git clone https://github.com/yourname/ecommerce-devops-platform.git
cd ecommerce-devops-platform
```

### 2. Start all services
```bash
docker compose up --build
```

This will:
1. Start **PostgreSQL** database
2. Build and start **FastAPI** backend → auto-creates tables + seeds 1,300+ records
3. Build and start **React** frontend (served via Nginx)

### 3. Open the application
| Service     | URL                             |
|-------------|---------------------------------|
| Frontend    | http://localhost:3000           |
| Backend API | http://localhost:8000           |
| API Docs    | http://localhost:8000/docs      |

---

## 🛠️ Local Development (Without Docker)

### Backend
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set database connection
export DATABASE_URL=postgresql://ecom_user:ecom_pass@localhost:5432/ecom_db

# Create tables + seed data
python seed_data.py

# Start server
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
REACT_APP_API_URL=http://localhost:8000 npm start
```

---

## 📡 API Endpoints

### Users
| Method | Endpoint                   | Description         |
|--------|----------------------------|---------------------|
| GET    | /api/users/                | List all users      |
| GET    | /api/users/{id}            | Get user by ID      |
| POST   | /api/users/                | Create user         |

### Products
| Method | Endpoint                   | Description           |
|--------|----------------------------|-----------------------|
| GET    | /api/products/             | List products         |
| GET    | /api/products/categories   | Get all categories    |
| GET    | /api/products/{id}         | Get product by ID     |
| POST   | /api/products/             | Create product        |

### Orders
| Method | Endpoint                   | Description           |
|--------|----------------------------|-----------------------|
| GET    | /api/orders/               | List orders (filtered)|
| GET    | /api/orders/{id}           | Get order by ID       |
| POST   | /api/orders/               | Create order          |

### Analytics
| Method | Endpoint                          | Description               |
|--------|-----------------------------------|---------------------------|
| GET    | /api/analytics/kpi                | KPI summary               |
| GET    | /api/analytics/daily-sales        | Daily revenue (last N days)|
| GET    | /api/analytics/weekly-sales       | Weekly revenue             |
| GET    | /api/analytics/top-products       | Top products by revenue    |
| GET    | /api/analytics/category-revenue   | Revenue per category       |
| GET    | /api/analytics/customer-segments  | Segment analysis           |
| GET    | /api/analytics/export/tableau     | Full export for Tableau    |

---

## 🗄️ Database Schema

```sql
users
  id          SERIAL PRIMARY KEY
  name        VARCHAR(100)
  email       VARCHAR(150) UNIQUE
  city        VARCHAR(100)
  country     VARCHAR(100)
  segment     VARCHAR(50)       -- VIP / Regular / New
  created_at  TIMESTAMP

products
  id          SERIAL PRIMARY KEY
  name        VARCHAR(200)
  category    VARCHAR(100)
  price       FLOAT
  stock       INTEGER
  description TEXT
  created_at  TIMESTAMP

orders
  id          SERIAL PRIMARY KEY
  user_id     INTEGER REFERENCES users(id)
  product_id  INTEGER REFERENCES products(id)
  quantity    INTEGER
  total_price FLOAT
  status      VARCHAR(50)       -- completed / pending / refunded
  created_at  TIMESTAMP
```

---

## 📊 Tableau Integration

1. Go to **Tableau Export** page in the dashboard
2. Click **Export CSV for Tableau**
3. Open the CSV in Tableau Desktop or Tableau Public
4. Follow the step-by-step guide in `tableau/TABLEAU_GUIDE.md`

Recommended dashboards to build:
- 📈 Monthly Sales Trend (Line/Area)
- 🏆 Top Products by Revenue (Bar)
- 🥧 Category Distribution (Pie/Treemap)
- 🌍 Customer Geography (Filled Map)
- 👥 Customer Segment KPIs

---

## 🔁 Git Workflow

### Branch strategy
```
main          ← production-ready code
develop       ← integration branch
feature/*     ← new features
fix/*         ← bug fixes
```

### Example commit history
```
feat: initialise project with FastAPI + SQLAlchemy
feat(db): add User, Product, Order models
feat(api): implement CRUD endpoints for users and products
feat(api): implement orders endpoint with joins
feat(analytics): add KPI, daily-sales, top-products endpoints
feat(analytics): add Tableau export endpoint
feat(frontend): scaffold React app with sidebar navigation
feat(frontend): implement Dashboard page with KPI cards + charts
feat(frontend): implement Analytics page with composite charts
feat(frontend): add Orders and Products filterable tables
feat(frontend): implement Tableau export page with guide
feat(devops): add Dockerfiles for backend and frontend
feat(devops): add docker-compose with all three services
feat(ci): add GitHub Actions CI/CD pipeline
docs: add README with setup, API reference, and schema
```

---

## 🔐 CI/CD Pipeline (GitHub Actions)

Defined in `.github/workflows/ci-cd.yml`:

```
Push to main/develop
        │
        ▼
┌───────────────┐    ┌──────────────────┐
│  Backend Tests │    │  Frontend Build   │
│  (pytest)      │    │  (npm run build)  │
└───────┬───────┘    └────────┬─────────┘
        └──────────┬──────────┘
                   ▼
        ┌──────────────────┐
        │  Docker Build     │
        │  & Push to Hub    │  ← main branch only
        └────────┬─────────┘
                 ▼
        ┌──────────────────┐
        │  Deploy to        │
        │  Production       │
        └──────────────────┘
```

---

## 🖥️ Dashboard Pages

| Page         | Features                                                   |
|--------------|------------------------------------------------------------|
| Dashboard    | KPI cards, revenue area chart, category pie, top-5 bar     |
| Analytics    | Composite trend chart, product bar, radar chart, segments  |
| Orders       | Filterable table (status), 100 records, date & customer    |
| Products     | Category filter, price, stock with low-stock warning       |
| Tableau      | CSV export + 7-step dashboard build guide                  |

---

## 📸 Screenshots Description (for Report)

1. **Dashboard Overview** — Dark-themed dashboard showing 4 KPI cards (revenue, orders, users, avg order value), area chart of 30-day revenue trend, donut chart of category revenue, and horizontal bar of top products
2. **Analytics Page** — Composed bar+line chart showing weekly revenue vs orders, horizontal bar of top 8 products by units, radar chart for category comparison, segment tiles
3. **Orders Table** — Sortable and filterable transaction table with status badges (green/yellow/red)
4. **Products Page** — Product catalogue with category pill filter and color-coded category badges
5. **Tableau Export** — Step-by-step guide UI with export button, numbered steps for building each dashboard

---

## 👥 Team / Credits

Built as a university DevOps + Data Analytics project demonstrating:
- **Backend API design** with FastAPI
- **Relational database** modelling with PostgreSQL + SQLAlchemy
- **Frontend dashboard** engineering with React + Recharts
- **Containerization** with Docker and Compose
- **CI/CD automation** with GitHub Actions
- **Business Intelligence** integration with Tableau

# Updated on 2026-01-22 by Anwar

# Updated on 2026-03-03 by Anwar

# Updated on 2026-04-02 by Anwar
change 12
change 15
change 33
change 26
change 6
change 11
