# Sujhav साथी – Flipkart Product Recommendation System
> **आपकी पसंद, हमारा सुझाव।**  
> *Your Preferences. Smarter Recommendations.*

An enterprise-grade, machine learning-powered e-commerce product recommendation platform built upon real catalogue data from the **Flipkart Products Dataset by PromptCloudHQ**. Featuring a dual-theme olive-green SaaS analytics dashboard, sub-25ms vector inference, and a transparent hybrid recommendation architecture.

---

## 👨‍💻 Project Metadata & Credits

* **Developer & Author:** **Sahil Kumar**
* **Academic Institution:** **Indian Institute of Technology Patna (IIT Patna)**, 3rd Year
* **Industry Internship:** **Codec Technologies** (Data Science & Machine Learning Internship Project)
* **Domain:** E-Commerce Machine Learning, Natural Language Processing (NLP), Full-Stack Systems

---

## 🌟 Key Highlights & Engineering Features

- **Real Flipkart Catalogue:** Audited and processed **20,000 raw product listings** down to **17,665 unique production products** across **262 primary categories** and **4,565 standardized brands**.
- **No Synthetic Customer Hallucinations:** Strictly preserves data integrity. Because catalogue datasets lack user interaction histories, the system avoids generating fake collaborative filtering, fictitious user ratings, or fabricated sales metrics.
- **4 Algorithmic Recommendation Strategies:**
  1. **Catalogue Listing Ranking:** Transparent multi-factor ranking combining verified customer ratings, discount percentage depth, and 7-point listing completeness.
  2. **Content-Based Filtering (TF-IDF):** Unigram & bigram sublinear TF-IDF vectorizer ($10,000$ features) with Cosine Similarity over titles, categories, descriptions, and parsed specifications.
  3. **Category & Brand Attribute Matching:** Strict taxonomy tree matching, brand affinity, and price-proximity alignment.
  4. **Dynamic Weighted Hybrid Engine:** Configurable normalized score fusion ($60\%$ Content, $25\%$ Category/Brand, $15\%$ Catalogue) with interactive real-time tuning sliders.
- **Proxy-Based Evaluation:** Mathematically evaluated on a stratified test sample of $N=300$ real queries across **Precision@K**, **Recall@K**, and **NDCG@K**.
- **High-Performance Architecture:** Precomputed top-50 sparse neighborhood lookups enabling instant $O(1)$ and sub-25ms response times on Flask REST API.
- **Official Sujhav साथी UI Design System:** Bespoke olive-green palette (`#1F2605`, `#1F6521`, `#53900F`, `#A4A71E`, `#D6CE15`, `#F2F2F2`) with zero-flicker global dark/light theme switching and responsive Recharts visualizations.

---

## 🏗️ System Architecture

```mermaid
flowchart TD
    subgraph Data_Pipeline["1. Data Ingestion & Preprocessing"]
        A1["Raw Flipkart CSV (20,000 Products)"] --> A2["Missing Price & Duplicate Cleaning"]
        A2 --> A3["Taxonomy Tree & Specification Parsing"]
        A3 --> A4["Feature Engineering: Discount %, Price Bands, Completeness"]
        A4 --> A5[("Clean Production Catalogue (17,665 Items)")]
    end

    subgraph ML_Engines["2. Recommendation Algorithms"]
        A5 --> M1["Algorithm 1: Catalogue Ranking<br/>(Ratings, Discount %, Completeness)"]
        A5 --> M2["Algorithm 2: TF-IDF Content Engine<br/>(10,000 Features + Cosine Similarity)"]
        A5 --> M3["Algorithm 3: Category & Brand Engine<br/>(Hierarchy, Brand, Price Proximity)"]
        
        M1 --> M4{"Algorithm 4: Weighted Hybrid Recommender<br/>(60% Content + 25% Brand/Cat + 15% Catalogue)"}
        M2 --> M4
        M3 --> M4
        
        M4 --> EV["Proxy Evaluation Engine<br/>(Precision@K, Recall@K, NDCG@K)"]
    end

    subgraph Backend["3. Modular Flask REST API (Port 5000)"]
        B1["Flask Application Factory (app.py)"]
        B1 --> B2["/api/products & /api/products/search (Pagination, Filters)"]
        B1 --> B3["/api/recommendations (popular, content, category, hybrid)"]
        B1 --> B4["/api/dashboard & /api/model/evaluation"]
        B1 --> B5["/api/categories & /api/brands"]
    end

    subgraph Frontend["4. React.js SaaS Dashboard (Port 5173)"]
        UI1["Global Olive-Green Theme System (Dark / Light Mode)"]
        UI2["Page 1: Analytics Dashboard (6 Recharts Visualizations)"]
        UI3["Page 2: Product Catalogue (Search & Filters)"]
        UI4["Page 3: Recommendations View (Dynamic Sliders & Explanations)"]
        UI5["Page 4: Category Explorer & Taxonomy"]
        UI6["Page 5: Model Performance Benchmarking"]
    end

    ML_Engines --> Backend
    Backend <-->|JSON REST APIs (CORS Enabled)| Frontend
```

---

## 📊 Model Evaluation Results (Proxy-Based Ground Truth)

Because catalogue datasets do not contain user clickstream logs, ground truth is formulated via **catalogue taxonomy congruence** (primary category tree alignment, subcategory match, brand family, and price bracket):

| Recommendation Engine | Precision@5 | Precision@10 | Recall@5 | Recall@10 | NDCG@5 | NDCG@10 |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Catalogue Listing Ranking** | 1.0000 | 0.9990 | 1.0000 | 0.9990 | 0.7687 | 0.8892 |
| **Content-Based (TF-IDF)** | **0.9720** | **0.9643** | **0.9720** | **0.9643** | **0.9328** | **0.9656** |
| **Category & Brand Attribute** | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| **Weighted Hybrid Recommender** | **0.9807** | **0.9763** | **0.9807** | **0.9763** | **0.9634** | **0.9831** |

*Test sample: $N = 300$ stratified products evaluated across top Flipkart categories.*

---

## 🎨 Official Brand Identity & Color Palette

**Brand Name:** Sujhav साथी  
**Hindi Tagline:** आपकी पसंद, हमारा सुझाव।  
**English Tagline:** Your Preferences. Smarter Recommendations.

| Hex Code | Color Name | Role in UI |
| :--- | :--- | :--- |
| **`#1F2605`** | **Deep Olive Black** | Main dark backgrounds, dark navbar/sidebar, primary text in light mode |
| **`#1F6521`** | **Forest Green** | Primary brand color, primary cards in dark mode, primary buttons in light mode |
| **`#53900F`** | **Vibrant Green** | Primary CTA buttons, secondary accents, active navigation badges |
| **`#A4A71E`** | **Olive Yellow** | Supporting highlights, secondary tags, chart accents |
| **`#D6CE15`** | **Neon Lime Yellow** | Key performance indicators, match percentage badges, active highlights |
| **`#F2F2F2`** | **Off White** | Light mode background, primary text in dark mode, clean card surfaces |

---

## 🛠️ Tech Stack

- **Backend:** Python 3.13, Flask 3.1, Flask-CORS, Joblib
- **Machine Learning & NLP:** Scikit-learn (TF-IDF, Cosine Similarity, Linear Kernel), NumPy, Pandas
- **Frontend:** React 19, Vite, Recharts, Lucide React
- **Data Visualizations:** Matplotlib, Seaborn, Recharts

---

## 🚀 Installation & Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/sahilkumar-iitp/SujhavSathi-Flipkart-Recommendation-System.git
cd SujhavSathi-Flipkart-Recommendation-System
```

### 2. Python Environment & Backend Setup
```bash
# Create and activate virtual environment (optional)
python -m venv venv
venv\Scripts\activate      # On Windows
source venv/bin/activate   # On Linux/macOS

# Install backend dependencies
pip install -r backend/requirements.txt

# Start the Flask REST API (Port 5000)
python backend/app.py
```
*Health Check:* `http://localhost:5000/api/health`

### 3. Frontend Setup & Launch
```bash
# In a new terminal window:
cd frontend
npm install
npm run dev
```
*Web Application:* `http://localhost:5173/`

---

## 📂 Project Structure

```text
E-commere Recommendation System/
├── backend/
│   ├── app.py                      # Flask REST API entry point
│   ├── requirements.txt            # Python dependencies
│   ├── postman_collection.json     # Postman API Collection
│   ├── models/
│   │   └── recommender.py          # ML Recommender singleton class
│   ├── routes/
│   │   ├── analytics.py            # Dashboard KPI & Evaluation routes
│   │   ├── products.py             # Products catalogue & search routes
│   │   └── recommendations.py      # Recommendation API endpoints
│   └── artifacts/                  # Serialized Joblib models & metadata
├── data/
│   ├── raw/                        # Original PromptCloudHQ dataset
│   └── processed/                  # Cleaned 17,665 product catalogue
├── frontend/
│   ├── src/
│   │   ├── context/ThemeContext.jsx# Dual-theme provider (Dark/Light)
│   │   ├── services/api.js         # REST API connector
│   │   ├── components/             # Navbar, Sidebar, ProductCard, PlaceholderImage
│   │   └── pages/                  # Dashboard, Catalogue, Recommendations, Categories, Performance
│   ├── index.html                  # HTML entry with brand fonts & title
│   └── package.json                # React dependencies (Recharts, Lucide)
├── notebooks/
│   └── eda_charts/                 # 8 high-resolution analytical visualizations
├── scripts/
│   ├── download_dataset.py         # Automated dataset downloader
│   ├── preprocess_and_eda.py       # Data cleaning & feature engineering pipeline
│   ├── train_and_export_models.py  # Model fitting & artifact serialization
│   ├── evaluate_models.py          # Precision@K, Recall@K, NDCG@K benchmarking
│   └── test_api_endpoints.py       # Automated unit test suite (13 passing tests)
├── PROJECT_REPORT.md               # Comprehensive Data Science Project Report
├── INTERVIEW_AND_VIVA_QUESTIONS.md # 25+ Comprehensive technical viva Q&As
└── README.md                       # Main Project Documentation
```

---

## 📜 Academic & Internship Attribution
Developed by **Sahil Kumar**, 3rd Year Undergraduate, **Indian Institute of Technology Patna (IIT Patna)** as part of the Data Science & Machine Learning Internship at **Codec Technologies**.
