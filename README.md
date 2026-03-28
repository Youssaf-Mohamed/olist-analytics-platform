<h1 align="center">
  <img src="assets/logo.png" alt="Olist BI Logo" width="120" />
  <br>
  OLIST BI Analytics Platform
</h1>

<p align="center">
  <strong>An advanced, modern, and intelligent dashboard built entirely in Python (Dash) for comprehensive e-commerce analytics, featuring an integrated AI Analyst.</strong>
</p>

<p align="center">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.9+-yellow.svg">
  <img alt="Dash" src="https://img.shields.io/badge/Dash-Plotly-blue.svg">
  <img alt="Status" src="https://img.shields.io/badge/Status-Active-success.svg">
  <img alt="Gemini AI" src="https://img.shields.io/badge/AI_Powered-Gemini-purple.svg">
</p>

---

## 📌 Overview

**OLIST BI** is a state-of-the-art interactive business intelligence platform tailored for extracting deep insights from e-commerce operational data. Instead of relying on traditional business intelligence software, this platform is completely coded in Python, leveraging Plotly Dash for rapid, custom interactive data visualization and Gemini AI for automated report generation.

The design philosophy relies strictly on **Dark Mode Glassmorphism** (custom Vanilla CSS without large external UI frameworks), ensuring lightning-fast loads, pixel-perfect layouts, and a truly premium user experience.

---

## 🚀 Key Features

*   📊 **Executive Analytics:** High-level KPIs with MoM growth indicators, tracking revenue, orders, AOV, satisfaction, and delivery performance over dynamic date ranges.
*   🛒 **Smart Recommendations:** An algorithmic engine predicting optimal product subsets based on category, price range, and recent trending data.
*   🗺️ **Geographic Heatmaps:** Interactive spatial insights identifying high-density delivery zones, regional delays, and localized revenue generation across Brazil — filterable by date and metric.
*   👥 **Customer Segmentation:** Integrated Machine Learning visualizations (RFM + K-Means) breaking down user behavior into defined tiers (Champions, At-Risk, Loyal) for targeted marketing.
*   📈 **Time-Series Forecasting:** Predictive models (Ridge regression + Fourier features) with confidence intervals to anticipate revenue trends.
*   💬 **Customer Sentiment:** Review score analysis with gauge, histograms, box plots, and WordCloud generation — filterable by date and category.
*   💳 **Payment & Delivery:** Comprehensive analysis of payment methods, delivery performance, and order value vs. delivery correlation — filterable by date.
*   🏪 **Seller Analytics:** Seller performance leaderboard, geographic distribution, delivery speed analysis, and customer satisfaction benchmarking.
*   🤖 **Integrated AI Analyst:** A conversational sidebar (powered by Google Gemini API) capable of parsing on-screen statistics and answering complex business questions.

---

## 🏗️ Technology Stack

| Domain | Technology |
| :--- | :--- |
| **Frontend UI Framework** | Dash (Plotly) |
| **Data Manipulation** | Pandas, NumPy |
| **Visualizations** | Plotly GO, Plotly Express |
| **Styling & Theming** | Custom Vanilla CSS (Glassmorphism, CSS Variables) |
| **Machine Learning / AI** | Scikit-Learn (K-Means, Ridge Regression), Google GenAI SDK |
| **NLP** | WordCloud |

---

## 📂 Project Structure

```text
olist-analytics-platform/
│
├── assets/                  # Core frontend assets
│   ├── 01_base.css          # Theme variables, typography, resets
│   ├── 02_layout.css        # Main app container, sidebar architecture
│   ├── 03_components.css    # Custom UI elements (cards, AI panel)
│   ├── 04_overrides.css     # Hard overrides for Dash core libraries
│   ├── 05_utilities.css     # Responsive media queries, animations
│   ├── fonts.css            # Google Fonts import
│   └── logo.png             # Project Identity
│
├── data/                    # Olist CSV datasets (~126 MB)
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
├── pages/                   # Isolated dashboard views (8 pages)
│   ├── overview.py          # Page 1: Sales Overview + KPIs + MoM Growth
│   ├── geography.py         # Page 2: Geographic Intelligence + Choropleth
│   ├── reviews.py           # Page 3: Customer Sentiment + WordCloud
│   ├── recommendations.py   # Page 4: Smart Recommendation Engine
│   ├── payments.py          # Page 5: Payments & Delivery Analytics
│   ├── segmentation.py      # Page 6: Customer Segmentation (ML)
│   ├── forecasting.py       # Page 7: Sales Forecasting (ML)
│   └── sellers.py           # Page 8: Seller Performance Analytics
│
├── utils/                   # Shared business logic
│   ├── data_loader.py       # CSV loading, merge pipeline, pickle cache
│   ├── cleaner.py           # Chart template, formatters, helpers
│   ├── gemini_analyst.py    # Gemini AI Integration + fallback
│   ├── recommender.py       # Content-based recommendation engine
│   ├── ml_segmentation.py   # RFM + K-Means clustering
│   └── ml_forecasting.py    # Ridge regression forecasting
│
├── app.py                   # Main entry point & layout definition
├── requirements.txt         # Production dependencies
├── SETUP.md                 # Local installation guide
└── CONTRIBUTING.md          # Team workflow rules
```

## 🛠️ Getting Started
If you are setting the project up locally for the first time, please refer to the comprehensive [SETUP.md](SETUP.md) guide.

## 🤝 Contributing
We welcome improvements! Before submitting a pull request, please review our [CONTRIBUTING.md](CONTRIBUTING.md) to understand our branching strategies, CSS architecture, and coding standards.

---
<p align="center">
  <i>Developed for Data-Driven Decisions.</i>
</p>
