import React, { useState, useEffect } from 'react';
import {
  Package,
  Layers,
  Award,
  IndianRupee,
  Percent,
  Sparkles,
  TrendingUp,
  AlertCircle
} from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';
import { api } from '../services/api';
import { useTheme } from '../context/ThemeContext';

export const DashboardPage = ({ onNavigateToCatalogue }) => {
  const { theme } = useTheme();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    setLoading(true);
    api.getDashboard()
      .then(res => {
        if (res.success) {
          setData(res);
        } else {
          setError(res.error || 'Failed to load dashboard data');
        }
      })
      .catch(err => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="page-wrapper" style={{ textAlign: 'center', padding: '60px 0' }}>
        <Sparkles size={36} className="spin-icon" style={{ color: 'var(--accent-primary)', marginBottom: '16px' }} />
        <h3 style={{ fontSize: '18px', fontWeight: 600 }}>Loading Catalogue Intelligence...</h3>
        <p style={{ color: 'var(--text-muted)', fontSize: '13px' }}>Aggregating 17,665 Flipkart products and metrics</p>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="page-wrapper">
        <div className="card" style={{ textAlign: 'center', padding: '40px', borderColor: '#ff4d4f' }}>
          <AlertCircle size={36} style={{ color: '#ff4d4f', marginBottom: '12px' }} />
          <h3>Unable to Connect to Flask Recommendation API</h3>
          <p style={{ color: 'var(--text-muted)', fontSize: '13px', margin: '8px 0 16px' }}>
            Ensure your backend is running: <code>python backend/app.py</code>
          </p>
          <button className="btn btn-primary" onClick={() => window.location.reload()}>Retry Connection</button>
        </div>
      </div>
    );
  }

  const { kpis, charts } = data;

  // Theme-aware chart colors based on official palette
  const chartColors = {
    forest: '#1F6521',
    vibrant: '#53900F',
    olive: '#A4A71E',
    lime: '#D6CE15',
    grid: theme === 'dark' ? '#354117' : '#E8EAE0',
    text: theme === 'dark' ? '#C4C7B1' : '#60634D',
    cardBg: theme === 'dark' ? '#1F2605' : '#FFFFFF'
  };

  const kpiCards = [
    { title: 'Total Products', value: kpis.total_products.toLocaleString('en-IN'), icon: Package, badge: 'Unique Items', color: 'var(--accent-vibrant)' },
    { title: 'Total Categories', value: kpis.total_categories, icon: Layers, badge: 'Hierarchy Levels', color: 'var(--accent-secondary)' },
    { title: 'Total Brands', value: kpis.total_brands.toLocaleString('en-IN'), icon: Award, badge: 'Standardized', color: 'var(--accent-primary)' },
    { title: 'Average Product Price', value: `₹${Math.round(kpis.avg_price).toLocaleString('en-IN')}`, icon: IndianRupee, badge: 'Selling Price', color: 'var(--accent-vibrant)' },
    { title: 'Average Discount', value: `${kpis.avg_discount}%`, icon: Percent, badge: 'Across Catalogue', color: 'var(--accent-primary)' }
  ];

  return (
    <div className="page-wrapper">
      {/* Welcome Banner */}
      <div
        className="card"
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '24px',
          background: 'linear-gradient(135deg, var(--card-primary) 0%, var(--card-secondary) 100%)',
          borderLeft: '4px solid var(--accent-primary)'
        }}
      >
        <div>
          <h2 style={{ fontSize: '20px', fontWeight: 800, marginBottom: '4px' }}>
            Catalogue Intelligence Overview
          </h2>
          <p style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>
            Real-time analytics across Flipkart PromptCloudHQ dataset • No synthetic transactions
          </p>
        </div>
        <button className="btn btn-primary" onClick={onNavigateToCatalogue}>
          <Package size={16} /> Browse Catalogue
        </button>
      </div>

      {/* KPI Cards Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(210px, 1fr))', gap: '16px', marginBottom: '28px' }}>
        {kpiCards.map((kpi, idx) => {
          const Icon = kpi.icon;
          return (
            <div key={idx} className="card" style={{ position: 'relative', overflow: 'hidden' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '10px' }}>
                <span style={{ fontSize: '12px', fontWeight: 600, color: 'var(--text-muted)' }}>{kpi.title}</span>
                <Icon size={18} style={{ color: kpi.color }} />
              </div>
              <div style={{ fontSize: '24px', fontWeight: 800, color: 'var(--text-primary)', marginBottom: '4px' }}>
                {kpi.value}
              </div>
              <span className="badge" style={{ fontSize: '10px' }}>{kpi.badge}</span>
            </div>
          );
        })}
      </div>

      {/* Charts Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(460px, 1fr))', gap: '20px' }}>
        {/* Chart 1: Products by Category */}
        <div className="card">
          <h3 style={{ fontSize: '15px', fontWeight: 700, marginBottom: '16px' }}>
            1. Products by Top Categories
          </h3>
          <div style={{ height: '260px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={charts.category_distribution} margin={{ top: 10, right: 10, left: -20, bottom: 40 }}>
                <CartesianGrid strokeDasharray="3 3" stroke={chartColors.grid} />
                <XAxis dataKey="name" angle={-30} textAnchor="end" tick={{ fill: chartColors.text, fontSize: 11 }} />
                <YAxis tick={{ fill: chartColors.text, fontSize: 11 }} />
                <Tooltip contentStyle={{ backgroundColor: chartColors.cardBg, borderColor: chartColors.grid, color: 'var(--text-primary)' }} />
                <Bar dataKey="count" fill={chartColors.forest} radius={[4, 4, 0, 0]} name="Product Count" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Chart 2: Brand Distribution */}
        <div className="card">
          <h3 style={{ fontSize: '15px', fontWeight: 700, marginBottom: '16px' }}>
            2. Brand Distribution (Top Specific Brands)
          </h3>
          <div style={{ height: '260px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={charts.brand_distribution} margin={{ top: 10, right: 10, left: -20, bottom: 40 }}>
                <CartesianGrid strokeDasharray="3 3" stroke={chartColors.grid} />
                <XAxis dataKey="name" angle={-30} textAnchor="end" tick={{ fill: chartColors.text, fontSize: 11 }} />
                <YAxis tick={{ fill: chartColors.text, fontSize: 11 }} />
                <Tooltip contentStyle={{ backgroundColor: chartColors.cardBg, borderColor: chartColors.grid, color: 'var(--text-primary)' }} />
                <Bar dataKey="count" fill={chartColors.vibrant} radius={[4, 4, 0, 0]} name="Product Count" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Chart 3: Product Price Range Distribution */}
        <div className="card">
          <h3 style={{ fontSize: '15px', fontWeight: 700, marginBottom: '16px' }}>
            3. Product Price Range Distribution
          </h3>
          <div style={{ height: '260px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={charts.price_distribution} margin={{ top: 10, right: 10, left: -10, bottom: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke={chartColors.grid} />
                <XAxis dataKey="tier" tick={{ fill: chartColors.text, fontSize: 11 }} />
                <YAxis tick={{ fill: chartColors.text, fontSize: 11 }} />
                <Tooltip contentStyle={{ backgroundColor: chartColors.cardBg, borderColor: chartColors.grid, color: 'var(--text-primary)' }} />
                <Bar dataKey="count" fill={chartColors.olive} radius={[4, 4, 0, 0]} name="Products" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Chart 4: Discount Distribution */}
        <div className="card">
          <h3 style={{ fontSize: '15px', fontWeight: 700, marginBottom: '16px' }}>
            4. Discount Percentage Distribution
          </h3>
          <div style={{ height: '260px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={charts.discount_distribution} margin={{ top: 10, right: 10, left: -10, bottom: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke={chartColors.grid} />
                <XAxis dataKey="range" tick={{ fill: chartColors.text, fontSize: 11 }} />
                <YAxis tick={{ fill: chartColors.text, fontSize: 11 }} />
                <Tooltip contentStyle={{ backgroundColor: chartColors.cardBg, borderColor: chartColors.grid, color: 'var(--text-primary)' }} />
                <Bar dataKey="count" fill={chartColors.lime} radius={[4, 4, 0, 0]} name="Products" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Chart 5: Category-wise Average Price */}
        <div className="card">
          <h3 style={{ fontSize: '15px', fontWeight: 700, marginBottom: '16px' }}>
            5. Category-wise Average Price (₹ INR)
          </h3>
          <div style={{ height: '260px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={charts.category_avg_price} margin={{ top: 10, right: 10, left: -10, bottom: 40 }}>
                <CartesianGrid strokeDasharray="3 3" stroke={chartColors.grid} />
                <XAxis dataKey="category" angle={-30} textAnchor="end" tick={{ fill: chartColors.text, fontSize: 11 }} />
                <YAxis tick={{ fill: chartColors.text, fontSize: 11 }} />
                <Tooltip formatter={(value) => `₹${value.toLocaleString('en-IN')}`} contentStyle={{ backgroundColor: chartColors.cardBg, borderColor: chartColors.grid, color: 'var(--text-primary)' }} />
                <Bar dataKey="avg_price" fill={chartColors.forest} radius={[4, 4, 0, 0]} name="Avg Price (₹)" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Chart 6: Model Evaluation Comparison */}
        <div className="card">
          <h3 style={{ fontSize: '15px', fontWeight: 700, marginBottom: '16px' }}>
            6. Recommendation Model Evaluation (NDCG@10 & Precision@10)
          </h3>
          <div style={{ height: '260px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={charts.model_evaluation} margin={{ top: 10, right: 10, left: -20, bottom: 30 }}>
                <CartesianGrid strokeDasharray="3 3" stroke={chartColors.grid} />
                <XAxis dataKey="model" angle={-15} textAnchor="end" tick={{ fill: chartColors.text, fontSize: 10 }} />
                <YAxis domain={[0.6, 1.0]} tick={{ fill: chartColors.text, fontSize: 11 }} />
                <Tooltip formatter={(v) => (v * 100).toFixed(1) + '%'} contentStyle={{ backgroundColor: chartColors.cardBg, borderColor: chartColors.grid, color: 'var(--text-primary)' }} />
                <Legend wrapperStyle={{ fontSize: 11 }} />
                <Bar dataKey="precision@10" fill={chartColors.forest} name="Precision@10" radius={[3, 3, 0, 0]} />
                <Bar dataKey="ndcg@10" fill={chartColors.lime} name="NDCG@10" radius={[3, 3, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
};
