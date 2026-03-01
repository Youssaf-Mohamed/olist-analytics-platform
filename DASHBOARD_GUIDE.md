# 🚀 E-Commerce Intelligence Dashboard — Plotly Dash Guide
> **Read this before writing any dashboard code**

---

## 🎯 What You're Building

A **dark-themed, multi-page Plotly Dash dashboard** that acts as a real business intelligence tool for the Olist E-Commerce dataset. It must feel like a premium SaaS analytics product — not a student project.

---

## 🎨 Design Direction — "Dark Data Terminal"

**Theme:** Dark industrial with electric accent colors
**Feel:** Bloomberg Terminal meets modern SaaS
**Color Palette:**
```
Background:     #0D0F14  (near black)
Surface:        #161A23  (dark card)
Border:         #1E2433  (subtle border)
Primary Accent: #00D4FF  (electric cyan)
Secondary:      #7C3AED  (deep purple)
Success:        #10B981  (emerald green)
Warning:        #F59E0B  (amber)
Danger:         #EF4444  (red)
Text Primary:   #F1F5F9  (near white)
Text Muted:     #64748B  (slate gray)
```

**Typography:**
- Numbers & KPIs: `"Space Mono"` (monospace, feels data-driven)
- Headers: `"Syne"` (geometric, modern)
- Body: `"DM Sans"` (clean, readable)

Load via Google Fonts in `assets/fonts.css`

---

## 📁 Project Structure

```
project/
│
├── app.py                    ← Main entry point
├── assets/
│   ├── style.css             ← Global dark theme styles
│   └── fonts.css             ← Google Fonts import
│
├── data/                     ← All 9 Olist CSV files here
│
├── utils/
│   ├── data_loader.py        ← Load & merge all CSVs (cached)
│   ├── cleaner.py            ← Clean & prepare data
│   └── recommender.py        ← Recommendation engine logic
│
└── pages/
    ├── overview.py           ← Page 1: Sales Overview
    ├── geography.py          ← Page 2: Geographic Map
    ├── reviews.py            ← Page 3: Reviews & Sentiment
    ├── recommendations.py    ← Page 4: Recommendation Engine
    └── payments.py           ← Page 5: Payments & Delivery
```

---

## 🏗️ app.py — Main Structure

```python
import dash
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc

app = Dash(
    __name__,
    use_pages=True,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@600;800&family=DM+Sans:wght@300;400;500&display=swap"
    ],
    suppress_callback_exceptions=True
)

app.layout = html.Div([
    # Sidebar Navigation
    html.Div([
        html.Div("⚡ OLIST BI", className="logo"),
        html.Hr(className="divider"),
        dbc.Nav([
            dbc.NavLink([html.Span("01"), " Overview"],     href="/",                active="exact"),
            dbc.NavLink([html.Span("02"), " Geography"],    href="/geography",        active="exact"),
            dbc.NavLink([html.Span("03"), " Reviews"],      href="/reviews",          active="exact"),
            dbc.NavLink([html.Span("04"), " Recommend"],    href="/recommendations",  active="exact"),
            dbc.NavLink([html.Span("05"), " Payments"],     href="/payments",         active="exact"),
        ], vertical=True, pills=True),
    ], className="sidebar"),

    # Main Content Area
    html.Div([
        dash.page_container
    ], className="main-content")
], className="app-wrapper")

if __name__ == "__main__":
    app.run(debug=True)
```

---

## 🎨 assets/style.css — Global Styles

```css
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@600;800&family=DM+Sans:wght@300;400;500&display=swap');

:root {
  --bg:         #0D0F14;
  --surface:    #161A23;
  --border:     #1E2433;
  --cyan:       #00D4FF;
  --purple:     #7C3AED;
  --green:      #10B981;
  --amber:      #F59E0B;
  --red:        #EF4444;
  --text:       #F1F5F9;
  --muted:      #64748B;
}

* { margin: 0; padding: 0; box-sizing: border-box; }
body { background: var(--bg); color: var(--text); font-family: 'DM Sans', sans-serif; }

/* Layout */
.app-wrapper    { display: flex; min-height: 100vh; }
.sidebar        { width: 220px; background: var(--surface); border-right: 1px solid var(--border);
                  padding: 24px 16px; position: fixed; height: 100vh; }
.main-content   { margin-left: 220px; padding: 32px; flex: 1; }

/* Logo */
.logo           { font-family: 'Syne', sans-serif; font-size: 20px; font-weight: 800;
                  color: var(--cyan); letter-spacing: 2px; padding: 8px 0 16px; }
.divider        { border-color: var(--border); margin: 8px 0 16px; }

/* Nav Links */
.nav-link       { color: var(--muted) !important; font-size: 13px; padding: 10px 12px !important;
                  border-radius: 8px; transition: all 0.2s; font-family: 'DM Sans', sans-serif; }
.nav-link span  { color: var(--cyan); font-family: 'Space Mono', monospace; font-size: 11px;
                  margin-right: 8px; }
.nav-link:hover { color: var(--text) !important; background: var(--border) !important; }
.nav-link.active { color: var(--cyan) !important; background: rgba(0,212,255,0.08) !important;
                   border-left: 2px solid var(--cyan); }

/* KPI Cards */
.kpi-card       { background: var(--surface); border: 1px solid var(--border); border-radius: 12px;
                  padding: 20px 24px; position: relative; overflow: hidden; }
.kpi-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px;
                    background: linear-gradient(90deg, var(--cyan), var(--purple)); }
.kpi-label      { font-size: 11px; color: var(--muted); text-transform: uppercase;
                  letter-spacing: 1.5px; font-family: 'Space Mono', monospace; }
.kpi-value      { font-size: 32px; font-weight: 700; font-family: 'Space Mono', monospace;
                  color: var(--text); margin: 8px 0 4px; }
.kpi-delta      { font-size: 12px; color: var(--green); }

/* Chart Cards */
.chart-card     { background: var(--surface); border: 1px solid var(--border); border-radius: 12px;
                  padding: 24px; margin-bottom: 24px; }
.chart-title    { font-family: 'Syne', sans-serif; font-size: 14px; font-weight: 600;
                  color: var(--text); text-transform: uppercase; letter-spacing: 1px;
                  margin-bottom: 16px; }

/* Page Header */
.page-header    { margin-bottom: 32px; }
.page-title     { font-family: 'Syne', sans-serif; font-size: 28px; font-weight: 800;
                  color: var(--text); }
.page-subtitle  { font-size: 14px; color: var(--muted); margin-top: 4px; }

/* Dropdowns & Sliders (Dash components) */
.Select-control, .Select-menu-outer { background: var(--surface) !important;
                                       border-color: var(--border) !important; color: var(--text) !important; }
.rc-slider-track  { background: var(--cyan) !important; }
.rc-slider-handle { border-color: var(--cyan) !important; }
```

---

## 📊 Plotly Chart Template

Use this template on EVERY chart for consistent dark styling:

```python
CHART_TEMPLATE = dict(
    layout=dict(
        paper_bgcolor="#161A23",
        plot_bgcolor="#0D0F14",
        font=dict(family="DM Sans", color="#F1F5F9", size=12),
        xaxis=dict(gridcolor="#1E2433", linecolor="#1E2433", tickfont=dict(color="#64748B")),
        yaxis=dict(gridcolor="#1E2433", linecolor="#1E2433", tickfont=dict(color="#64748B")),
        margin=dict(l=40, r=20, t=20, b=40),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#64748B")),
        colorway=["#00D4FF", "#7C3AED", "#10B981", "#F59E0B", "#EF4444",
                  "#06B6D4", "#8B5CF6", "#34D399", "#FCD34D", "#F87171"]
    )
)

# Usage:
fig = px.line(df, x="date", y="revenue")
fig.update_layout(**CHART_TEMPLATE["layout"])
```

---

## 📄 Page 1 — Overview (pages/overview.py)

```python
import dash
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
from utils.data_loader import load_master_data

dash.register_page(__name__, path="/", name="Overview")

def layout():
    master = load_master_data()
    return html.Div([

        # Page Header
        html.Div([
            html.H1("Sales Overview", className="page-title"),
            html.P("Real-time business performance metrics", className="page-subtitle"),
        ], className="page-header"),

        # Global Date Filter
        html.Div([
            dcc.DatePickerRange(
                id="date-filter",
                min_date_allowed=master["order_purchase_timestamp"].min(),
                max_date_allowed=master["order_purchase_timestamp"].max(),
                start_date="2017-01-01",
                end_date="2018-08-31",
                style={"marginBottom": "24px"}
            )
        ]),

        # KPI Cards Row
        dbc.Row([
            dbc.Col(html.Div(id="kpi-revenue"), md=3),
            dbc.Col(html.Div(id="kpi-orders"),  md=3),
            dbc.Col(html.Div(id="kpi-rating"),  md=3),
            dbc.Col(html.Div(id="kpi-delivery"), md=3),
        ], className="mb-4"),

        # Charts Row
        dbc.Row([
            dbc.Col(html.Div([
                html.P("Revenue Over Time", className="chart-title"),
                dcc.Graph(id="revenue-chart")
            ], className="chart-card"), md=8),

            dbc.Col(html.Div([
                html.P("Orders by Status", className="chart-title"),
                dcc.Graph(id="status-pie")
            ], className="chart-card"), md=4),
        ]),

        # Top Categories Chart
        html.Div([
            html.P("Top 10 Categories by Revenue", className="chart-title"),
            dcc.Graph(id="categories-chart")
        ], className="chart-card"),

    ])

# Callback — update everything based on date filter
@callback(
    Output("kpi-revenue",      "children"),
    Output("kpi-orders",       "children"),
    Output("kpi-rating",       "children"),
    Output("kpi-delivery",     "children"),
    Output("revenue-chart",    "figure"),
    Output("status-pie",       "figure"),
    Output("categories-chart", "figure"),
    Input("date-filter", "start_date"),
    Input("date-filter", "end_date"),
)
def update_overview(start_date, end_date):
    master = load_master_data()
    filtered = master[
        (master["order_purchase_timestamp"] >= start_date) &
        (master["order_purchase_timestamp"] <= end_date)
    ]

    # KPIs
    total_revenue = filtered["payment_value"].sum()
    total_orders  = filtered["order_id"].nunique()
    avg_rating    = filtered["review_score"].mean()
    on_time_rate  = (filtered["order_delivered_customer_date"] <=
                     filtered["order_estimated_delivery_date"]).mean() * 100

    def kpi_card(label, value, delta=None):
        return html.Div([
            html.P(label, className="kpi-label"),
            html.P(value, className="kpi-value"),
            html.P(delta, className="kpi-delta") if delta else None
        ], className="kpi-card")

    kpi1 = kpi_card("Total Revenue",   f"R${total_revenue:,.0f}")
    kpi2 = kpi_card("Total Orders",    f"{total_orders:,}")
    kpi3 = kpi_card("Avg Rating",      f"{avg_rating:.2f} ⭐")
    kpi4 = kpi_card("On-Time Delivery",f"{on_time_rate:.1f}%")

    # Revenue Over Time
    monthly = (filtered.groupby(
        filtered["order_purchase_timestamp"].dt.to_period("M").astype(str)
    )["payment_value"].sum().reset_index())
    monthly.columns = ["month", "revenue"]
    fig_line = px.line(monthly, x="month", y="revenue", markers=True)
    fig_line.update_traces(line_color="#00D4FF", marker_color="#00D4FF")
    fig_line.update_layout(**CHART_TEMPLATE["layout"])

    # Orders by Status
    status_counts = filtered["order_status"].value_counts().reset_index()
    fig_pie = px.pie(status_counts, names="order_status", values="count", hole=0.6)
    fig_pie.update_layout(**CHART_TEMPLATE["layout"])

    # Top 10 Categories
    cat_rev = (filtered.groupby("product_category_name_english")["payment_value"]
               .sum().nlargest(10).reset_index())
    fig_bar = px.bar(cat_rev, x="payment_value", y="product_category_name_english",
                     orientation="h")
    fig_bar.update_traces(marker_color="#7C3AED")
    fig_bar.update_layout(**CHART_TEMPLATE["layout"])

    return kpi1, kpi2, kpi3, kpi4, fig_line, fig_pie, fig_bar
```

---

## 📄 Page 2 — Geography (pages/geography.py)

```python
# Key elements:
# - Choropleth map of Brazil states colored by selected metric
# - Dropdown: choose Revenue / Orders / Avg Rating
# - Top 10 cities table updates with map

import plotly.express as px

# Brazil GeoJSON — use this URL:
BRAZIL_GEOJSON = "https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson"

# Map creation:
fig_map = px.choropleth(
    df_states,
    geojson=BRAZIL_GEOJSON,
    locations="customer_state",
    featureidkey="properties.sigla",
    color="value",
    color_continuous_scale=[[0, "#1E2433"], [0.5, "#7C3AED"], [1, "#00D4FF"]],
    scope="south america"
)
fig_map.update_geos(
    bgcolor="#0D0F14",
    lakecolor="#0D0F14",
    landcolor="#161A23",
    showcoastlines=True, coastlinecolor="#1E2433"
)
fig_map.update_layout(**CHART_TEMPLATE["layout"])
```

---

## 📄 Page 3 — Reviews (pages/reviews.py)

```python
# Key elements:
# - Sentiment Gauge (go.Indicator)
# - Review score histogram
# - Box plot: review score per top 10 categories
# - Category filter dropdown → all charts update
# - WordCloud image generated from review_comment_message

from wordcloud import WordCloud
import matplotlib.pyplot as plt
import base64
from io import BytesIO

def generate_wordcloud(text_series):
    text = " ".join(text_series.dropna().values)
    wc = WordCloud(
        width=800, height=300,
        background_color="#161A23",
        colormap="cool",
        max_words=100
    ).generate(text)
    buf = BytesIO()
    plt.figure(figsize=(10, 4), facecolor="#161A23")
    plt.imshow(wc, interpolation="bilinear")
    plt.axis("off")
    plt.tight_layout(pad=0)
    plt.savefig(buf, format="png", bbox_inches="tight", facecolor="#161A23")
    plt.close()
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()

# Sentiment Gauge:
fig_gauge = go.Figure(go.Indicator(
    mode="gauge+number",
    value=avg_score,
    domain={"x": [0, 1], "y": [0, 1]},
    gauge={
        "axis": {"range": [1, 5], "tickcolor": "#64748B"},
        "bar":  {"color": "#00D4FF"},
        "bgcolor": "#161A23",
        "steps": [
            {"range": [1, 2], "color": "#EF4444"},
            {"range": [2, 3], "color": "#F59E0B"},
            {"range": [3, 4], "color": "#7C3AED"},
            {"range": [4, 5], "color": "#10B981"},
        ],
    }
))
```

---

## 📄 Page 4 — Recommendations (pages/recommendations.py)

```python
# Key elements:
# - Category dropdown → returns top 5 recommended products
# - Price range slider → filters recommendations
# - Result cards with: product_id, avg_price, avg_rating, total_sales
# - "Trending Now" section: top 5 products in last 90 days

# Layout structure:
html.Div([
    html.Div([
        # Controls
        dcc.Dropdown(id="cat-select", options=categories, placeholder="Select Category..."),
        dcc.RangeSlider(id="price-slider", min=0, max=1000, step=10, value=[0, 500]),
        html.Button("Get Recommendations", id="rec-btn", className="rec-btn"),
    ], className="rec-controls"),

    # Results
    html.Div(id="rec-results", className="rec-grid"),

    html.Hr(),

    # Trending
    html.P("🔥 Trending Now — Last 90 Days", className="chart-title"),
    html.Div(id="trending-results", className="rec-grid"),
])

# Recommendation Card CSS:
"""
.rec-grid   { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
              gap: 16px; margin-top: 24px; }
.rec-card   { background: var(--surface); border: 1px solid var(--border);
              border-radius: 12px; padding: 20px;
              border-top: 3px solid var(--cyan); transition: transform 0.2s; }
.rec-card:hover { transform: translateY(-4px); border-top-color: var(--purple); }
.rec-btn    { background: var(--cyan); color: var(--bg); border: none;
              padding: 10px 24px; border-radius: 8px; font-weight: 600;
              font-family: 'Syne', sans-serif; cursor: pointer; margin-top: 16px; }
"""
```

---

## 📄 Page 5 — Payments & Delivery (pages/payments.py)

```python
# Key elements:
# - Pie chart: payment type distribution
# - Bar chart: avg delivery days per state (top 15)
# - Scatter plot: order value vs delivery time
# - KPI: % delivered on time vs late

# Delivery time calculation:
master["delivery_days"] = (
    master["order_delivered_customer_date"] -
    master["order_purchase_timestamp"]
).dt.days
```

---

## ⚡ utils/data_loader.py — Cached Data Loading

```python
import pandas as pd
from dash import DiskcacheManager
import diskcache

cache = diskcache.Cache("./cache")

def load_master_data():
    """Load and merge all Olist CSVs. Run once, cache forever."""

    orders    = pd.read_csv("data/olist_orders_dataset.csv")
    items     = pd.read_csv("data/olist_order_items_dataset.csv")
    customers = pd.read_csv("data/olist_customers_dataset.csv")
    products  = pd.read_csv("data/olist_products_dataset.csv")
    reviews   = pd.read_csv("data/olist_order_reviews_dataset.csv")
    payments  = pd.read_csv("data/olist_order_payments_dataset.csv")
    cat_trans = pd.read_csv("data/product_category_name_translation.csv")

    # Parse dates
    for col in ["order_purchase_timestamp", "order_delivered_customer_date",
                "order_estimated_delivery_date"]:
        orders[col] = pd.to_datetime(orders[col])

    # Translate categories
    products = products.merge(cat_trans, on="product_category_name", how="left")
    products["product_category_name_english"].fillna("not_defined", inplace=True)

    # Aggregate payments per order
    payments_agg = payments.groupby("order_id").agg(
        payment_value=("payment_value", "sum"),
        payment_type=("payment_type", "first")
    ).reset_index()

    # Aggregate reviews per order
    reviews_agg = reviews.groupby("order_id").agg(
        review_score=("review_score", "mean"),
        review_comment=("review_comment_message", "first")
    ).reset_index()

    # Build master dataframe
    master = (
        orders
        .merge(items.groupby("order_id").agg(
            product_id=("product_id", "first"),
            seller_id=("seller_id", "first"),
            price=("price", "sum"),
            freight_value=("freight_value", "sum")
        ).reset_index(), on="order_id", how="left")
        .merge(products[["product_id", "product_category_name_english"]], on="product_id", how="left")
        .merge(customers[["customer_id", "customer_unique_id", "customer_state", "customer_city"]], on="customer_id", how="left")
        .merge(payments_agg, on="order_id", how="left")
        .merge(reviews_agg,  on="order_id", how="left")
    )

    # Filter to best date range
    master = master[master["order_purchase_timestamp"].between("2017-01-01", "2018-08-31")]

    return master
```

---

## 📦 Install All Required Libraries

```bash
pip install dash dash-bootstrap-components plotly pandas numpy scikit-learn wordcloud matplotlib diskcache
```

---

## 🚀 Run the App

```bash
python app.py
# Open: http://127.0.0.1:8050
```

---

*Big Data & Analytics Course Project*
*Stack: Plotly Dash + Pandas + Scikit-learn*
*Dataset: Olist Brazilian E-Commerce (Kaggle)*
