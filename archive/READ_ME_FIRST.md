# 📦 OLIST E-COMMERCE — PROJECT DOCUMENTATION
> **⚠️ READ THIS FILE FIRST BEFORE WRITING ANY CODE**

---

## 🎯 PROJECT GOAL

Build an **E-Commerce Recommendation & Analytics System** using the Olist Brazilian E-Commerce Dataset.

The system will:
1. Analyze sales data and extract business insights
2. Build a product recommendation engine
3. Display everything on an interactive Streamlit dashboard

---

## 📁 DATASET OVERVIEW

- **Source:** [Kaggle — Olist Brazilian E-Commerce](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)
- **Size:** ~100,000 real orders from 2016 to 2018
- **Format:** 9 separate CSV files that connect to each other like a relational database
- **Language:** Portuguese (product categories) — translation file is included

---

## 🗂️ FILES & THEIR PURPOSE

| File Name | What's Inside | Key Columns |
|-----------|--------------|-------------|
| `olist_orders_dataset.csv` | ⭐ MAIN TABLE — every order and its status | `order_id`, `customer_id`, `order_status`, `order_purchase_timestamp`, `order_delivered_customer_date` |
| `olist_order_items_dataset.csv` | Products inside each order + price + shipping | `order_id`, `product_id`, `seller_id`, `price`, `freight_value`, `shipping_limit_date` |
| `olist_customers_dataset.csv` | Customer info and location | `customer_id`, `customer_unique_id`, `customer_city`, `customer_state`, `customer_zip_code_prefix` |
| `olist_products_dataset.csv` | Product details and category | `product_id`, `product_category_name`, `product_weight_g`, `product_length_cm` |
| `olist_sellers_dataset.csv` | Seller info and location | `seller_id`, `seller_city`, `seller_state`, `seller_zip_code_prefix` |
| `olist_order_reviews_dataset.csv` | Customer ratings and text reviews | `order_id`, `review_score` (1–5), `review_comment_title`, `review_comment_message`, `review_creation_date` |
| `olist_order_payments_dataset.csv` | Payment method and amount | `order_id`, `payment_type`, `payment_installments`, `payment_value` |
| `olist_geolocation_dataset.csv` | Zip codes mapped to lat/lng coordinates | `geolocation_zip_code_prefix`, `geolocation_lat`, `geolocation_lng`, `geolocation_city`, `geolocation_state` |
| `product_category_name_translation.csv` | Translates Portuguese category names to English | `product_category_name`, `product_category_name_english` |

---

## 🔗 HOW THE TABLES CONNECT (Relationships)

```
olist_orders  ──────────────────────────────────────────────────────┐
     │                                                               │
     ├──[order_id]──► olist_order_items ──[product_id]──► olist_products
     │                       │                                  │
     │                  [seller_id]                    [product_category_name]
     │                       │                                  │
     │               olist_sellers              product_category_name_translation
     │
     ├──[order_id]──► olist_order_reviews
     │
     ├──[order_id]──► olist_order_payments
     │
     └──[customer_id]──► olist_customers ──[zip_code]──► olist_geolocation
```

**The main join key is `order_id`** — it connects orders to items, reviews, and payments.
**`customer_unique_id`** is the real customer identifier (same customer can have multiple `customer_id` values across orders).

---

## ⚠️ IMPORTANT DATA NOTES

1. **Same customer, different IDs:** `customer_id` changes per order — always use `customer_unique_id` to track real customers.
2. **One order, multiple items:** One `order_id` can appear multiple times in `olist_order_items_dataset.csv`.
3. **Sparse repeat buyers:** Most customers bought only once — this affects collaborative filtering. Use content-based or popularity-based recommendation instead.
4. **Date range:** September 2016 to October 2018. Best analysis window is January 2017 to August 2018.
5. **Currency:** All prices are in Brazilian Real (BRL) — not USD.
6. **Null values:** `olist_products_dataset.csv` has null category names — replace with `"not_defined"`.
7. **Category names in Portuguese:** Always join with `product_category_name_translation.csv` to get English names.

---

## 📊 KEY FACTS ABOUT THE DATA

| Metric | Value |
|--------|-------|
| Total Orders | ~100,000 |
| Total Revenue | ~$16M (BRL) |
| Average Order Value | ~125 BRL |
| Average Review Score | 4.03 / 5 |
| Order Cancellation Rate | 0.59% |
| Top Category | Bed Bath Table |
| Most Used Payment | Credit Card |
| Peak Sales Period | Q2 2018 |

---

## 🏗️ PROJECT STRUCTURE (How to Build It)

```
project/
│
├── READ_ME_FIRST.md          ← YOU ARE HERE
│
├── data/                     ← Put all CSV files here
│   ├── olist_orders_dataset.csv
│   ├── olist_order_items_dataset.csv
│   ├── olist_customers_dataset.csv
│   ├── olist_products_dataset.csv
│   ├── olist_sellers_dataset.csv
│   ├── olist_order_reviews_dataset.csv
│   ├── olist_order_payments_dataset.csv
│   ├── olist_geolocation_dataset.csv
│   └── product_category_name_translation.csv
│
├── 01_data_loading.py        ← Load and merge all tables
├── 02_data_cleaning.py       ← Handle nulls, fix types, filter dates
├── 03_eda.py                 ← Exploratory analysis and insights
├── 04_recommendation.py      ← Build the recommendation engine
└── 05_dashboard.py           ← Streamlit dashboard (MAIN APP)
```

---

## 🔧 HOW TO LOAD THE DATA (Python)

```python
import pandas as pd

# Load all tables
orders    = pd.read_csv('data/olist_orders_dataset.csv')
items     = pd.read_csv('data/olist_order_items_dataset.csv')
customers = pd.read_csv('data/olist_customers_dataset.csv')
products  = pd.read_csv('data/olist_products_dataset.csv')
sellers   = pd.read_csv('data/olist_sellers_dataset.csv')
reviews   = pd.read_csv('data/olist_order_reviews_dataset.csv')
payments  = pd.read_csv('data/olist_order_payments_dataset.csv')
geo       = pd.read_csv('data/olist_geolocation_dataset.csv')
cat_trans = pd.read_csv('data/product_category_name_translation.csv')

# Parse date columns
date_cols = ['order_purchase_timestamp', 'order_approved_at',
             'order_delivered_carrier_date', 'order_delivered_customer_date',
             'order_estimated_delivery_date']
for col in date_cols:
    orders[col] = pd.to_datetime(orders[col])

# Translate product categories to English
products = products.merge(cat_trans, on='product_category_name', how='left')
products['product_category_name_english'].fillna('not_defined', inplace=True)

# Build master dataframe (the big merged table)
master = (
    orders
    .merge(items,     on='order_id',    how='left')
    .merge(products,  on='product_id',  how='left')
    .merge(customers, on='customer_id', how='left')
    .merge(payments,  on='order_id',    how='left')
    .merge(reviews,   on='order_id',    how='left')
)
```

---

## 🤖 RECOMMENDATION ENGINE APPROACH

Since most customers bought only once, use **two approaches combined:**

### Approach 1 — Content-Based Filtering
Recommend products similar to what the customer bought, based on category and price range.

```python
# Logic: customer bought product in category X with price ~Y
# → recommend top-rated products in same category with similar price
def get_content_recommendations(product_id, top_n=5):
    product = products[products['product_id'] == product_id].iloc[0]
    category = product['product_category_name_english']
    price = items[items['product_id'] == product_id]['price'].mean()

    # Filter same category
    same_cat = items.merge(products, on='product_id')
    same_cat = same_cat[same_cat['product_category_name_english'] == category]

    # Filter similar price range (±30%)
    same_cat = same_cat[(same_cat['price'] >= price * 0.7) &
                        (same_cat['price'] <= price * 1.3)]

    # Rank by review score
    same_cat = same_cat.merge(reviews[['order_id','review_score']], on='order_id')
    top_products = (same_cat.groupby('product_id')['review_score']
                             .mean()
                             .sort_values(ascending=False)
                             .head(top_n))
    return top_products
```

### Approach 2 — Popularity-Based (Trending)
Recommend the best-selling, highest-rated products overall or by category.

```python
# Top products by category
def get_popular_by_category(category, top_n=5):
    cat_items = items.merge(products, on='product_id')
    cat_items = cat_items[cat_items['product_category_name_english'] == category]
    cat_items = cat_items.merge(reviews[['order_id','review_score']], on='order_id')

    top = (cat_items.groupby('product_id')
                    .agg(total_sales=('order_id','count'),
                         avg_rating=('review_score','mean'))
                    .query('total_sales >= 10')
                    .sort_values(['avg_rating','total_sales'], ascending=False)
                    .head(top_n))
    return top
```

---

## 📈 DASHBOARD SECTIONS (Streamlit)

Build the dashboard with these 4 tabs:

### Tab 1 — 📊 Sales Overview
- Total revenue over time (line chart)
- Monthly orders trend
- Revenue by product category (bar chart)
- Orders by status (pie chart)

### Tab 2 — 🗺️ Geographic Map
- Customer distribution across Brazil states (choropleth map using Folium or Plotly)
- Top 10 cities by number of orders

### Tab 3 — ⭐ Product Insights
- Top 10 categories by sales volume
- Average review score per category
- Price distribution per category (box plot)
- Review score distribution (histogram)

### Tab 4 — 🤖 Recommendation Engine
- Input: Select a product category
- Output: Top 5 recommended products with rating and price
- Show "Trending Now" section with most popular products this month

---

## 🛠️ REQUIRED LIBRARIES

```bash
pip install pandas numpy scikit-learn streamlit plotly folium streamlit-folium seaborn matplotlib
```

```python
# In your code
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import LabelEncoder
import folium
from streamlit_folium import st_folium
```

---

## ✅ DEVELOPMENT CHECKLIST

- [ ] Download all 9 CSV files from Kaggle and put in `/data` folder
- [ ] Run `01_data_loading.py` — verify all tables load correctly
- [ ] Run `02_data_cleaning.py` — handle nulls and fix date columns
- [ ] Run `03_eda.py` — generate insights and verify data makes sense
- [ ] Run `04_recommendation.py` — test recommendation functions
- [ ] Run `05_dashboard.py` — launch Streamlit app with `streamlit run 05_dashboard.py`

---

## 🚀 QUICK START COMMAND

```bash
# After setting up, launch the dashboard with:
streamlit run 05_dashboard.py
```

---

*Documentation prepared for Big Data & Analytics Course Project*
*Dataset: Olist Brazilian E-Commerce Public Dataset (Kaggle)*
