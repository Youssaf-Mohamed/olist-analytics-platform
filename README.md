<h1 align="center">
  <img src="assets/logo.svg" alt="Olist BI Logo" width="128" />
  <br>
  OLIST BI Analytics Platform
</h1>

<p align="center">
  <strong>A polished Dash business intelligence platform for Olist marketplace data, combining trustworthy analytics, AI-assisted insights, and a premium dual-theme dashboard experience.</strong>
</p>

<p align="center">
  <a href="#overview">Overview</a> •
  <a href="#features">Features</a> •
  <a href="#screenshots">Screenshots</a> •
  <a href="#quick-start">Quick Start</a> •
  <a href="#testing">Testing</a>
</p>

<p align="center">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.9+-yellow.svg">
  <img alt="Dash" src="https://img.shields.io/badge/Dash-Plotly-blue.svg">
  <img alt="UI" src="https://img.shields.io/badge/UI-Light%20%2F%20Dark-0ea5e9.svg">
  <img alt="Tests" src="https://img.shields.io/badge/Tests-Unittest-success.svg">
  <img alt="License" src="https://img.shields.io/badge/License-MIT-black.svg">
</p>

---

## Overview

**OLIST BI** is a multi-page analytics dashboard built with Python, Dash, Plotly, and machine learning utilities for the Brazilian Olist marketplace dataset.

It is designed to feel like a modern decision-support workspace rather than a collection of disconnected charts. The platform combines:

- corrected and trustworthy analytics on the proper data grain
- synchronized filtering across pages
- premium light and dark themes
- context-aware AI guidance
- regression-tested dashboard behavior

---

## Features

- **Executive overview** with revenue, order trends, AOV, review score, and delivery signals.
- **Geographic analytics** with Brazil state choropleth and city-level breakdowns.
- **Review intelligence** including sentiment-oriented scoring visuals, distributions, and text summaries.
- **Recommendations** for product discovery and trend-based suggestions.
- **Payments and operations** analysis covering payment behavior, shipping timing, and fulfillment patterns.
- **Customer segmentation** using RFM-style features and clustering outputs.
- **Cohort retention** tracking for delivered orders across customer lifecycle periods.
- **Forecasting** with backtest-aware evaluation instead of misleading train-only metrics.
- **Seller analytics** for delivery, satisfaction, and regional performance benchmarking.
- **AI Analyst panel** with quick actions, page-aware context, and fallback responses when Gemini is unavailable.

---

## Recent Improvements

- Fixed end-date filtering so the selected last day is fully included.
- Corrected misleading multi-item and multi-payment aggregation behavior.
- Improved delivery KPI accuracy by evaluating on-time rates on delivered orders.
- Refactored shared layout logic into `components/`.
- Redesigned the AI panel to feel more like a premium dashboard copilot.
- Reduced dark-theme flashes during navigation with early theme hydration.
- Improved loading experience with cleaner page-level transitions.
- Enhanced light-mode readability, table sizing, and map styling.
- Added regression tests for dashboard callbacks and analytics assumptions.

---

## Screenshots

Add screenshots here for a stronger GitHub presentation. Recommended captures:

- `Overview` dashboard
- `Geography` choropleth in light mode
- `AI Analyst` panel
- `Forecasting` page
- `Sellers` page

Example structure:

```text
docs/screenshots/overview.png
docs/screenshots/geography-light.png
docs/screenshots/ai-panel.png
docs/screenshots/forecasting.png
docs/screenshots/sellers.png
```

Then reference them in the README with standard markdown images.

---

## Architecture Highlights

### Multi-grain analytics bundle

The application builds and caches a structured analytics bundle in `.cache/analytics_bundle.pkl`. This keeps pages on the right analytical grain and avoids repeatedly rebuilding expensive joins and marts.

Included views now cover:

- `orders`
- `order_items`
- `payments`
- `seller_orders`
- pre-aggregated daily marts

### Shared UI shell

Reusable interface logic lives in:

- `components/shell.py`
- `components/ai_panel.py`
- `components/page_helpers.py`

This reduces duplication and keeps page modules more focused.

### Theme-safe rendering

The dashboard supports both `light` and `dark` modes using CSS variables, early theme hydration, and chart-aware styling so transitions stay visually stable.

### Regression-tested behavior

Core analytics and callback outputs are covered by tests under `tests/` and `test_dashboard_callbacks.py`.

---

## Technology Stack

| Domain | Technology |
| :--- | :--- |
| Frontend UI | Dash, Plotly |
| Data Processing | Pandas, NumPy |
| Machine Learning | Scikit-Learn |
| AI Assistant | Google GenAI SDK with fallback mode |
| NLP | WordCloud |
| Testing | Python `unittest` |
| Styling | Custom CSS architecture |

---

## Project Structure

```text
Big Data & Analytic/
|
|-- assets/                    # Theme, layout, components, logo
|-- components/                # Shared shell, AI panel, page wrappers
|-- data/                      # Olist CSV datasets
|-- pages/                     # Dashboard pages
|-- tests/                     # Regression tests
|-- utils/                     # Data, AI, ML, retention helpers
|-- app.py                     # Dash entry point
|-- README.md
|-- SETUP.md
|-- CONTRIBUTING.md
`-- run.md
```

---

## Quick Start

```powershell
cd "D:\programing\Graduation project\Big Data & Analytic"
venv\Scripts\python.exe app.py
```

Then open:

```text
http://127.0.0.1:8050/
```

For full local setup, see [SETUP.md](SETUP.md).

---

## AI Analyst

- If `GEMINI_API_KEY` is set, the assistant uses Gemini.
- If the key is missing, the panel still works in fallback mode.
- The panel is context-aware and can consume:
  - active page
  - active filters
  - headline metrics

---

## Testing

Run:

```bash
python -m unittest tests.test_data_integrity test_dashboard_callbacks -v
```

Current coverage includes:

- data integrity checks
- callback output validation
- review filtering behavior
- forecasting context
- retention assumptions
- seller and payment payload checks

---

## Roadmap

- add report export workflows
- expand screenshot and demo assets
- introduce GitHub Actions quality gates
- improve AI memory and guided analysis flows
- support deployment-ready configuration

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for architecture and contribution guidance.

---

## License

This project is licensed under the [MIT License](LICENSE).

---

<p align="center">
  <i>Built for polished analytical storytelling and practical decision support.</i>
</p>
