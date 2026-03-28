"""
Product recommendation helpers built on item-level analytics data.
"""

from __future__ import annotations

import pandas as pd
from sklearn.preprocessing import MinMaxScaler

from utils.data_loader import load_data_bundle


def _get_item_data() -> pd.DataFrame:
    return load_data_bundle()["order_items"]


def _build_product_stats(df: pd.DataFrame) -> pd.DataFrame:
    stats = (
        df.groupby("product_id", as_index=False)
        .agg(
            category=("product_category_name_english", "first"),
            avg_price=("price", "mean"),
            avg_rating=("review_score", "mean"),
            total_sales=("order_id", "nunique"),
            purchase_date_max=("order_purchase_timestamp", "max"),
        )
        .reset_index(drop=True)
    )
    stats["category"] = stats["category"].fillna("Not Defined")
    stats["avg_rating"] = stats["avg_rating"].fillna(0)
    return stats


def get_content_recommendations(
    category: str,
    min_price: float = 0.0,
    max_price: float = 10_000.0,
    top_n: int = 5,
) -> list[dict]:
    df = _get_item_data()
    stats = _build_product_stats(df)

    filtered = stats.loc[
        (stats["category"].str.lower() == str(category).lower())
        & (stats["avg_price"] >= min_price)
        & (stats["avg_price"] <= max_price)
    ].copy()

    if filtered.empty:
        return []

    if filtered["total_sales"].max() > filtered["total_sales"].min():
        scaler = MinMaxScaler()
        filtered["sales_norm"] = scaler.fit_transform(
            filtered[["total_sales"]]
        ).ravel()
    else:
        filtered["sales_norm"] = 1.0

    filtered["score"] = (filtered["avg_rating"] / 5.0) * 0.6 + (
        filtered["sales_norm"] * 0.4
    )

    top = filtered.nlargest(top_n, "score")[
        ["product_id", "category", "avg_price", "avg_rating", "total_sales", "score"]
    ]
    return top.reset_index(drop=True).to_dict(orient="records")


def get_trending_products(days: int = 90, top_n: int = 5) -> list[dict]:
    df = _get_item_data()
    max_date = df["order_purchase_timestamp"].max()
    cutoff = max_date - pd.Timedelta(days=days)

    recent = df.loc[df["order_purchase_timestamp"] >= cutoff].copy()
    if recent.empty:
        return []

    stats = _build_product_stats(recent)
    if stats["total_sales"].max() > stats["total_sales"].min():
        scaler = MinMaxScaler()
        stats["score"] = scaler.fit_transform(stats[["total_sales"]]).ravel()
    else:
        stats["score"] = 1.0

    top = stats.nlargest(top_n, "total_sales")[
        ["product_id", "category", "avg_price", "avg_rating", "total_sales", "score"]
    ]
    return top.reset_index(drop=True).to_dict(orient="records")
