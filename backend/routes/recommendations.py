from flask import Blueprint, jsonify, request, current_app

recommendations_bp = Blueprint("recommendations", __name__)

@recommendations_bp.route("/api/recommendations/popular", methods=["GET"])
def get_popular_recommendations():
    """
    Returns catalogue listing ranking recommendations based on composite score:
    customer ratings, discount depth, and listing completeness.
    Query parameters:
      - limit: int (default 10, max 50)
      - category: str (optional)
      - price_range: str (optional: Budget, Mid-Range, Premium)
      - brand: str (optional)
    """
    recommender = current_app.config.get("RECOMMENDER")
    if not recommender or not recommender.is_loaded:
        return jsonify({"success": False, "error": "Recommender service not loaded"}), 503

    limit = max(1, min(50, request.args.get("limit", 10, type=int)))
    category = request.args.get("category", None)
    price_range = request.args.get("price_range", None)
    brand = request.args.get("brand", None)

    results = recommender.get_catalogue_ranking(
        top_k=limit,
        category=category,
        price_range=price_range,
        brand=brand
    )

    return jsonify({
        "success": True,
        "method": "Catalogue-Based Ranking",
        "description": "Ranked by transparent composite score of verified rating, discount depth, and catalogue completeness.",
        "filters_applied": {
            "category": category,
            "price_range": price_range,
            "brand": brand
        },
        "count": len(results),
        "recommendations": results
    }), 200

@recommendations_bp.route("/api/recommendations/content/<product_id>", methods=["GET"])
def get_content_recommendations(product_id):
    """
    Returns content-based recommendations using TF-IDF cosine similarity.
    Query parameters:
      - limit: int (default 10, max 50)
    """
    recommender = current_app.config.get("RECOMMENDER")
    if not recommender or not recommender.is_loaded:
        return jsonify({"success": False, "error": "Recommender service not loaded"}), 503

    if product_id not in recommender.id_to_idx:
        return jsonify({"success": False, "error": f"Product with ID '{product_id}' not found"}), 404

    limit = max(1, min(50, request.args.get("limit", 10, type=int)))
    query_product = recommender._format_product(recommender.id_to_idx[product_id])
    results = recommender.get_content_recommendations(product_id=product_id, top_k=limit)

    return jsonify({
        "success": True,
        "query_product": query_product,
        "method": "Content-Based Filtering (TF-IDF)",
        "description": "Discovers semantically and technically aligned products using TF-IDF Vectorizer and Cosine Similarity.",
        "count": len(results),
        "recommendations": results
    }), 200

@recommendations_bp.route("/api/recommendations/category/<product_id>", methods=["GET"])
def get_category_recommendations(product_id):
    """
    Returns recommendations based on exact category hierarchy, brand matching, and price band.
    Query parameters:
      - limit: int (default 10, max 50)
    """
    recommender = current_app.config.get("RECOMMENDER")
    if not recommender or not recommender.is_loaded:
        return jsonify({"success": False, "error": "Recommender service not loaded"}), 503

    if product_id not in recommender.id_to_idx:
        return jsonify({"success": False, "error": f"Product with ID '{product_id}' not found"}), 404

    limit = max(1, min(50, request.args.get("limit", 10, type=int)))
    query_product = recommender._format_product(recommender.id_to_idx[product_id])
    results = recommender.get_category_brand_recommendations(product_id=product_id, top_k=limit)

    return jsonify({
        "success": True,
        "query_product": query_product,
        "method": "Category & Brand Attribute Filtering",
        "description": "Recommends products sharing identical category sub-trees, matching brand family, and price proximity.",
        "count": len(results),
        "recommendations": results
    }), 200

@recommendations_bp.route("/api/recommendations/hybrid/<product_id>", methods=["GET"])
def get_hybrid_recommendations(product_id):
    """
    Returns weighted hybrid recommendations combining Content-Based (60%), Category/Brand (25%),
    and Catalogue Ranking (15%). Weights are configurable via query parameters.
    Query parameters:
      - limit: int (default 10, max 50)
      - w_content: float (default 0.60)
      - w_category_brand: float (default 0.25)
      - w_catalogue: float (default 0.15)
    """
    recommender = current_app.config.get("RECOMMENDER")
    if not recommender or not recommender.is_loaded:
        return jsonify({"success": False, "error": "Recommender service not loaded"}), 503

    if product_id not in recommender.id_to_idx:
        return jsonify({"success": False, "error": f"Product with ID '{product_id}' not found"}), 404

    limit = max(1, min(50, request.args.get("limit", 10, type=int)))
    w_content = max(0.0, request.args.get("w_content", 0.60, type=float))
    w_catbrand = max(0.0, request.args.get("w_category_brand", 0.25, type=float))
    w_catalogue = max(0.0, request.args.get("w_catalogue", 0.15, type=float))

    weights = {
        "content": w_content,
        "category_brand": w_catbrand,
        "catalogue": w_catalogue
    }

    query_product = recommender._format_product(recommender.id_to_idx[product_id])
    results = recommender.get_hybrid_recommendations(
        product_id=product_id,
        top_k=limit,
        weights=weights
    )

    return jsonify({
        "success": True,
        "query_product": query_product,
        "method": "Weighted Hybrid Recommender",
        "description": "Normalized fusion of Content-Based TF-IDF Similarity, Category & Brand Affinity, and Catalogue Ranking Score.",
        "weights_applied": {
            "content": round(w_content, 2),
            "category_brand": round(w_catbrand, 2),
            "catalogue": round(w_catalogue, 2)
        },
        "count": len(results),
        "recommendations": results
    }), 200
