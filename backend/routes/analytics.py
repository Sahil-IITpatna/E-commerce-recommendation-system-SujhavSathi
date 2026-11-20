import os
import json
from flask import Blueprint, jsonify, current_app

analytics_bp = Blueprint("analytics", __name__)

@analytics_bp.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint to verify backend operational status."""
    recommender = current_app.config.get("RECOMMENDER")
    is_ready = recommender is not None and recommender.is_loaded
    return jsonify({
        "status": "healthy" if is_ready else "initializing",
        "service": "SujhavSathi Flipkart Recommendation API",
        "version": "1.0.0",
        "dataset_products": len(recommender.df) if is_ready else 0,
        "models_ready": is_ready
    }), 200

@analytics_bp.route("/api/dashboard", methods=["GET"])
def get_dashboard_data():
    """
    Returns high-level KPI cards and aggregated chart data for the React dashboard.
    """
    recommender = current_app.config.get("RECOMMENDER")
    if not recommender or not recommender.is_loaded:
        return jsonify({"success": False, "error": "Recommender service not loaded"}), 503

    df = recommender.df

    # 1. KPI Metrics
    total_products = len(df)
    total_categories = int(df["primary_category"].nunique())
    total_brands = int(df["brand_cleaned"].nunique())
    avg_price = float(round(df["discounted_price"].mean(), 2))
    avg_discount = float(round(df["discount_percentage"].mean(), 2))

    # 2. Category Distribution (Top 8)
    top_cats = df["primary_category"].value_counts().head(8)
    cat_distribution = [{"name": cat, "count": int(count)} for cat, count in top_cats.items()]

    # 3. Brand Distribution (Top 8, excluding Generic)
    top_brands = df[df["brand_cleaned"] != "Generic"]["brand_cleaned"].value_counts().head(8)
    brand_distribution = [{"name": brand, "count": int(count)} for brand, count in top_brands.items()]

    # 4. Price Tier Distribution
    price_tiers = df["price_range"].value_counts()
    price_distribution = [
        {"tier": "Budget (< ₹500)", "count": int(price_tiers.get("Budget", 0))},
        {"tier": "Mid-Range (₹500-2K)", "count": int(price_tiers.get("Mid-Range", 0))},
        {"tier": "Premium (≥ ₹2K)", "count": int(price_tiers.get("Premium", 0))}
    ]

    # 5. Discount Bins Distribution
    bins = [0, 20, 40, 60, 80, 100]
    labels = ["0-20%", "20-40%", "40-60%", "60-80%", "80-100%"]
    discount_binned = pd_cut_binned = pd_cut(df["discount_percentage"], bins=bins, labels=labels)
    discount_distribution = [
        {"range": label, "count": int(discount_binned.get(label, 0))} for label in labels
    ]

    # 6. Category-wise Average Price (Top 8 categories)
    cat_avg_prices = (
        df[df["primary_category"].isin(top_cats.index)]
        .groupby("primary_category")["discounted_price"]
        .mean()
        .round(2)
        .sort_values(ascending=False)
    )
    category_avg_price = [
        {"category": cat, "avg_price": float(avg_p)} for cat, avg_p in cat_avg_prices.items()
    ]

    # 7. Model Evaluation Comparison from saved artifact
    eval_metrics_path = os.path.join(recommender.artifacts_dir, "evaluation_metrics.json")
    evaluation_data = []
    if os.path.exists(eval_metrics_path):
        with open(eval_metrics_path, "r") as f:
            eval_payload = json.load(f)
            evaluation_data = eval_payload.get("metrics", [])

    return jsonify({
        "success": True,
        "kpis": {
            "total_products": total_products,
            "total_categories": total_categories,
            "total_brands": total_brands,
            "avg_price": avg_price,
            "avg_discount": avg_discount
        },
        "charts": {
            "category_distribution": cat_distribution,
            "brand_distribution": brand_distribution,
            "price_distribution": price_distribution,
            "discount_distribution": discount_distribution,
            "category_avg_price": category_avg_price,
            "model_evaluation": evaluation_data
        }
    }), 200

def pd_cut(series, bins, labels):
    """Simple histogram binning helper."""
    import pandas as pd
    binned = pd.cut(series, bins=bins, labels=labels, include_lowest=True)
    return binned.value_counts().to_dict()

@analytics_bp.route("/api/analytics", methods=["GET"])
def get_analytics():
    """Detailed analytics breakdown."""
    return get_dashboard_data()

@analytics_bp.route("/api/model/evaluation", methods=["GET"])
def get_model_evaluation():
    """
    Returns exact calculated recommendation evaluation metrics (Precision@K, Recall@K, NDCG@K).
    """
    recommender = current_app.config.get("RECOMMENDER")
    if not recommender or not recommender.is_loaded:
        return jsonify({"success": False, "error": "Recommender service not loaded"}), 503

    eval_metrics_path = os.path.join(recommender.artifacts_dir, "evaluation_metrics.json")
    if not os.path.exists(eval_metrics_path):
        return jsonify({"success": False, "error": "Evaluation metrics artifact not found"}), 404

    with open(eval_metrics_path, "r") as f:
        data = json.load(f)

    return jsonify({
        "success": True,
        "data": data
    }), 200
