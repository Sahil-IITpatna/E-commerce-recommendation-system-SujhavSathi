import pandas as pd
import json

raw_path = "data/raw/flipkart_com-ecommerce_sample.csv"
print(f"Loading {raw_path}...")
df = pd.read_csv(raw_path)

print("\n--- DATASET SHAPE ---")
print(f"Rows: {df.shape[0]}, Columns: {df.shape[1]}")

print("\n--- COLUMN NAMES AND DTYPES ---")
for col in df.columns:
    print(f"- {col} (dtype: {df[col].dtype})")

print("\n--- MISSING VALUES ---")
null_counts = df.isnull().sum()
null_pct = (null_counts / len(df)) * 100
missing_df = pd.DataFrame({"Missing Count": null_counts, "Missing %": null_pct})
print(missing_df[missing_df["Missing Count"] > 0])

print("\n--- DUPLICATE CHECKS ---")
print(f"Duplicate full rows: {df.duplicated().sum()}")
if "uniq_id" in df.columns:
    print(f"Unique 'uniq_id': {df['uniq_id'].nunique()} out of {len(df)}")
if "pid" in df.columns:
    print(f"Unique 'pid': {df['pid'].nunique()} out of {len(df)}")
if "product_name" in df.columns:
    print(f"Unique 'product_name': {df['product_name'].nunique()} out of {len(df)}")

print("\n--- SAMPLE ROW (FIRST RECORD) ---")
first_row = df.iloc[0].to_dict()
for k, v in first_row.items():
    v_str = str(v)
    if len(v_str) > 100:
        v_str = v_str[:100] + "..."
    print(f"{k}: {v_str}")

print("\n--- VALUE COUNTS FOR RATINGS ---")
if "product_rating" in df.columns:
    print("Product Rating unique values preview:")
    print(df["product_rating"].value_counts().head(10))

if "overall_rating" in df.columns:
    print("\nOverall Rating unique values preview:")
    print(df["overall_rating"].value_counts().head(10))

print("\n--- SAMPLE CATEGORY TREES ---")
if "product_category_tree" in df.columns:
    for cat in df["product_category_tree"].dropna().head(5):
        print(f"  {cat}")

print("\n--- SAMPLE IMAGES ---")
if "image" in df.columns:
    for img in df["image"].dropna().head(3):
        print(f"  {img}")
