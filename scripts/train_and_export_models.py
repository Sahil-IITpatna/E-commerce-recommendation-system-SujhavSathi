import os
import sys
import time
import joblib
import numpy as np
import pandas as pd

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

DATA_PATH = os.path.join("data", "processed", "flipkart_cleaned.joblib")
ARTIFACTS_DIR = os.path.join("backend", "artifacts")
os.makedirs(ARTIFACTS_DIR, exist_ok=True)

print("--- PHASE 3: RECOMMENDATION MODEL TRAINING & SERIALIZATION ---")

# 1. Load dataset
print("Loading cleaned dataset...")
df = joblib.load(DATA_PATH)
n_products = len(df)
print(f"Loaded {n_products} products.")

# 2. Compute Catalogue Ranking Scores
print("\nComputing Catalogue Ranking Scores...")
# Rating score: if rated, rating / 5.0; if unrated, median prior baseline 0.50
rating_norm = np.where(df["has_rating"], df["rating_numeric"] / 5.0, 0.50)
discount_norm = (df["discount_percentage"] / 100.0).clip(0.0, 1.0).values
completeness_norm = (df["completeness_score"] / 100.0).clip(0.0, 1.0).values

# Transparent composite formula:
catalogue_scores = (
    0.40 * rating_norm + 
    0.35 * discount_norm + 
    0.25 * completeness_norm
).astype(np.float32)

print(f"Catalogue scores computed. Mean: {catalogue_scores.mean():.4f}, Min: {catalogue_scores.min():.4f}, Max: {catalogue_scores.max():.4f}")

# 3. Fit TF-IDF Vectorizer
print("\nFitting TF-IDF Vectorizer on composite product text...")
t0 = time.time()
tfidf = TfidfVectorizer(
    max_features=10000,
    ngram_range=(1, 2),
    sublinear_tf=True,
    stop_words="english"
)
tfidf_matrix = tfidf.fit_transform(df["product_text"])
t1 = time.time()
print(f"TF-IDF Matrix fitted in {t1-t0:.2f}s with shape: {tfidf_matrix.shape}")

# 4. Precompute Top-50 Content Neighbors
print("\nPrecomputing Top-50 Content-Based Neighbors in Batches...")
t0 = time.time()
batch_size = 1000
top_k_precompute = 50

top50_indices = np.zeros((n_products, top_k_precompute), dtype=np.int32)
top50_scores = np.zeros((n_products, top_k_precompute), dtype=np.float32)

for start_idx in range(0, n_products, batch_size):
    end_idx = min(start_idx + batch_size, n_products)
    block = tfidf_matrix[start_idx:end_idx]
    # Matrix product (block_size x n_products)
    sim_block = linear_kernel(block, tfidf_matrix)
    
    # Exclude self by setting diagonal / self similarity to -1
    for i in range(end_idx - start_idx):
        sim_block[i, start_idx + i] = -1.0
        
    # Get top 50 for each row in block
    part_idx = np.argpartition(-sim_block, top_k_precompute, axis=1)[:, :top_k_precompute]
    for row_pos in range(end_idx - start_idx):
        row_cands = part_idx[row_pos]
        row_scores = sim_block[row_pos, row_cands]
        sort_order = np.argsort(-row_scores)
        top50_indices[start_idx + row_pos] = row_cands[sort_order]
        top50_scores[start_idx + row_pos] = row_scores[sort_order]
        
    print(f"  Processed {end_idx}/{n_products} products ({(end_idx/n_products)*100:.1f}%)...")

t1 = time.time()
print(f"All top-50 neighbors precomputed in {t1-t0:.2f}s!")

# 5. Export Artifacts
print("\nExporting model artifacts to backend/artifacts/...")
catalogue_dest = os.path.join(ARTIFACTS_DIR, "flipkart_catalogue.joblib")
joblib.dump(df, catalogue_dest, compress=3)

tfidf_dest = os.path.join(ARTIFACTS_DIR, "tfidf_model.joblib")
joblib.dump({"vectorizer": tfidf, "matrix": tfidf_matrix}, tfidf_dest, compress=3)

meta_dest = os.path.join(ARTIFACTS_DIR, "metadata.joblib")
metadata = {
    "catalogue_scores": catalogue_scores,
    "categories": sorted(df["primary_category"].unique().tolist()),
    "brands": sorted(df["brand_cleaned"].unique().tolist()),
    "total_products": n_products,
    "feature_names_count": len(tfidf.get_feature_names_out())
}
joblib.dump(metadata, meta_dest, compress=3)

top50_dest = os.path.join(ARTIFACTS_DIR, "content_top50.joblib")
joblib.dump({"indices": top50_indices, "scores": top50_scores}, top50_dest, compress=3)

print("All artifacts successfully saved:")
for f in os.listdir(ARTIFACTS_DIR):
    f_path = os.path.join(ARTIFACTS_DIR, f)
    print(f"  - {f}: {os.path.getsize(f_path):,} bytes")

# 6. Test with Real Product Records
print("\n--- VALIDATION TESTS WITH REAL FLIPKART PRODUCTS ---")
from backend.models.recommender import SujhavRecommender

recommender = SujhavRecommender(artifacts_dir=ARTIFACTS_DIR)
recommender.load_artifacts()

test_cases = [
    ("Alisha Cycling Shorts (Clothing)", df[df["primary_category"] == "Clothing"].iloc[0]["uniq_id"]),
    ("FabHomeDecor Sofa (Furniture)", df[df["primary_category"].str.contains("Furniture", case=False, na=False)].iloc[0]["uniq_id"]),
    ("AW Bellies Footwear (Footwear)", df[df["primary_category"] == "Footwear"].iloc[0]["uniq_id"]),
    ("Mobiles & Accessories Item", df[df["primary_category"].str.contains("Mobile", case=False, na=False)].iloc[0]["uniq_id"])
]

for label, p_id in test_cases:
    query_item = recommender.df[recommender.df["uniq_id"] == p_id].iloc[0]
    print(f"\n========================================================")
    print(f"TEST QUERY: [{label}]")
    print(f"Title: {query_item['product_name']}")
    print(f"Category: {query_item['primary_category']} > {query_item['sub_category']}")
    print(f"Brand: {query_item['brand_cleaned']} | Price: ₹{query_item['discounted_price']} (MRP: ₹{query_item['retail_price']})")
    print(f"========================================================")
    
    # 1. Content Recommendations
    content_recs = recommender.get_content_recommendations(p_id, top_k=3)
    print("  [Algorithm 2: Content-Based Filtering (Top 3)]")
    for r in content_recs:
        print(f"    * {r['product_name']} | Sim: {r['recommendation_score']:.4f} | Brand: {r['brand']} | ₹{r['discounted_price']}")
        print(f"      Reason: {r['recommendation_reason']}")
        
    # 2. Category & Brand Recommendations
    cat_recs = recommender.get_category_brand_recommendations(p_id, top_k=3)
    print("  [Algorithm 3: Category & Brand Recommendations (Top 3)]")
    for r in cat_recs:
        print(f"    * {r['product_name']} | Match: {r['recommendation_score']:.4f} | Brand: {r['brand']} | ₹{r['discounted_price']}")
        print(f"      Reason: {r['recommendation_reason']}")
        
    # 3. Hybrid Recommendations
    hybrid_recs = recommender.get_hybrid_recommendations(p_id, top_k=3)
    print("  [Algorithm 4: Weighted Hybrid Recommendations (Top 3)]")
    for r in hybrid_recs:
        print(f"    * {r['product_name']} | Hybrid Score: {r['recommendation_score']:.4f} | ₹{r['discounted_price']}")
        print(f"      Reason: {r['recommendation_reason']}")

# Test Catalogue Ranking independently
print("\n========================================================")
print("TEST: Algorithm 1 - Catalogue Listing Ranking (Top 3 in Footwear, Budget)")
cat_rank_recs = recommender.get_catalogue_ranking(top_k=3, category="Footwear", price_range="Budget")
for r in cat_rank_recs:
    print(f"  * {r['product_name']} | Listing Score: {r['recommendation_score']:.4f} | Brand: {r['brand']} | ₹{r['discounted_price']}")
    print(f"    Reason: {r['recommendation_reason']}")
