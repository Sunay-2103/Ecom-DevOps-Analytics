import React, { useState } from 'react';
import {
  ComposedChart, Bar, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Legend, BarChart, Cell,
  RadarChart, PolarGrid, PolarAngleAxis, Radar, PolarRadiusAxis,
} from 'recharts';
import useApi from '../hooks/useApi';
import { getWeeklySales, getDailySales, getTopProducts, getCategoryRevenue, getCustomerSegments } from '../services/api';

const COLORS = [
  '#10b981', // Emerald
  '#6366f1', // Indigo
  '#ef4444', // Red
  '#f59e0b', // Amber
  '#8b5cf6', // Violet
  '#06b6d4', // Cyan
  '#ec4899', // Pink
  '#14b8a6', // Teal
];

const fmtINR = n => {
  if (n == null) return '₹0';
  if (n >= 100000) return `₹${(n / 100000).toFixed(1)}L`;
  if (n >= 1000)   return `₹${(n / 1000).toFixed(1)}K`;
  return `₹${Math.round(n).toLocaleString('en-IN')}`;
};
const fmtINRFull = n => `₹${Number(n ?? 0).toLocaleString('en-IN', { maximumFractionDigits: 0 })}`;

export default function Analytics() {
  const [trendView, setTrendView] = useState('weekly');

  const { data: weekly }   = useApi(() => getWeeklySales(16), []);
  const { data: daily }    = useApi(() => getDailySales(60),  []);
  const { data: topProds } = useApi(() => getTopProducts(8),  []);
  const { data: catRev }   = useApi(() => getCategoryRevenue(), []);
  const { data: segments } = useApi(() => getCustomerSegments(), []);

  const salesData = trendView === 'weekly' ? (weekly ?? []) : (daily ?? []);

  const radarData = (catRev ?? [])
    .filter(c => c.category !== 'Imported')
    .map(c => ({
    subject: c.category.replace(' & ', '/'),
    revenue: Math.round(c.revenue / 1000),
    orders:  Math.round(c.orders  / 10),
    target:  Math.round((c.target || 0) / 1000),
  }));

  const SEGMENT_COLOR = ['#10b981','#6366f1','#ef4444'];

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
            <div className="card-subtitle">Composite view of revenue and order volume over time</div>
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
        <ResponsiveContainer width="100%" height={320}>
          <ComposedChart data={salesData} margin={{ top: 10, right: 20, left: -10, bottom: 5 }}>
            <defs>
              <linearGradient id="barGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%"   stopColor="#6366f1" stopOpacity={0.8} />
                <stop offset="100%" stopColor="#6366f1" stopOpacity={0.2} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" vertical={false} />
            <XAxis
              dataKey="date" 
              tick={{ fill: '#64748b', fontSize: 12 }} 
              tickLine={false} 
              axisLine={false}
              tickFormatter={d => d?.slice(5)}
              interval={Math.floor((salesData.length - 1) / 8 || 0)}
            />
            <YAxis
              yAxisId="left" 
              tick={{ fill: '#64748b', fontSize: 12 }} 
              tickLine={false} 
              axisLine={false}
              tickFormatter={v => `₹${(v / 1000).toFixed(0)}K`}
            />
            <YAxis
              yAxisId="right" 
              orientation="right"
              tick={{ fill: '#64748b', fontSize: 12 }} 
              tickLine={false} 
              axisLine={false}
            />
            <Tooltip
              contentStyle={{ 
                background: '#ffffff', 
                border: '2px solid #e2e8f0', 
                borderRadius: 12, 
                fontSize: 13,
                boxShadow: '0 4px 24px rgba(0,0,0,0.1)',
              }}
              formatter={(v, n) => n === 'revenue' ? [fmtINRFull(v), 'Revenue'] : [v, 'Orders']}
            />
            <Legend 
              formatter={v => <span style={{ color: '#64748b', fontSize: 12, fontWeight: 500, textTransform: 'capitalize' }}>{v}</span>} 
            />
            <Bar 
              yAxisId="left"  
              dataKey="revenue" 
              fill="url(#barGrad)" 
              radius={[8,8,0,0]} 
              name="revenue"
              animationDuration={800}
            />
            <Line 
              yAxisId="right" 
              type="monotone" 
              dataKey="orders" 
              stroke="#10b981" 
              strokeWidth={3}
              dot={false} 
              name="orders"
              animationDuration={800}
            />
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
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={topProds ?? []} layout="vertical" margin={{ left: 10, right: 20, top: 5, bottom: 5 }}>
              <defs>
                {COLORS.map((color, i) => (
                  <linearGradient key={i} id={`grad-units-${i}`} x1="0" y1="0" x2="1" y2="0">
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
              />
              <YAxis
                type="category" 
                dataKey="product_name"
                tick={{ fill: '#0f172a', fontSize: 12, fontWeight: 500 }} 
                tickLine={false} 
                axisLine={false} 
                width={160}
              />
              <Tooltip
                contentStyle={{ 
                  background: '#ffffff', 
                  border: '2px solid #e2e8f0', 
                  borderRadius: 12, 
                  fontSize: 13,
                  boxShadow: '0 4px 24px rgba(0,0,0,0.1)',
                }}
                formatter={v => [v, 'Units Sold']}
              />
              <Bar 
                dataKey="total_quantity" 
                radius={[0, 8, 8, 0]}
                animationDuration={800}
              >
                {(topProds ?? []).map((_, i) => <Cell key={i} fill={`url(#grad-units-${i % COLORS.length})`} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Radar */}
        <div className="card">
          <div className="card-header">
            <div>
              <div className="card-title">Category Performance Radar</div>
              <div className="card-subtitle">Revenue vs order volume by category</div>
            </div>
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <RadarChart data={radarData}>
              <defs>
                <linearGradient id="radarGrad1" x1="0%" y1="0%" x2="0%" y2="100%">
                  <stop offset="0%" stopColor="#10b981" stopOpacity={0.3} />
                  <stop offset="100%" stopColor="#10b981" stopOpacity={0.05} />
                </linearGradient>
                <linearGradient id="radarGrad2" x1="0%" y1="0%" x2="0%" y2="100%">
                  <stop offset="0%" stopColor="#6366f1" stopOpacity={0.3} />
                  <stop offset="100%" stopColor="#6366f1" stopOpacity={0.05} />
                </linearGradient>
              </defs>
              <PolarGrid stroke="#e2e8f0" />
              <PolarAngleAxis dataKey="subject" tick={{ fill: '#64748b', fontSize: 11, fontWeight: 500 }} />
              <PolarRadiusAxis tick={{ fill: '#64748b', fontSize: 10 }} />
              <Radar 
                name="Revenue (₹K)" 
                dataKey="revenue" 
                stroke="#10b981" 
                fill="url(#radarGrad1)"
                fillOpacity={0.6}
                strokeWidth={2}
                animationDuration={800}
              />
              <Radar 
                name="Orders (×10)" 
                dataKey="orders"  
                stroke="#6366f1" 
                fill="url(#radarGrad2)"
                fillOpacity={0.5}
                strokeWidth={2}
                animationDuration={800}
              />
              <Radar
                name="Target (₹K)"
                dataKey="target"
                stroke="#f59e0b"
                fill="none"
                strokeWidth={2}
                strokeDasharray="5 3"
                animationDuration={800}
              />
              <Legend 
                formatter={v => <span style={{ color: '#64748b', fontSize: 12, fontWeight: 500 }}>{v}</span>}
                wrapperStyle={{ paddingTop: 20 }}
              />
              <Tooltip 
                contentStyle={{ 
                  background: '#ffffff', 
                  border: '2px solid #e2e8f0', 
                  borderRadius: 12, 
                  fontSize: 13,
                  boxShadow: '0 4px 24px rgba(0,0,0,0.1)',
                }} 
              />
            </RadarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Segment cards */}
      <div className="card">
        <div className="card-title">Customer Segment Analysis</div>
        <div className="card-subtitle" style={{ marginBottom: 20 }}>Revenue &amp; customer count breakdown by tier</div>
        <div className="seg-grid">
          {(segments ?? []).map((seg, i) => (
            <div 
              key={seg.segment} 
              className="seg-card" 
              style={{ 
                borderTop: `4px solid ${SEGMENT_COLOR[i % 3]}`,
                boxShadow: '0 2px 8px rgba(0,0,0,0.05)',
              }}
            >
              <div style={{ fontSize: 11, color: '#64748b', textTransform: 'uppercase', fontWeight: 700, letterSpacing: '.1em' }}>
                {seg.segment}
              </div>
              <div style={{ fontSize: 28, fontWeight: 700, color: '#0f172a', margin: '10px 0 5px' }}>
                {seg.count.toLocaleString()}
              </div>
              <div style={{ fontSize: 13, color: SEGMENT_COLOR[i % 3], fontWeight: 600 }}>
                ₹{seg.revenue.toLocaleString('en-IN', { maximumFractionDigits: 0 })} revenue
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
