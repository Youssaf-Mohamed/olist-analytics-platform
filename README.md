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

*   📊 **Executive Analytics:** High-level key performance indicators, tracking revenue, distinct customer counts, and order volumes over dynamic periods.
*   🛒 **Smart Recommendations:** An algorithmic engine predicting optimal product subsets based on category, sub-category, price range parameters, and recent trending data.
*   🗺️ **Geographic Heatmaps:** Interactive spatial insights identifying high-density delivery zones, regional delays, and localized revenue generation across Brazil.
*   👥 **Customer Segmentation:** Integrated Machine Learning visualizations breaking down user behavior into defined tiers (e.g., Champions, At-Risk, Loyal) for targeted marketing.
*   📈 **Time-Series Forecasting:** Predictive models mapped visually to anticipate order volumes and prepare infrastructure.
*   🤖 **Integrated AI Analyst:** A conversational sidebar (powered by Google Gemini API) capable of parsing on-screen statistics and generating natural language summaries to answer complex business questions on the fly.

---

## 🏗️ Technology Stack

| Domain | Technology |
| :--- | :--- |
| **Frontend UI Framework** | Dash (Plotly) |
| **Data Manipulation** | Pandas, NumPy |
| **Visualizations** | Plotly GO, Plotly Express |
| **Styling & Theming** | Custom Vanilla CSS (Glassmorphism, CSS Variables) |
| **Machine Learning / AI** | Scikit-Learn (Segmentation/Forecasting), Google GenAI SDK |

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
│   └── logo.png             # Project Identity
│
├── data/
│   ├── processed/           # Cleaned .csv / .parquet datasets
│   └── raw/                 # Original source database dumps
│
├── pages/                   # Isolated dashboard views
│   ├── geography.py
│   ├── recommendations.py
│   ├── reviews.py
│   ├── sales_overview.py
│   └── segmentation.py
│
├── utils/                   # Shared business logic
│   ├── cleaner.py           # Data formatting (currency, strings)
│   ├── data_loader.py       # Caching & DataFrame loading protocols
│   ├── gemini_analyst.py    # AI Integration module
│   └── recommender.py       # Algorithmic suggestion logic
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
