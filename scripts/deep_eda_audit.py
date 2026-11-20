import pandas as pd
import numpy as np
import re
import ast

df = pd.read_csv("data/raw/flipkart_com-ecommerce_sample.csv")

print("--- PRICE ANOMALY AUDIT ---")
print(f"Total rows: {len(df)}")
null_prices = df[df["retail_price"].isnull() | df["discounted_price"].isnull()]
print(f"Rows with null retail or discounted price: {len(null_prices)}")

valid_prices = df.dropna(subset=["retail_price", "discounted_price"]).copy()
print(f"Retail price <= 0: {(valid_prices['retail_price'] <= 0).sum()}")
print(f"Discounted price <= 0: {(valid_prices['discounted_price'] <= 0).sum()}")

invalid_discount = valid_prices[valid_prices["discounted_price"] > valid_prices["retail_price"]]
print(f"Discounted price > Retail price: {len(invalid_discount)}")
if len(invalid_discount) > 0:
    print(invalid_discount[["product_name", "retail_price", "discounted_price"]].head(5))

print("\n--- CATEGORY TREE PARSING ---")
def extract_categories(cat_tree):
    if pd.isna(cat_tree):
        return []
    try:
        # It's usually formatted as ["A >> B >> C"]
        parsed = ast.literal_eval(cat_tree)
        if isinstance(parsed, list) and len(parsed) > 0:
            parts = [p.strip() for p in parsed[0].split(">>")]
            return parts
    except:
        # Fallback regex
        clean = re.sub(r'[\[\]"]', '', str(cat_tree))
        return [p.strip() for p in clean.split(">>") if p.strip()]
    return []

sample_cats = df["product_category_tree"].apply(extract_categories)
primary_cats = sample_cats.apply(lambda x: x[0] if len(x) > 0 else "Unknown")
secondary_cats = sample_cats.apply(lambda x: x[1] if len(x) > 1 else "Unknown")

print("Top 15 Primary Categories:")
print(primary_cats.value_counts().head(15))

print("\n--- BRAND EXTRACTION & CLEANING ---")
print(f"Missing brands: {df['brand'].isnull().sum()} ({df['brand'].isnull().mean()*100:.2f}%)")
# Can brand be inferred from product_name?
# e.g., 'Alisha Solid...' -> 'Alisha'
print("Sample product names where brand is missing:")
missing_brand_sample = df[df['brand'].isnull()][['product_name']].head(10)
for idx, r in missing_brand_sample.iterrows():
    print(f"  - {r['product_name']}")

print("\n--- IMAGE EXTRACTION ---")
def extract_primary_image(img_str):
    if pd.isna(img_str):
        return ""
    try:
        parsed = ast.literal_eval(img_str)
        if isinstance(parsed, list) and len(parsed) > 0:
            return parsed[0]
    except:
        match = re.search(r'http[s]?://[^\s",\]]+', str(img_str))
        if match:
            return match.group(0)
    return ""

img_samples = df["image"].apply(extract_primary_image)
print(f"Extracted valid primary images: {(img_samples != '').sum()} / {len(df)}")
print("Sample primary image URL:")
print(img_samples.iloc[0])

print("\n--- SPECIFICATIONS PARSING ---")
def extract_specs_text(spec_str):
    if pd.isna(spec_str):
        return ""
    # Usually contains {"product_specification"=>[{"key"=>"...", "value"=>"..."}]}
    # We can extract key: value pairs using regex
    pairs = re.findall(r'"key"=>"([^"]+)",\s*"value"=>"([^"]+)"', str(spec_str))
    if pairs:
        return "; ".join([f"{k}: {v}" for k, v in pairs[:10]])
    return ""

specs_sample = df["product_specifications"].apply(extract_specs_text)
print("Sample parsed specs text:")
print(specs_sample.iloc[0])
