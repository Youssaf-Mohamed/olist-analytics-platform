"""
utils/recommender.py
Content-based and popularity-based product recommendation engine.
"""

import pandas as pd
from sklearn.preprocessing import MinMaxScaler

from utils.data_loader import load_master_data

# ── Shared product stats (computed once) ─────────────────────────────────────


def _build_product_stats(df: pd.DataFrame) -> pd.DataFrame:
    """
    Build a per-product summary table from the master DataFrame.
    Returns columns: product_id, category, avg_price, avg_rating,
                     total_sales, purchase_date_max
    """
    stats = (
        df.groupby("product_id")
        .agg(
            category=("product_category_name_english", "first"),
            avg_price=("item_price", "mean"),
            avg_rating=("review_score", "mean"),
            total_sales=("order_id", "nunique"),
            purchase_date_max=("order_purchase_timestamp", "max"),
        )
        .reset_index()
    )
    stats["category"] = stats["category"].fillna("not_defined")
    return stats


# ── Recommendation 1: Content-Based ──────────────────────────────────────────


def get_content_recommendations(
    category: str,
    min_price: float = 0.0,
    max_price: float = 10_000.0,
    top_n: int = 5,
) -> list[dict]:
    """
    Return top_n products in `category` within the price range,
    scored by: (avg_review_score × 0.6) + (normalised_sales_count × 0.4).

    Each result has: product_id, category, avg_price, avg_rating,
                     total_sales, score
    """
    df = load_master_data()
    stats = _build_product_stats(df)

    # Filter by category and price
    mask = (
        (stats["category"].str.lower() == str(category).lower())
        & (stats["avg_price"] >= min_price)
        & (stats["avg_price"] <= max_price)
    )
    filtered = stats.loc[mask].copy()

    if filtered.empty:
        return []

    # Normalise sales count to [0, 1]
    if filtered["total_sales"].max() > filtered["total_sales"].min():
        scaler = MinMaxScaler()
        filtered["sales_norm"] = scaler.fit_transform(
            filtered[["total_sales"]]
        ).flatten()
    else:
        filtered["sales_norm"] = 1.0

    # Score
    filtered["score"] = (filtered["avg_rating"] / 5.0) * 0.6 + filtered[
        "sales_norm"
    ] * 0.4

    top = filtered.nlargest(top_n, "score")[
        ["product_id", "category", "avg_price", "avg_rating", "total_sales", "score"]
    ].reset_index(drop=True)

    return top.to_dict(orient="records")


# ── Recommendation 2: Trending Products ──────────────────────────────────────


def get_trending_products(days: int = 90, top_n: int = 5) -> list[dict]:
    """
    Return top_n most-purchased products in the last `days` days
    (relative to the latest order date in the dataset).

    Each result has: product_id, category, avg_price, avg_rating,
                     total_sales, score (= normalised sales count)
    """
    df = load_master_data()

    max_date = df["order_purchase_timestamp"].max()
    cutoff = max_date - pd.Timedelta(days=days)

    recent = df.loc[df["order_purchase_timestamp"] >= cutoff].copy()

    if recent.empty:
        return []

    stats = _build_product_stats(recent)

    if stats["total_sales"].max() > stats["total_sales"].min():
        scaler = MinMaxScaler()
        stats["score"] = scaler.fit_transform(stats[["total_sales"]]).flatten()
    else:
        stats["score"] = 1.0

    top = stats.nlargest(top_n, "total_sales")[
        ["product_id", "category", "avg_price", "avg_rating", "total_sales", "score"]
    ].reset_index(drop=True)

    return top.to_dict(orient="records")
