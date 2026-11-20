import React, { useState, useEffect } from 'react';
import { Search, Filter, ArrowUpDown, ChevronLeft, ChevronRight, RotateCcw } from 'lucide-react';
import { api } from '../services/api';
import { ProductCard } from '../components/ProductCard';

export const CataloguePage = ({ onSelectProductForRec }) => {
  const [products, setProducts] = useState([]);
  const [pagination, setPagination] = useState({ page: 1, limit: 12, total_products: 0, total_pages: 1 });
  const [loading, setLoading] = useState(true);

  // Filter states
  const [search, setSearch] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [selectedBrand, setSelectedBrand] = useState('All');
  const [selectedPriceRange, setSelectedPriceRange] = useState('All');
  const [sortBy, setSortBy] = useState('relevance');

  // Directory options
  const [categories, setCategories] = useState([]);
  const [brands, setBrands] = useState([]);

  // Fetch categories & brands for filter dropdowns
  useEffect(() => {
    api.getCategories().then(res => setCategories(res.categories || [])).catch(() => {});
    api.getBrands().then(res => setBrands(res.brands || [])).catch(() => {});
  }, []);

  // Fetch products whenever filters or page change
  const fetchProducts = (targetPage = 1) => {
    setLoading(true);
    api.getProducts({
      page: targetPage,
      limit: 12,
      search,
      category: selectedCategory,
      brand: selectedBrand,
      price_range: selectedPriceRange,
      sort_by: sortBy
    })
      .then(res => {
        if (res.success) {
          setProducts(res.products || []);
          setPagination(res.pagination || {});
        }
      })
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchProducts(1);
  }, [selectedCategory, selectedBrand, selectedPriceRange, sortBy]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    fetchProducts(1);
  };

  const handleResetFilters = () => {
    setSearch('');
    setSelectedCategory('All');
    setSelectedBrand('All');
    setSelectedPriceRange('All');
    setSortBy('relevance');
  };

  return (
    <div className="page-wrapper">
      {/* Header and Controls */}
      <div style={{ marginBottom: '24px' }}>
        <h2 style={{ fontSize: '20px', fontWeight: 800, marginBottom: '6px' }}>
          Flipkart Product Catalogue
        </h2>
        <p style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>
          Browse 17,665 curated listings with real-time filtering, instant search, and ranking
        </p>
      </div>

      {/* Filter Toolbar */}
      <div
        className="card"
        style={{
          display: 'flex',
          flexDirection: 'column',
          gap: '14px',
          marginBottom: '24px',
          backgroundColor: 'var(--card-secondary)'
        }}
      >
        <form onSubmit={handleSearchSubmit} style={{ display: 'flex', gap: '10px' }}>
          <div style={{ flex: 1, position: 'relative' }}>
            <Search size={16} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
            <input
              type="text"
              className="input-control"
              placeholder="Search by title, brand, or specifications..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              style={{ paddingLeft: '36px' }}
            />
          </div>
          <button type="submit" className="btn btn-primary">
            Search
          </button>
          <button type="button" onClick={handleResetFilters} className="btn btn-outline" title="Reset Filters">
            <RotateCcw size={15} />
          </button>
        </form>

        {/* Filter Dropdowns Grid */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '12px' }}>
          {/* Category Dropdown */}
          <div>
            <label style={{ fontSize: '11px', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '4px', display: 'block' }}>
              Category
            </label>
            <select
              className="input-control"
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
            >
              <option value="All">All Categories ({categories.length})</option>
              {categories.slice(0, 40).map(c => (
                <option key={c.name} value={c.name}>{c.name} ({c.count})</option>
              ))}
            </select>
          </div>

          {/* Brand Dropdown */}
          <div>
            <label style={{ fontSize: '11px', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '4px', display: 'block' }}>
              Brand
            </label>
            <select
              className="input-control"
              value={selectedBrand}
              onChange={(e) => setSelectedBrand(e.target.value)}
            >
              <option value="All">All Brands</option>
              {brands.slice(0, 40).map(b => (
                <option key={b.name} value={b.name}>{b.name} ({b.count})</option>
              ))}
            </select>
          </div>

          {/* Price Range Dropdown */}
          <div>
            <label style={{ fontSize: '11px', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '4px', display: 'block' }}>
              Price Tier
            </label>
            <select
              className="input-control"
              value={selectedPriceRange}
              onChange={(e) => setSelectedPriceRange(e.target.value)}
            >
              <option value="All">All Price Tiers</option>
              <option value="Budget">Budget (&lt; ₹500)</option>
              <option value="Mid-Range">Mid-Range (₹500 - ₹2,000)</option>
              <option value="Premium">Premium (&ge; ₹2,000)</option>
            </select>
          </div>

          {/* Sorting Dropdown */}
          <div>
            <label style={{ fontSize: '11px', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '4px', display: 'block' }}>
              Sort By
            </label>
            <select
              className="input-control"
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
            >
              <option value="relevance">Catalogue Score (Relevance)</option>
              <option value="price_asc">Price: Low to High</option>
              <option value="price_desc">Price: High to Low</option>
              <option value="discount_desc">Highest Discount %</option>
              <option value="rating_desc">Highest Customer Rating</option>
            </select>
          </div>
        </div>
      </div>

      {/* Results Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
        <span style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>
          Showing <strong>{products.length}</strong> of <strong>{pagination.total_products?.toLocaleString('en-IN') || 0}</strong> products
        </span>
        <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
          Page {pagination.page} of {pagination.total_pages}
        </span>
      </div>

      {/* Products Grid */}
      {loading ? (
        <div style={{ textAlign: 'center', padding: '60px 0' }}>
          <p style={{ color: 'var(--text-muted)' }}>Loading product catalogue...</p>
        </div>
      ) : products.length === 0 ? (
        <div className="card" style={{ textAlign: 'center', padding: '50px 20px' }}>
          <h3>No products found</h3>
          <p style={{ color: 'var(--text-muted)', fontSize: '13px', marginTop: '6px' }}>
            Try broadening your search query or clearing some filters.
          </p>
          <button onClick={handleResetFilters} className="btn btn-primary" style={{ marginTop: '16px' }}>
            Reset All Filters
          </button>
        </div>
      ) : (
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(260px, 1fr))',
            gap: '20px',
            marginBottom: '32px'
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

      {/* Pagination Controls */}
      {pagination.total_pages > 1 && (
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '12px' }}>
          <button
            className="btn btn-outline"
            disabled={!pagination.has_prev}
            onClick={() => fetchProducts(pagination.page - 1)}
            style={{ opacity: pagination.has_prev ? 1 : 0.5, cursor: pagination.has_prev ? 'pointer' : 'not-allowed' }}
          >
            <ChevronLeft size={16} /> Previous
          </button>

          <span style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-primary)' }}>
            Page {pagination.page} of {pagination.total_pages}
          </span>

          <button
            className="btn btn-outline"
            disabled={!pagination.has_next}
            onClick={() => fetchProducts(pagination.page + 1)}
            style={{ opacity: pagination.has_next ? 1 : 0.5, cursor: pagination.has_next ? 'pointer' : 'not-allowed' }}
          >
            Next <ChevronRight size={16} />
          </button>
        </div>
      )}
    </div>
  );
};
