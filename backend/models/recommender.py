import os
import joblib
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import linear_kernel

class SujhavRecommender:
    """
    Sujhav साथी E-Commerce Recommendation Engine.
    Implements 4 Algorithms:
      1. Popularity / Catalogue Listing Ranking
      2. TF-IDF Content-Based Filtering
      3. Category & Brand Attribute Matching
      4. Configurable Weighted Hybrid Recommendation System
    """

    def __init__(self, artifacts_dir=None):
        if artifacts_dir is None:
            artifacts_dir = os.path.join(os.path.dirname(__file__), "..", "artifacts")
        self.artifacts_dir = artifacts_dir
        self.is_loaded = False
        self.df = None
        self.tfidf = None
        self.tfidf_matrix = None
        self.catalogue_scores = None
        self.top50_indices = None
        self.top50_scores = None
        self.id_to_idx = {}
        self.idx_to_id = {}
        self.categories = []
        self.brands = []

    def load_artifacts(self):
        """Loads precomputed models and matrices from artifacts directory."""
        print(f"Loading recommendation artifacts from {self.artifacts_dir}...")
        
        # Load dataset
        data_path = os.path.join(self.artifacts_dir, "flipkart_catalogue.joblib")
        if not os.path.exists(data_path):
            # Fallback to data/processed
            data_path = os.path.join(os.path.dirname(self.artifacts_dir), "..", "data", "processed", "flipkart_cleaned.joblib")
        
        self.df = joblib.load(data_path).reset_index(drop=True)
        
        # Create fast lookup maps
        self.id_to_idx = {uid: i for i, uid in enumerate(self.df["uniq_id"])}
        self.idx_to_id = {i: uid for i, uid in enumerate(self.df["uniq_id"])}
        
        # Load TF-IDF pipeline and sparse matrix
        tfidf_path = os.path.join(self.artifacts_dir, "tfidf_model.joblib")
        tfidf_data = joblib.load(tfidf_path)
        self.tfidf = tfidf_data["vectorizer"]
        self.tfidf_matrix = tfidf_data["matrix"]
        
        # Load precomputed catalogue ranking scores
        meta_path = os.path.join(self.artifacts_dir, "metadata.joblib")
        metadata = joblib.load(meta_path)
        self.catalogue_scores = metadata["catalogue_scores"]
        self.categories = metadata.get("categories", sorted(self.df["primary_category"].unique().tolist()))
        self.brands = metadata.get("brands", sorted(self.df["brand_cleaned"].unique().tolist()))
        
        # Load precomputed top-50 content indices (if available for O(1) performance)
        top50_path = os.path.join(self.artifacts_dir, "content_top50.joblib")
        if os.path.exists(top50_path):
            top50_data = joblib.load(top50_path)
            self.top50_indices = top50_data["indices"]
            self.top50_scores = top50_data["scores"]
            
        self.is_loaded = True
        print(f"Recommender successfully loaded: {len(self.df)} products, {len(self.categories)} categories, {len(self.brands)} brands.")

    def _format_product(self, idx, extra_fields=None):
        """Helper to format a dataframe row into a clean dictionary for API and client display."""
        row = self.df.iloc[idx]
        item = {
            "uniq_id": str(row["uniq_id"]),
            "pid": str(row.get("pid", "")),
            "product_name": str(row["product_name"]),
            "brand": str(row.get("brand_cleaned", "Generic")),
            "primary_category": str(row.get("primary_category", "General")),
            "sub_category": str(row.get("sub_category", "")),
            "category_path": str(row.get("category_path", "")),
            "retail_price": float(row.get("retail_price", 0.0)),
            "discounted_price": float(row.get("discounted_price", 0.0)),
            "discount_amount": float(row.get("discount_amount", 0.0)),
            "discount_percentage": float(row.get("discount_percentage", 0.0)),
            "price_range": str(row.get("price_range", "Mid-Range")),
            "primary_image": str(row.get("primary_image", "")),
            "rating": float(row.get("rating_numeric", 0.0)),
            "has_rating": bool(row.get("has_rating", False)),
            "description": str(row.get("description", "")),
            "specifications": str(row.get("specs_cleaned", "")),
            "completeness_score": int(row.get("completeness_score", 100)),
            "catalogue_score": float(self.catalogue_scores[idx]) if self.catalogue_scores is not None else 0.5
        }
        if extra_fields:
            item.update(extra_fields)
        return item

    # -------------------------------------------------------------------------
    # ALGORITHM 1: CATALOGUE LISTING RANKING
    # -------------------------------------------------------------------------
    def get_catalogue_ranking(self, top_k=10, category=None, price_range=None, brand=None):
        """
        Ranks products based on a transparent composite score of:
          - Customer rating (normalized, if available)
          - Discount depth (percentage discount)
          - Listing completeness score
        """
        subset = self.df
        mask = np.ones(len(subset), dtype=bool)
        
        if category and category.lower() != "all":
            mask &= (subset["primary_category"].str.lower() == category.lower())
        if price_range and price_range.lower() != "all":
            mask &= (subset["price_range"].str.lower() == price_range.lower())
        if brand and brand.lower() != "all":
            mask &= (subset["brand_cleaned"].str.lower() == brand.lower())
            
        candidate_indices = np.where(mask)[0]
        if len(candidate_indices) == 0:
            candidate_indices = np.arange(min(100, len(self.df)))

        # Sort candidate indices by precomputed catalogue score descending
        sorted_candidates = candidate_indices[np.argsort(-self.catalogue_scores[candidate_indices])]
        top_indices = sorted_candidates[:top_k]
        
        results = []
        for rank, idx in enumerate(top_indices, 1):
            score = float(self.catalogue_scores[idx])
            reason = (
                f"Rank #{rank} in catalogue ranking with a composite listing score of {score*100:.1f}%. "
                f"Features {self.df.iloc[idx]['discount_percentage']:.0f}% discount, "
                f"{self.df.iloc[idx]['completeness_score']}% listing completeness"
                + (f" and {self.df.iloc[idx]['rating_numeric']}★ customer rating." if self.df.iloc[idx]['has_rating'] else ".")
            )
            results.append(self._format_product(idx, {
                "recommendation_score": round(score, 4),
                "recommendation_method": "Catalogue-Based Ranking",
                "recommendation_reason": reason
            }))
        return results

    # -------------------------------------------------------------------------
    # ALGORITHM 2: TF-IDF CONTENT-BASED FILTERING
    # -------------------------------------------------------------------------
    def get_content_recommendations(self, product_id, top_k=10):
        """
        Recommends products sharing high textual and specification similarity
        using TF-IDF Vectorizer and Cosine Similarity.
        """
        if product_id not in self.id_to_idx:
            # Fallback to catalogue ranking if product not found
            return self.get_catalogue_ranking(top_k=top_k)

        query_idx = self.id_to_idx[product_id]
        query_row = self.df.iloc[query_idx]

        # Use precomputed top-50 if available
        if self.top50_indices is not None:
            indices = self.top50_indices[query_idx]
            scores = self.top50_scores[query_idx]
            
            # Exclude self
            valid_mask = indices != query_idx
            cand_indices = indices[valid_mask][:top_k]
            cand_scores = scores[valid_mask][:top_k]
        else:
            # On-the-fly linear_kernel
            query_vec = self.tfidf_matrix[query_idx]
            sim_scores = linear_kernel(query_vec, self.tfidf_matrix).flatten()
            sorted_indices = np.argsort(-sim_scores)
            # Filter self
            valid_indices = [i for i in sorted_indices if i != query_idx]
            cand_indices = valid_indices[:top_k]
            cand_scores = [sim_scores[i] for i in cand_indices]

        results = []
        for idx, score in zip(cand_indices, cand_scores):
            target_row = self.df.iloc[idx]
            sim_pct = max(0.0, min(100.0, float(score) * 100))
            
            # Formulate human-readable explanation
            reasons = []
            if query_row.get("primary_category") == target_row.get("primary_category"):
                reasons.append(f"same category '{query_row.get('primary_category')}'")
            if (query_row.get("brand_cleaned") != "Generic" and 
                query_row.get("brand_cleaned") == target_row.get("brand_cleaned")):
                reasons.append(f"matching brand '{query_row.get('brand_cleaned')}'")
            if query_row.get("price_range") == target_row.get("price_range"):
                reasons.append(f"similar {query_row.get('price_range')} price bracket")
                
            attr_summary = ", ".join(reasons) if reasons else "high vocabulary and specification overlap"
            reason_str = (
                f"{sim_pct:.1f}% semantic similarity based on product description, specifications, "
                f"and titles ({attr_summary})."
            )

            results.append(self._format_product(idx, {
                "recommendation_score": round(float(score), 4),
                "recommendation_method": "Content-Based (TF-IDF Cosine Similarity)",
                "recommendation_reason": reason_str
            }))
            
        # Fallback if too few recommendations
        if len(results) < top_k:
            fallback = self.get_category_brand_recommendations(product_id, top_k=top_k - len(results))
            for f in fallback:
                if f["uniq_id"] not in [r["uniq_id"] for r in results] and f["uniq_id"] != product_id:
                    results.append(f)
                    
        return results[:top_k]

    # -------------------------------------------------------------------------
    # ALGORITHM 3: CATEGORY & BRAND ATTRIBUTE MATCHING
    # -------------------------------------------------------------------------
    def get_category_brand_recommendations(self, product_id, top_k=10):
        """
        Recommends products sharing strict category hierarchy, brand affinity,
        and price tier alignment.
        """
        if product_id not in self.id_to_idx:
            return self.get_catalogue_ranking(top_k=top_k)

        query_idx = self.id_to_idx[product_id]
        query_row = self.df.iloc[query_idx]
        
        q_cat = str(query_row.get("primary_category", ""))
        q_subcat = str(query_row.get("sub_category", ""))
        q_brand = str(query_row.get("brand_cleaned", ""))
        q_price = float(query_row.get("discounted_price", 1.0))
        q_tier = str(query_row.get("price_range", ""))

        # Filter candidates in the same primary category
        cat_mask = (self.df["primary_category"] == q_cat) & (self.df["uniq_id"] != product_id)
        candidate_indices = np.where(cat_mask)[0]
        
        if len(candidate_indices) < top_k:
            # Expand to broader catalogue if category is small
            candidate_indices = np.where(self.df["uniq_id"] != product_id)[0]

        cand_df = self.df.iloc[candidate_indices]
        
        # Attribute similarity score components:
        # 1. Subcategory exact match: 0.35
        # 2. Brand match: 0.35 (if not generic)
        # 3. Price tier match: 0.15
        # 4. Price proximity: 0.15 * (1 - |p_diff| / max(p1, p2))
        subcat_score = (cand_df["sub_category"] == q_subcat).astype(float) * 0.35
        
        if q_brand not in ["Generic", "Unknown", ""]:
            brand_score = (cand_df["brand_cleaned"] == q_brand).astype(float) * 0.35
        else:
            brand_score = np.zeros(len(cand_df))
            
        tier_score = (cand_df["price_range"] == q_tier).astype(float) * 0.15
        
        max_prices = np.maximum(cand_df["discounted_price"], q_price)
        price_diff = np.abs(cand_df["discounted_price"] - q_price)
        price_prox = (1.0 - (price_diff / max_prices)).clip(0.0, 1.0) * 0.15
        
        attr_scores = subcat_score + brand_score + tier_score + price_prox
        
        # Sort top candidates
        top_cand_subidx = np.argsort(-attr_scores.values)[:top_k]
        top_indices = candidate_indices[top_cand_subidx]
        
        results = []
        for i, idx in enumerate(top_indices):
            score = float(attr_scores.iloc[top_cand_subidx[i]])
            target_row = self.df.iloc[idx]
            
            reasons = []
            if target_row["primary_category"] == q_cat:
                reasons.append(f"Category: {q_cat}")
            if target_row["brand_cleaned"] == q_brand and q_brand != "Generic":
                reasons.append(f"Brand: {q_brand}")
            if target_row["price_range"] == q_tier:
                reasons.append(f"Price Tier: {q_tier}")
                
            reason_str = (
                f"Attribute alignment score {score*100:.0f}% (" + ", ".join(reasons) + 
                f", Price ₹{target_row['discounted_price']:,.0f} vs ₹{q_price:,.0f})."
            )
            
            results.append(self._format_product(idx, {
                "recommendation_score": round(score, 4),
                "recommendation_method": "Category & Brand Attribute Filtering",
                "recommendation_reason": reason_str
            }))
        return results

    # -------------------------------------------------------------------------
    # ALGORITHM 4: HYBRID RECOMMENDATION SYSTEM
    # -------------------------------------------------------------------------
    def get_hybrid_recommendations(self, product_id, top_k=10, weights=None):
        """
        Combines Content-Based, Category & Brand, and Catalogue Ranking.
        Default weights:
          - Content-based: 60%
          - Category & Brand: 25%
          - Catalogue Listing Score: 15%
        Component scores are normalized to [0, 1] before combination.
        """
        if weights is None:
            weights = {"content": 0.60, "category_brand": 0.25, "catalogue": 0.15}
            
        w_content = float(weights.get("content", 0.60))
        w_catbrand = float(weights.get("category_brand", 0.25))
        w_cat = float(weights.get("catalogue", 0.15))
        
        # Normalize weights to sum to 1.0
        total_w = w_content + w_catbrand + w_cat
        if total_w > 0:
            w_content /= total_w
            w_catbrand /= total_w
            w_cat /= total_w

        if product_id not in self.id_to_idx:
            return self.get_catalogue_ranking(top_k=top_k)

        query_idx = self.id_to_idx[product_id]
        query_row = self.df.iloc[query_idx]
        
        # Fetch candidate pool (e.g. top 60 content items + same category items)
        if self.top50_indices is not None:
            content_candidates = [i for i in self.top50_indices[query_idx] if i != query_idx]
        else:
            q_vec = self.tfidf_matrix[query_idx]
            sims = linear_kernel(q_vec, self.tfidf_matrix).flatten()
            content_candidates = [i for i in np.argsort(-sims) if i != query_idx][:60]
            
        # Same category candidates
        cat_mask = (self.df["primary_category"] == query_row["primary_category"]) & (self.df["uniq_id"] != product_id)
        cat_candidates = np.where(cat_mask)[0][:60].tolist()
        
        # Combine unique candidates pool
        pool_indices = list(dict.fromkeys(content_candidates + cat_candidates))[:100]
        if not pool_indices:
            pool_indices = [i for i in range(min(50, len(self.df))) if i != query_idx]

        # 1. Content component scores
        query_vec = self.tfidf_matrix[query_idx]
        content_scores_raw = linear_kernel(query_vec, self.tfidf_matrix[pool_indices]).flatten()
        c_min, c_max = content_scores_raw.min(), content_scores_raw.max()
        norm_content = (content_scores_raw - c_min) / (c_max - c_min + 1e-8) if c_max > c_min else content_scores_raw

        # 2. Category & Brand component scores
        q_cat = str(query_row.get("primary_category", ""))
        q_subcat = str(query_row.get("sub_category", ""))
        q_brand = str(query_row.get("brand_cleaned", ""))
        q_price = float(query_row.get("discounted_price", 1.0))
        q_tier = str(query_row.get("price_range", ""))
        
        pool_df = self.df.iloc[pool_indices]
        
        subcat_m = (pool_df["sub_category"] == q_subcat).astype(float) * 0.35
        if q_brand not in ["Generic", "Unknown", ""]:
            brand_m = (pool_df["brand_cleaned"] == q_brand).astype(float) * 0.35
        else:
            brand_m = np.zeros(len(pool_df))
        tier_m = (pool_df["price_range"] == q_tier).astype(float) * 0.15
        
        max_p = np.maximum(pool_df["discounted_price"], q_price)
        diff_p = np.abs(pool_df["discounted_price"] - q_price)
        prox_p = (1.0 - (diff_p / max_p)).clip(0.0, 1.0) * 0.15
        
        catbrand_scores_raw = (subcat_m + brand_m + tier_m + prox_p).values
        cb_min, cb_max = catbrand_scores_raw.min(), catbrand_scores_raw.max()
        norm_catbrand = (catbrand_scores_raw - cb_min) / (cb_max - cb_min + 1e-8) if cb_max > cb_min else catbrand_scores_raw

        # 3. Catalogue ranking component scores
        cat_scores_raw = self.catalogue_scores[pool_indices]
        ct_min, ct_max = cat_scores_raw.min(), cat_scores_raw.max()
        norm_catalogue = (cat_scores_raw - ct_min) / (ct_max - ct_min + 1e-8) if ct_max > ct_min else cat_scores_raw

        # 4. Hybrid score combination
        hybrid_scores = (
            w_content * norm_content + 
            w_catbrand * norm_catbrand + 
            w_cat * norm_catalogue
        )

        # Sort top candidates
        top_pool_pos = np.argsort(-hybrid_scores)[:top_k]
        
        results = []
        for pos in top_pool_pos:
            idx = pool_indices[pos]
            target_row = self.df.iloc[idx]
            h_score = float(hybrid_scores[pos])
            c_score = float(norm_content[pos])
            cb_score = float(norm_catbrand[pos])
            ct_score = float(norm_catalogue[pos])
            
            reason_str = (
                f"Hybrid Match Score: {h_score*100:.1f}% [Content: {c_score*100:.0f}% (wt {w_content*100:.0f}%), "
                f"Brand/Cat: {cb_score*100:.0f}% (wt {w_catbrand*100:.0f}%), "
                f"Catalogue: {ct_score*100:.0f}% (wt {w_cat*100:.0f}%)]. "
                f"Shares category '{target_row['primary_category']}'"
                + (f" and brand '{target_row['brand_cleaned']}'" if target_row['brand_cleaned'] != 'Generic' else '')
                + f" with ₹{target_row['discounted_price']:,.0f} price point."
            )
            
            results.append(self._format_product(idx, {
                "recommendation_score": round(h_score, 4),
                "content_score": round(c_score, 4),
                "category_brand_score": round(cb_score, 4),
                "catalogue_score": round(ct_score, 4),
                "recommendation_method": "Weighted Hybrid Recommender",
                "recommendation_reason": reason_str
            }))
            
        return results
