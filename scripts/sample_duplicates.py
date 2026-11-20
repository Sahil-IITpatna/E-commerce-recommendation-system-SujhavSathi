import pandas as pd

df = pd.read_csv("data/raw/flipkart_com-ecommerce_sample.csv")
sample_dup = df[df.duplicated(subset=["product_name", "description", "retail_price"], keep=False)].sort_values("product_name")
print(sample_dup[["product_name", "brand", "retail_price", "discounted_price", "uniq_id"]].head(10))
