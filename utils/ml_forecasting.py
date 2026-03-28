"""
Time-series revenue forecasting with a chronological backtest.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_absolute_percentage_error, r2_score
from sklearn.preprocessing import StandardScaler


def build_time_series(df: pd.DataFrame) -> pd.DataFrame:
    ts = (
        df.dropna(subset=["order_purchase_timestamp", "total_order_value"])
        .assign(date=lambda x: x["order_purchase_timestamp"].dt.normalize())
        .groupby("date", as_index=False)["total_order_value"]
        .sum()
        .rename(columns={"total_order_value": "revenue"})
        .sort_values("date")
        .reset_index(drop=True)
    )

    full_range = pd.date_range(ts["date"].min(), ts["date"].max(), freq="D")
    ts = ts.set_index("date").reindex(full_range, fill_value=0).reset_index()
    ts.columns = ["date", "revenue"]
    ts["revenue_smooth"] = ts["revenue"].rolling(7, min_periods=1, center=True).mean()
    return ts


def _build_features(dates: pd.DatetimeIndex, start_index: int = 0) -> np.ndarray:
    t = np.arange(start_index, start_index + len(dates))
    t_year = 365.25
    t_week = 7.0
    return np.column_stack(
        [
            t,
            np.sin(2 * np.pi * t / t_year),
            np.cos(2 * np.pi * t / t_year),
            np.sin(2 * np.pi * t / t_week),
            np.cos(2 * np.pi * t / t_week),
            np.sin(4 * np.pi * t / t_year),
            np.cos(4 * np.pi * t / t_year),
            dates.month.values.astype(float),
            dates.dayofweek.values.astype(float),
        ]
    )


def _safe_mape(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    adjusted_true = np.where(y_true == 0, 1.0, y_true)
    return float(mean_absolute_percentage_error(adjusted_true, y_pred))


def _fit_ridge_model(dates: pd.DatetimeIndex, target: np.ndarray, start_index: int = 0):
    features = _build_features(dates, start_index=start_index)
    scaler = StandardScaler()
    scaled = scaler.fit_transform(features)
    model = Ridge(alpha=1.0)
    model.fit(scaled, target)
    return model, scaler


def forecast_revenue(ts_df: pd.DataFrame, horizon_days: int = 90):
    ts = ts_df.copy().reset_index(drop=True)
    horizon_days = int(horizon_days)

    if len(ts) < 60:
        raise ValueError("Forecasting requires at least 60 daily observations.")

    holdout_days = max(30, int(len(ts) * 0.15))
    holdout_days = min(holdout_days, len(ts) - 14)

    train = ts.iloc[:-holdout_days].copy()
    test = ts.iloc[-holdout_days:].copy()

    train_dates = pd.DatetimeIndex(train["date"])
    test_dates = pd.DatetimeIndex(test["date"])
    y_train = train["revenue_smooth"].to_numpy()
    y_test = test["revenue_smooth"].to_numpy()

    backtest_model, backtest_scaler = _fit_ridge_model(train_dates, y_train, start_index=0)
    x_test = _build_features(test_dates, start_index=len(train))
    y_test_pred = backtest_model.predict(backtest_scaler.transform(x_test))

    backtest_r2 = float(r2_score(y_test, y_test_pred))
    backtest_mae = float(mean_absolute_error(y_test, y_test_pred))
    backtest_mape = _safe_mape(y_test, y_test_pred)

    full_dates = pd.DatetimeIndex(ts["date"])
    y_full = ts["revenue_smooth"].to_numpy()
    full_model, full_scaler = _fit_ridge_model(full_dates, y_full, start_index=0)

    full_features = _build_features(full_dates, start_index=0)
    y_pred_in = full_model.predict(full_scaler.transform(full_features))
    residual_source = y_test - y_test_pred if len(test) > 1 else y_full - y_pred_in
    residuals_std = float(np.std(residual_source))

    last_date = ts["date"].max()
    future_dates = pd.date_range(
        last_date + pd.Timedelta(days=1), periods=horizon_days, freq="D"
    )
    x_future = _build_features(future_dates, start_index=len(ts))
    y_future = full_model.predict(full_scaler.transform(x_future))
    y_future = np.clip(y_future, 0, None)

    conf_mult = 1.96
    forecast_df = pd.DataFrame(
        {
            "date": future_dates,
            "predicted": y_future,
            "lower": np.clip(y_future - conf_mult * residuals_std, 0, None),
            "upper": y_future + conf_mult * residuals_std,
        }
    )

    hist_last_30 = ts.loc[ts["date"] >= (last_date - pd.Timedelta(days=30)), "revenue"].sum()
    forecast_total = float(forecast_df["predicted"].sum())
    growth_rate = (
        (forecast_df["predicted"].iloc[:30].sum() - hist_last_30) / max(hist_last_30, 1)
    ) * 100

    forecast_df["month"] = forecast_df["date"].dt.strftime("%Y-%m")
    monthly = (
        forecast_df.groupby("month", as_index=False)["predicted"]
        .sum()
        .reset_index(drop=True)
    )

    metrics = {
        "total_forecast_brl": forecast_total,
        "growth_pct": float(growth_rate),
        "peak_month": monthly.loc[monthly["predicted"].idxmax(), "month"],
        "peak_month_value": float(monthly["predicted"].max()),
        "avg_daily": float(forecast_df["predicted"].mean()),
        "confidence_pct": 95,
        "backtest_days": int(holdout_days),
        "r2_score": backtest_r2,
        "mae": backtest_mae,
        "mape": backtest_mape,
    }

    return ts, forecast_df, metrics, monthly
