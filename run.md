# Quick Run

## Start The App

```powershell
cd "D:\programing\Graduation project\Big Data & Analytic"
venv\Scripts\python.exe app.py
```

Open:

```text
http://127.0.0.1:8050/
```

## Run Tests

```powershell
cd "D:\programing\Graduation project\Big Data & Analytic"
venv\Scripts\python.exe -m unittest tests.test_data_integrity test_dashboard_callbacks -v
```

## Useful Notes

- If CSS or theme changes do not appear immediately, use `Ctrl + F5`.
- If you want Gemini-powered AI responses, set `GEMINI_API_KEY` before starting the app.
- If you need to rebuild cached analytics marts, delete `.cache/analytics_bundle.pkl` and restart the server.
