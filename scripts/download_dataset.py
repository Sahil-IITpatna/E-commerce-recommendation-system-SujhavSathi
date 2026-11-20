import os
import urllib.request
import sys

URL = "https://raw.githubusercontent.com/jashmehta3300/Flipkart-Products/main/flipkart_com-ecommerce_sample.csv"
DEST = os.path.join(os.path.dirname(__file__), "..", "data", "raw", "flipkart_com-ecommerce_sample.csv")

def download_dataset():
    dest_path = os.path.abspath(DEST)
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    
    if os.path.exists(dest_path) and os.path.getsize(dest_path) > 10000000:
        print(f"Dataset already exists at: {dest_path} ({os.path.getsize(dest_path)} bytes)")
        return
    
    print(f"Downloading PromptCloudHQ Flipkart dataset (~38MB) from {URL}...")
    try:
        def reporthook(block_num, block_size, total_size):
            read_so_far = block_num * block_size
            if total_size > 0:
                percent = read_so_far * 1e2 / total_size
                if block_num % 500 == 0 or read_so_far >= total_size:
                    print(f"Downloaded {read_so_far / (1024*1024):.1f} MB / {total_size / (1024*1024):.1f} MB ({percent:.1f}%)")
                    sys.stdout.flush()

        urllib.request.urlretrieve(URL, dest_path, reporthook=reporthook)
        print(f"Download complete: {dest_path} ({os.path.getsize(dest_path)} bytes)")
    except Exception as e:
        print(f"Error downloading dataset: {e}")

if __name__ == "__main__":
    download_dataset()
