import React, { useState } from 'react';
import { Sparkles, Star, Tag } from 'lucide-react';
import { PlaceholderImage } from './PlaceholderImage';

export const ProductCard = ({ product, onSelectForRec, showRecDetails = false }) => {
  const [imageError, setImageError] = useState(false);

  const {
    uniq_id,
    product_name,
    brand,
    primary_category,
    retail_price,
    discounted_price,
    discount_percentage,
    price_range,
    primary_image,
    rating,
    has_rating,
    recommendation_score,
    recommendation_method,
    recommendation_reason,
    content_score,
    category_brand_score,
    catalogue_score
  } = product;

  return (
    <div
      className="card product-card"
      style={{
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'space-between',
        height: '100%',
        position: 'relative',
        overflow: 'hidden'
      }}
    >
      <div>
        {/* Image Container */}
        <div
          style={{
            position: 'relative',
            width: '100%',
            height: '180px',
            borderRadius: '8px',
            overflow: 'hidden',
            backgroundColor: 'var(--card-elevated)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            marginBottom: '14px'
          }}
        >
          {primary_image && !imageError ? (
            <img
              src={primary_image}
              alt={product_name}
              onError={() => setImageError(true)}
              style={{
                width: '100%',
                height: '100%',
                objectFit: 'contain',
                padding: '8px'
              }}
              loading="lazy"
            />
          ) : (
            <PlaceholderImage title={product_name} />
          )}

          {/* Discount Tag */}
          {discount_percentage > 0 && (
            <span
              style={{
                position: 'absolute',
                top: '8px',
                left: '8px',
                backgroundColor: 'var(--accent-primary)',
                color: 'var(--bg-main)',
                padding: '3px 7px',
                borderRadius: '4px',
                fontSize: '11px',
                fontWeight: 700,
                boxShadow: '0 2px 4px rgba(0,0,0,0.3)'
              }}
            >
              {Math.round(discount_percentage)}% OFF
            </span>
          )}

          {/* Price Tier Badge */}
          <span
            style={{
              position: 'absolute',
              top: '8px',
              right: '8px',
              backgroundColor: 'var(--card-secondary)',
              color: 'var(--text-secondary)',
              border: '1px solid var(--border-color)',
              padding: '2px 6px',
              borderRadius: '4px',
              fontSize: '10px',
              fontWeight: 600
            }}
          >
            {price_range}
          </span>
        </div>

        {/* Brand & Category */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '6px' }}>
          <span style={{ fontSize: '12px', fontWeight: 600, color: 'var(--accent-secondary)' }}>
            {brand || 'Generic'}
          </span>
          <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
            {primary_category}
          </span>
        </div>

        {/* Product Title */}
        <h4
          title={product_name}
          style={{
            fontSize: '14px',
            fontWeight: 600,
            lineHeight: 1.35,
            marginBottom: '8px',
            color: 'var(--text-primary)',
            display: '-webkit-box',
            WebkitLineClamp: 2,
            WebkitBoxOrient: 'vertical',
            overflow: 'hidden',
            minHeight: '38px'
          }}
        >
          {product_name}
        </h4>

        {/* Rating if available */}
        {has_rating && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '4px', marginBottom: '8px' }}>
            <span
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '3px',
                backgroundColor: 'var(--accent-vibrant)',
                color: '#fff',
                fontSize: '11px',
                fontWeight: 700,
                padding: '2px 6px',
                borderRadius: '4px'
              }}
            >
              {rating.toFixed(1)} <Star size={10} fill="#fff" />
            </span>
            <span style={{ fontSize: '10px', color: 'var(--text-muted)' }}>verified rating</span>
          </div>
        )}

        {/* Pricing Details */}
        <div style={{ display: 'flex', alignItems: 'baseline', gap: '8px', marginBottom: '12px' }}>
          <span style={{ fontSize: '18px', fontWeight: 700, color: 'var(--text-primary)' }}>
            ₹{discounted_price ? discounted_price.toLocaleString('en-IN') : 0}
          </span>
          {retail_price > discounted_price && (
            <span
              style={{
                fontSize: '12px',
                color: 'var(--text-muted)',
                textDecoration: 'line-through'
              }}
            >
              ₹{retail_price.toLocaleString('en-IN')}
            </span>
          )}
        </div>

        {/* Recommendation Score & Explanations (when in recommendation view) */}
        {showRecDetails && recommendation_score !== undefined && (
          <div
            style={{
              backgroundColor: 'var(--card-secondary)',
              border: '1px solid var(--border-color)',
              borderRadius: '8px',
              padding: '10px',
              marginBottom: '12px',
              fontSize: '12px'
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '4px' }}>
              <span style={{ fontWeight: 600, color: 'var(--accent-primary)', display: 'flex', alignItems: 'center', gap: '4px' }}>
                <Sparkles size={13} /> {(recommendation_score * 100).toFixed(1)}% Match
              </span>
              <span style={{ fontSize: '10px', color: 'var(--text-muted)' }}>
                {recommendation_method || 'Hybrid Engine'}
              </span>
            </div>

            {content_score !== undefined && (
              <div style={{ display: 'flex', gap: '6px', fontSize: '10px', marginBottom: '6px', color: 'var(--text-secondary)' }}>
                <span>Content: <strong>{(content_score * 100).toFixed(0)}%</strong></span>
                <span>•</span>
                <span>Brand/Cat: <strong>{(category_brand_score * 100).toFixed(0)}%</strong></span>
                <span>•</span>
                <span>Catalogue: <strong>{(catalogue_score * 100).toFixed(0)}%</strong></span>
              </div>
            )}

            {recommendation_reason && (
              <p style={{ fontSize: '11px', color: 'var(--text-secondary)', lineHeight: 1.35 }}>
                {recommendation_reason}
              </p>
            )}
          </div>
        )}
      </div>

      {/* Action Button */}
      {onSelectForRec && (
        <button
          onClick={() => onSelectForRec(product)}
          className="btn btn-primary"
          style={{ width: '100%', marginTop: '6px', fontSize: '13px' }}
        >
          <Sparkles size={14} /> Recommend Similar
        </button>
      )}
    </div>
  );
};
