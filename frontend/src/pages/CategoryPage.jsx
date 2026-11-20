import React, { useState, useEffect } from 'react';
import { FolderTree, Sparkles, Layers, Tag, IndianRupee } from 'lucide-react';
import { api } from '../services/api';
import { ProductCard } from '../components/ProductCard';

export const CategoryPage = ({ onSelectProductForRec }) => {
  const [categories, setCategories] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('');
  const [categoryStats, setCategoryStats] = useState(null);
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(false);

  // Filters within category
  const [selectedPriceTier, setSelectedPriceTier] = useState('All');
  const [selectedBrand, setSelectedBrand] = useState('All');
  const [availableBrands, setAvailableBrands] = useState([]);

  // Load category list on mount
  useEffect(() => {
    api.getCategories()
      .then(res => {
        if (res.categories && res.categories.length > 0) {
          setCategories(res.categories);
          setSelectedCategory(res.categories[0].name);
        }
      })
      .catch(err => console.error(err));
  }, []);

  // Update products when category or filters change
  useEffect(() => {
    if (!selectedCategory) return;
    setLoading(true);

    // Find stats for selected category
    const foundStats = categories.find(c => c.name === selectedCategory);
    setCategoryStats(foundStats || null);

    api.getProducts({
      page: 1,
      limit: 12,
      category: selectedCategory,
      price_range: selectedPriceTier,
      brand: selectedBrand
    })
      .then(res => {
        setProducts(res.products || []);
        // Extract brands from returned products or API
        const bSet = new Set((res.products || []).map(p => p.brand).filter(b => b && b !== 'Generic'));
        setAvailableBrands(Array.from(bSet));
      })
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  }, [selectedCategory, selectedPriceTier, selectedBrand, categories]);

  // Related categories heuristic (e.g. fashion related, tech related)
  const getRelatedCategories = () => {
    if (!selectedCategory) return [];
    return categories
      .filter(c => c.name !== selectedCategory)
      .slice(0, 4);
  };

  return (
    <div className="page-wrapper">
      {/* Page Header */}
      <div style={{ marginBottom: '24px' }}>
        <h2 style={{ fontSize: '20px', fontWeight: 800, marginBottom: '6px' }}>
          Category Explorer & Related Recommendations
        </h2>
        <p style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>
          Browse hierarchical catalogue branches and discover cross-category product alternatives
        </p>
      </div>

      {/* Category Selector Cards */}
      <div style={{ marginBottom: '24px' }}>
        <label style={{ fontSize: '12px', fontWeight: 700, color: 'var(--text-muted)', marginBottom: '8px', display: 'block' }}>
          Select Primary Category:
        </label>
        <div style={{ display: 'flex', gap: '8px', overflowX: 'auto', paddingBottom: '8px' }}>
          {categories.slice(0, 12).map(cat => (
            <button
              key={cat.name}
              onClick={() => {
                setSelectedCategory(cat.name);
                setSelectedBrand('All');
                setSelectedPriceTier('All');
              }}
              className="btn"
              style={{
                backgroundColor: selectedCategory === cat.name ? 'var(--accent-vibrant)' : 'var(--card-secondary)',
                color: selectedCategory === cat.name ? '#fff' : 'var(--text-primary)',
                border: '1px solid var(--border-color)',
                fontSize: '12px',
                whiteSpace: 'nowrap',
                flexShrink: 0
              }}
            >
              {cat.name} ({cat.count})
            </button>
          ))}
        </div>
      </div>

      {/* Category Info KPI Banner */}
      {categoryStats && (
        <div
          className="card"
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: '24px',
            backgroundColor: 'var(--card-secondary)',
            borderLeft: '4px solid var(--accent-vibrant)'
          }}
        >
          <div>
            <h3 style={{ fontSize: '17px', fontWeight: 800, marginBottom: '4px' }}>
              {categoryStats.name}
            </h3>
            <p style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
              Flipkart taxonomy branch • <strong>{categoryStats.count.toLocaleString('en-IN')}</strong> total listings
            </p>
          </div>

          <div style={{ display: 'flex', gap: '24px', textAlign: 'right' }}>
            <div>
              <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Average Price</span>
              <div style={{ fontSize: '16px', fontWeight: 700, color: 'var(--text-primary)' }}>
                ₹{Math.round(categoryStats.avg_price).toLocaleString('en-IN')}
              </div>
            </div>
            <div>
              <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Average Discount</span>
              <div style={{ fontSize: '16px', fontWeight: 700, color: 'var(--accent-primary)' }}>
                {Math.round(categoryStats.avg_discount)}%
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Related Categories Pills */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '24px' }}>
        <span style={{ fontSize: '12px', fontWeight: 600, color: 'var(--text-muted)' }}>
          Related Categories:
        </span>
        <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
          {getRelatedCategories().map(rc => (
            <button
              key={rc.name}
              onClick={() => setSelectedCategory(rc.name)}
              className="badge"
              style={{ cursor: 'pointer', padding: '4px 10px', fontSize: '11px' }}
            >
              <Sparkles size={11} /> {rc.name}
            </button>
          ))}
        </div>
      </div>

      {/* In-Category Filtering Bar */}
      <div
        className="card"
        style={{
          display: 'flex',
          gap: '16px',
          alignItems: 'center',
          marginBottom: '20px',
          padding: '12px 18px',
          backgroundColor: 'var(--card-elevated)'
        }}
      >
        <span style={{ fontSize: '12px', fontWeight: 700 }}>Filter within category:</span>

        {/* Price Tier Filter */}
        <select
          className="input-control"
          style={{ maxWidth: '180px', height: '34px', fontSize: '12px' }}
          value={selectedPriceTier}
          onChange={(e) => setSelectedPriceTier(e.target.value)}
        >
          <option value="All">All Price Tiers</option>
          <option value="Budget">Budget (&lt; ₹500)</option>
          <option value="Mid-Range">Mid-Range (₹500-2K)</option>
          <option value="Premium">Premium (&ge; ₹2K)</option>
        </select>

        {/* Brand Filter */}
        <select
          className="input-control"
          style={{ maxWidth: '180px', height: '34px', fontSize: '12px' }}
          value={selectedBrand}
          onChange={(e) => setSelectedBrand(e.target.value)}
        >
          <option value="All">All Brands</option>
          {availableBrands.map(b => (
            <option key={b} value={b}>{b}</option>
          ))}
        </select>
      </div>

      {/* Product Grid */}
      {loading ? (
        <div style={{ textAlign: 'center', padding: '60px 0' }}>
          <p style={{ color: 'var(--text-muted)' }}>Loading products in {selectedCategory}...</p>
        </div>
      ) : products.length === 0 ? (
        <div className="card" style={{ textAlign: 'center', padding: '40px' }}>
          <p style={{ color: 'var(--text-muted)' }}>No products match the selected filters in this category.</p>
        </div>
      ) : (
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(260px, 1fr))',
            gap: '20px'
          }}
        >
          {products.map(product => (
            <ProductCard
              key={product.uniq_id}
              product={product}
              onSelectForRec={onSelectProductForRec}
            />
          ))}
        </div>
      )}
    </div>
  );
};
