import React, { useState, useEffect, useRef } from 'react';
import { Moon, Sun, Search, CheckCircle2, AlertCircle, ShoppingBag } from 'lucide-react';
import { useTheme } from '../context/ThemeContext';
import { api } from '../services/api';

export const Navbar = ({ activePage, onNavigateToProduct }) => {
  const { theme, toggleTheme } = useTheme();
  const [searchQuery, setSearchQuery] = useState('');
  const [suggestions, setSuggestions] = useState([]);
  const [isSearching, setIsSearching] = useState(false);
  const [backendHealth, setBackendHealth] = useState({ healthy: false, count: 0 });
  const searchRef = useRef(null);

  // Poll health once on mount
  useEffect(() => {
    api.getHealth()
      .then(res => setBackendHealth({ healthy: res.status === 'healthy', count: res.dataset_products }))
      .catch(() => setBackendHealth({ healthy: false, count: 0 }));
  }, []);

  // Quick search autocomplete
  useEffect(() => {
    if (searchQuery.trim().length < 2) {
      setSuggestions([]);
      return;
    }

    const timer = setTimeout(() => {
      setIsSearching(true);
      api.searchProducts(searchQuery, 6)
        .then(res => setSuggestions(res.results || []))
        .catch(() => setSuggestions([]))
        .finally(() => setIsSearching(false));
    }, 250);

    return () => clearTimeout(timer);
  }, [searchQuery]);

  // Click outside listener for search suggestions dropdown
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (searchRef.current && !searchRef.current.contains(e.target)) {
        setSuggestions([]);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const pageTitles = {
    dashboard: 'Catalogue Intelligence & Dashboard',
    catalogue: 'Flipkart Product Catalogue',
    recommendations: 'Intelligent Product Recommendations',
    categories: 'Category Explorer & Hierarchy',
    performance: 'Model Performance & Proxy Evaluation'
  };

  return (
    <header
      style={{
        height: '70px',
        backgroundColor: 'var(--bg-navbar)',
        borderBottom: '1px solid var(--border-color)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '0 28px',
        position: 'sticky',
        top: 0,
        zIndex: 50
      }}
    >
      {/* Page Title */}
      <div>
        <h2 style={{ fontSize: '18px', fontWeight: 700, color: 'var(--text-primary)' }}>
          {pageTitles[activePage] || 'Sujhav साथी'}
        </h2>
        <p style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
          Flipkart E-Commerce Recommendation Engine
        </p>
      </div>

      {/* Center Search Bar with Autocomplete Dropdown */}
      <div ref={searchRef} style={{ position: 'relative', width: '380px' }}>
        <div style={{ position: 'relative' }}>
          <Search
            size={16}
            style={{
              position: 'absolute',
              left: '12px',
              top: '50%',
              transform: 'translateY(-50%)',
              color: 'var(--text-muted)'
            }}
          />
          <input
            type="text"
            className="input-control"
            placeholder="Search 17,665 Flipkart products, brands..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            style={{ paddingLeft: '36px', height: '38px', borderRadius: '20px' }}
          />
        </div>

        {/* Search Suggestions Dropdown */}
        {suggestions.length > 0 && (
          <div
            style={{
              position: 'absolute',
              top: '46px',
              left: 0,
              right: 0,
              backgroundColor: 'var(--card-secondary)',
              border: '1px solid var(--border-color)',
              borderRadius: '10px',
              boxShadow: 'var(--shadow-sm)',
              overflow: 'hidden',
              zIndex: 100
            }}
          >
            {suggestions.map((item) => (
              <div
                key={item.uniq_id}
                onClick={() => {
                  setSuggestions([]);
                  setSearchQuery('');
                  if (onNavigateToProduct) onNavigateToProduct(item);
                }}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '10px',
                  padding: '10px 14px',
                  cursor: 'pointer',
                  borderBottom: '1px solid var(--border-color)',
                  transition: 'background-color 0.15s ease'
                }}
                onMouseEnter={(e) => e.currentTarget.style.backgroundColor = 'var(--card-elevated)'}
                onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
              >
                <ShoppingBag size={16} style={{ color: 'var(--accent-secondary)' }} />
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ fontSize: '12px', fontWeight: 600, color: 'var(--text-primary)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                    {item.product_name}
                  </div>
                  <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                    {item.brand} • ₹{item.discounted_price}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Right Controls: Backend Status & Theme Switcher */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '18px' }}>
        {/* Backend Indicator */}
        <div
          title={backendHealth.healthy ? `Flask API online: ${backendHealth.count} products` : 'Connecting to Flask API...'}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            fontSize: '12px',
            color: backendHealth.healthy ? 'var(--accent-vibrant)' : 'var(--text-muted)'
          }}
        >
          {backendHealth.healthy ? (
            <>
              <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: 'var(--accent-vibrant)', display: 'inline-block' }} />
              <span style={{ fontWeight: 500 }}>Live Engine</span>
            </>
          ) : (
            <>
              <AlertCircle size={14} style={{ color: 'var(--accent-secondary)' }} />
              <span>Offline</span>
            </>
          )}
        </div>

        {/* Global Monochrome Theme Toggle */}
        <button
          onClick={toggleTheme}
          aria-label="Toggle Theme"
          style={{
            background: 'none',
            border: 'none',
            color: 'var(--text-primary)',
            cursor: 'pointer',
            padding: '6px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            borderRadius: '6px'
          }}
        >
          {theme === 'dark' ? (
            <Moon size={20} strokeWidth={1.8} style={{ color: 'var(--text-primary)' }} />
          ) : (
            <Sun size={20} strokeWidth={1.8} style={{ color: 'var(--text-primary)' }} />
          )}
        </button>
      </div>
    </header>
  );
};
