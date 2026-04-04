import React, { useState } from 'react';
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, PieChart, Pie, Cell, Legend,
  BarChart, Bar, LineChart, Line, ComposedChart,
} from 'recharts';
import useApi from '../hooks/useApi';
import { getKPI, getDailySales, getCategoryRevenue, getTopProducts } from '../services/api';

const COLORS = [
  '#10b981', // Emerald
  '#6366f1', // Indigo
  '#ef4444', // Red
  '#f59e0b', // Amber
  '#8b5cf6', // Violet
  '#06b6d4', // Cyan
  '#ec4899', // Pink
  '#14b8a6', // Teal
  '#f97316', // Orange
  '#3b82f6', // Blue
];
const fmtINR = n => {
  if (n == null) return '₹0';
  if (n >= 10000000) return `₹${(n / 10000000).toFixed(1)}Cr`;
  if (n >= 100000)  return `₹${(n / 100000).toFixed(1)}L`;
  if (n >= 1000)    return `₹${(n / 1000).toFixed(1)}K`;
  return `₹${Math.round(n).toLocaleString('en-IN')}`;
};
const fmt = fmtINR;
const fmtINRFull = n => `₹${Number(n ?? 0).toLocaleString('en-IN', { maximumFractionDigits: 0 })}`;
const fmtChange = pct => pct == null ? null : (pct >= 0 ? `+${pct.toFixed(1)}%` : `${pct.toFixed(1)}%`);

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

  // Filter out "Imported" category from pie chart
  const catRevFiltered = (catRev ?? []).filter(c => c.category !== 'Imported');

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
            <KPICard label="Total Revenue"   value={fmt(kpi?.total_revenue)}   change={fmtChange(kpi?.revenue_change)} color="green"  icon="💰" />
            <KPICard label="Total Orders"    value={kpi?.total_orders?.toLocaleString()} change={fmtChange(kpi?.orders_change)}  color="purple" icon="🛒" />
            <KPICard label="Active Users"    value={kpi?.total_users?.toLocaleString()}  change={fmtChange(kpi?.users_change)}   color="red"    icon="👥" />
            <KPICard label="Avg Order Value" value={fmt(kpi?.avg_order_value)}  change={fmtChange(kpi?.aov_change)} color="yellow" icon="📈" />
          </>
        )}
      </div>

      {/* Revenue + Category Pie */}
      <div className="chart-row">
        <div className="card">
          <div className="card-header">
            <div>
              <div className="card-title">Revenue Over Time</div>
              <div className="card-subtitle">Daily sales trend with smooth animation</div>
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
            <div className="skeleton" style={{ height: 280 }} />
          ) : (
            <ResponsiveContainer width="100%" height={280}>
              <AreaChart data={daily ?? []} margin={{ top: 10, right: 20, left: -10, bottom: 5 }}>
                <defs>
                  <linearGradient id="revGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%"  stopColor="#10b981" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                  </linearGradient>
                  <filter id="shadow" x="-50%" y="-50%" width="200%" height="200%">
                    <feDropShadow dx="0" dy="2" stdDeviation="3" floodOpacity="0.1" />
                  </filter>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" vertical={false} />
                <XAxis
                  dataKey="date" tick={{ fill: '#64748b', fontSize: 12 }}
                  tickLine={false} axisLine={false}
                  tickFormatter={d => {
                    const date = new Date(d);
                    return `${date.getMonth() + 1}/${date.getDate()}`;
                  }}
                  interval={Math.floor(((daily?.length ?? 1) - 1) / 6)}
                  style={{ fontSize: 12 }}
                />
                <YAxis
                  tick={{ fill: '#64748b', fontSize: 12 }} tickLine={false} axisLine={false}
                  tickFormatter={v => `₹${(v / 1000).toFixed(0)}K`}
                  style={{ fontSize: 12 }}
                />
                <Tooltip
                  contentStyle={{ 
                    background: '#ffffff', 
                    border: '2px solid #e2e8f0', 
                    borderRadius: 12, 
                    fontSize: 13,
                    boxShadow: '0 4px 24px rgba(0,0,0,0.1)',
                  }}
                  labelStyle={{ color: '#0f172a', fontWeight: 600 }}
                  labelFormatter={d => {
                    const date = new Date(d);
                    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
                  }}
                  formatter={v => [fmtINRFull(v), 'Daily Revenue']}  
                />
                <Area 
                  type="monotone" 
                  dataKey="revenue" 
                  stroke="#10b981" 
                  strokeWidth={3}
                  fill="url(#revGrad)"
                  isAnimationActive={true}
                  animationDuration={800}
                />
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
          <ResponsiveContainer width="100%" height={280}>
            <PieChart>
              <Pie
                data={catRevFiltered} 
                dataKey="revenue" 
                nameKey="category"
                cx="50%" 
                cy="45%" 
                outerRadius={90} 
                innerRadius={50} 
                paddingAngle={4}
                animationDuration={800}
              >
                {(catRevFiltered ?? []).map((_, i) => (
                  <Cell key={i} fill={COLORS[i % COLORS.length]} />
                ))}
              </Pie>
              <Legend
                iconType="circle" 
                iconSize={10}
                verticalAlign="bottom"
                height={36}
                formatter={v => <span style={{ color: '#64748b', fontSize: 12, fontWeight: 500 }}>{v}</span>}
              />
              <Tooltip
                contentStyle={{ 
                  background: '#ffffff', 
                  border: '2px solid #e2e8f0', 
                  borderRadius: 12, 
                  fontSize: 13,
                  boxShadow: '0 4px 24px rgba(0,0,0,0.1)',
                }}
                formatter={v => [fmtINRFull(v), 'Revenue']}
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
        <ResponsiveContainer width="100%" height={260}>
          <BarChart data={topProds ?? []} layout="vertical" margin={{ left: 10, right: 20, top: 5, bottom: 5 }}>
            <defs>
              {COLORS.map((color, i) => (
                <linearGradient key={i} id={`grad${i}`} x1="0" y1="0" x2="1" y2="0">
                  <stop offset="0%" stopColor={color} stopOpacity={0.7} />
                  <stop offset="100%" stopColor={color} stopOpacity={1} />
                </linearGradient>
              ))}
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" horizontal={false} />
            <XAxis
              type="number" 
              tick={{ fill: '#64748b', fontSize: 12 }} 
              tickLine={false} 
              axisLine={false}
              tickFormatter={v => `₹${(v / 1000).toFixed(0)}K`}
            />
            <YAxis
              type="category" 
              dataKey="product_name"
              tick={{ fill: '#0f172a', fontSize: 12, fontWeight: 500 }} 
              tickLine={false} 
              axisLine={false} 
              width={180}
            />
            <Tooltip
              contentStyle={{ 
                background: '#ffffff', 
                border: '2px solid #e2e8f0', 
                borderRadius: 12, 
                fontSize: 13,
                boxShadow: '0 4px 24px rgba(0,0,0,0.1)',
              }}
              formatter={v => [fmtINRFull(v), 'Revenue']}
            />
            <Bar 
              dataKey="total_revenue" 
              radius={[0, 8, 8, 0]}
              animationDuration={800}
            >
              {(topProds ?? []).map((_, i) => (
                <Cell key={i} fill={`url(#grad${i % COLORS.length})`} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
