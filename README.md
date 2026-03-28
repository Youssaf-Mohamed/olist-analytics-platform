<h1 align="center">
  <img src="assets/logo.svg" alt="Olist BI Logo" width="120" />
  <br>
  OLIST BI Analytics Platform
</h1>

<p align="center">
  <strong>A polished Dash analytics platform for Olist marketplace data, with synchronized filters, dual-theme UI, tested analytics, and a context-aware AI copilot.</strong>
</p>

<p align="center">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.9+-yellow.svg">
  <img alt="Dash" src="https://img.shields.io/badge/Dash-Plotly-blue.svg">
  <img alt="Tests" src="https://img.shields.io/badge/Tests-Unittest-success.svg">
  <img alt="Themes" src="https://img.shields.io/badge/UI-Light%20%2F%20Dark-0ea5e9.svg">
</p>

---

## Overview

**OLIST BI** is a multi-page business intelligence dashboard built in Python with Dash and Plotly. It turns the Olist e-commerce datasets into an interactive analytics workspace covering executive KPIs, geography, reviews, recommendations, payments, segmentation, cohorts, forecasting, and seller performance.

The current version is centered around:

- trustworthy analytics on the correct data grain
- a premium dual-theme interface with improved transitions
- a context-aware AI analyst panel
- automated regression coverage for core analytics behavior

---

## Recent Improvements

- **Corrected analytics grain**: the app now uses a cached multi-grain analytics bundle instead of collapsing multi-item orders into misleading first-item summaries.
- **Fixed date filtering**: the selected end date now includes the full final day.
- **Improved delivery KPIs**: on-time metrics are based on delivered orders instead of mixing in undelivered orders.
- **Context-aware AI Analyst**: the AI panel now reads the active page, filters, and headline metrics before answering.
- **Professional AI panel UI**: richer header, quick actions, live context card, better chat layout, and improved theme handling.
- **Stable theme transitions**: light and dark mode are applied early to reduce dark flashes during navigation and loading.
- **Cleaner loading experience**: page-level loading shells replaced the older fragmented per-chart loading feel.
- **Improved geography styling**: Brazil state choropleth now has a cleaner light-theme palette and clearer borders.
- **Larger readable tables**: table font sizes, spacing, and badges were increased across the dashboard.
- **Refactored structure**: shared shell and page helpers now live in `components/`.

---

## Core Features

- **Executive analytics**: revenue, orders, AOV, review score, delivery speed, and growth tracking.
- **Geographic intelligence**: Brazil state choropleth plus ranked city tables.
- **Customer sentiment**: review gauge, histogram, box plot, and word cloud.
- **Recommendations**: category-aware product suggestions and trending items.
- **Payments and delivery**: payment mix, delivery behavior, cancellations, and operational signals.
- **Customer segmentation**: RFM + K-Means clustering with actionable segment summaries.
- **Cohort retention**: delivered-order retention heatmaps and lifecycle signals.
- **Forecasting**: time-series forecasting with holdout backtest metrics.
- **Seller analytics**: seller leaderboard, state distribution, delivery performance, and satisfaction benchmarking.
- **AI dashboard copilot**: executive summaries, smart prompts, and context-aware answers with Gemini or local fallback mode.

---

## Architecture Highlights

### Multi-grain analytics bundle

The app now builds and caches a structured analytics bundle in `.cache/analytics_bundle.pkl`, including:

- `orders`
- `order_items`
- `payments`
- `seller_orders`
- pre-aggregated daily marts

This keeps each page on the correct grain and reduces repeated expensive preprocessing.

### Shared UI shell

Reusable layout and component helpers now live in:

- `components/shell.py`
- `components/ai_panel.py`
- `components/page_helpers.py`

This keeps page modules more focused and reduces repeated layout code.

### Theme-aware experience

The platform supports both `light` and `dark` mode using CSS variables and early theme hydration, including loaders and transitions.

### Regression-tested dashboard

Core analytics behavior and callback outputs are covered by regression tests under `tests/` and `test_dashboard_callbacks.py`.

---

## Technology Stack

| Domain | Technology |
| :--- | :--- |
| Frontend UI | Dash (Plotly) |
| Data Processing | Pandas, NumPy |
| Charts | Plotly Graph Objects, Plotly Express |
| Styling | Custom CSS variables and component styling |
| Machine Learning | Scikit-Learn |
| AI Assistant | Google GenAI SDK with fallback mode |
| NLP | WordCloud |
| Testing | Python `unittest` |

---

## Project Structure

```text
Big Data & Analytic/
|
|-- assets/                    # Theme, layout, component styling, logo
|-- components/                # Shared shell, AI panel, page helpers
|-- data/                      # Olist CSV datasets
|-- pages/                     # Dashboard pages
|   |-- overview.py
|   |-- geography.py
|   |-- reviews.py
|   |-- recommendations.py
|   |-- payments.py
|   |-- segmentation.py
|   |-- cohorts.py
|   |-- forecasting.py
|   `-- sellers.py
|-- tests/                     # Data integrity and regression tests
|-- utils/                     # Data loading, formatting, AI, ML, retention
|-- app.py                     # Dash entry point and callbacks
|-- requirements.txt
|-- SETUP.md
|-- CONTRIBUTING.md
`-- run.md
```

---

## Running The App

```powershell
cd "D:\programing\Graduation project\Big Data & Analytic"
venv\Scripts\python.exe app.py
```

Then open:

```text
http://127.0.0.1:8050/
```

---

## AI Analyst Notes

- If `GEMINI_API_KEY` is available, the AI panel uses Gemini.
- If the key is missing, the assistant still works in fallback mode.
- The AI panel is context-aware and receives:
  - active page
  - visible headline metrics
  - active filter summary

---

## Running Tests

```bash
python -m unittest tests.test_data_integrity test_dashboard_callbacks -v
```

Current regression coverage includes:

- data integrity checks
- callback output validation
- review filtering behavior
- forecasting context
- cohort retention assumptions
- seller and payment payload checks

---

## Documentation

- [SETUP.md](SETUP.md): local setup and troubleshooting
- [CONTRIBUTING.md](CONTRIBUTING.md): architecture and workflow rules
- [run.md](run.md): quick local run commands

---

<p align="center">
  <i>Built for data-driven decisions and polished analytical storytelling.</i>
</p>
