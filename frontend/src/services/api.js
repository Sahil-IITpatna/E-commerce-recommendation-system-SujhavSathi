const API_BASE = 'http://localhost:5000/api';

async function handleResponse(res) {
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.error || `HTTP error! status: ${res.status}`);
  }
  return res.json();
}

export const api = {
  // Health
  getHealth: async () => {
    const res = await fetch(`${API_BASE}/health`);
    return handleResponse(res);
  },

  // Dashboard & Analytics
  getDashboard: async () => {
    const res = await fetch(`${API_BASE}/dashboard`);
    return handleResponse(res);
  },

  // Products with pagination & filters
  getProducts: async ({
    page = 1,
    limit = 12,
    search = '',
    category = '',
    brand = '',
    price_range = '',
    sort_by = 'relevance'
  } = {}) => {
    const params = new URLSearchParams();
    if (page) params.append('page', page);
    if (limit) params.append('limit', limit);
    if (search) params.append('search', search);
    if (category && category !== 'All') params.append('category', category);
    if (brand && brand !== 'All') params.append('brand', brand);
    if (price_range && price_range !== 'All') params.append('price_range', price_range);
    if (sort_by) params.append('sort_by', sort_by);

    const res = await fetch(`${API_BASE}/products?${params.toString()}`);
    return handleResponse(res);
  },

  // Single Product
  getProductById: async (productId) => {
    const res = await fetch(`${API_BASE}/products/${productId}`);
    return handleResponse(res);
  },

  // Autocomplete / Search
  searchProducts: async (q, limit = 8) => {
    const res = await fetch(`${API_BASE}/products/search?q=${encodeURIComponent(q)}&limit=${limit}`);
    return handleResponse(res);
  },

  // Algorithm 1: Catalogue Popular Ranking
  getPopularRecommendations: async ({ limit = 10, category = '', price_range = '', brand = '' } = {}) => {
    const params = new URLSearchParams();
    params.append('limit', limit);
    if (category && category !== 'All') params.append('category', category);
    if (price_range && price_range !== 'All') params.append('price_range', price_range);
    if (brand && brand !== 'All') params.append('brand', brand);

    const res = await fetch(`${API_BASE}/recommendations/popular?${params.toString()}`);
    return handleResponse(res);
  },

  // Algorithm 2: Content-Based Filtering
  getContentRecommendations: async (productId, limit = 8) => {
    const res = await fetch(`${API_BASE}/recommendations/content/${productId}?limit=${limit}`);
    return handleResponse(res);
  },

  // Algorithm 3: Category & Brand Recommendations
  getCategoryRecommendations: async (productId, limit = 8) => {
    const res = await fetch(`${API_BASE}/recommendations/category/${productId}?limit=${limit}`);
    return handleResponse(res);
  },

  // Algorithm 4: Hybrid Recommendations
  getHybridRecommendations: async (productId, { limit = 8, w_content = 0.6, w_category_brand = 0.25, w_catalogue = 0.15 } = {}) => {
    const params = new URLSearchParams();
    params.append('limit', limit);
    params.append('w_content', w_content);
    params.append('w_category_brand', w_category_brand);
    params.append('w_catalogue', w_catalogue);

    const res = await fetch(`${API_BASE}/recommendations/hybrid/${productId}?${params.toString()}`);
    return handleResponse(res);
  },

  // Categories & Brands
  getCategories: async () => {
    const res = await fetch(`${API_BASE}/categories`);
    return handleResponse(res);
  },

  getBrands: async () => {
    const res = await fetch(`${API_BASE}/brands`);
    return handleResponse(res);
  },

  // Model Evaluation
  getModelEvaluation: async () => {
    const res = await fetch(`${API_BASE}/model/evaluation`);
    return handleResponse(res);
  }
};
