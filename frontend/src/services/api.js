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

# Updated on 2026-02-01 by Sunay

# Updated on 2026-03-11 by Anwar
change 31
change 17
change 17
