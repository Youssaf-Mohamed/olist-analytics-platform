# Local Setup Guide

This guide reflects the current project structure and the recent analytics and UI improvements.

## Prerequisites

- Python 3.9+
- `pip`
- Git

---

## 1. Open The Project

If the project already exists locally:

```powershell
cd "D:\programing\Graduation project\Big Data & Analytic"
```

If you are cloning it from a remote repository, clone first and then enter the project folder.

---

## 2. Create And Activate A Virtual Environment

Windows PowerShell:

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

Windows CMD:

```cmd
python -m venv venv
venv\Scripts\activate.bat
```

macOS / Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Prepare The Data Folder

The app expects the Olist CSV files directly inside:

```text
data/
```

The application now creates a cached analytics bundle automatically in:

```text
.cache/analytics_bundle.pkl
```

You do not need to create this file manually.

---

## 5. Optional AI Configuration

If you want Gemini-powered AI responses, set `GEMINI_API_KEY`.

PowerShell:

```powershell
$env:GEMINI_API_KEY="YOUR_API_KEY_HERE"
```

CMD:

```cmd
set GEMINI_API_KEY=YOUR_API_KEY_HERE
```

macOS / Linux:

```bash
export GEMINI_API_KEY="YOUR_API_KEY_HERE"
```

If the key is missing, the AI panel still works in fallback mode.

---

## 6. Run The Dashboard

```powershell
venv\Scripts\python.exe app.py
```

Then open:

```text
http://127.0.0.1:8050/
```

---

## 7. Run Tests

Run the regression suite:

```bash
python -m unittest tests.test_data_integrity test_dashboard_callbacks -v
```

The current tests cover:

- data integrity assumptions
- callback payload structure
- review filtering behavior
- forecasting context
- cohort and seller analytics outputs

---

## Troubleshooting

- **`ModuleNotFoundError`**: activate the virtual environment and reinstall dependencies.
- **App opens without the latest UI changes**: do a hard refresh with `Ctrl + F5`.
- **AI Analyst uses fallback answers**: `GEMINI_API_KEY` is missing or invalid.
- **Data load errors**: make sure the required Olist CSV files are present directly under `data/`.
- **Need to rebuild the cached marts**: delete `.cache/analytics_bundle.pkl` and restart the app.
- **Theme or loading colors look stale**: restart the app and hard refresh the browser.
