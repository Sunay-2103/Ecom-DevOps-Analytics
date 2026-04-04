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
