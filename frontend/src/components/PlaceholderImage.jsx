import React from 'react';
import { Package } from 'lucide-react';

export const PlaceholderImage = ({ title = 'Product', className = '' }) => {
  return (
    <div
      className={`placeholder-img-container ${className}`}
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        backgroundColor: 'var(--card-secondary)',
        border: '1px dashed var(--border-color)',
        borderRadius: '8px',
        width: '100%',
        height: '100%',
        minHeight: '160px',
        color: 'var(--text-muted)',
        padding: '12px',
        textAlign: 'center'
      }}
    >
      <Package size={36} strokeWidth={1.5} style={{ marginBottom: '8px', color: 'var(--accent-secondary)' }} />
      <span style={{ fontSize: '11px', fontWeight: 500, maxWidth: '140px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
        {title}
      </span>
      <span style={{ fontSize: '9px', opacity: 0.7, marginTop: '2px' }}>
        Flipkart Catalogue
      </span>
    </div>
  );
};
