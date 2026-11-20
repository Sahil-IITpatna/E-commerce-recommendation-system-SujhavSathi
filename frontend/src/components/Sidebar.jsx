import React from 'react';
import {
  LayoutDashboard,
  ShoppingBag,
  Sparkles,
  FolderTree,
  BarChart3,
  Flame,
  Layers
} from 'lucide-react';

export const Sidebar = ({ activePage, setActivePage }) => {
  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'catalogue', label: 'Products Catalogue', icon: ShoppingBag },
    { id: 'recommendations', label: 'Recommendations', icon: Sparkles },
    { id: 'categories', label: 'Categories', icon: FolderTree },
    { id: 'performance', label: 'Model Performance', icon: BarChart3 }
  ];

  return (
    <aside
      style={{
        width: '260px',
        backgroundColor: 'var(--bg-sidebar)',
        borderRight: '1px solid var(--border-color)',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'space-between',
        padding: '24px 16px',
        height: '100vh',
        position: 'sticky',
        top: 0
      }}
    >
      <div>
        {/* Brand Header */}
        <div style={{ padding: '0 8px', marginBottom: '28px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '6px' }}>
            <div
              style={{
                width: '36px',
                height: '36px',
                borderRadius: '8px',
                backgroundColor: 'var(--accent-vibrant)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: '#fff',
                boxShadow: '0 2px 8px rgba(31, 101, 33, 0.4)'
              }}
            >
              <Sparkles size={20} strokeWidth={2.2} />
            </div>
            <div>
              <h1 style={{ fontSize: '18px', fontWeight: 800, color: 'var(--text-primary)', letterSpacing: '-0.3px' }}>
                Sujhav <span style={{ color: 'var(--accent-primary)' }}>साथी</span>
              </h1>
              <span style={{ fontSize: '10px', fontWeight: 600, color: 'var(--accent-secondary)' }}>
                E-COMMERCE ML
              </span>
            </div>
          </div>

          {/* Dual Taglines */}
          <div style={{ marginTop: '8px', padding: '8px', backgroundColor: 'var(--card-secondary)', borderRadius: '6px', border: '1px solid var(--border-color)' }}>
            <p style={{ fontSize: '11px', fontWeight: 600, color: 'var(--accent-primary)' }}>
              आपकी पसंद, हमारा सुझाव।
            </p>
            <p style={{ fontSize: '10px', color: 'var(--text-muted)', marginTop: '2px' }}>
              Your Preferences. Smarter Recommendations.
            </p>
          </div>
        </div>

        {/* Navigation Items */}
        <nav style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activePage === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActivePage(item.id)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '12px',
                  padding: '11px 14px',
                  borderRadius: '10px',
                  fontSize: '13px',
                  fontWeight: isActive ? 600 : 500,
                  backgroundColor: isActive ? 'var(--nav-active)' : 'transparent',
                  color: isActive ? 'var(--nav-active-text)' : 'var(--text-secondary)',
                  border: isActive ? '1px solid var(--border-color)' : '1px solid transparent',
                  cursor: 'pointer',
                  textAlign: 'left',
                  width: '100%',
                  transition: 'all 0.15s ease'
                }}
              >
                <Icon size={18} strokeWidth={isActive ? 2.2 : 1.8} />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>
      </div>

      {/* Dataset & Architecture Footnote */}
      <div
        style={{
          padding: '12px',
          backgroundColor: 'var(--card-secondary)',
          borderRadius: '8px',
          border: '1px solid var(--border-color)',
          fontSize: '11px'
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontWeight: 600, color: 'var(--accent-secondary)', marginBottom: '4px' }}>
          <Layers size={13} />
          <span>Flipkart PromptCloudHQ</span>
        </div>
        <p style={{ color: 'var(--text-muted)', fontSize: '10px', lineHeight: 1.3 }}>
          17,665 Cleaned Products • TF-IDF + Hybrid Engine
        </p>
      </div>
    </aside>
  );
};
