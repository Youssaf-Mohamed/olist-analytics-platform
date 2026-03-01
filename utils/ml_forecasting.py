"""
utils/ml_forecasting.py
Time-series revenue forecasting using scikit-learn (Ridge regression
with Fourier + lag features). No extra library installs required.
"""

import pandas as pd
import numpy as np
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler


def build_time_series(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate master DataFrame into a daily revenue time-series.
    Returns DataFrame with columns: date, revenue
    """
    ts = (
        df.dropna(subset=["order_purchase_timestamp", "total_order_value"])
        .assign(date=lambda x: x["order_purchase_timestamp"].dt.normalize())
        .groupby("date")["total_order_value"]
        .sum()
        .reset_index()
        .rename(columns={"total_order_value": "revenue"})
        .sort_values("date")
    )

    # Reindex to fill missing days with 0
    full_range = pd.date_range(ts["date"].min(), ts["date"].max(), freq="D")
    ts = ts.set_index("date").reindex(full_range, fill_value=0).reset_index()
    ts.columns = ["date", "revenue"]

    # 7-day rolling average to smooth noise
    ts["revenue_smooth"] = ts["revenue"].rolling(7, min_periods=1, center=True).mean()
    return ts


def _build_features(dates: pd.DatetimeIndex) -> np.ndarray:
    """Build Fourier + trend features for a sequence of dates."""
    t = np.arange(len(dates))
    T_year = 365.25
    T_week = 7.0

    features = [
        t,  # linear trend
        np.sin(2 * np.pi * t / T_year),  # annual seasonality
        np.cos(2 * np.pi * t / T_year),
        np.sin(2 * np.pi * t / T_week),  # weekly seasonality
        np.cos(2 * np.pi * t / T_week),
        np.sin(4 * np.pi * t / T_year),  # bi-annual
        np.cos(4 * np.pi * t / T_year),
        (dates.month.values).astype(float),  # month of year
        (dates.dayofweek.values).astype(float),  # day of week
    ]
    return np.column_stack(features)


def forecast_revenue(ts_df: pd.DataFrame, horizon_days: int = 90):
    """
    Fit a Ridge regression model on historical smoothed revenue
    and predict `horizon_days` into the future.

    Returns:
        historical_df : original ts_df (date + revenue + revenue_smooth)
        forecast_df   : DataFrame with date, predicted, lower, upper columns
        metrics       : dict with summary stats
    """
    ts = ts_df.copy()
    dates_hist = pd.DatetimeIndex(ts["date"])
    X_hist = _build_features(dates_hist)
    y_hist = ts["revenue_smooth"].values

    # Scale
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_hist)

    # Fit
    model = Ridge(alpha=1.0)
    model.fit(X_scaled, y_hist)

    # In-sample residual std for confidence band
    y_pred_in = model.predict(X_scaled)
    residuals_std = np.std(y_hist - y_pred_in)

    # Future dates
    last_date = ts["date"].max()
    future_dates = pd.date_range(
        last_date + pd.Timedelta(days=1),
        periods=horizon_days,
        freq="D",
    )

    # Build future feature matrix (t continues from history)
    n_hist = len(ts)
    t_future = np.arange(n_hist, n_hist + horizon_days)
    T_year = 365.25
    T_week = 7.0

    features_future = [
        t_future,
        np.sin(2 * np.pi * t_future / T_year),
        np.cos(2 * np.pi * t_future / T_year),
        np.sin(2 * np.pi * t_future / T_week),
        np.cos(2 * np.pi * t_future / T_week),
        np.sin(4 * np.pi * t_future / T_year),
        np.cos(4 * np.pi * t_future / T_year),
        future_dates.month.values.astype(float),
        future_dates.dayofweek.values.astype(float),
    ]
    X_future = np.column_stack(features_future)
    X_future_scaled = scaler.transform(X_future)

    y_future = model.predict(X_future_scaled)
    y_future = np.clip(y_future, 0, None)  # revenue can't be negative

    conf_mult = 1.96  # 95% confidence interval
    forecast_df = pd.DataFrame(
        {
            "date": future_dates,
            "predicted": y_future,
            "lower": np.clip(y_future - conf_mult * residuals_std, 0, None),
            "upper": y_future + conf_mult * residuals_std,
        }
    )

    # ── Summary metrics ────────────────────────────────────────────────────────
    hist_last_30 = ts[ts["date"] >= (last_date - pd.Timedelta(days=30))][
        "revenue"
    ].sum()
    forecast_total = forecast_df["predicted"].sum()
    growth_rate = (
        (forecast_df["predicted"][:30].sum() - hist_last_30) / max(hist_last_30, 1)
    ) * 100

    # Monthly roll-up for the forecast period
    forecast_df["month"] = forecast_df["date"].dt.strftime("%Y-%m")
    monthly = forecast_df.groupby("month")["predicted"].sum().reset_index()

    metrics = {
        "total_forecast_brl": forecast_total,
        "growth_pct": growth_rate,
        "peak_month": monthly.loc[monthly["predicted"].idxmax(), "month"],
        "peak_month_value": monthly["predicted"].max(),
        "avg_daily": forecast_df["predicted"].mean(),
        "confidence_pct": 95,
    }

    return ts, forecast_df, metrics, monthly
