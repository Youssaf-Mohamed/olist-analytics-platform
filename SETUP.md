# Local Environment Setup Guide

This guide provides step-by-step instructions for running the **OLIST BI Analytics Platform** on your local machine.

## Prerequisites
- **Python 3.9+** (Ensure Python is added to your system PATH)
- **Git** (For cloning the repository)
- **Pip** (Python package installer)

---

## 🚀 Step-by-Step Installation

### 1. Clone the Repository
Open your terminal (Command Prompt, PowerShell, or Git Bash) and run:
```bash
git clone https://github.com/Youssaf-Mohamed/olist-analytics-platform.git
cd olist-analytics-platform
```

### 2. Create a Virtual Environment
It is highly recommended to use a virtual environment to avoid dependency conflicts.
```bash
# For Windows:
python -m venv venv
venv\Scripts\activate

# For Mac/Linux:
python3 -m venv venv
source venv/bin/activate
```
*(You will see `(venv)` appear at the beginning of your terminal prompt when activated).*

### 3. Install Dependencies
Install all required Python packages from the `requirements.txt` file:
```bash
pip install -r requirements.txt
```

### 4. Setup Environment Variables (Important)
The platform uses the **Gemini AI** API for the Smart Analyst Assistant. You must formulate an environment variable to run it.

For Windows (PowerShell):
```powershell
$env:GEMINI_API_KEY="YOUR_API_KEY_HERE"
```

For Windows (CMD):
```cmd
set GEMINI_API_KEY=YOUR_API_KEY_HERE
```

For Mac/Linux:
```bash
export GEMINI_API_KEY="YOUR_API_KEY_HERE"
```
*(Ask the project administrator/Youssaf for the development API key if you don't have one).*

### 5. Run the Application
Start the Dash server:
```bash
python app.py
```

### 6. Access the Dashboard
Once the console says `Dash is running`, open your web browser and navigate to:
👉 **[http://127.0.0.1:8050/](http://127.0.0.1:8050/)**

---

## 🛠️ Troubleshooting

- **`ModuleNotFoundError: No module named 'dash'`**: Your virtual environment is not activated, or you forgot to run `pip install -r requirements.txt`.
- **AI Analyst not responding**: Check if the `GEMINI_API_KEY` was correctly set in your terminal session before running `app.py`.
- **Data loading errors**: Ensure you have the required `.csv` or `.parquet` data files in the `data/processed` folder. If they are missing, reach out to the lead developer to get the data dump.
