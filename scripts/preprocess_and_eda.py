import os
import ast
import re
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import joblib

# Set paths
RAW_PATH = os.path.join("data", "raw", "flipkart_com-ecommerce_sample.csv")
PROCESSED_CSV = os.path.join("data", "processed", "flipkart_cleaned.csv")
PROCESSED_JOBLIB = os.path.join("data", "processed", "flipkart_cleaned.joblib")
CHARTS_DIR = os.path.join("notebooks", "eda_charts")
os.makedirs("data/processed", exist_ok=True)
os.makedirs(CHARTS_DIR, exist_ok=True)

# -------------------------------------------------------------
# 1. LOAD DATASET
# -------------------------------------------------------------
print("Step 1: Loading raw dataset...")
df = pd.read_csv(RAW_PATH)
initial_shape = df.shape
print(f"Initial Dataset Shape: {initial_shape[0]} rows, {initial_shape[1]} columns")

# -------------------------------------------------------------
# 2. PARSE CATEGORIES & HIERARCHY
# -------------------------------------------------------------
print("\nStep 2: Parsing category tree...")
def parse_category_tree(cat_tree_str):
    if pd.isna(cat_tree_str):
        return ["Unknown"]
    try:
        parsed = ast.literal_eval(cat_tree_str)
        if isinstance(parsed, list) and len(parsed) > 0:
            parts = [re.sub(r'["\']', '', p).strip() for p in parsed[0].split(">>")]
            return [p for p in parts if p]
    except Exception:
        clean = re.sub(r'[\[\]"]', '', str(cat_tree_str))
        parts = [p.strip() for p in clean.split(">>") if p.strip()]
        if parts:
            return parts
    return ["Unknown"]

cat_lists = df["product_category_tree"].apply(parse_category_tree)
df["primary_category"] = cat_lists.apply(lambda x: x[0] if len(x) > 0 else "Unknown")
df["sub_category"] = cat_lists.apply(lambda x: x[1] if len(x) > 1 else (x[0] if len(x) > 0 else "Unknown"))
df["category_path"] = cat_lists.apply(lambda x: " > ".join(x))

# Clean common primary category anomalies (e.g. single quote or bracket artifacts)
df["primary_category"] = df["primary_category"].str.strip('"\'] ')
df.loc[df["primary_category"] == "", "primary_category"] = "Unknown"

# -------------------------------------------------------------
# 3. PARSE IMAGES & FALLBACK PLACEHOLDER
# -------------------------------------------------------------
print("Step 3: Extracting primary image URLs...")
def extract_primary_image(img_str):
    if pd.isna(img_str):
        return ""
    try:
        parsed = ast.literal_eval(img_str)
        if isinstance(parsed, list) and len(parsed) > 0:
            url = parsed[0].strip()
            # Handle possible quotes or protocol issues
            return url
    except Exception:
        match = re.search(r'http[s]?://[^\s",\]]+', str(img_str))
        if match:
            return match.group(0)
    return ""

df["primary_image"] = df["image"].apply(extract_primary_image)
# Replace missing with empty string
df["primary_image"] = df["primary_image"].fillna("")

# -------------------------------------------------------------
# 4. PARSE SPECIFICATIONS
# -------------------------------------------------------------
print("Step 4: Parsing product specifications...")
def extract_specs_text(spec_str):
    if pd.isna(spec_str):
        return ""
    try:
        pairs = re.findall(r'"key"=>"([^"]+)",\s*"value"=>"([^"]+)"', str(spec_str))
        if pairs:
            # Clean and combine key-value pairs
            clean_pairs = [f"{k.strip()}: {v.strip()}" for k, v in pairs[:15] if k and v]
            return "; ".join(clean_pairs)
    except Exception:
        pass
    return ""

df["specs_cleaned"] = df["product_specifications"].apply(extract_specs_text)

# -------------------------------------------------------------
# 5. PARSE RATINGS
# -------------------------------------------------------------
print("Step 5: Standardizing product ratings...")
def parse_numeric_rating(rating_str):
    if pd.isna(rating_str):
        return 0.0
    r_str = str(rating_str).strip()
    if r_str == "No rating available" or r_str == "" or r_str == "nan":
        return 0.0
    try:
        val = float(r_str)
        return val if (1.0 <= val <= 5.0) else 0.0
    except ValueError:
        return 0.0

df["rating_numeric"] = df["product_rating"].apply(parse_numeric_rating)
df["has_rating"] = df["rating_numeric"] > 0.0

# -------------------------------------------------------------
# 6. HANDLE MISSING VALUES & CLEAN PRICES
# -------------------------------------------------------------
print("Step 6: Handling missing values and prices...")
# Drop rows with null retail or discounted price (only 78 rows out of 20000 = 0.39%)
df_clean = df.dropna(subset=["retail_price", "discounted_price"]).copy()

# Ensure numeric prices
df_clean["retail_price"] = pd.to_numeric(df_clean["retail_price"], errors="coerce")
df_clean["discounted_price"] = pd.to_numeric(df_clean["discounted_price"], errors="coerce")

# Drop any non-numeric price rows
df_clean = df_clean.dropna(subset=["retail_price", "discounted_price"])

# Ensure no negative or zero prices
df_clean = df_clean[(df_clean["retail_price"] > 0) & (df_clean["discounted_price"] > 0)]

# If discounted_price > retail_price due to data entry inversion, cap it
df_clean.loc[df_clean["discounted_price"] > df_clean["retail_price"], "discounted_price"] = df_clean["retail_price"]

# Clean descriptions
df_clean["description"] = df_clean["description"].fillna("").astype(str).str.strip()

# -------------------------------------------------------------
# 7. STANDARDIZE BRAND NAMES
# -------------------------------------------------------------
print("Step 7: Standardizing brand names...")
def clean_brand(brand_val, product_name):
    if pd.notna(brand_val) and str(brand_val).strip() != "":
        b = str(brand_val).strip()
        # Remove unwanted punctuation
        b = re.sub(r'^[^\w]+|[^\w]+$', '', b)
        if len(b) > 1:
            return b.title()
    # If missing, try to extract first word from product_name if it looks like a brand
    if pd.notna(product_name):
        tokens = str(product_name).strip().split()
        if tokens:
            candidate = tokens[0].strip()
            # If not a generic stop word like 'Women', 'Men', 'Pack', 'The'
            if len(candidate) > 2 and candidate.isalnum() and candidate.lower() not in [
                "the", "for", "set", "pack", "combo", "women", "men", "girls", "boys", "all"
            ]:
                return candidate.title()
    return "Generic"

df_clean["brand_cleaned"] = [
    clean_brand(b, p) for b, p in zip(df_clean["brand"], df_clean["product_name"])
]

# -------------------------------------------------------------
# 8. DEDUPLICATION
# -------------------------------------------------------------
print("Step 8: Deduplicating identical product listings...")
before_dedup = len(df_clean)
df_clean = df_clean.drop_duplicates(subset=["product_name", "description", "retail_price"], keep="first")
after_dedup = len(df_clean)
print(f"Removed {before_dedup - after_dedup} duplicate listings. Remaining: {after_dedup}")

# -------------------------------------------------------------
# 9. FEATURE ENGINEERING
# -------------------------------------------------------------
print("Step 9: Feature Engineering...")
# A. Discount Amount and Percentage
df_clean["discount_amount"] = (df_clean["retail_price"] - df_clean["discounted_price"]).round(2)
df_clean["discount_percentage"] = (
    (df_clean["discount_amount"] / df_clean["retail_price"]) * 100
).round(2).clip(0.0, 100.0)

# B. Price Range Categorization
# Budget (< 500), Mid-Range (500 - 2000), Premium (>= 2000)
def categorize_price_range(price):
    if price < 500:
        return "Budget"
    elif price < 2000:
        return "Mid-Range"
    else:
        return "Premium"

df_clean["price_range"] = df_clean["discounted_price"].apply(categorize_price_range)

# C. Category & Brand Frequencies
cat_counts = df_clean["primary_category"].value_counts().to_dict()
brand_counts = df_clean["brand_cleaned"].value_counts().to_dict()
df_clean["category_freq"] = df_clean["primary_category"].map(cat_counts).fillna(1).astype(int)
df_clean["brand_freq"] = df_clean["brand_cleaned"].map(brand_counts).fillna(1).astype(int)

# D. Product Completeness Score (0 - 100)
def compute_completeness(row):
    score = 0
    # Name present & meaningful (> 5 chars)
    if len(str(row.get("product_name", ""))) > 5:
        score += 15
    # Description detailed (> 25 words -> +20, non-empty -> +10)
    desc_len = len(str(row.get("description", "")).split())
    if desc_len >= 25:
        score += 20
    elif desc_len > 0:
        score += 10
    # Brand is identified (not Generic)
    if row.get("brand_cleaned", "") not in ["Generic", "Unknown", ""]:
        score += 15
    else:
        score += 5
    # Category identified
    if row.get("primary_category", "") not in ["Unknown", ""]:
        score += 15
    # Image URL exists
    if len(str(row.get("primary_image", ""))) > 10:
        score += 15
    # Price is valid and positive
    if row.get("retail_price", 0) > 0 and row.get("discounted_price", 0) > 0:
        score += 10
    # Specifications present
    if len(str(row.get("specs_cleaned", ""))) > 10:
        score += 10
    return min(100, score)

df_clean["completeness_score"] = df_clean.apply(compute_completeness, axis=1)

# E. Combined Product Text for TF-IDF Vectorization
def create_product_text(row):
    parts = [
        str(row.get("product_name", "")),
        str(row.get("brand_cleaned", "")),
        str(row.get("primary_category", "")),
        str(row.get("sub_category", "")),
        str(row.get("description", "")),
        str(row.get("specs_cleaned", ""))
    ]
    # Clean up whitespace and non-alphanumeric noise
    text = " ".join([p for p in parts if p and p != "Unknown" and p != "Generic"])
    text = re.sub(r'[\r\n\t]+', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

df_clean["product_text"] = df_clean.apply(create_product_text, axis=1)

# -------------------------------------------------------------
# 10. SAVE CLEANED DATASET
# -------------------------------------------------------------
print("\nStep 10: Saving cleaned dataset...")
df_clean.to_csv(PROCESSED_CSV, index=False)
joblib.dump(df_clean, PROCESSED_JOBLIB, compress=3)
print(f"Cleaned dataset saved: {PROCESSED_CSV} ({os.path.getsize(PROCESSED_CSV)} bytes)")
print(f"Joblib serialized copy: {PROCESSED_JOBLIB} ({os.path.getsize(PROCESSED_JOBLIB)} bytes)")

# -------------------------------------------------------------
# 11. GENERATE EDA CHARTS (OFFICIAL BRAND PALETTE)
# -------------------------------------------------------------
print("\nStep 11: Generating EDA visualizations...")

# SujhavSathi Brand Palette
c_olive_black = "#1F2605"
c_forest_green = "#1F6521"
c_vibrant_green = "#53900F"
c_olive_yellow = "#A4A71E"
c_neon_lime = "#D6CE15"
c_off_white = "#F2F2F2"

plt.rcParams.update({
    "font.family": "sans-serif",
    "axes.edgecolor": "#46501D",
    "axes.linewidth": 1.2,
    "grid.color": "#E1E3D4",
    "grid.linestyle": "--",
    "grid.alpha": 0.5
})

# Chart 1: Top 15 Product Categories
plt.figure(figsize=(12, 6))
top_cats = df_clean["primary_category"].value_counts().head(15)
bars = plt.barh(top_cats.index[::-1], top_cats.values[::-1], color=c_forest_green, edgecolor=c_olive_black)
plt.title("Top 15 Product Categories in Flipkart Catalogue", fontsize=14, fontweight="bold", color=c_olive_black)
plt.xlabel("Number of Products", fontsize=11, fontweight="bold")
plt.grid(axis="x")
for bar in bars:
    plt.text(bar.get_width() + 40, bar.get_y() + bar.get_height()/2, f"{int(bar.get_width()):,}", 
             va="center", ha="left", fontsize=9, color=c_olive_black)
plt.tight_layout()
plt.savefig(os.path.join(CHARTS_DIR, "01_top_categories.png"), dpi=200)
plt.close()

# Chart 2: Top 15 Brands
plt.figure(figsize=(12, 6))
top_brands = df_clean[df_clean["brand_cleaned"] != "Generic"]["brand_cleaned"].value_counts().head(15)
bars = plt.barh(top_brands.index[::-1], top_brands.values[::-1], color=c_vibrant_green, edgecolor=c_olive_black)
plt.title("Top 15 Specific Brands in Catalogue (Excl. Generic)", fontsize=14, fontweight="bold", color=c_olive_black)
plt.xlabel("Number of Products", fontsize=11, fontweight="bold")
plt.grid(axis="x")
for bar in bars:
    plt.text(bar.get_width() + 10, bar.get_y() + bar.get_height()/2, f"{int(bar.get_width()):,}", 
             va="center", ha="left", fontsize=9, color=c_olive_black)
plt.tight_layout()
plt.savefig(os.path.join(CHARTS_DIR, "02_top_brands.png"), dpi=200)
plt.close()

# Chart 3: Retail vs Discounted Price Distribution (Up to 95th Percentile)
plt.figure(figsize=(11, 5))
p95 = df_clean["retail_price"].quantile(0.95)
filtered_prices = df_clean[df_clean["retail_price"] <= p95]
sns.histplot(filtered_prices["retail_price"], color=c_forest_green, label="Retail Price (MRP)", kde=True, bins=40, alpha=0.6)
sns.histplot(filtered_prices["discounted_price"], color=c_neon_lime, label="Discounted Price", kde=True, bins=40, alpha=0.6)
plt.title("Price Distribution Comparison (Truncated at 95th Percentile: ₹8,000)", fontsize=14, fontweight="bold", color=c_olive_black)
plt.xlabel("Price (₹ INR)", fontsize=11, fontweight="bold")
plt.ylabel("Catalogue Product Count", fontsize=11, fontweight="bold")
plt.legend(frameon=True, facecolor=c_off_white, edgecolor=c_olive_black)
plt.grid(True)
plt.tight_layout()
plt.savefig(os.path.join(CHARTS_DIR, "03_price_distribution.png"), dpi=200)
plt.close()

# Chart 4: Discount Percentage Distribution
plt.figure(figsize=(10, 5))
sns.histplot(df_clean["discount_percentage"], color=c_olive_yellow, kde=True, bins=30, edgecolor=c_olive_black)
plt.axvline(df_clean["discount_percentage"].median(), color=c_forest_green, linestyle="--", linewidth=2, 
            label=f"Median Discount: {df_clean['discount_percentage'].median():.1f}%")
plt.title("Distribution of Discount Percentages across Flipkart Products", fontsize=14, fontweight="bold", color=c_olive_black)
plt.xlabel("Discount Percentage (%)", fontsize=11, fontweight="bold")
plt.ylabel("Number of Products", fontsize=11, fontweight="bold")
plt.legend(frameon=True, facecolor=c_off_white, edgecolor=c_olive_black)
plt.grid(True)
plt.tight_layout()
plt.savefig(os.path.join(CHARTS_DIR, "04_discount_distribution.png"), dpi=200)
plt.close()

# Chart 5: Category-wise Average Price
plt.figure(figsize=(12, 6))
top_10_cat_names = df_clean["primary_category"].value_counts().head(10).index
cat_avg_prices = df_clean[df_clean["primary_category"].isin(top_10_cat_names)].groupby("primary_category")["discounted_price"].mean().sort_values()
bars = plt.barh(cat_avg_prices.index, cat_avg_prices.values, color=c_forest_green, edgecolor=c_olive_black)
plt.title("Average Discounted Price by Top 10 Categories", fontsize=14, fontweight="bold", color=c_olive_black)
plt.xlabel("Average Discounted Price (₹ INR)", fontsize=11, fontweight="bold")
plt.grid(axis="x")
for bar in bars:
    plt.text(bar.get_width() + 40, bar.get_y() + bar.get_height()/2, f"₹{bar.get_width():,.0f}", 
             va="center", ha="left", fontsize=9, color=c_olive_black)
plt.tight_layout()
plt.savefig(os.path.join(CHARTS_DIR, "05_category_avg_price.png"), dpi=200)
plt.close()

# Chart 6: Price Range Breakdown (Budget vs Mid-Range vs Premium)
plt.figure(figsize=(8, 5))
range_counts = df_clean["price_range"].value_counts()[["Budget", "Mid-Range", "Premium"]]
colors = [c_vibrant_green, c_forest_green, c_olive_yellow]
bars = plt.bar(range_counts.index, range_counts.values, color=colors, edgecolor=c_olive_black, width=0.55)
plt.title("Product Catalogue Distribution by Price Tier", fontsize=14, fontweight="bold", color=c_olive_black)
plt.xlabel("Price Tier", fontsize=11, fontweight="bold")
plt.ylabel("Product Count", fontsize=11, fontweight="bold")
plt.grid(axis="y")
for bar in bars:
    plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 100, 
             f"{int(bar.get_height()):,} ({bar.get_height()/len(df_clean)*100:.1f}%)", 
             ha="center", va="bottom", fontsize=10, fontweight="bold", color=c_olive_black)
plt.tight_layout()
plt.savefig(os.path.join(CHARTS_DIR, "06_price_tiers.png"), dpi=200)
plt.close()

# Chart 7: Product Completeness Score Distribution
plt.figure(figsize=(10, 5))
sns.histplot(df_clean["completeness_score"], color=c_forest_green, bins=20, edgecolor=c_olive_black)
plt.axvline(df_clean["completeness_score"].mean(), color=c_neon_lime, linestyle="--", linewidth=2.5, 
            label=f"Average Score: {df_clean['completeness_score'].mean():.1f}/100")
plt.title("Product Listing Completeness Score Distribution", fontsize=14, fontweight="bold", color=c_olive_black)
plt.xlabel("Listing Completeness Score (0 - 100)", fontsize=11, fontweight="bold")
plt.ylabel("Product Count", fontsize=11, fontweight="bold")
plt.legend(frameon=True, facecolor=c_off_white, edgecolor=c_olive_black)
plt.grid(True)
plt.tight_layout()
plt.savefig(os.path.join(CHARTS_DIR, "07_completeness_score.png"), dpi=200)
plt.close()

print("All 7 EDA visualizations successfully generated in notebooks/eda_charts/!")

# -------------------------------------------------------------
# 12. PRINT FINAL SUMMARY STATS
# -------------------------------------------------------------
summary_stats = {
    "total_raw_rows": int(initial_shape[0]),
    "cleaned_rows": int(len(df_clean)),
    "deduplicated_removed": int(before_dedup - after_dedup),
    "unique_categories": int(df_clean["primary_category"].nunique()),
    "unique_brands": int(df_clean["brand_cleaned"].nunique()),
    "avg_retail_price": float(round(df_clean["retail_price"].mean(), 2)),
    "avg_discounted_price": float(round(df_clean["discounted_price"].mean(), 2)),
    "avg_discount_percentage": float(round(df_clean["discount_percentage"].mean(), 2)),
    "median_discount_percentage": float(round(df_clean["discount_percentage"].median(), 2)),
    "budget_products": int((df_clean["price_range"] == "Budget").sum()),
    "mid_range_products": int((df_clean["price_range"] == "Mid-Range").sum()),
    "premium_products": int((df_clean["price_range"] == "Premium").sum()),
    "avg_completeness_score": float(round(df_clean["completeness_score"].mean(), 2)),
    "rated_products_count": int(df_clean["has_rating"].sum()),
    "rated_products_pct": float(round(df_clean["has_rating"].mean() * 100, 2))
}

with open(os.path.join("data", "processed", "eda_summary.json"), "w") as f:
    json.dump(summary_stats, f, indent=4)

print("\n--- FINAL EDA SUMMARY METRICS ---")
for k, v in summary_stats.items():
    print(f"{k}: {v}")
