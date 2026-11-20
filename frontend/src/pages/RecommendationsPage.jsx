import React, { useState, useEffect } from 'react';
import { Sparkles, Sliders, Layers, Search, RefreshCw, Info, Tag } from 'lucide-react';
import { api } from '../services/api';
import { ProductCard } from '../components/ProductCard';

export const RecommendationsPage = ({ selectedProduct, onSelectProduct }) => {
  const [currentProduct, setCurrentProduct] = useState(selectedProduct || null);
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('hybrid'); // 'hybrid', 'content', 'category', 'catalogue'

  // Hybrid Weights
  const [wContent, setWContent] = useState(0.60);
  const [wCategoryBrand, setWCategoryBrand] = useState(0.25);
  const [wCatalogue, setWCatalogue] = useState(0.15);

  // Search picker state
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);

  // If no product is selected yet, fetch a default popular product
  useEffect(() => {
    if (!currentProduct) {
      api.getProducts({ page: 1, limit: 1 })
        .then(res => {
          if (res.products && res.products.length > 0) {
            setCurrentProduct(res.products[0]);
          }
        })
        .catch(() => {});
    }
  }, [currentProduct]);

  // Fetch recommendations whenever currentProduct, activeTab, or weights change
  const fetchRecommendations = () => {
    if (!currentProduct) return;
    setLoading(true);

    const pid = currentProduct.uniq_id;

    if (activeTab === 'hybrid') {
      api.getHybridRecommendations(pid, {
        limit: 8,
        w_content: wContent,
        w_category_brand: wCategoryBrand,
        w_catalogue: wCatalogue
      })
        .then(res => setRecommendations(res.recommendations || []))
        .catch(err => console.error(err))
        .finally(() => setLoading(false));
    } else if (activeTab === 'content') {
      api.getContentRecommendations(pid, 8)
        .then(res => setRecommendations(res.recommendations || []))
        .catch(err => console.error(err))
        .finally(() => setLoading(false));
    } else if (activeTab === 'category') {
      api.getCategoryRecommendations(pid, 8)
        .then(res => setRecommendations(res.recommendations || []))
        .catch(err => console.error(err))
        .finally(() => setLoading(false));
    } else if (activeTab === 'catalogue') {
      api.getPopularRecommendations({
        limit: 8,
        category: currentProduct.primary_category,
        price_range: currentProduct.price_range
      })
        .then(res => setRecommendations(res.recommendations || []))
        .catch(err => console.error(err))
        .finally(() => setLoading(false));
    }
  };

  useEffect(() => {
    fetchRecommendations();
  }, [currentProduct, activeTab, wContent, wCategoryBrand, wCatalogue]);

  // Handle autocomplete search
  const handleSearchChange = (e) => {
    const q = e.target.value;
    setSearchQuery(q);
    if (q.trim().length > 1) {
      api.searchProducts(q, 5)
        .then(res => setSearchResults(res.results || []))
        .catch(() => setSearchResults([]));
    } else {
      setSearchResults([]);
    }
  };

  const handleSelectSearchedProduct = (prod) => {
    setCurrentProduct(prod);
    setSearchQuery('');
    setSearchResults([]);
  };

  return (
    <div className="page-wrapper">
      {/* Page Header */}
      <div style={{ marginBottom: '24px' }}>
        <h2 style={{ fontSize: '20px', fontWeight: 800, marginBottom: '6px' }}>
          Intelligent Product Recommendations
        </h2>
        <p style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>
          Compare TF-IDF Content-Based, Category/Brand attribute matching, and Hybrid recommendation algorithms
        </p>
      </div>

      {/* Selected Query Product Spotlight Banner */}
      {currentProduct && (
        <div
          className="card"
          style={{
            marginBottom: '24px',
            backgroundColor: 'var(--card-secondary)',
            borderLeft: '4px solid var(--accent-primary)'
          }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
            <span style={{ fontSize: '12px', fontWeight: 700, color: 'var(--accent-primary)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
              Current Query Product
            </span>

            {/* Quick Product Search Switcher */}
            <div style={{ position: 'relative', width: '280px' }}>
              <input
                type="text"
                className="input-control"
                placeholder="Switch product (type name)..."
                value={searchQuery}
                onChange={handleSearchChange}
                style={{ height: '34px', fontSize: '12px' }}
              />
              {searchResults.length > 0 && (
                <div
                  style={{
                    position: 'absolute',
                    top: '38px',
                    left: 0,
                    right: 0,
                    backgroundColor: 'var(--card-elevated)',
                    border: '1px solid var(--border-color)',
                    borderRadius: '8px',
                    boxShadow: 'var(--shadow-sm)',
                    zIndex: 40
                  }}
                >
                  {searchResults.map(p => (
                    <div
                      key={p.uniq_id}
                      onClick={() => handleSelectSearchedProduct(p)}
                      style={{ padding: '8px 12px', cursor: 'pointer', borderBottom: '1px solid var(--border-color)', fontSize: '11px' }}
                      onMouseEnter={(e) => e.currentTarget.style.backgroundColor = 'var(--card-secondary)'}
                      onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
                    >
                      <div style={{ fontWeight: 600, color: 'var(--text-primary)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                        {p.product_name}
                      </div>
                      <span style={{ color: 'var(--text-muted)' }}>{p.brand} • ₹{p.discounted_price}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          <div style={{ display: 'flex', gap: '20px', alignItems: 'center' }}>
            <div
              style={{
                width: '100px',
                height: '100px',
                borderRadius: '8px',
                backgroundColor: 'var(--card-elevated)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                overflow: 'hidden',
                flexShrink: 0
              }}
            >
              {currentProduct.primary_image ? (
                <img src={currentProduct.primary_image} alt="" style={{ width: '100%', height: '100%', objectFit: 'contain', padding: '6px' }} />
              ) : (
                <Tag size={28} style={{ color: 'var(--accent-secondary)' }} />
              )}
            </div>

            <div style={{ flex: 1, minWidth: 0 }}>
              <div style={{ display: 'flex', gap: '8px', marginBottom: '4px' }}>
                <span className="badge">{currentProduct.brand}</span>
                <span className="badge" style={{ backgroundColor: 'var(--card-elevated)', color: 'var(--text-secondary)' }}>
                  {currentProduct.primary_category} &gt; {currentProduct.sub_category}
                </span>
                <span className="badge" style={{ backgroundColor: 'var(--card-elevated)', color: 'var(--text-secondary)' }}>
                  {currentProduct.price_range}
                </span>
              </div>
              <h3 style={{ fontSize: '16px', fontWeight: 700, marginBottom: '6px', color: 'var(--text-primary)' }}>
                {currentProduct.product_name}
              </h3>
              <div style={{ display: 'flex', gap: '12px', alignItems: 'baseline', fontSize: '13px' }}>
                <span style={{ fontSize: '18px', fontWeight: 800, color: 'var(--text-primary)' }}>
                  ₹{currentProduct.discounted_price?.toLocaleString('en-IN')}
                </span>
                {currentProduct.retail_price > currentProduct.discounted_price && (
                  <span style={{ textDecoration: 'line-through', color: 'var(--text-muted)', fontSize: '12px' }}>
                    MRP ₹{currentProduct.retail_price?.toLocaleString('en-IN')}
                  </span>
                )}
                <span style={{ color: 'var(--accent-primary)', fontWeight: 600 }}>
                  ({Math.round(currentProduct.discount_percentage)}% discount)
                </span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Algorithm Tabs */}
      <div
        style={{
          display: 'flex',
          gap: '8px',
          borderBottom: '1px solid var(--border-color)',
          marginBottom: '20px',
          paddingBottom: '2px'
        }}
      >
        {[
          { id: 'hybrid', label: 'Weighted Hybrid Recommender' },
          { id: 'content', label: 'Content-Based (TF-IDF)' },
          { id: 'category', label: 'Category & Brand Matching' },
          { id: 'catalogue', label: 'Catalogue Listing Ranking' }
        ].map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            style={{
              padding: '10px 18px',
              border: 'none',
              background: 'none',
              borderBottom: activeTab === tab.id ? '2px solid var(--accent-primary)' : '2px solid transparent',
              color: activeTab === tab.id ? 'var(--accent-primary)' : 'var(--text-secondary)',
              fontWeight: activeTab === tab.id ? 700 : 500,
              fontSize: '13px',
              cursor: 'pointer',
              transition: 'all 0.15s ease'
            }}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Configurable Hybrid Weight Sliders (Visible when Hybrid tab is selected) */}
      {activeTab === 'hybrid' && (
        <div
          className="card"
          style={{
            marginBottom: '24px',
            backgroundColor: 'var(--card-elevated)',
            display: 'flex',
            flexDirection: 'column',
            gap: '12px'
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <span style={{ fontSize: '13px', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '6px' }}>
              <Sliders size={16} style={{ color: 'var(--accent-secondary)' }} />
              Dynamic Hybrid Weights Tuning
            </span>
            <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
              Normalized weights automatically sum to 100%
            </span>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px' }}>
            {/* Weight 1: Content */}
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', marginBottom: '4px' }}>
                <span style={{ fontWeight: 600 }}>TF-IDF Content Similarity</span>
                <span style={{ color: 'var(--accent-primary)', fontWeight: 700 }}>{Math.round(wContent * 100)}%</span>
              </div>
              <input
                type="range"
                min="0"
                max="1"
                step="0.05"
                value={wContent}
                onChange={(e) => setWContent(parseFloat(e.target.value))}
                style={{ width: '100%', accentColor: 'var(--accent-vibrant)' }}
              />
            </div>

            {/* Weight 2: Category & Brand */}
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', marginBottom: '4px' }}>
                <span style={{ fontWeight: 600 }}>Category & Brand Alignment</span>
                <span style={{ color: 'var(--accent-secondary)', fontWeight: 700 }}>{Math.round(wCategoryBrand * 100)}%</span>
              </div>
              <input
                type="range"
                min="0"
                max="1"
                step="0.05"
                value={wCategoryBrand}
                onChange={(e) => setWCategoryBrand(parseFloat(e.target.value))}
                style={{ width: '100%', accentColor: 'var(--accent-secondary)' }}
              />
            </div>

            {/* Weight 3: Catalogue */}
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', marginBottom: '4px' }}>
                <span style={{ fontWeight: 600 }}>Catalogue Listing Score</span>
                <span style={{ color: 'var(--accent-primary)', fontWeight: 700 }}>{Math.round(wCatalogue * 100)}%</span>
              </div>
              <input
                type="range"
                min="0"
                max="1"
                step="0.05"
                value={wCatalogue}
                onChange={(e) => setWCatalogue(parseFloat(e.target.value))}
                style={{ width: '100%', accentColor: 'var(--accent-primary)' }}
              />
            </div>
          </div>
        </div>
      )}

      {/* Recommendations Results Grid */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
        <h3 style={{ fontSize: '15px', fontWeight: 700 }}>
          Recommended Products ({recommendations.length})
        </h3>
        <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
          Excludes query product from results
        </span>
      </div>

      {loading ? (
        <div style={{ textAlign: 'center', padding: '60px 0' }}>
          <p style={{ color: 'var(--text-muted)' }}>Calculating recommendation vectors...</p>
        </div>
      ) : recommendations.length === 0 ? (
        <div className="card" style={{ textAlign: 'center', padding: '40px' }}>
          <p style={{ color: 'var(--text-muted)' }}>No recommendations found for this product selection.</p>
        </div>
      ) : (
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
            gap: '20px'
          }}
        >
          {recommendations.map(product => (
            <ProductCard
              key={product.uniq_id}
              product={product}
              showRecDetails={true}
              onSelectForRec={(p) => setCurrentProduct(p)}
            />
          ))}
        </div>
      )}
    </div>
  );
};
