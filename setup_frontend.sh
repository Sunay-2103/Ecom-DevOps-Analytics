#!/usr/bin/env bash
# ============================================================
#  E-Commerce DevOps Analytics Platform — React Frontend
#  Run from your project root:  bash setup_frontend.sh
# ============================================================
set -e

FRONTEND="./frontend"
mkdir -p "$FRONTEND/public"
mkdir -p "$FRONTEND/src/components"
mkdir -p "$FRONTEND/src/pages"
mkdir -p "$FRONTEND/src/hooks"
mkdir -p "$FRONTEND/src/services"

# ────────────────────────────────────────────────────────────
# package.json
# ────────────────────────────────────────────────────────────
cat > "$FRONTEND/package.json" << 'EOF'
{
  "name": "ecommerce-analytics-frontend",
  "version": "1.0.0",
  "private": true,
  "dependencies": {
    "axios": "^1.7.2",
    "date-fns": "^3.6.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-scripts": "5.0.1",
    "recharts": "^2.12.7"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test":  "react-scripts test --watchAll=false"
  },
  "eslintConfig": {
    "extends": ["react-app"]
  },
  "browserslist": {
    "production": [">0.2%", "not dead", "not op_mini all"],
    "development": ["last 1 chrome version", "last 1 firefox version"]
  }
}
EOF

# ────────────────────────────────────────────────────────────
# nginx.conf
# ────────────────────────────────────────────────────────────
cat > "$FRONTEND/nginx.conf" << 'EOF'
server {
    listen 3000;
    root /usr/share/nginx/html;
    index index.html;

    location /api/ {
        proxy_pass         http://backend:8000;
        proxy_set_header   Host              $host;
        proxy_set_header   X-Real-IP         $remote_addr;
        proxy_set_header   X-Forwarded-For   $proxy_add_x_forwarded_for;
    }

    location / {
        try_files $uri $uri/ /index.html;
    }
}
EOF

# ────────────────────────────────────────────────────────────
# Dockerfile
# ────────────────────────────────────────────────────────────
cat > "$FRONTEND/Dockerfile" << 'EOF'
FROM node:20-alpine AS builder
WORKDIR /app
COPY package.json ./
RUN npm install --legacy-peer-deps
COPY . .
ENV CI=false
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 3000
CMD ["nginx", "-g", "daemon off;"]
EOF

# ────────────────────────────────────────────────────────────
# public/index.html
# ────────────────────────────────────────────────────────────
cat > "$FRONTEND/public/index.html" << 'EOF'
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="theme-color" content="#0a0c10" />
    <title>EcomAnalytics — DevOps Dashboard</title>
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link
      href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap"
      rel="stylesheet"
    />
    <style>
      * { box-sizing: border-box; margin: 0; padding: 0; }
      body { background: #0a0c10; color: #e8ecf1; font-family: 'Inter', system-ui, sans-serif; }
    </style>
  </head>
  <body>
    <noscript>You need to enable JavaScript to run this application.</noscript>
    <div id="root"></div>
  </body>
</html>
EOF

# ────────────────────────────────────────────────────────────
# src/index.js
# ────────────────────────────────────────────────────────────
cat > "$FRONTEND/src/index.js" << 'EOF'
import React from 'react';
import ReactDOM from 'react-dom/client';
import './App.css';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
EOF

# ────────────────────────────────────────────────────────────
# src/App.js
# ────────────────────────────────────────────────────────────
cat > "$FRONTEND/src/App.js" << 'EOF'
import React, { useState } from 'react';
import Sidebar from './components/Sidebar';
import Navbar  from './components/Navbar';
import Dashboard     from './pages/Dashboard';
import Analytics     from './pages/Analytics';
import Orders        from './pages/Orders';
import Products      from './pages/Products';
import TableauExport from './pages/TableauExport';

const PAGES = {
  dashboard: { label: 'Dashboard',      component: <Dashboard /> },
  analytics: { label: 'Analytics',      component: <Analytics /> },
  orders:    { label: 'Orders',          component: <Orders /> },
  products:  { label: 'Products',        component: <Products /> },
  tableau:   { label: 'Tableau Export',  component: <TableauExport /> },
};

export default function App() {
  const [page, setPage] = useState('dashboard');
  const [sidebarOpen, setSidebarOpen] = useState(true);

  return (
    <div className="app-shell">
      <Sidebar
        activePage={page}
        onNavigate={setPage}
        collapsed={!sidebarOpen}
      />
      <div className="app-body">
        <Navbar
          title={PAGES[page]?.label ?? ''}
          onToggleSidebar={() => setSidebarOpen(o => !o)}
        />
        <main className="main-content">
          {PAGES[page]?.component ?? <Dashboard />}
        </main>
      </div>
    </div>
  );
}
EOF

# ────────────────────────────────────────────────────────────
# src/App.css
# ────────────────────────────────────────────────────────────
cat > "$FRONTEND/src/App.css" << 'EOF'
/* ── Reset ──────────────────────────────────────────── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

/* ── Tokens ─────────────────────────────────────────── */
:root {
  --bg:        #0a0c10;
  --bg2:       #111318;
  --bg3:       #181c23;
  --border:    #1f2430;
  --accent:    #00e5b0;
  --accent2:   #6c63ff;
  --accent3:   #ff6b6b;
  --accent4:   #ffd166;
  --text:      #e8ecf1;
  --text2:     #8892a4;
  --text3:     #4a5568;
  --sidebar-w: 220px;
  --navbar-h:  56px;
  --radius:    10px;
  --radius-lg: 16px;
  --shadow:    0 4px 24px rgba(0,0,0,.45);
  --transition: .15s ease;
}

html, body { height: 100%; }

/* ── Shell ───────────────────────────────────────────── */
.app-shell {
  display: flex;
  min-height: 100vh;
  background: var(--bg);
}

.app-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  overflow: hidden;
}

/* ── Sidebar ─────────────────────────────────────────── */
.sidebar {
  width: var(--sidebar-w);
  min-height: 100vh;
  background: var(--bg2);
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  transition: width var(--transition);
  overflow: hidden;
}
.sidebar.collapsed { width: 60px; }

.sidebar-logo {
  padding: 20px 16px;
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: center;
  gap: 10px;
  white-space: nowrap;
}
.logo-icon {
  width: 34px; height: 34px;
  background: linear-gradient(135deg, var(--accent), var(--accent2));
  border-radius: 9px;
  display: flex; align-items: center; justify-content: center;
  font-size: 16px; flex-shrink: 0;
}
.logo-text  { font-size: 14px; font-weight: 700; color: var(--text); }
.logo-sub   { font-size: 10px; color: var(--text2); letter-spacing: .07em; text-transform: uppercase; }

.sidebar-nav {
  flex: 1;
  padding: 12px 8px;
  display: flex;
  flex-direction: column;
  gap: 2px;
  overflow-y: auto;
}
.nav-section {
  font-size: 10px; font-weight: 600;
  color: var(--text3); letter-spacing: .1em; text-transform: uppercase;
  padding: 10px 8px 5px;
  white-space: nowrap; overflow: hidden;
}
.nav-item {
  display: flex; align-items: center; gap: 10px;
  padding: 9px 10px;
  border-radius: 8px;
  cursor: pointer;
  color: var(--text2);
  font-size: 13px; font-weight: 500;
  transition: all var(--transition);
  border: 1px solid transparent;
  user-select: none;
  white-space: nowrap;
  overflow: hidden;
}
.nav-item:hover { background: var(--bg3); color: var(--text); }
.nav-item.active {
  background: rgba(0,229,176,.08);
  color: var(--accent);
  border-color: rgba(0,229,176,.15);
}
.nav-icon { font-size: 16px; flex-shrink: 0; width: 20px; text-align: center; }
.nav-badge {
  margin-left: auto; background: var(--accent2); color: #fff;
  font-size: 9px; font-weight: 700; padding: 2px 6px; border-radius: 20px;
}

.sidebar-footer {
  padding: 12px;
  border-top: 1px solid var(--border);
}
.status-pill {
  display: flex; align-items: center; gap: 8px;
  background: rgba(0,229,176,.06);
  border: 1px solid rgba(0,229,176,.15);
  border-radius: 8px; padding: 9px 10px;
  overflow: hidden; white-space: nowrap;
}
.status-dot {
  width: 7px; height: 7px; border-radius: 50%;
  background: var(--accent); flex-shrink: 0;
  animation: blink 2s infinite;
}
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:.35} }

/* ── Navbar ──────────────────────────────────────────── */
.navbar {
  height: var(--navbar-h);
  background: var(--bg2);
  border-bottom: 1px solid var(--border);
  display: flex; align-items: center; justify-content: space-between;
  padding: 0 24px;
  flex-shrink: 0;
}
.navbar-left { display: flex; align-items: center; gap: 14px; }
.navbar-title {
  font-size: 15px; font-weight: 700; color: var(--text);
}
.menu-btn {
  background: none; border: 1px solid var(--border);
  border-radius: 7px; padding: 5px 8px;
  color: var(--text2); cursor: pointer; font-size: 16px;
  transition: all var(--transition);
}
.menu-btn:hover { background: var(--bg3); color: var(--text); }
.navbar-right { display: flex; align-items: center; gap: 10px; }
.navbar-badge {
  font-size: 11px; color: var(--text2);
  background: var(--bg3); border: 1px solid var(--border);
  padding: 4px 10px; border-radius: 20px;
}

/* ── Main content ────────────────────────────────────── */
.main-content {
  flex: 1;
  padding: 28px 32px;
  overflow-y: auto;
  background: var(--bg);
}

/* ── Page header ─────────────────────────────────────── */
.page-header { margin-bottom: 24px; }
.page-title  { font-size: 22px; font-weight: 700; color: var(--text); }
.page-subtitle { font-size: 13px; color: var(--text2); margin-top: 3px; }

/* ── KPI Grid ────────────────────────────────────────── */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
  gap: 14px;
  margin-bottom: 24px;
}
.kpi-card {
  background: var(--bg2);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 20px 22px;
  position: relative; overflow: hidden;
  transition: transform var(--transition), box-shadow var(--transition);
}
.kpi-card:hover { transform: translateY(-2px); box-shadow: var(--shadow); }
.kpi-card::before {
  content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px;
}
.kpi-card.green::before  { background: linear-gradient(90deg, var(--accent),  transparent); }
.kpi-card.purple::before { background: linear-gradient(90deg, var(--accent2), transparent); }
.kpi-card.red::before    { background: linear-gradient(90deg, var(--accent3), transparent); }
.kpi-card.yellow::before { background: linear-gradient(90deg, var(--accent4), transparent); }
.kpi-label {
  font-size: 10px; font-weight: 600; color: var(--text2);
  text-transform: uppercase; letter-spacing: .08em;
}
.kpi-value {
  font-size: 28px; font-weight: 700; color: var(--text);
  margin: 7px 0 3px; line-height: 1;
}
.kpi-change { font-size: 11px; }
.kpi-change.up   { color: var(--accent); }
.kpi-change.down { color: var(--accent3); }
.kpi-icon {
  position: absolute; right: 18px; top: 50%; transform: translateY(-50%);
  width: 40px; height: 40px; border-radius: 10px;
  display: flex; align-items: center; justify-content: center; font-size: 18px;
}
.kpi-card.green  .kpi-icon { background: rgba(0,229,176,.1); }
.kpi-card.purple .kpi-icon { background: rgba(108,99,255,.1); }
.kpi-card.red    .kpi-icon { background: rgba(255,107,107,.1); }
.kpi-card.yellow .kpi-icon { background: rgba(255,209,102,.1); }

/* ── Charts ──────────────────────────────────────────── */
.chart-row   { display: grid; grid-template-columns: 2fr 1fr; gap: 16px; margin-bottom: 16px; }
.chart-row-2 { display: grid; grid-template-columns: 1fr 1fr;  gap: 16px; margin-bottom: 16px; }
.chart-row-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px; margin-bottom: 16px; }

.card {
  background: var(--bg2);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 20px 22px;
}
.card.full { grid-column: 1 / -1; }

.card-header {
  display: flex; align-items: flex-start; justify-content: space-between;
  margin-bottom: 16px;
}
.card-title    { font-size: 14px; font-weight: 700; color: var(--text); }
.card-subtitle { font-size: 11px; color: var(--text2); margin-top: 2px; }

/* ── Filter bar ──────────────────────────────────────── */
.filter-bar { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 18px; }
.filter-btn {
  padding: 6px 14px; border-radius: 20px; font-size: 12px; font-weight: 600;
  border: 1px solid var(--border); background: var(--bg2); color: var(--text2);
  cursor: pointer; transition: all var(--transition);
}
.filter-btn:hover,
.filter-btn.active {
  border-color: var(--accent); color: var(--accent);
  background: rgba(0,229,176,.06);
}

/* ── Table ───────────────────────────────────────────── */
.data-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.data-table th {
  text-align: left; padding: 9px 14px;
  font-size: 10px; font-weight: 700; color: var(--text2);
  text-transform: uppercase; letter-spacing: .07em;
  border-bottom: 1px solid var(--border);
}
.data-table td {
  padding: 11px 14px;
  border-bottom: 1px solid rgba(31,36,48,.7);
  color: var(--text);
}
.data-table tr:hover td { background: rgba(255,255,255,.02); }
.data-table tr:last-child td { border-bottom: none; }

/* ── Badges ──────────────────────────────────────────── */
.badge {
  display: inline-flex; align-items: center;
  padding: 3px 9px; border-radius: 20px;
  font-size: 11px; font-weight: 600;
}
.badge-green  { background: rgba(0,229,176,.12);  color: var(--accent); }
.badge-red    { background: rgba(255,107,107,.12); color: var(--accent3); }
.badge-yellow { background: rgba(255,209,102,.12); color: var(--accent4); }
.badge-purple { background: rgba(108,99,255,.12);  color: var(--accent2); }
.badge-gray   { background: rgba(255,255,255,.06); color: var(--text2); }

/* ── Loading ─────────────────────────────────────────── */
.spinner-wrap { display: flex; justify-content: center; align-items: center; padding: 60px; }
.spinner {
  width: 36px; height: 36px;
  border: 3px solid var(--border); border-top-color: var(--accent);
  border-radius: 50%; animation: spin .75s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

.skeleton {
  background: linear-gradient(90deg, var(--bg2) 25%, var(--bg3) 50%, var(--bg2) 75%);
  background-size: 200% 100%;
  animation: shimmer 1.6s infinite;
  border-radius: var(--radius);
}
@keyframes shimmer { 0%{background-position:200% 0} 100%{background-position:-200% 0} }

/* ── Error ───────────────────────────────────────────── */
.error-box {
  background: rgba(255,107,107,.08); border: 1px solid rgba(255,107,107,.2);
  border-radius: var(--radius); padding: 14px 18px;
  color: var(--accent3); font-size: 13px;
}

/* ── Tableau page ────────────────────────────────────── */
.tableau-step {
  display: flex; gap: 14px; align-items: flex-start;
  background: var(--bg3); border: 1px solid var(--border);
  border-radius: var(--radius); padding: 16px 18px;
  margin-bottom: 10px;
}
.step-num {
  width: 28px; height: 28px; border-radius: 50%; flex-shrink: 0;
  background: linear-gradient(135deg, var(--accent), var(--accent2));
  display: flex; align-items: center; justify-content: center;
  font-size: 12px; font-weight: 700; color: #000;
}
.step-body h4 { font-size: 13px; font-weight: 700; color: var(--text); margin-bottom: 4px; }
.step-body p  { font-size: 12px; color: var(--text2); line-height: 1.65; }
.step-body code {
  background: var(--bg2); padding: 1px 7px; border-radius: 4px;
  font-family: monospace; font-size: 11px; color: var(--accent);
}

.export-btn {
  display: inline-flex; align-items: center; gap: 8px;
  background: linear-gradient(135deg, var(--accent), var(--accent2));
  color: #000; font-weight: 700; font-size: 14px;
  padding: 11px 22px; border-radius: 9px; border: none;
  cursor: pointer; transition: opacity var(--transition), transform var(--transition);
}
.export-btn:hover   { opacity: .88; transform: translateY(-1px); }
.export-btn:disabled { opacity: .5; cursor: not-allowed; transform: none; }

/* ── Segment cards ───────────────────────────────────── */
.seg-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-top: 12px; }
.seg-card {
  background: var(--bg3); border: 1px solid var(--border);
  border-radius: var(--radius); padding: 16px 18px;
}

/* ── Scrollbar ───────────────────────────────────────── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track  { background: var(--bg); }
::-webkit-scrollbar-thumb  { background: var(--border); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--text3); }

/* ── Responsive ──────────────────────────────────────── */
@media (max-width: 1100px) {
  .chart-row   { grid-template-columns: 1fr; }
  .chart-row-3 { grid-template-columns: 1fr 1fr; }
}
@media (max-width: 768px) {
  .sidebar       { display: none; }
  .main-content  { padding: 18px 14px; }
  .chart-row-2,
  .chart-row-3   { grid-template-columns: 1fr; }
  .kpi-grid      { grid-template-columns: 1fr 1fr; }
  .seg-grid      { grid-template-columns: 1fr; }
}
EOF

# ────────────────────────────────────────────────────────────
# src/services/api.js
# ────────────────────────────────────────────────────────────
cat > "$FRONTEND/src/services/api.js" << 'EOF'
import axios from 'axios';

const BASE_URL = process.env.REACT_APP_API_URL || '';

const client = axios.create({
  baseURL: BASE_URL,
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' },
});

// ── Analytics ────────────────────────────────────────────
export const getKPI            = ()           => client.get('/api/analytics/kpi').then(r => r.data);
export const getDailySales     = (days = 30)  => client.get(`/api/analytics/daily-sales?days=${days}`).then(r => r.data);
export const getWeeklySales    = (weeks = 12) => client.get(`/api/analytics/weekly-sales?weeks=${weeks}`).then(r => r.data);
export const getTopProducts    = (limit = 10) => client.get(`/api/analytics/top-products?limit=${limit}`).then(r => r.data);
export const getCategoryRevenue = ()          => client.get('/api/analytics/category-revenue').then(r => r.data);
export const getCustomerSegments = ()         => client.get('/api/analytics/customer-segments').then(r => r.data);
export const exportTableau     = ()           => client.get('/api/analytics/export/tableau').then(r => r.data);

// ── Orders ───────────────────────────────────────────────
export const getOrders  = (params = '') => client.get(`/api/orders/?limit=100${params}`).then(r => r.data);

// ── Products ─────────────────────────────────────────────
export const getProducts   = (params = '') => client.get(`/api/products/?limit=100${params}`).then(r => r.data);
export const getCategories = ()            => client.get('/api/products/categories').then(r => r.data);

// ── Users ────────────────────────────────────────────────
export const getUsers = (params = '') => client.get(`/api/users/?limit=100${params}`).then(r => r.data);

export default client;
EOF

# ────────────────────────────────────────────────────────────
# src/hooks/useApi.js
# ────────────────────────────────────────────────────────────
cat > "$FRONTEND/src/hooks/useApi.js" << 'EOF'
import { useState, useEffect, useCallback } from 'react';

/**
 * Generic data-fetching hook.
 * @param {Function} apiFn  - Function that returns a Promise (from api.js)
 * @param {Array}    deps   - Re-fetch whenever these change
 */
export default function useApi(apiFn, deps = []) {
  const [data,    setData]    = useState(null);
  const [loading, setLoading] = useState(true);
  const [error,   setError]   = useState(null);

  const fetch = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await apiFn();
      setData(result);
    } catch (err) {
      const msg = err?.response?.data?.detail ?? err?.message ?? 'Unknown error';
      setError(msg);
    } finally {
      setLoading(false);
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);

  useEffect(() => { fetch(); }, [fetch]);

  return { data, loading, error, refetch: fetch };
}
EOF

# ────────────────────────────────────────────────────────────
# src/components/Sidebar.js
# ────────────────────────────────────────────────────────────
cat > "$FRONTEND/src/components/Sidebar.js" << 'EOF'
import React from 'react';

const NAV_ITEMS = [
  { id: 'dashboard', icon: '⬡', label: 'Dashboard' },
  { id: 'analytics', icon: '↗', label: 'Analytics' },
  { id: 'orders',    icon: '☰', label: 'Orders' },
  { id: 'products',  icon: '⊞', label: 'Products' },
  { id: 'tableau',   icon: '⬇', label: 'Tableau Export', badge: 'CSV' },
];

export default function Sidebar({ activePage, onNavigate, collapsed }) {
  return (
    <aside className={`sidebar${collapsed ? ' collapsed' : ''}`}>
      <div className="sidebar-logo">
        <div className="logo-icon">📊</div>
        {!collapsed && (
          <div>
            <div className="logo-text">EcomAnalytics</div>
            <div className="logo-sub">DevOps Platform</div>
          </div>
        )}
      </div>

      <nav className="sidebar-nav">
        {!collapsed && <div className="nav-section">Navigation</div>}
        {NAV_ITEMS.map(item => (
          <div
            key={item.id}
            className={`nav-item${activePage === item.id ? ' active' : ''}`}
            onClick={() => onNavigate(item.id)}
            title={collapsed ? item.label : undefined}
          >
            <span className="nav-icon">{item.icon}</span>
            {!collapsed && item.label}
            {!collapsed && item.badge && (
              <span className="nav-badge">{item.badge}</span>
            )}
          </div>
        ))}
      </nav>

      {!collapsed && (
        <div className="sidebar-footer">
          <div className="status-pill">
            <div className="status-dot" />
            <div>
              <div style={{ fontSize: 11, fontWeight: 500, color: 'var(--text)' }}>API Connected</div>
              <div style={{ fontSize: 10, color: 'var(--text2)' }}>FastAPI · PostgreSQL</div>
            </div>
          </div>
        </div>
      )}
    </aside>
  );
}
EOF

# ────────────────────────────────────────────────────────────
# src/components/Navbar.js
# ────────────────────────────────────────────────────────────
cat > "$FRONTEND/src/components/Navbar.js" << 'EOF'
import React from 'react';

export default function Navbar({ title, onToggleSidebar }) {
  const today = new Date().toLocaleDateString('en-US', {
    weekday: 'short', year: 'numeric', month: 'short', day: 'numeric',
  });

  return (
    <header className="navbar">
      <div className="navbar-left">
        <button className="menu-btn" onClick={onToggleSidebar} aria-label="Toggle sidebar">
          ☰
        </button>
        <span className="navbar-title">{title}</span>
      </div>

      <div className="navbar-right">
        <span className="navbar-badge">🐳 Docker · FastAPI</span>
        <span className="navbar-badge">{today}</span>
      </div>
    </header>
  );
}
EOF

# ────────────────────────────────────────────────────────────
# src/pages/Dashboard.js
# ────────────────────────────────────────────────────────────
cat > "$FRONTEND/src/pages/Dashboard.js" << 'EOF'
import React, { useState } from 'react';
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, PieChart, Pie, Cell, Legend,
  BarChart, Bar,
} from 'recharts';
import useApi from '../hooks/useApi';
import { getKPI, getDailySales, getCategoryRevenue, getTopProducts } from '../services/api';

const COLORS = ['#00e5b0','#6c63ff','#ff6b6b','#ffd166','#06d6a0','#118ab2'];
const fmt = n => (n >= 1000 ? `$${(n / 1000).toFixed(1)}k` : `$${Number(n ?? 0).toFixed(0)}`);

function KPICard({ label, value, change, color, icon }) {
  return (
    <div className={`kpi-card ${color}`}>
      <div className="kpi-label">{label}</div>
      <div className="kpi-value">{value ?? '—'}</div>
      {change && (
        <div className={`kpi-change ${change.startsWith('+') ? 'up' : 'down'}`}>
          {change} vs last month
        </div>
      )}
      <div className="kpi-icon">{icon}</div>
    </div>
  );
}

export default function Dashboard() {
  const [days, setDays] = useState(30);

  const { data: kpi,      loading: kpiLoad }   = useApi(() => getKPI(),            []);
  const { data: daily,    loading: dailyLoad }  = useApi(() => getDailySales(days), [days]);
  const { data: catRev }                        = useApi(() => getCategoryRevenue(), []);
  const { data: topProds }                      = useApi(() => getTopProducts(5),    []);

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Dashboard</h1>
        <p className="page-subtitle">Real-time overview of your e-commerce performance</p>
      </div>

      {/* KPI Cards */}
      <div className="kpi-grid">
        {kpiLoad ? (
          [1,2,3,4].map(i => (
            <div key={i} className="skeleton" style={{ height: 110, borderRadius: 16 }} />
          ))
        ) : (
          <>
            <KPICard label="Total Revenue"   value={fmt(kpi?.total_revenue)}   change="+12.4%" color="green"  icon="💰" />
            <KPICard label="Total Orders"    value={kpi?.total_orders?.toLocaleString()} change="+8.1%"  color="purple" icon="🛒" />
            <KPICard label="Active Users"    value={kpi?.total_users?.toLocaleString()}  change="+5.6%"  color="red"    icon="👥" />
            <KPICard label="Avg Order Value" value={fmt(kpi?.avg_order_value)}  change="+3.2%" color="yellow" icon="📈" />
          </>
        )}
      </div>

      {/* Revenue + Category Pie */}
      <div className="chart-row">
        <div className="card">
          <div className="card-header">
            <div>
              <div className="card-title">Revenue Over Time</div>
              <div className="card-subtitle">Daily sales trend</div>
            </div>
            <div className="filter-bar" style={{ marginBottom: 0 }}>
              {[7,14,30,90].map(d => (
                <button
                  key={d}
                  className={`filter-btn${days === d ? ' active' : ''}`}
                  onClick={() => setDays(d)}
                >
                  {d}d
                </button>
              ))}
            </div>
          </div>
          {dailyLoad ? (
            <div className="skeleton" style={{ height: 260 }} />
          ) : (
            <ResponsiveContainer width="100%" height={260}>
              <AreaChart data={daily ?? []} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
                <defs>
                  <linearGradient id="revGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%"  stopColor="#00e5b0" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#00e5b0" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1f2430" />
                <XAxis
                  dataKey="date" tick={{ fill: '#8892a4', fontSize: 11 }}
                  tickLine={false} axisLine={false}
                  tickFormatter={d => d?.slice(5)}
                  interval={Math.floor(((daily?.length ?? 1) - 1) / 6)}
                />
                <YAxis
                  tick={{ fill: '#8892a4', fontSize: 11 }} tickLine={false} axisLine={false}
                  tickFormatter={v => `$${(v / 1000).toFixed(0)}k`}
                />
                <Tooltip
                  contentStyle={{ background: '#181c23', border: '1px solid #1f2430', borderRadius: 8, fontSize: 12 }}
                  labelStyle={{ color: '#e8ecf1' }}
                  formatter={v => [`$${Number(v).toFixed(2)}`, 'Revenue']}
                />
                <Area type="monotone" dataKey="revenue" stroke="#00e5b0" strokeWidth={2} fill="url(#revGrad)" />
              </AreaChart>
            </ResponsiveContainer>
          )}
        </div>

        <div className="card">
          <div className="card-header">
            <div>
              <div className="card-title">Revenue by Category</div>
              <div className="card-subtitle">Distribution breakdown</div>
            </div>
          </div>
          <ResponsiveContainer width="100%" height={260}>
            <PieChart>
              <Pie
                data={catRev ?? []} dataKey="revenue" nameKey="category"
                cx="50%" cy="45%" outerRadius={80} innerRadius={46} paddingAngle={3}
              >
                {(catRev ?? []).map((_, i) => (
                  <Cell key={i} fill={COLORS[i % COLORS.length]} />
                ))}
              </Pie>
              <Legend
                iconType="circle" iconSize={8}
                formatter={v => <span style={{ color: '#8892a4', fontSize: 11 }}>{v}</span>}
              />
              <Tooltip
                contentStyle={{ background: '#181c23', border: '1px solid #1f2430', borderRadius: 8, fontSize: 12 }}
                formatter={v => [`$${Number(v).toFixed(2)}`, 'Revenue']}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Top Products */}
      <div className="card">
        <div className="card-header">
          <div>
            <div className="card-title">Top 5 Products by Revenue</div>
            <div className="card-subtitle">Best performing products this period</div>
          </div>
        </div>
        <ResponsiveContainer width="100%" height={220}>
          <BarChart data={topProds ?? []} layout="vertical" margin={{ left: 10, right: 20 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1f2430" horizontal={false} />
            <XAxis
              type="number" tick={{ fill: '#8892a4', fontSize: 11 }} tickLine={false} axisLine={false}
              tickFormatter={v => `$${(v / 1000).toFixed(0)}k`}
            />
            <YAxis
              type="category" dataKey="product_name"
              tick={{ fill: '#e8ecf1', fontSize: 11 }} tickLine={false} axisLine={false} width={170}
            />
            <Tooltip
              contentStyle={{ background: '#181c23', border: '1px solid #1f2430', borderRadius: 8, fontSize: 12 }}
              formatter={v => [`$${Number(v).toFixed(2)}`, 'Revenue']}
            />
            <Bar dataKey="total_revenue" radius={[0, 6, 6, 0]}>
              {(topProds ?? []).map((_, i) => (
                <Cell key={i} fill={COLORS[i % COLORS.length]} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
EOF

# ────────────────────────────────────────────────────────────
# src/pages/Analytics.js
# ────────────────────────────────────────────────────────────
cat > "$FRONTEND/src/pages/Analytics.js" << 'EOF'
import React, { useState } from 'react';
import {
  ComposedChart, Bar, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Legend, BarChart, Cell,
  RadarChart, PolarGrid, PolarAngleAxis, Radar,
} from 'recharts';
import useApi from '../hooks/useApi';
import { getWeeklySales, getDailySales, getTopProducts, getCategoryRevenue, getCustomerSegments } from '../services/api';

const COLORS = ['#00e5b0','#6c63ff','#ff6b6b','#ffd166','#06d6a0','#118ab2'];

export default function Analytics() {
  const [trendView, setTrendView] = useState('weekly');

  const { data: weekly }   = useApi(() => getWeeklySales(16), []);
  const { data: daily }    = useApi(() => getDailySales(60),  []);
  const { data: topProds } = useApi(() => getTopProducts(8),  []);
  const { data: catRev }   = useApi(() => getCategoryRevenue(), []);
  const { data: segments } = useApi(() => getCustomerSegments(), []);

  const salesData = trendView === 'weekly' ? (weekly ?? []) : (daily ?? []);

  const radarData = (catRev ?? []).map(c => ({
    subject: c.category.replace(' & ', '/'),
    revenue: Math.round(c.revenue),
    orders:  c.orders * 15,
  }));

  const SEGMENT_COLOR = ['#00e5b0','#6c63ff','#ff6b6b'];

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Analytics</h1>
        <p className="page-subtitle">Deep-dive into sales performance, trends and customer insights</p>
      </div>

      {/* Trend chart */}
      <div className="card" style={{ marginBottom: 16 }}>
        <div className="card-header">
          <div>
            <div className="card-title">Sales Trend — Revenue &amp; Orders</div>
            <div className="card-subtitle">Composite view of revenue and order volume</div>
          </div>
          <div className="filter-bar" style={{ marginBottom: 0 }}>
            <button
              className={`filter-btn${trendView === 'weekly' ? ' active' : ''}`}
              onClick={() => setTrendView('weekly')}
            >Weekly</button>
            <button
              className={`filter-btn${trendView === 'daily' ? ' active' : ''}`}
              onClick={() => setTrendView('daily')}
            >Daily</button>
          </div>
        </div>
        <ResponsiveContainer width="100%" height={300}>
          <ComposedChart data={salesData} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
            <defs>
              <linearGradient id="barGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%"   stopColor="#6c63ff" stopOpacity={0.9} />
                <stop offset="100%" stopColor="#6c63ff" stopOpacity={0.3} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#1f2430" />
            <XAxis
              dataKey="date" tick={{ fill: '#8892a4', fontSize: 10 }} tickLine={false} axisLine={false}
              tickFormatter={d => d?.slice(5)}
              interval={Math.floor((salesData.length - 1) / 8 || 0)}
            />
            <YAxis
              yAxisId="left" tick={{ fill: '#8892a4', fontSize: 11 }} tickLine={false} axisLine={false}
              tickFormatter={v => `$${(v / 1000).toFixed(0)}k`}
            />
            <YAxis
              yAxisId="right" orientation="right"
              tick={{ fill: '#8892a4', fontSize: 11 }} tickLine={false} axisLine={false}
            />
            <Tooltip
              contentStyle={{ background: '#181c23', border: '1px solid #1f2430', borderRadius: 8, fontSize: 12 }}
              formatter={(v, n) => n === 'revenue' ? [`$${Number(v).toFixed(2)}`, 'Revenue'] : [v, 'Orders']}
            />
            <Legend formatter={v => <span style={{ color: '#8892a4', fontSize: 11, textTransform: 'capitalize' }}>{v}</span>} />
            <Bar yAxisId="left"  dataKey="revenue" fill="url(#barGrad)" radius={[4,4,0,0]} name="revenue" />
            <Line yAxisId="right" type="monotone" dataKey="orders" stroke="#00e5b0" strokeWidth={2} dot={false} name="orders" />
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      <div className="chart-row-2">
        {/* Units sold bar */}
        <div className="card">
          <div className="card-header">
            <div>
              <div className="card-title">Top Products — Units Sold</div>
              <div className="card-subtitle">By total quantity ordered</div>
            </div>
          </div>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={topProds ?? []} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke="#1f2430" horizontal={false} />
              <XAxis type="number" tick={{ fill: '#8892a4', fontSize: 10 }} tickLine={false} axisLine={false} />
              <YAxis
                type="category" dataKey="product_name"
                tick={{ fill: '#e8ecf1', fontSize: 10 }} tickLine={false} axisLine={false} width={150}
              />
              <Tooltip
                contentStyle={{ background: '#181c23', border: '1px solid #1f2430', borderRadius: 8, fontSize: 12 }}
                formatter={v => [v, 'Units Sold']}
              />
              <Bar dataKey="total_quantity" radius={[0, 6, 6, 0]}>
                {(topProds ?? []).map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Radar */}
        <div className="card">
          <div className="card-header">
            <div>
              <div className="card-title">Category Radar</div>
              <div className="card-subtitle">Revenue vs order volume by category</div>
            </div>
          </div>
          <ResponsiveContainer width="100%" height={280}>
            <RadarChart data={radarData}>
              <PolarGrid stroke="#1f2430" />
              <PolarAngleAxis dataKey="subject" tick={{ fill: '#8892a4', fontSize: 10 }} />
              <Radar name="Revenue" dataKey="revenue" stroke="#00e5b0" fill="#00e5b0" fillOpacity={0.2} strokeWidth={2} />
              <Radar name="Order Vol" dataKey="orders"  stroke="#6c63ff" fill="#6c63ff" fillOpacity={0.15} strokeWidth={2} />
              <Legend formatter={v => <span style={{ color: '#8892a4', fontSize: 11 }}>{v}</span>} />
              <Tooltip contentStyle={{ background: '#181c23', border: '1px solid #1f2430', borderRadius: 8, fontSize: 12 }} />
            </RadarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Segment cards */}
      <div className="card">
        <div className="card-title">Customer Segment Analysis</div>
        <div className="card-subtitle" style={{ marginBottom: 0 }}>Revenue &amp; count breakdown by customer tier</div>
        <div className="seg-grid">
          {(segments ?? []).map((seg, i) => (
            <div key={seg.segment} className="seg-card" style={{ borderTop: `3px solid ${SEGMENT_COLOR[i % 3]}` }}>
              <div style={{ fontSize: 10, color: 'var(--text2)', textTransform: 'uppercase', fontWeight: 600, letterSpacing: '.08em' }}>
                {seg.segment}
              </div>
              <div style={{ fontSize: 26, fontWeight: 700, color: 'var(--text)', margin: '7px 0 3px' }}>
                {seg.count.toLocaleString()}
              </div>
              <div style={{ fontSize: 12, color: SEGMENT_COLOR[i % 3], fontWeight: 600 }}>
                ${seg.revenue.toLocaleString(undefined, { maximumFractionDigits: 0 })} revenue
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
EOF

# ────────────────────────────────────────────────────────────
# src/pages/Orders.js
# ────────────────────────────────────────────────────────────
cat > "$FRONTEND/src/pages/Orders.js" << 'EOF'
import React, { useState } from 'react';
import useApi from '../hooks/useApi';
import { getOrders } from '../services/api';

const STATUS_CLASS = {
  completed: 'badge-green',
  pending:   'badge-yellow',
  refunded:  'badge-red',
};

export default function Orders() {
  const [status, setStatus] = useState('');

  const { data: orders, loading, error } = useApi(
    () => getOrders(status ? `&status=${status}` : ''),
    [status]
  );

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Orders</h1>
        <p className="page-subtitle">All customer orders across your platform</p>
      </div>

      <div className="filter-bar">
        {[
          { key: '',           label: 'All Orders' },
          { key: 'completed',  label: 'Completed'  },
          { key: 'pending',    label: 'Pending'    },
          { key: 'refunded',   label: 'Refunded'   },
        ].map(({ key, label }) => (
          <button
            key={key}
            className={`filter-btn${status === key ? ' active' : ''}`}
            onClick={() => setStatus(key)}
          >
            {label}
          </button>
        ))}
      </div>

      <div className="card">
        <div className="card-header">
          <div>
            <div className="card-title">Order History</div>
            <div className="card-subtitle">{orders?.length ?? 0} records shown</div>
          </div>
        </div>

        {loading && <div className="spinner-wrap"><div className="spinner" /></div>}
        {error   && <div className="error-box">Error: {error}</div>}

        {!loading && !error && (
          <div style={{ overflowX: 'auto' }}>
            <table className="data-table">
              <thead>
                <tr>
                  <th>#ID</th>
                  <th>Customer</th>
                  <th>Product</th>
                  <th>Qty</th>
                  <th>Total</th>
                  <th>Status</th>
                  <th>Date</th>
                </tr>
              </thead>
              <tbody>
                {(orders ?? []).map(o => (
                  <tr key={o.id}>
                    <td style={{ color: 'var(--text2)', fontFamily: 'monospace' }}>
                      #{String(o.id).padStart(5, '0')}
                    </td>
                    <td style={{ fontWeight: 500 }}>{o.user_name ?? `User #${o.user_id}`}</td>
                    <td style={{ color: 'var(--text2)' }}>{o.product_name ?? `Product #${o.product_id}`}</td>
                    <td style={{ color: 'var(--text2)' }}>{o.quantity}</td>
                    <td style={{ fontWeight: 600, color: 'var(--accent)' }}>
                      ${Number(o.total_price).toFixed(2)}
                    </td>
                    <td>
                      <span className={`badge ${STATUS_CLASS[o.status] ?? 'badge-gray'}`}>
                        {o.status}
                      </span>
                    </td>
                    <td style={{ color: 'var(--text2)' }}>
                      {new Date(o.created_at).toLocaleDateString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
EOF

# ────────────────────────────────────────────────────────────
# src/pages/Products.js
# ────────────────────────────────────────────────────────────
cat > "$FRONTEND/src/pages/Products.js" << 'EOF'
import React, { useState } from 'react';
import useApi from '../hooks/useApi';
import { getProducts, getCategories } from '../services/api';

const CATEGORY_BADGE = {
  'Electronics':    'badge-purple',
  'Clothing':       'badge-green',
  'Books':          'badge-yellow',
  'Home & Garden':  'badge-green',
  'Sports':         'badge-red',
  'Beauty':         'badge-red',
  'Toys':           'badge-yellow',
  'Food':           'badge-green',
};

export default function Products() {
  const [category, setCategory] = useState('');

  const { data: catData }                    = useApi(() => getCategories(), []);
  const { data: products, loading, error }   = useApi(
    () => getProducts(category ? `&category=${encodeURIComponent(category)}` : ''),
    [category]
  );

  const categories = catData?.categories ?? [];

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Products</h1>
        <p className="page-subtitle">Browse and filter your product catalogue</p>
      </div>

      <div className="filter-bar">
        <button
          className={`filter-btn${category === '' ? ' active' : ''}`}
          onClick={() => setCategory('')}
        >
          All
        </button>
        {categories.map(c => (
          <button
            key={c}
            className={`filter-btn${category === c ? ' active' : ''}`}
            onClick={() => setCategory(c)}
          >
            {c}
          </button>
        ))}
      </div>

      <div className="card">
        <div className="card-header">
          <div>
            <div className="card-title">Product Catalogue</div>
            <div className="card-subtitle">{products?.length ?? 0} products found</div>
          </div>
        </div>

        {loading && <div className="spinner-wrap"><div className="spinner" /></div>}
        {error   && <div className="error-box">Error: {error}</div>}

        {!loading && !error && (
          <div style={{ overflowX: 'auto' }}>
            <table className="data-table">
              <thead>
                <tr>
                  <th>#ID</th>
                  <th>Product Name</th>
                  <th>Category</th>
                  <th>Price</th>
                  <th>Stock</th>
                </tr>
              </thead>
              <tbody>
                {(products ?? []).map(p => (
                  <tr key={p.id}>
                    <td style={{ color: 'var(--text2)', fontFamily: 'monospace' }}>
                      #{String(p.id).padStart(4, '0')}
                    </td>
                    <td style={{ fontWeight: 500 }}>{p.name}</td>
                    <td>
                      <span className={`badge ${CATEGORY_BADGE[p.category] ?? 'badge-gray'}`}>
                        {p.category}
                      </span>
                    </td>
                    <td style={{ fontWeight: 600, color: 'var(--accent)' }}>
                      ${Number(p.price).toFixed(2)}
                    </td>
                    <td style={{ color: p.stock < 20 ? 'var(--accent3)' : 'var(--text2)' }}>
                      {p.stock} units{p.stock < 20 ? ' ⚠' : ''}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
EOF

# ────────────────────────────────────────────────────────────
# src/pages/TableauExport.js
# ────────────────────────────────────────────────────────────
cat > "$FRONTEND/src/pages/TableauExport.js" << 'EOF'
import React, { useState } from 'react';
import { exportTableau } from '../services/api';

function jsonToCSV(rows) {
  if (!rows?.length) return '';
  const headers = Object.keys(rows[0]);
  const escape  = v => {
    if (v === null || v === undefined) return '';
    const s = String(v);
    return s.includes(',') || s.includes('"') || s.includes('\n')
      ? `"${s.replace(/"/g, '""')}"`
      : s;
  };
  return [
    headers.join(','),
    ...rows.map(r => headers.map(h => escape(r[h])).join(',')),
  ].join('\n');
}

const STEPS = [
  {
    title: 'Export the Dataset',
    body: <>Click <strong>Export CSV for Tableau</strong> below. The file is fully denormalized — one row per order — with customer, product, date, and revenue columns.</>,
  },
  {
    title: 'Open Tableau Desktop or Tableau Public',
    body: <>Go to <code>Connect → Text File</code> and open <code>ecom_tableau_export.csv</code>. Tableau auto-detects all column types.</>,
  },
  {
    title: 'Build Sales Trend Chart',
    body: <>Drag <code>order_date</code> to Columns, <code>SUM(total_price)</code> to Rows. Right-click the date → select <em>Month</em>. Change mark to Line or Area.</>,
  },
  {
    title: 'Build Top Products Bar',
    body: <>New sheet. Drag <code>product_name</code> to Rows, <code>SUM(total_price)</code> to Columns. Sort descending, color by <code>category</code>.</>,
  },
  {
    title: 'Build Revenue by Category',
    body: <>New sheet. Drag <code>category</code> to Color and Label, <code>SUM(total_price)</code> to Size. Change mark type to <em>Pie</em> or <em>Treemap</em>.</>,
  },
  {
    title: 'Build Customer Geography Map',
    body: <>New sheet. Drag <code>country</code> to the canvas — Tableau geocodes automatically. Add <code>SUM(total_price)</code> to Color and Size for a revenue heatmap.</>,
  },
  {
    title: 'Assemble the Dashboard',
    body: <>Click <em>New Dashboard</em>. Drag all sheets onto the canvas. Add filter actions so selecting a category cross-filters all views. Add a <code>segment</code> global filter.</>,
  },
];

export default function TableauExport() {
  const [loading,  setLoading]  = useState(false);
  const [exported, setExported] = useState(false);
  const [error,    setError]    = useState(null);

  async function handleExport() {
    setLoading(true);
    setError(null);
    try {
      const data = await exportTableau();
      const csv  = jsonToCSV(data);
      const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
      const url  = URL.createObjectURL(blob);
      const a    = document.createElement('a');
      a.href     = url;
      a.download = 'ecom_tableau_export.csv';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      setExported(true);
    } catch (err) {
      setError(err?.response?.data?.detail ?? err?.message ?? 'Export failed');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ maxWidth: 860 }}>
      <div className="page-header">
        <h1 className="page-title">Tableau Integration</h1>
        <p className="page-subtitle">Export your dataset and build professional dashboards in Tableau</p>
      </div>

      {/* Export card */}
      <div className="card" style={{ marginBottom: 18 }}>
        <div className="card-title" style={{ marginBottom: 8 }}>Download Tableau Dataset</div>
        <p style={{ color: 'var(--text2)', fontSize: 13, lineHeight: 1.7, marginBottom: 16 }}>
          Exports a fully denormalized CSV (1,300+ rows) with order date, customer segment,
          product category, country, revenue, quantity, and status.
        </p>
        <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
          <button className="export-btn" onClick={handleExport} disabled={loading}>
            {loading ? '⏳ Exporting...' : '⬇ Export CSV for Tableau'}
          </button>
          {exported && !error && (
            <span style={{ color: 'var(--accent)', fontSize: 13 }}>✓ File downloaded</span>
          )}
        </div>
        {error && <div className="error-box" style={{ marginTop: 12 }}>Export error: {error}</div>}
      </div>

      {/* Step-by-step guide */}
      <div className="card" style={{ marginBottom: 18 }}>
        <div className="card-title" style={{ marginBottom: 4 }}>Tableau Dashboard Build Guide</div>
        <p style={{ color: 'var(--text2)', fontSize: 13, marginBottom: 16 }}>
          Follow these steps to build the full 4-chart analytics dashboard in Tableau.
        </p>
        {STEPS.map((s, i) => (
          <div key={i} className="tableau-step">
            <div className="step-num">{i + 1}</div>
            <div className="step-body">
              <h4>{s.title}</h4>
              <p>{s.body}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Recommended views */}
      <div className="card">
        <div className="card-title" style={{ marginBottom: 14 }}>Recommended Tableau Views</div>
        <div className="chart-row-2">
          {[
            { icon: '📈', title: 'Sales Trend',        desc: 'Line/Area — order_date × SUM(total_price), grouped by month' },
            { icon: '🏆', title: 'Top Products',        desc: 'Bar — product_name × SUM(total_price), sorted desc, colored by category' },
            { icon: '🥧', title: 'Category Revenue',    desc: 'Pie/Treemap — category dimension, SUM(total_price) measure, % labels' },
            { icon: '🌍', title: 'Customer Geography',  desc: 'Filled Map — country auto-geocoded, SUM(total_price) on color + size' },
          ].map(c => (
            <div
              key={c.title}
              style={{
                background: 'var(--bg3)', border: '1px solid var(--border)',
                borderRadius: 10, padding: '14px 16px',
                display: 'flex', gap: 12,
              }}
            >
              <span style={{ fontSize: 24 }}>{c.icon}</span>
              <div>
                <div style={{ fontWeight: 700, fontSize: 13, color: 'var(--text)', marginBottom: 5 }}>
                  {c.title}
                </div>
                <div style={{ fontSize: 12, color: 'var(--text2)', lineHeight: 1.55 }}>{c.desc}</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
EOF

echo ""
echo "✅ Frontend scaffold complete."
echo ""
echo "Next steps:"
echo "  cd frontend && npm install && npm run build   # local build"
echo "  docker compose up --build                     # full stack"
echo ""
echo "URLs:"
echo "  Frontend  → http://localhost:3000"
echo "  API       → http://localhost:8000"
echo "  API Docs  → http://localhost:8000/docs"
EOF

chmod +x /home/claude/ecommerce-devops-platform/setup_frontend.sh
echo "Script created"
