import React, { useState, useEffect } from 'react';
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
import { Award, ShieldAlert, CheckCircle, HelpCircle, BarChart2 } from 'lucide-react';
import { api } from '../services/api';
import { useTheme } from '../context/ThemeContext';

export const ModelPerformancePage = () => {
  const { theme } = useTheme();
  const [evalData, setEvalData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getModelEvaluation()
      .then(res => {
        if (res.success) {
          setEvalData(res.data);
        }
      })
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  const chartColors = {
    forest: '#1F6521',
    vibrant: '#53900F',
    olive: '#A4A71E',
    lime: '#D6CE15',
    grid: theme === 'dark' ? '#354117' : '#E8EAE0',
    text: theme === 'dark' ? '#C4C7B1' : '#60634D',
    cardBg: theme === 'dark' ? '#1F2605' : '#FFFFFF'
  };

  return (
    <div className="page-wrapper">
      {/* Page Header */}
      <div style={{ marginBottom: '24px' }}>
        <h2 style={{ fontSize: '20px', fontWeight: 800, marginBottom: '6px' }}>
          Model Performance & Proxy-Based Evaluation
        </h2>
        <p style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>
          Transparent benchmarking of recommendation quality, precision, recall, and NDCG rankings
        </p>
      </div>

      {/* Responsible AI & Methodology Notice Banner */}
      <div
        className="card"
        style={{
          marginBottom: '24px',
          backgroundColor: 'var(--card-secondary)',
          borderLeft: '4px solid var(--accent-secondary)'
        }}
      >
        <div style={{ display: 'flex', gap: '14px', alignItems: 'flex-start' }}>
          <ShieldAlert size={22} style={{ color: 'var(--accent-secondary)', flexShrink: 0, marginTop: '2px' }} />
          <div>
            <h4 style={{ fontSize: '14px', fontWeight: 700, marginBottom: '4px' }}>
              Evaluation Methodology: Weak Proxy Relevance
            </h4>
            <p style={{ fontSize: '12px', color: 'var(--text-secondary)', lineHeight: 1.45 }}>
              The PromptCloudHQ dataset is an e-commerce catalogue without user interaction logs or transactions.
              Relevance ground-truth is established using <strong>catalogue taxonomy congruence</strong> (primary category tree alignment, subcategory match, brand family consistency, and price tier).
              These metrics reflect semantic and taxonomic retrieval accuracy rather than commercial conversion rates.
            </p>
          </div>
        </div>
      </div>

      {/* Metrics Comparison Table */}
      <div className="card" style={{ marginBottom: '28px', overflowX: 'auto' }}>
        <h3 style={{ fontSize: '15px', fontWeight: 700, marginBottom: '14px' }}>
          Recommendation Models Benchmark (N = 300 Stratified Queries)
        </h3>

        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px', textAlign: 'left' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid var(--border-color)', color: 'var(--text-muted)' }}>
              <th style={{ padding: '10px 14px' }}>Recommendation Engine</th>
              <th style={{ padding: '10px 14px' }}>Precision@5</th>
              <th style={{ padding: '10px 14px' }}>Precision@10</th>
              <th style={{ padding: '10px 14px' }}>Recall@5</th>
              <th style={{ padding: '10px 14px' }}>Recall@10</th>
              <th style={{ padding: '10px 14px' }}>NDCG@5</th>
              <th style={{ padding: '10px 14px' }}>NDCG@10</th>
            </tr>
          </thead>
          <tbody>
            {evalData?.metrics?.map((m, idx) => {
              const isHybrid = m.model.includes('Hybrid');
              return (
                <tr
                  key={m.model}
                  style={{
                    borderBottom: '1px solid var(--border-color)',
                    backgroundColor: isHybrid ? 'var(--card-elevated)' : 'transparent',
                    fontWeight: isHybrid ? 600 : 400
                  }}
                >
                  <td style={{ padding: '12px 14px', color: isHybrid ? 'var(--accent-primary)' : 'var(--text-primary)' }}>
                    {m.model} {isHybrid && <span className="badge" style={{ marginLeft: '6px' }}>Recommended</span>}
                  </td>
                  <td style={{ padding: '12px 14px' }}>{(m['precision@5'] * 100).toFixed(1)}%</td>
                  <td style={{ padding: '12px 14px' }}>{(m['precision@10'] * 100).toFixed(1)}%</td>
                  <td style={{ padding: '12px 14px' }}>{(m['recall@5'] * 100).toFixed(1)}%</td>
                  <td style={{ padding: '12px 14px' }}>{(m['recall@10'] * 100).toFixed(1)}%</td>
                  <td style={{ padding: '12px 14px', fontWeight: 700, color: 'var(--accent-primary)' }}>
                    {m['ndcg@5'].toFixed(4)}
                  </td>
                  <td style={{ padding: '12px 14px', fontWeight: 700, color: 'var(--accent-vibrant)' }}>
                    {m['ndcg@10'].toFixed(4)}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Comparative Charts */}
      {evalData?.metrics && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(460px, 1fr))', gap: '20px', marginBottom: '28px' }}>
          {/* Precision Comparison */}
          <div className="card">
            <h4 style={{ fontSize: '14px', fontWeight: 700, marginBottom: '14px' }}>
              Precision @ 5 and Precision @ 10 Comparison
            </h4>
            <div style={{ height: '260px' }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={evalData.metrics} margin={{ top: 10, right: 10, left: -20, bottom: 25 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke={chartColors.grid} />
                  <XAxis dataKey="model" angle={-15} textAnchor="end" tick={{ fill: chartColors.text, fontSize: 10 }} />
                  <YAxis domain={[0.9, 1.0]} tick={{ fill: chartColors.text, fontSize: 11 }} />
                  <Tooltip formatter={(v) => (v * 100).toFixed(1) + '%'} contentStyle={{ backgroundColor: chartColors.cardBg, borderColor: chartColors.grid }} />
                  <Legend wrapperStyle={{ fontSize: 11 }} />
                  <Bar dataKey="precision@5" fill={chartColors.forest} name="Precision@5" radius={[3, 3, 0, 0]} />
                  <Bar dataKey="precision@10" fill={chartColors.lime} name="Precision@10" radius={[3, 3, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* NDCG Comparison */}
          <div className="card">
            <h4 style={{ fontSize: '14px', fontWeight: 700, marginBottom: '14px' }}>
              NDCG @ 5 and NDCG @ 10 (Ranking Quality)
            </h4>
            <div style={{ height: '260px' }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={evalData.metrics} margin={{ top: 10, right: 10, left: -20, bottom: 25 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke={chartColors.grid} />
                  <XAxis dataKey="model" angle={-15} textAnchor="end" tick={{ fill: chartColors.text, fontSize: 10 }} />
                  <YAxis domain={[0.7, 1.0]} tick={{ fill: chartColors.text, fontSize: 11 }} />
                  <Tooltip formatter={(v) => v.toFixed(4)} contentStyle={{ backgroundColor: chartColors.cardBg, borderColor: chartColors.grid }} />
                  <Legend wrapperStyle={{ fontSize: 11 }} />
                  <Bar dataKey="ndcg@5" fill={chartColors.vibrant} name="NDCG@5" radius={[3, 3, 0, 0]} />
                  <Bar dataKey="ndcg@10" fill={chartColors.olive} name="NDCG@10" radius={[3, 3, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      )}

      {/* Metric Definitions & Mathematical Formulation */}
      <div className="card-secondary" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '20px' }}>
        <div>
          <h4 style={{ fontSize: '13px', fontWeight: 700, color: 'var(--accent-primary)', marginBottom: '6px' }}>
            Precision@K Formulation
          </h4>
          <p style={{ fontSize: '12px', color: 'var(--text-secondary)', lineHeight: 1.4 }}>
            Measures the proportion of the top-K recommended products that are taxonomy-relevant:
            <br />
            <code>Precision@K = (1 / K) * Σ r_i</code>
          </p>
        </div>

        <div>
          <h4 style={{ fontSize: '13px', fontWeight: 700, color: 'var(--accent-secondary)', marginBottom: '6px' }}>
            Recall@K Formulation
          </h4>
          <p style={{ fontSize: '12px', color: 'var(--text-secondary)', lineHeight: 1.4 }}>
            Measures the coverage of candidate products retrieved out of the relevant benchmark set:
            <br />
            <code>Recall@K = Σ r_i / min(|R|, K_norm)</code>
          </p>
        </div>

        <div>
          <h4 style={{ fontSize: '13px', fontWeight: 700, color: 'var(--accent-vibrant)', marginBottom: '6px' }}>
            NDCG@K Formulation
          </h4>
          <p style={{ fontSize: '12px', color: 'var(--text-secondary)', lineHeight: 1.4 }}>
            Evaluates ranking order using graded relevance (0, 1, 2, 3) penalizing lower-ranked matches:
            <br />
            <code>DCG@K / IDCG@K</code>
          </p>
        </div>
      </div>
    </div>
  );
};
