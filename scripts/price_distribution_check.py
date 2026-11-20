import pandas as pd
import numpy as np

df = pd.read_csv("data/raw/flipkart_com-ecommerce_sample.csv")
valid_df = df.dropna(subset=["retail_price", "discounted_price"]).copy()

print("--- RETAIL PRICE STATS ---")
print(valid_df["retail_price"].describe(percentiles=[0.25, 0.50, 0.75, 0.90, 0.95]))

print("\n--- DISCOUNTED PRICE STATS ---")
print(valid_df["discounted_price"].describe(percentiles=[0.25, 0.50, 0.75, 0.90, 0.95]))

# Price tiers:
# < 500: Budget (entry level items, accessories, budget clothing)
# 500 - 2000: Mid-Range (watches, footwear, fashion, home decor)
# > 2000: Premium (electronics, luxury jewellery, high-end furniture)

valid_df["discount_amount"] = valid_df["retail_price"] - valid_df["discounted_price"]
valid_df["discount_pct"] = (valid_df["discount_amount"] / valid_df["retail_price"]) * 100

print("\n--- DISCOUNT PERCENTAGE STATS ---")
print(valid_df["discount_pct"].describe(percentiles=[0.25, 0.50, 0.75, 0.90, 0.95]))
