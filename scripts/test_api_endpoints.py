import os
import sys
import json
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from backend.app import create_app

class FlaskAPITestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print("\n--- INITIALIZING FLASK TEST CLIENT ---")
        cls.app = create_app()
        cls.client = cls.app.test_client()
        cls.test_product_id = cls.app.config["RECOMMENDER"].df.iloc[0]["uniq_id"]
        print(f"Sample test product ID: {cls.test_product_id}")

    def test_01_health(self):
        res = self.client.get("/api/health")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["status"], "healthy")
        self.assertEqual(data["dataset_products"], 17665)
        print("✓ /api/health passed")

    def test_02_dashboard(self):
        res = self.client.get("/api/dashboard")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertIn("kpis", data)
        self.assertEqual(data["kpis"]["total_products"], 17665)
        self.assertIn("charts", data)
        self.assertIn("category_distribution", data["charts"])
        self.assertIn("brand_distribution", data["charts"])
        self.assertIn("price_distribution", data["charts"])
        self.assertIn("discount_distribution", data["charts"])
        self.assertIn("category_avg_price", data["charts"])
        self.assertIn("model_evaluation", data["charts"])
        print("✓ /api/dashboard passed")

    def test_03_products_pagination(self):
        res = self.client.get("/api/products?page=1&limit=6")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertEqual(len(data["products"]), 6)
        self.assertEqual(data["pagination"]["page"], 1)
        self.assertEqual(data["pagination"]["limit"], 6)
        self.assertGreater(data["pagination"]["total_pages"], 1000)
        print("✓ /api/products pagination passed")

    def test_04_products_filtering(self):
        res = self.client.get("/api/products?category=Clothing&price_range=Budget&limit=5")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertGreater(len(data["products"]), 0)
        for p in data["products"]:
            self.assertEqual(p["primary_category"], "Clothing")
            self.assertEqual(p["price_range"], "Budget")
        print("✓ /api/products category & price filters passed")

    def test_05_product_by_id(self):
        # Valid ID
        res = self.client.get(f"/api/products/{self.test_product_id}")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertEqual(data["product"]["uniq_id"], self.test_product_id)

        # Invalid ID
        res_invalid = self.client.get("/api/products/invalid_id_12345")
        self.assertEqual(res_invalid.status_code, 404)
        print("✓ /api/products/<product_id> (valid & 404) passed")

    def test_06_products_search(self):
        res = self.client.get("/api/products/search?q=Alisha&limit=5")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertGreater(len(data["results"]), 0)
        print("✓ /api/products/search passed")

    def test_07_categories_and_brands(self):
        res_cat = self.client.get("/api/categories")
        self.assertEqual(res_cat.status_code, 200)
        data_cat = res_cat.get_json()
        self.assertTrue(data_cat["success"])
        self.assertEqual(data_cat["total_categories"], 262)

        res_brand = self.client.get("/api/brands")
        self.assertEqual(res_brand.status_code, 200)
        data_brand = res_brand.get_json()
        self.assertTrue(data_brand["success"])
        self.assertGreater(data_brand["total_brands"], 50)
        print("✓ /api/categories & /api/brands passed")

    def test_08_popular_recommendations(self):
        res = self.client.get("/api/recommendations/popular?limit=5&category=Clothing")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertEqual(len(data["recommendations"]), 5)
        self.assertEqual(data["method"], "Catalogue-Based Ranking")
        print("✓ /api/recommendations/popular passed")

    def test_09_content_recommendations(self):
        res = self.client.get(f"/api/recommendations/content/{self.test_product_id}?limit=4")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertEqual(len(data["recommendations"]), 4)
        # Verify self is excluded
        rec_ids = [r["uniq_id"] for r in data["recommendations"]]
        self.assertNotIn(self.test_product_id, rec_ids)
        print("✓ /api/recommendations/content/<id> passed")

    def test_10_category_recommendations(self):
        res = self.client.get(f"/api/recommendations/category/{self.test_product_id}?limit=4")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertEqual(len(data["recommendations"]), 4)
        print("✓ /api/recommendations/category/<id> passed")

    def test_11_hybrid_recommendations(self):
        res = self.client.get(
            f"/api/recommendations/hybrid/{self.test_product_id}?limit=4&w_content=0.5&w_category_brand=0.3&w_catalogue=0.2"
        )
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertEqual(len(data["recommendations"]), 4)
        for r in data["recommendations"]:
            self.assertIn("content_score", r)
            self.assertIn("category_brand_score", r)
            self.assertIn("catalogue_score", r)
            self.assertIn("recommendation_reason", r)
        print("✓ /api/recommendations/hybrid/<id> passed")

    def test_12_model_evaluation(self):
        res = self.client.get("/api/model/evaluation")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertIn("data", data)
        self.assertEqual(len(data["data"]["metrics"]), 4)
        print("✓ /api/model/evaluation passed")

    def test_13_not_found_error(self):
        res = self.client.get("/api/non_existent_route")
        self.assertEqual(res.status_code, 404)
        data = res.get_json()
        self.assertFalse(data["success"])
        print("✓ 404 error handler passed")

if __name__ == "__main__":
    unittest.main()
