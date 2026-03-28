# Contributing To OLIST BI

This guide reflects the current architecture after the analytics, theme, loading, AI, and refactoring updates.

## Project Architecture

The project is organized into clear layers:

- `assets/`: theme variables, layout styling, component styling, overrides, responsive utilities
- `components/`: shared app shell, AI panel, and reusable page helpers
- `pages/`: page-specific layouts and callbacks
- `utils/`: data loading, formatting, ML, retention, AI helpers
- `tests/`: regression tests for analytics and callback outputs
- `app.py`: application bootstrap and high-level callback wiring

## Core Rules

### 1. Keep `app.py` focused

`app.py` should stay focused on:

- Dash initialization
- top-level stores
- high-level callbacks
- theme synchronization
- root app wiring

Do not move large page-specific business logic into `app.py`.

### 2. Use the correct data grain

Prefer `load_data_bundle()` and choose the proper dataset:

- `orders` for order-level KPIs
- `order_items` for category and item analysis
- `payments` for payment-type analysis
- `seller_orders` for seller analytics

Do not reintroduce old shortcuts like "first product", "first seller", or "first payment type" into analytics logic.

### 3. Reuse shared UI helpers

Before adding repeated layout markup, check:

- `components/shell.py`
- `components/ai_panel.py`
- `components/page_helpers.py`

Use shared wrappers for page loading and chart loading instead of duplicating the same Dash structure across pages.

### 4. Respect both themes

Every visual change must work in:

- `dark` mode
- `light` mode

Rules:

- use CSS variables from `assets/01_base.css`
- avoid hardcoded dark-only text or overlay colors
- verify charts, tables, badges, loaders, and hover labels in both themes
- if a chart uses custom colors, explicitly review the light-mode version

### 5. Keep AI context structured

When a page returns AI context, keep the payload structured as:

- `page`
- `filters`
- `headline_metrics`

This keeps the AI Analyst predictable and useful.

---

## Page Implementation Pattern

Each page should ideally follow this shape:

1. register the page
2. load shared data once at module level
3. build a readable layout
4. use shared wrappers for loading states
5. keep callbacks grouped and readable
6. return page context when needed

If a callback gets too large, split chart construction into local helper functions.

---

## Styling Guidelines

### Python

- follow PEP 8
- prefer explicit variable names
- keep callbacks readable
- document non-trivial helpers with short docstrings

### CSS

- prefer CSS variables over hardcoded hex values
- avoid unnecessary inline styling
- update both theme variants when changing components with strong visual identity

### Tables

- keep table typography readable
- prefer shared `.data-table` styles for HTML tables
- if you use `go.Table`, make sure header, cell colors, and font sizes are theme-aware

---

## Testing Requirements

Before finalizing meaningful work, run:

```bash
python -m unittest tests.test_data_integrity test_dashboard_callbacks -v
```

At minimum, verify:

- imports still work
- page callbacks return valid shapes
- analytics logic still respects the corrected data model
- UI changes remain readable in both light and dark mode

---

## Pull Request Checklist

Include in your PR:

- what changed
- why it changed
- whether analytics behavior changed
- screenshots for UI changes
- any dependency or environment changes
- confirmation that tests passed

---

## Getting Help

If you are unsure about:

- which dataset grain to use
- where a shared helper should live
- how to keep a visual change theme-safe
- how AI context is assembled

ask early before adding duplicated or misleading logic.
