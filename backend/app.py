import os
import sys
from flask import Flask, jsonify
from flask_cors import CORS

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.models.recommender import SujhavRecommender
from backend.routes.analytics import analytics_bp
from backend.routes.products import products_bp
from backend.routes.recommendations import recommendations_bp

def create_app():
    """Application factory for Sujhav साथी Flask REST API."""
    app = Flask(__name__)
    
    # Enable CORS for React frontend (localhost:3000, localhost:5173, etc.)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Load and cache recommendation models
    artifacts_dir = os.path.join(os.path.dirname(__file__), "artifacts")
    recommender = SujhavRecommender(artifacts_dir=artifacts_dir)
    recommender.load_artifacts()
    app.config["RECOMMENDER"] = recommender

    # Register modular blueprints
    app.register_blueprint(analytics_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(recommendations_bp)

    # Global Error Handlers
    @app.errorhandler(404)
    def handle_not_found(e):
        return jsonify({
            "success": False,
            "error": "The requested API endpoint or resource was not found",
            "status_code": 404
        }), 404

    @app.errorhandler(400)
    def handle_bad_request(e):
        return jsonify({
            "success": False,
            "error": "Bad request. Please verify input parameters",
            "status_code": 400
        }), 400

    @app.errorhandler(500)
    def handle_server_error(e):
        return jsonify({
            "success": False,
            "error": "An internal server error occurred while processing the request",
            "status_code": 500
        }), 500

    return app

if __name__ == "__main__":
    app = create_app()
    port = int(os.environ.get("PORT", 5000))
    print(f"\n=======================================================")
    print(f"  Sujhav साथी API Server listening on port {port}")
    print(f"  Health Check: http://localhost:{port}/api/health")
    print(f"  Dashboard:    http://localhost:{port}/api/dashboard")
    print(f"=======================================================\n")
    app.run(host="0.0.0.0", port=port, debug=False)
