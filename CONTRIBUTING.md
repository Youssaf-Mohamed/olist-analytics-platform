# Contributing to OLIST BI 🚀

Welcome to the **OLIST BI Analytics Platform**! We're thrilled to have you onboard. This guide outlines the workflow and architecture rules to help keep the codebase clean, professional, and easy to maintain as our team grows.

## 🏗️ Project Architecture Overview

The system is built on **Plotly Dash** and **Python**. We follow a strong modular structure to keep the main application file clean.

### Directory Structure
- **`/assets/`**: Contains all static files (CSS, images, fonts). Important: We use a custom, dark-theme Glassmorphism CSS system separated into multiple files (`01_base.css`, `02_layout.css`, etc.). **Do not use inline CSS** unless making dynamic color changes (e.g., in graphs or dynamic KPI logic).
- **`/pages/`**: Every major dashboard view (Sales, Geography, Recommendations, Segmentation) lives here as an independent file.
- **`/utils/`**: Shared Python utilities (`data_loader.py` for reading datasets, `cleaner.py` for formatting, etc.).
- **`app.py`**: The main entry point. **Do not put complex business logic or layout inside `app.py`.** It should only handle routing, the main layout wrapper (sidebar/topbar), and server initialization.

---

## 🔧 Development Workflow

### 1. Branching Strategy
We use a feature-branch workflow. **NEVER push directly to the `main` branch.**

- **Feature Work:** `feature/your-feature-name` (e.g., `feature/add-revenue-chart`)
- **Bug Fixes:** `bugfix/issue-name` (e.g., `bugfix/dropdown-z-index`)
- **Refactoring:** `refactor/component-name` (e.g., `refactor/clean-css`)

### 2. Making Changes
1. Checkout the latest `main` branch.
2. Create your branch: `git checkout -b feature/your-name`
3. Write your code following the **Style Guidelines** below.
4. Commit often, with clear, descriptive commit messages.

### 3. Creating a Pull Request (PR)
When your feature is complete:
1. Push your branch to GitHub.
2. Open a Pull Request targeting the `main` branch.
3. Provide a clear description of:
   - What you added/changed.
   - Any new dependencies added to `requirements.txt`.
   - Screenshots if you altered the UI.
4. Request a review from the Lead Developer/Admin.

---

## 🎨 Style & UI Guidelines

### Python (Backend)
- Follow **PEP 8** formatting guidelines.
- Use explicit variable names (e.g., `total_revenue` instead of `tr`).
- Document complex functions using docstrings.

### CSS (Frontend)
- **Avoid `!important` tags.** If a component isn't styling correctly, verify CSS specificity (e.g., use `#parent-id .child-class` instead of `.child-class !important`). Dash injects default inline styles, so use high-specificity selectors.
- Use the **CSS Variables** defined in `assets/01_base.css` (e.g., `var(--cyan)`, `var(--input-bg)`) rather than hardcoding hex colors. This ensures theme consistency.

### Dash Components
- We are migrating towards **Dash 4.x** standards.
- Ensure all inputs and filters use our custom `.filter-bar` and dark theme wrapper classes overrides.

---

## 🤝 Getting Help
If you get stuck on an issue, or you don’t understand how the Gemeni AI Integration in `utils/gemini_analyst.py` is caching data, please reach out to the project Lead or open an issue on GitHub.
