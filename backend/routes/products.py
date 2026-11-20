import math
import numpy as np
import pandas as pd
from flask import Blueprint, jsonify, request, current_app

products_bp = Blueprint("products", __name__)

@products_bp.route("/api/products", methods=["GET"])
def get_products():
    """
    Paginated product catalogue with multi-attribute filtering and sorting.
    Query parameters:
      - page: int (default 1)
      - limit: int (default 12)
      - search: str (text search)
      - category: str
      - brand: str
      - price_range: str (Budget / Mid-Range / Premium)
      - min_price: float
      - max_price: float
      - sort_by: str (relevance, price_asc, price_desc, discount_desc, rating_desc)
    """
    recommender = current_app.config.get("RECOMMENDER")
    if not recommender or not recommender.is_loaded:
        return jsonify({"success": False, "error": "Recommender service not loaded"}), 503

    df = recommender.df

    # Parse query parameters with validation
    try:
        page = max(1, int(request.args.get("page", 1)))
        limit = max(1, min(100, int(request.args.get("limit", 12))))
    except ValueError:
        return jsonify({"success": False, "error": "Invalid pagination parameters"}), 400

    search = request.args.get("search", "").strip()
    category = request.args.get("category", "").strip()
    brand = request.args.get("brand", "").strip()
    price_range = request.args.get("price_range", "").strip()
    min_price = request.args.get("min_price", type=float)
    max_price = request.args.get("max_price", type=float)
    sort_by = request.args.get("sort_by", "relevance").strip()

    # Apply filters
    mask = np.ones(len(df), dtype=bool)

    if category and category.lower() != "all":
        mask &= (df["primary_category"].str.lower() == category.lower())

    if brand and brand.lower() != "all":
        mask &= (df["brand_cleaned"].str.lower() == brand.lower())

    if price_range and price_range.lower() != "all":
        mask &= (df["price_range"].str.lower() == price_range.lower())

    if min_price is not None:
        mask &= (df["discounted_price"] >= min_price)

    if max_price is not None:
        mask &= (df["discounted_price"] <= max_price)

    if search:
        search_lower = search.lower()
        search_mask = (
            df["product_name"].str.lower().str.contains(search_lower, regex=False, na=False) |
            df["brand_cleaned"].str.lower().str.contains(search_lower, regex=False, na=False) |
            df["description"].str.lower().str.contains(search_lower, regex=False, na=False)
        )
        mask &= search_mask

    filtered_df = df[mask].copy()
    total_matches = len(filtered_df)

    # Apply sorting
    if sort_by == "price_asc":
        filtered_df = filtered_df.sort_values("discounted_price", ascending=True)
    elif sort_by == "price_desc":
        filtered_df = filtered_df.sort_values("discounted_price", ascending=False)
    elif sort_by == "discount_desc":
        filtered_df = filtered_df.sort_values("discount_percentage", ascending=False)
    elif sort_by == "rating_desc":
        filtered_df = filtered_df.sort_values("rating_numeric", ascending=False)
    else:  # relevance / catalogue score
        cat_scores = recommender.catalogue_scores[filtered_df.index.to_numpy()]
        filtered_df["_sort_score"] = cat_scores
        filtered_df = filtered_df.sort_values("_sort_score", ascending=False)


    # Pagination slice
    total_pages = max(1, math.ceil(total_matches / limit))
    start_idx = (page - 1) * limit
    end_idx = start_idx + limit
    page_items_df = filtered_df.iloc[start_idx:end_idx]

    products = []
    for orig_idx in page_items_df.index:
        pos = recommender.id_to_idx.get(df.loc[orig_idx, "uniq_id"])
        if pos is not None:
            products.append(recommender._format_product(pos))

    return jsonify({
        "success": True,
        "products": products,
        "pagination": {
            "page": page,
            "limit": limit,
            "total_products": total_matches,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1
        }
    }), 200

@products_bp.route("/api/products/<product_id>", methods=["GET"])
def get_product_by_id(product_id):
    """Returns single product details by uniq_id."""
    recommender = current_app.config.get("RECOMMENDER")
    if not recommender or not recommender.is_loaded:
        return jsonify({"success": False, "error": "Recommender service not loaded"}), 503

    pos = recommender.id_to_idx.get(product_id)
    if pos is None:
        return jsonify({"success": False, "error": f"Product with ID '{product_id}' not found"}), 404

    product = recommender._format_product(pos)
    return jsonify({
        "success": True,
        "product": product
    }), 200

@products_bp.route("/api/products/search", methods=["GET"])
def search_products():
    """
    Quick search endpoint for autocomplete and header search bar.
    Query parameters:
      - q: search keyword
      - limit: int (default 10)
    """
    recommender = current_app.config.get("RECOMMENDER")
    if not recommender or not recommender.is_loaded:
        return jsonify({"success": False, "error": "Recommender service not loaded"}), 503

    query = request.args.get("q", "").strip()
    if not query:
        return jsonify({"success": True, "results": []}), 200

    limit = max(1, min(20, request.args.get("limit", 10, type=int)))
    df = recommender.df

    q_lower = query.lower()
    matches = df[
        df["product_name"].str.lower().str.contains(q_lower, regex=False, na=False) |
        df["brand_cleaned"].str.lower().str.contains(q_lower, regex=False, na=False)
    ].head(limit)

    results = []
    for orig_idx in matches.index:
        pos = recommender.id_to_idx.get(df.loc[orig_idx, "uniq_id"])
        if pos is not None:
            results.append(recommender._format_product(pos))

    return jsonify({
        "success": True,
        "query": query,
        "count": len(results),
        "results": results
    }), 200

@products_bp.route("/api/categories", methods=["GET"])
def get_categories():
    """Returns structured list of primary categories with product counts and average prices."""
    recommender = current_app.config.get("RECOMMENDER")
    if not recommender or not recommender.is_loaded:
        return jsonify({"success": False, "error": "Recommender service not loaded"}), 503

    df = recommender.df
    cat_stats = df.groupby("primary_category").agg(
        product_count=("uniq_id", "count"),
        avg_price=("discounted_price", "mean"),
        avg_discount=("discount_percentage", "mean")
    ).reset_index().sort_values("product_count", ascending=False)

    categories = [
        {
            "name": row["primary_category"],
            "count": int(row["product_count"]),
            "avg_price": round(float(row["avg_price"]), 2),
            "avg_discount": round(float(row["avg_discount"]), 2)
        }
        for _, row in cat_stats.iterrows()
    ]

    return jsonify({
        "success": True,
        "total_categories": len(categories),
        "categories": categories
    }), 200

@products_bp.route("/api/brands", methods=["GET"])
def get_brands():
    """Returns list of top brands with product counts."""
    recommender = current_app.config.get("RECOMMENDER")
    if not recommender or not recommender.is_loaded:
        return jsonify({"success": False, "error": "Recommender service not loaded"}), 503

    df = recommender.df
    top_brands = (
        df[df["brand_cleaned"] != "Generic"]
        .groupby("brand_cleaned")
        .agg(product_count=("uniq_id", "count"))
        .reset_index()
        .sort_values("product_count", ascending=False)
        .head(100)
    )

    brands = [
        {"name": row["brand_cleaned"], "count": int(row["product_count"])}
        for _, row in top_brands.iterrows()
    ]

    return jsonify({
        "success": True,
        "total_brands": len(brands),
        "brands": brands
    }), 200
