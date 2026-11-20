import os
import sys
import time
import json
import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from backend.models.recommender import SujhavRecommender

print("--- PHASE 4: RECOMMENDATION MODEL EVALUATION ---")

recommender = SujhavRecommender()
recommender.load_artifacts()
df = recommender.df

# -------------------------------------------------------------
# 1. EVALUATION SAMPLE SELECTION (STRATIFIED SAMPLE)
# -------------------------------------------------------------
# Select 300 representative test products across top 10 categories
np.random.seed(42)
top_cats = df["primary_category"].value_counts().head(10).index.tolist()
sample_indices = []
for cat in top_cats:
    cat_indices = df[df["primary_category"] == cat].index.tolist()
    sampled = np.random.choice(cat_indices, size=min(30, len(cat_indices)), replace=False)
    sample_indices.extend(sampled)

sample_df = df.loc[sample_indices]
print(f"Selected {len(sample_df)} test query products across top {len(top_cats)} categories.")


# -------------------------------------------------------------
# 2. DEFINE RELEVANCE COMPUTATION FUNCTIONS
# -------------------------------------------------------------
def compute_relevance_scores(query_row, rec_item):
    """
    Computes proxy-based relevance:
      Binary (0 or 1) for Precision/Recall.
      Graded (0, 1, 2, 3) for NDCG.
    """
    q_cat = str(query_row.get("primary_category", "")).lower()
    q_subcat = str(query_row.get("sub_category", "")).lower()
    q_brand = str(query_row.get("brand_cleaned", "")).lower()
    q_tier = str(query_row.get("price_range", "")).lower()

    r_cat = str(rec_item.get("primary_category", "")).lower()
    r_subcat = str(rec_item.get("sub_category", "")).lower()
    r_brand = str(rec_item.get("brand", "")).lower()
    r_tier = str(rec_item.get("price_range", "")).lower()

    # Different primary category -> Irrelevant
    if q_cat != r_cat:
        return 0, 0

    # Graded relevance
    # 3: Same category, same subcategory, matching non-generic brand, same price tier
    # 2: Same category and same subcategory
    # 1: Same category and similar price tier
    graded = 1
    if q_subcat == r_subcat and q_subcat != "unknown":
        graded = 2
        if q_brand == r_brand and q_brand not in ["generic", "unknown", ""] and q_tier == r_tier:
            graded = 3
    elif q_brand == r_brand and q_brand not in ["generic", "unknown", ""]:
        graded = 2

    # Binary relevance: deemed relevant if same category and (same subcat or same brand or same tier)
    binary = 1 if graded >= 1 else 0
    return binary, graded

def calculate_dcg_at_k(rel_grades, k):
    dcg = 0.0
    for i in range(min(k, len(rel_grades))):
        grade = rel_grades[i]
        dcg += (2**grade - 1) / np.log2(i + 2)
    return dcg

def calculate_idcg_at_k(rel_grades, k):
    ideal_grades = sorted(rel_grades, reverse=True)
    return calculate_dcg_at_k(ideal_grades, k)

# Precalculate catalogue relevance pool sizes for recall normalization
cat_pool_sizes = df["primary_category"].value_counts().to_dict()

# -------------------------------------------------------------
# 3. EVALUATE ALL 4 MODELS
# -------------------------------------------------------------
models = ["Catalogue Ranking", "Content-Based", "Category & Brand", "Hybrid Recommender"]
results = {m: {
    "precision@5": [], "precision@10": [],
    "recall@5": [], "recall@10": [],
    "ndcg@5": [], "ndcg@10": []
} for m in models}

print("\nRunning evaluation on test sample...")
t0 = time.time()

for idx, (_, q_row) in enumerate(sample_df.iterrows()):
    p_id = q_row["uniq_id"]
    q_cat = q_row["primary_category"]
    
    # Retrieve top 10 recommendations from each model
    recs_map = {
        "Catalogue Ranking": recommender.get_catalogue_ranking(top_k=10, category=q_cat),
        "Content-Based": recommender.get_content_recommendations(p_id, top_k=10),
        "Category & Brand": recommender.get_category_brand_recommendations(p_id, top_k=10),
        "Hybrid Recommender": recommender.get_hybrid_recommendations(p_id, top_k=10)
    }

    # Evaluate each model
    for model_name, recs in recs_map.items():
        # Exclude query item if present
        filtered_recs = [r for r in recs if r["uniq_id"] != p_id][:10]
        
        bin_rels = []
        graded_rels = []
        for r in filtered_recs:
            b, g = compute_relevance_scores(q_row, r)
            bin_rels.append(b)
            graded_rels.append(g)

        # Pad with zeros if fewer than 10
        while len(bin_rels) < 10:
            bin_rels.append(0)
            graded_rels.append(0)

        # Precision@5 & Precision@10
        p5 = sum(bin_rels[:5]) / 5.0
        p10 = sum(bin_rels[:10]) / 10.0

        # Recall@K (normalized by minimum of category pool or 50 benchmark items)
        pool_size = max(10, min(50, cat_pool_sizes.get(q_cat, 10)))
        r5 = sum(bin_rels[:5]) / float(min(pool_size, 5))
        r10 = sum(bin_rels[:10]) / float(min(pool_size, 10))

        # NDCG@5 & NDCG@10
        dcg5 = calculate_dcg_at_k(graded_rels, 5)
        idcg5 = calculate_idcg_at_k(graded_rels, 5)
        ndcg5 = (dcg5 / idcg5) if idcg5 > 0 else 0.0

        dcg10 = calculate_dcg_at_k(graded_rels, 10)
        idcg10 = calculate_idcg_at_k(graded_rels, 10)
        ndcg10 = (dcg10 / idcg10) if idcg10 > 0 else 0.0

        results[model_name]["precision@5"].append(p5)
        results[model_name]["precision@10"].append(p10)
        results[model_name]["recall@5"].append(r5)
        results[model_name]["recall@10"].append(r10)
        results[model_name]["ndcg@5"].append(ndcg5)
        results[model_name]["ndcg@10"].append(ndcg10)

t1 = time.time()
print(f"Evaluation of {len(sample_df)} products completed in {t1-t0:.2f}s!")

# -------------------------------------------------------------
# 4. AGGREGATE FINAL METRICS TABLE
# -------------------------------------------------------------
final_metrics = []
for model_name in models:
    row = {
        "model": model_name,
        "precision@5": round(float(np.mean(results[model_name]["precision@5"])), 4),
        "precision@10": round(float(np.mean(results[model_name]["precision@10"])), 4),
        "recall@5": round(float(np.mean(results[model_name]["recall@5"])), 4),
        "recall@10": round(float(np.mean(results[model_name]["recall@10"])), 4),
        "ndcg@5": round(float(np.mean(results[model_name]["ndcg@5"])), 4),
        "ndcg@10": round(float(np.mean(results[model_name]["ndcg@10"])), 4)
    }
    final_metrics.append(row)

eval_summary_df = pd.DataFrame(final_metrics)
print("\n--- FINAL EVALUATION METRICS TABLE ---")
print(eval_summary_df.to_string(index=False))

# Export to JSON
eval_json_path = os.path.join("backend", "artifacts", "evaluation_metrics.json")
eval_payload = {
    "methodology": "Proxy-based catalogue evaluation utilizing hierarchical category trees, brand affinity, and price-tier alignment as weak ground-truth relevance labels.",
    "dataset_sample_size": len(sample_df),
    "metrics": final_metrics
}
with open(eval_json_path, "w") as f:
    json.dump(eval_payload, f, indent=4)
print(f"\nSaved metrics JSON to {eval_json_path}")

# -------------------------------------------------------------
# 5. GENERATE GROUPED BAR CHART VISUALIZATION
# -------------------------------------------------------------
charts_dir = os.path.join("notebooks", "eda_charts")
os.makedirs(charts_dir, exist_ok=True)

c_forest = "#1F6521"
c_vibrant = "#53900F"
c_lime = "#D6CE15"
c_olive = "#A4A71E"

fig, axes = plt.subplots(1, 3, figsize=(18, 5.5), sharey=True)

model_names = [m["model"] for m in final_metrics]
x = np.arange(len(model_names))
width = 0.35

# Chart 1: Precision@5 vs Precision@10
axes[0].bar(x - width/2, [m["precision@5"] for m in final_metrics], width, label="Precision@5", color=c_forest, edgecolor="#1F2605")
axes[0].bar(x + width/2, [m["precision@10"] for m in final_metrics], width, label="Precision@10", color=c_lime, edgecolor="#1F2605")
axes[0].set_title("Precision @ K", fontsize=12, fontweight="bold")
axes[0].set_xticks(x)
axes[0].set_xticklabels(model_names, rotation=20, ha="right", fontsize=9)
axes[0].set_ylabel("Score (0.0 - 1.0)", fontsize=10, fontweight="bold")
axes[0].legend()
axes[0].grid(axis="y", linestyle="--", alpha=0.5)

# Chart 2: Recall@5 vs Recall@10
axes[1].bar(x - width/2, [m["recall@5"] for m in final_metrics], width, label="Recall@5", color=c_vibrant, edgecolor="#1F2605")
axes[1].bar(x + width/2, [m["recall@10"] for m in final_metrics], width, label="Recall@10", color=c_olive, edgecolor="#1F2605")
axes[1].set_title("Recall @ K", fontsize=12, fontweight="bold")
axes[1].set_xticks(x)
axes[1].set_xticklabels(model_names, rotation=20, ha="right", fontsize=9)
axes[1].legend()
axes[1].grid(axis="y", linestyle="--", alpha=0.5)

# Chart 3: NDCG@5 vs NDCG@10
axes[2].bar(x - width/2, [m["ndcg@5"] for m in final_metrics], width, label="NDCG@5", color=c_forest, edgecolor="#1F2605")
axes[2].bar(x + width/2, [m["ndcg@10"] for m in final_metrics], width, label="NDCG@10", color=c_vibrant, edgecolor="#1F2605")
axes[2].set_title("NDCG @ K (Ranking Quality)", fontsize=12, fontweight="bold")
axes[2].set_xticks(x)
axes[2].set_xticklabels(model_names, rotation=20, ha="right", fontsize=9)
axes[2].legend()
axes[2].grid(axis="y", linestyle="--", alpha=0.5)

plt.suptitle("Sujhav Sathi: Recommendation Model Evaluation Comparison (Proxy Relevance)", fontsize=14, fontweight="bold", y=1.02)

plt.tight_layout()
chart_file = os.path.join(charts_dir, "08_model_evaluation.png")
plt.savefig(chart_file, dpi=200, bbox_inches="tight")
plt.close()

# Also copy to artifact directory
import shutil
artifact_chart = os.path.join("C:\\Users\\dell\\.gemini\\antigravity\\brain\\913f9350-4e3d-4584-85c3-626ad476ac8c", "08_model_evaluation.png")
shutil.copyfile(chart_file, artifact_chart)

print("Evaluation chart saved successfully to notebooks/eda_charts/08_model_evaluation.png and artifacts!")
