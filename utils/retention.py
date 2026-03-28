"""
Cohort retention and repeat-purchase analytics helpers.
"""

from __future__ import annotations

import pandas as pd

from utils.cleaner import filter_by_date


def prepare_delivered_orders(
    orders_df: pd.DataFrame, start_date: str | None = None, end_date: str | None = None
) -> pd.DataFrame:
    dff = orders_df.copy()
    if start_date and end_date:
        dff = filter_by_date(dff, start_date, end_date)
    return dff[dff["order_status"] == "delivered"].copy()


def build_cohort_table(
    orders_df: pd.DataFrame, start_date: str | None = None, end_date: str | None = None
) -> pd.DataFrame:
    delivered = prepare_delivered_orders(orders_df, start_date, end_date)
    delivered = delivered.dropna(subset=["customer_unique_id", "order_purchase_timestamp"])
    delivered["order_month"] = delivered["order_purchase_timestamp"].dt.to_period("M")

    first_order = delivered.groupby("customer_unique_id")["order_month"].min()
    cohort_df = delivered.merge(
        first_order.rename("cohort_month"),
        on="customer_unique_id",
        how="left",
    )
    cohort_df["month_number"] = (
        cohort_df["order_month"] - cohort_df["cohort_month"]
    ).apply(lambda value: value.n)
    return cohort_df


def build_retention_matrix(
    orders_df: pd.DataFrame, start_date: str | None = None, end_date: str | None = None
) -> tuple[pd.DataFrame, pd.DataFrame]:
    cohort_df = build_cohort_table(orders_df, start_date, end_date)

    grouped = (
        cohort_df.groupby(["cohort_month", "month_number"])["customer_unique_id"]
        .nunique()
        .reset_index(name="customers")
    )
    cohort_sizes = grouped[grouped["month_number"] == 0][
        ["cohort_month", "customers"]
    ].rename(columns={"customers": "cohort_size"})
    grouped = grouped.merge(cohort_sizes, on="cohort_month", how="left")
    grouped["retention_pct"] = grouped["customers"] / grouped["cohort_size"] * 100

    count_matrix = grouped.pivot(
        index="cohort_month", columns="month_number", values="customers"
    ).fillna(0)
    pct_matrix = grouped.pivot(
        index="cohort_month", columns="month_number", values="retention_pct"
    ).fillna(0)

    count_matrix.index = count_matrix.index.astype(str)
    pct_matrix.index = pct_matrix.index.astype(str)
    return pct_matrix, count_matrix


def get_retention_kpis(
    orders_df: pd.DataFrame, start_date: str | None = None, end_date: str | None = None
) -> dict[str, float]:
    cohort_df = build_cohort_table(orders_df, start_date, end_date)
    customer_orders = cohort_df.groupby("customer_unique_id")["order_id"].nunique()

    repeat_rate = (customer_orders.gt(1).mean() * 100) if len(customer_orders) else 0.0
    avg_orders = customer_orders.mean() if len(customer_orders) else 0.0
    active_customers = float(customer_orders.shape[0])

    pct_matrix, _ = build_retention_matrix(orders_df, start_date, end_date)
    latest_m1 = 0.0
    if 1 in pct_matrix.columns and not pct_matrix.empty:
        latest_m1 = float(pct_matrix[1].iloc[-1])

    return {
        "active_customers": active_customers,
        "repeat_rate_pct": float(repeat_rate),
        "avg_orders_per_customer": float(avg_orders),
        "latest_month_1_retention_pct": latest_m1,
    }
