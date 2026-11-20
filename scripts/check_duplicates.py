import pandas as pd

df = pd.read_csv("data/raw/flipkart_com-ecommerce_sample.csv")
print(f"Total rows: {len(df)}")

exact_dups = df.duplicated().sum()
print(f"Exact full-row duplicates: {exact_dups}")

pid_dups = df[df.duplicated(subset=["pid"], keep=False)]
print(f"Duplicate PIDs: {len(pid_dups)}")
print(pid_dups[["uniq_id", "pid", "product_name", "retail_price"]])

name_desc_dups = df.duplicated(subset=["product_name", "description", "retail_price"]).sum()
print(f"Duplicate product_name + description + retail_price: {name_desc_dups}")
