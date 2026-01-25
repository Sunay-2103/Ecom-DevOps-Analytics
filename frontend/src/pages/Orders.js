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
change 13
change 22
