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
change 9
change 12
