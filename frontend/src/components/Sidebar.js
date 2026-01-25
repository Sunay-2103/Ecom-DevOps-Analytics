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
change 21
change 1
change 14
change 22
