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
