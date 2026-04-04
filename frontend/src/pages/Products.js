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
