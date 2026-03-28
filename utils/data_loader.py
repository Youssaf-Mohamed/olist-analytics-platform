"""
Shared data loading, enrichment, and caching utilities.

The project needs multiple analytical grains:
- orders: one row per order
- order_items: one row per order item
- payments: one row per payment record
- seller_orders: one row per (order, seller)
"""

from __future__ import annotations

import pickle
from pathlib import Path
from typing import Any

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
CACHE_FILE = ROOT / ".cache" / "analytics_bundle.pkl"
CACHE_SCHEMA_VERSION = 3

DATA_FILES = [
    "olist_orders_dataset.csv",
    "olist_order_items_dataset.csv",
    "olist_customers_dataset.csv",
    "olist_products_dataset.csv",
    "olist_sellers_dataset.csv",
    "olist_order_reviews_dataset.csv",
    "olist_order_payments_dataset.csv",
    "olist_geolocation_dataset.csv",
    "product_category_name_translation.csv",
]

REQUIRED_BUNDLE_KEYS = {
    "orders",
    "order_items",
    "payments",
    "seller_orders",
    "agg_orders_daily",
    "agg_status_daily",
    "agg_dow_hour_daily",
    "agg_category_daily",
    "agg_state_daily",
    "agg_city_daily",
    "agg_payments_daily",
    "agg_delivery_state_daily",
    "agg_cancellations_daily",
    "agg_scatter_orders_sample",
}

ORDER_DATE_COLS = [
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date",
]

WINDOW_START = pd.Timestamp("2017-01-01")
WINDOW_END_EXCLUSIVE = pd.Timestamp("2018-09-01")

_MEMORY_CACHE: dict[str, Any] = {}


def _read_csv(filename: str, parse_dates: list[str] | None = None) -> pd.DataFrame:
    path = DATA_DIR / filename
    if not path.exists():
        raise FileNotFoundError(
            f"Missing dataset file: {path}\n"
            "Please place all 9 Olist CSV files inside the data/ folder."
        )

    kwargs: dict[str, Any] = {"low_memory": False}
    if parse_dates:
        kwargs["parse_dates"] = parse_dates
    return pd.read_csv(path, **kwargs)


def _source_signature() -> dict[str, tuple[int, int]]:
    signature: dict[str, tuple[int, int]] = {}
    for filename in DATA_FILES:
        path = DATA_DIR / filename
        stat = path.stat()
        signature[filename] = (stat.st_mtime_ns, stat.st_size)
    return signature


def _load_cached_bundle() -> dict[str, pd.DataFrame] | None:
    if not CACHE_FILE.exists():
        return None

    try:
        with open(CACHE_FILE, "rb") as handle:
            payload = pickle.load(handle)
    except Exception as exc:
        print(f"[data_loader] Cache read failed ({exc}), rebuilding bundle.")
        return None

    if payload.get("schema_version") != CACHE_SCHEMA_VERSION:
        print("[data_loader] Cache version changed, rebuilding analytics bundle.")
        return None

    if payload.get("signature") != _source_signature():
        print("[data_loader] Source data changed, rebuilding bundle cache.")
        return None

    bundle = payload.get("bundle")
    if not isinstance(bundle, dict):
        return None
    if not REQUIRED_BUNDLE_KEYS.issubset(bundle.keys()):
        print("[data_loader] Cache schema changed, rebuilding analytics bundle.")
        return None

    print("[data_loader] Loaded analytics bundle from cache.")
    return bundle


def _save_cached_bundle(bundle: dict[str, pd.DataFrame]) -> None:
    CACHE_FILE.parent.mkdir(exist_ok=True)
    payload = {
        "schema_version": CACHE_SCHEMA_VERSION,
        "signature": _source_signature(),
        "bundle": bundle,
    }
    with open(CACHE_FILE, "wb") as handle:
        pickle.dump(payload, handle, protocol=pickle.HIGHEST_PROTOCOL)
    print(f"[data_loader] Cached analytics bundle to {CACHE_FILE}")


def _apply_common_time_features(df: pd.DataFrame) -> pd.DataFrame:
    enriched = df.copy()

    delivered_mask = (
        enriched["order_status"].eq("delivered")
        & enriched["order_delivered_customer_date"].notna()
        & enriched["order_estimated_delivery_date"].notna()
    )

    delivery_days = (
        enriched["order_delivered_customer_date"] - enriched["order_purchase_timestamp"]
    ).dt.total_seconds() / 86_400
    delivery_days = delivery_days.where(delivered_mask)
    delivery_days = delivery_days.clip(lower=0)

    is_on_time = (
        enriched["order_delivered_customer_date"]
        <= enriched["order_estimated_delivery_date"]
    ).where(delivered_mask)

    enriched["delivery_days"] = delivery_days
    enriched["is_on_time"] = pd.Series(is_on_time, index=enriched.index).astype(
        "boolean"
    )
    enriched["order_date"] = enriched["order_purchase_timestamp"].dt.floor("D")
    enriched["month_year"] = enriched["order_purchase_timestamp"].dt.strftime("%Y-%m")
    enriched["purchase_year"] = enriched["order_purchase_timestamp"].dt.year
    enriched["purchase_month"] = enriched["order_purchase_timestamp"].dt.month
    enriched["purchase_dow"] = enriched["order_purchase_timestamp"].dt.day_name()
    enriched["purchase_hour"] = enriched["order_purchase_timestamp"].dt.hour
    return enriched


def _optimize_frame(df: pd.DataFrame) -> pd.DataFrame:
    optimized = df.copy()
    for column in optimized.select_dtypes(include="object").columns:
        if column in {"payment_type"}:
            continue
        try:
            unique_ratio = optimized[column].nunique(dropna=False) / max(len(optimized), 1)
        except TypeError:
            continue
        if unique_ratio <= 0.4:
            optimized[column] = optimized[column].astype("category")

    for column in optimized.select_dtypes(include="integer").columns:
        optimized[column] = pd.to_numeric(optimized[column], downcast="integer")

    for column in optimized.select_dtypes(include="floating").columns:
        if column in {"payment_value"}:
            continue
        optimized[column] = pd.to_numeric(optimized[column], downcast="float")

    return optimized


def _build_aggregate_tables(
    orders_df: pd.DataFrame,
    order_items_df: pd.DataFrame,
    payments_df: pd.DataFrame,
) -> dict[str, pd.DataFrame]:
    orders_perf = orders_df.copy()
    orders_perf["review_present"] = orders_perf["review_score"].notna().astype("int8")
    orders_perf["review_score_filled"] = orders_perf["review_score"].fillna(0.0)
    orders_perf["delivered_order"] = orders_perf["order_status"].eq("delivered").astype(
        "int8"
    )
    orders_perf["on_time_order"] = (
        orders_perf["is_on_time"].fillna(False).astype("int8")
    )

    orders_daily = (
        orders_perf.groupby("order_date", as_index=False)
        .agg(
            revenue_sum=("total_order_value", "sum"),
            order_count=("order_id", "nunique"),
            review_sum=("review_score_filled", "sum"),
            review_count=("review_present", "sum"),
            delivered_count=("delivered_order", "sum"),
            on_time_count=("on_time_order", "sum"),
        )
        .reset_index(drop=True)
    )

    status_daily = (
        orders_df.groupby(["order_date", "order_status"], as_index=False)
        .agg(order_count=("order_id", "nunique"))
        .reset_index(drop=True)
    )

    dow_hour_daily = (
        orders_df.groupby(["order_date", "purchase_dow", "purchase_hour"], as_index=False)
        .agg(revenue_sum=("total_order_value", "sum"))
        .reset_index(drop=True)
    )

    category_daily = (
        order_items_df.groupby(
            ["order_date", "product_category_name_english"], as_index=False
        )
        .agg(revenue_sum=("line_total", "sum"))
        .reset_index(drop=True)
    )

    state_source = orders_perf[
        [
            "order_date",
            "customer_state",
            "total_order_value",
            "order_id",
            "review_score_filled",
            "review_present",
        ]
    ].copy()
    state_daily = (
        state_source.groupby(["order_date", "customer_state"], as_index=False)
        .agg(
            revenue_sum=("total_order_value", "sum"),
            order_count=("order_id", "nunique"),
            review_sum=("review_score_filled", "sum"),
            review_count=("review_present", "sum"),
        )
        .reset_index(drop=True)
    )

    city_source = orders_perf[
        [
            "order_date",
            "customer_city",
            "customer_state",
            "total_order_value",
            "order_id",
            "review_score_filled",
            "review_present",
        ]
    ].copy()
    city_daily = (
        city_source.groupby(["order_date", "customer_city", "customer_state"], as_index=False)
        .agg(
            revenue_sum=("total_order_value", "sum"),
            order_count=("order_id", "nunique"),
            review_sum=("review_score_filled", "sum"),
            review_count=("review_present", "sum"),
        )
        .reset_index(drop=True)
    )

    payments_daily = (
        payments_df.groupby(["order_date", "payment_type"], as_index=False)
        .agg(payment_value_sum=("payment_value", "sum"))
        .reset_index(drop=True)
    )

    delivered = orders_df[orders_df["order_status"] == "delivered"].copy()
    delivered["delivery_days_filled"] = delivered["delivery_days"].fillna(0.0)
    delivery_state_daily = (
        delivered.groupby(["order_date", "customer_state"], as_index=False)
        .agg(
            delivery_days_sum=("delivery_days_filled", "sum"),
            delivered_count=("order_id", "nunique"),
        )
        .reset_index(drop=True)
    )

    cancellations_daily = (
        orders_df[orders_df["order_status"] == "canceled"]
        .groupby("order_date", as_index=False)
        .agg(canceled_orders=("order_id", "nunique"))
        .reset_index(drop=True)
    )

    scatter_source = orders_df.dropna(subset=["total_order_value", "delivery_days"]).copy()
    if len(scatter_source) > 12_000:
        scatter_source = scatter_source.sample(12_000, random_state=42)

    return {
        "agg_orders_daily": _optimize_frame(orders_daily),
        "agg_status_daily": _optimize_frame(status_daily),
        "agg_dow_hour_daily": _optimize_frame(dow_hour_daily),
        "agg_category_daily": _optimize_frame(category_daily),
        "agg_state_daily": _optimize_frame(state_daily),
        "agg_city_daily": _optimize_frame(city_daily),
        "agg_payments_daily": _optimize_frame(payments_daily),
        "agg_delivery_state_daily": _optimize_frame(delivery_state_daily),
        "agg_cancellations_daily": _optimize_frame(cancellations_daily),
        "agg_scatter_orders_sample": _optimize_frame(scatter_source.reset_index(drop=True)),
    }


def _build_bundle() -> dict[str, pd.DataFrame]:
    print("[data_loader] Loading source CSV files...")

    orders = _read_csv("olist_orders_dataset.csv", parse_dates=ORDER_DATE_COLS)
    orders = orders.loc[
        (orders["order_purchase_timestamp"] >= WINDOW_START)
        & (orders["order_purchase_timestamp"] < WINDOW_END_EXCLUSIVE)
    ].copy()

    valid_order_ids = set(orders["order_id"])

    customers = _read_csv("olist_customers_dataset.csv")[
        [
            "customer_id",
            "customer_unique_id",
            "customer_city",
            "customer_state",
            "customer_zip_code_prefix",
        ]
    ]

    products = _read_csv("olist_products_dataset.csv")[
        [
            "product_id",
            "product_category_name",
            "product_weight_g",
            "product_length_cm",
            "product_height_cm",
            "product_width_cm",
        ]
    ]
    products["product_category_name"] = products["product_category_name"].fillna(
        "not_defined"
    )

    translation = _read_csv("product_category_name_translation.csv")
    products = products.merge(translation, on="product_category_name", how="left")
    products["product_category_name_english"] = (
        products["product_category_name_english"]
        .fillna(products["product_category_name"])
        .str.replace("_", " ")
        .str.title()
    )

    sellers = _read_csv("olist_sellers_dataset.csv")[
        ["seller_id", "seller_city", "seller_state"]
    ]

    reviews_raw = _read_csv("olist_order_reviews_dataset.csv")
    reviews_raw = reviews_raw[reviews_raw["order_id"].isin(valid_order_ids)].copy()
    reviews = (
        reviews_raw.groupby("order_id", as_index=False)
        .agg(
            review_score=("review_score", "mean"),
            review_comment=("review_comment_message", "first"),
            review_count=("review_id", "count"),
        )
        .reset_index(drop=True)
    )

    payments_raw = _read_csv("olist_order_payments_dataset.csv")
    payments_raw = payments_raw[payments_raw["order_id"].isin(valid_order_ids)].copy()
    payments = (
        payments_raw.groupby("order_id", as_index=False)
        .agg(
            payment_value=("payment_value", "sum"),
            payment_installments=("payment_installments", "max"),
            payment_type_primary=("payment_type", "first"),
            payment_type_count=("payment_type", "nunique"),
            payment_types=("payment_type", lambda s: sorted(set(s.dropna()))),
        )
        .reset_index(drop=True)
    )
    payments["payment_types_label"] = payments["payment_types"].apply(
        lambda values: ", ".join(values) if values else "not_defined"
    )
    payments["has_multi_payment_types"] = payments["payment_type_count"] > 1

    geo = _read_csv("olist_geolocation_dataset.csv")
    geo = (
        geo.groupby("geolocation_zip_code_prefix", as_index=False)
        .first()[
            [
                "geolocation_zip_code_prefix",
                "geolocation_lat",
                "geolocation_lng",
                "geolocation_state",
            ]
        ]
        .reset_index(drop=True)
    )

    items_raw = _read_csv("olist_order_items_dataset.csv")
    items_raw = items_raw[items_raw["order_id"].isin(valid_order_ids)].copy()
    items_raw["line_total"] = items_raw["price"] + items_raw["freight_value"]

    item_summary = (
        items_raw.groupby("order_id", as_index=False)
        .agg(
            item_price=("price", "sum"),
            item_freight=("freight_value", "sum"),
            total_order_value=("line_total", "sum"),
            num_items=("order_item_id", "count"),
            num_products=("product_id", "nunique"),
            num_sellers=("seller_id", "nunique"),
        )
        .reset_index(drop=True)
    )

    print("[data_loader] Building order-level analytics table...")
    orders_df = (
        orders.merge(item_summary, on="order_id", how="left")
        .merge(customers, on="customer_id", how="left")
        .merge(reviews, on="order_id", how="left")
        .merge(payments, on="order_id", how="left")
        .merge(
            geo.rename(
                columns={
                    "geolocation_zip_code_prefix": "customer_zip_code_prefix",
                    "geolocation_lat": "customer_lat",
                    "geolocation_lng": "customer_lng",
                }
            ),
            on="customer_zip_code_prefix",
            how="left",
        )
    )

    numeric_fill = {
        "item_price": 0.0,
        "item_freight": 0.0,
        "total_order_value": 0.0,
        "num_items": 0,
        "num_products": 0,
        "num_sellers": 0,
        "payment_value": 0.0,
        "payment_installments": 0.0,
        "payment_type_count": 0,
        "review_count": 0,
    }
    for column, value in numeric_fill.items():
        orders_df[column] = orders_df[column].fillna(value)

    for column in ["num_items", "num_products", "num_sellers", "payment_type_count", "review_count"]:
        orders_df[column] = orders_df[column].astype(int)

    orders_df["payment_type_primary"] = orders_df["payment_type_primary"].fillna(
        "not_defined"
    )
    orders_df["payment_types_label"] = orders_df["payment_types_label"].fillna(
        "not_defined"
    )
    orders_df["has_multi_payment_types"] = orders_df["has_multi_payment_types"].fillna(
        False
    )
    orders_df["review_comment"] = orders_df["review_comment"].fillna("")
    orders_df = _apply_common_time_features(orders_df)

    order_context = orders_df[
        [
            "order_id",
            "order_status",
            "order_purchase_timestamp",
            "order_approved_at",
            "order_delivered_carrier_date",
            "order_delivered_customer_date",
            "order_estimated_delivery_date",
            "customer_id",
            "customer_unique_id",
            "customer_city",
            "customer_state",
            "customer_zip_code_prefix",
            "customer_lat",
            "customer_lng",
            "review_score",
            "review_comment",
            "review_count",
            "delivery_days",
            "is_on_time",
            "order_date",
            "month_year",
            "purchase_year",
            "purchase_month",
            "purchase_dow",
            "purchase_hour",
        ]
    ].copy()

    print("[data_loader] Building item-level analytics table...")
    order_items_df = (
        items_raw.merge(order_context, on="order_id", how="left")
        .merge(products, on="product_id", how="left")
        .merge(sellers, on="seller_id", how="left")
        .reset_index(drop=True)
    )
    order_items_df["product_category_name"] = order_items_df[
        "product_category_name"
    ].fillna("not_defined")
    order_items_df["product_category_name_english"] = order_items_df[
        "product_category_name_english"
    ].fillna("Not Defined")
    order_items_df["review_comment"] = order_items_df["review_comment"].fillna("")

    print("[data_loader] Building payment-level analytics table...")
    payment_context = orders_df[
        [
            "order_id",
            "order_purchase_timestamp",
            "order_date",
            "order_status",
            "customer_state",
            "customer_city",
            "month_year",
        ]
    ].copy()
    payments_df = payments_raw.merge(payment_context, on="order_id", how="left")

    print("[data_loader] Building seller-order analytics table...")
    seller_orders_df = (
        order_items_df.groupby(["order_id", "seller_id"], as_index=False)
        .agg(
            seller_revenue=("line_total", "sum"),
            seller_item_count=("order_item_id", "count"),
            seller_product_count=("product_id", "nunique"),
            seller_city=("seller_city", "first"),
            seller_state=("seller_state", "first"),
            order_purchase_timestamp=("order_purchase_timestamp", "first"),
            order_status=("order_status", "first"),
            review_score=("review_score", "first"),
            delivery_days=("delivery_days", "first"),
            is_on_time=("is_on_time", "first"),
            customer_state=("customer_state", "first"),
            month_year=("month_year", "first"),
        )
        .reset_index(drop=True)
    )

    orders_df = _optimize_frame(orders_df.reset_index(drop=True))
    order_items_df = _optimize_frame(order_items_df.reset_index(drop=True))
    payments_df = _optimize_frame(payments_df.reset_index(drop=True))
    seller_orders_df = _optimize_frame(seller_orders_df.reset_index(drop=True))

    bundle = {
        "orders": orders_df,
        "order_items": order_items_df,
        "payments": payments_df,
        "seller_orders": seller_orders_df,
    }
    bundle.update(_build_aggregate_tables(orders_df, order_items_df, payments_df))

    print(
        "[data_loader] Bundle ready: "
        f"orders={len(bundle['orders']):,}, "
        f"items={len(bundle['order_items']):,}, "
        f"payments={len(bundle['payments']):,}, "
        f"seller_orders={len(bundle['seller_orders']):,}"
    )
    return bundle


def load_data_bundle(force_reload: bool = False) -> dict[str, pd.DataFrame]:
    if not force_reload and "bundle" in _MEMORY_CACHE:
        return _MEMORY_CACHE["bundle"]

    if not force_reload:
        cached = _load_cached_bundle()
        if cached is not None:
            _MEMORY_CACHE["bundle"] = cached
            return cached

    bundle = _build_bundle()
    _MEMORY_CACHE["bundle"] = bundle
    _save_cached_bundle(bundle)
    return bundle


def load_master_data(force_reload: bool = False) -> pd.DataFrame:
    """
    Backward-compatible accessor for the order-level analytics table.
    """
    return load_data_bundle(force_reload=force_reload)["orders"]


def get_unique_categories(df: pd.DataFrame | None = None) -> list[str]:
    source_df = df if df is not None else load_data_bundle()["order_items"]
    categories = source_df["product_category_name_english"].dropna().unique().tolist()
    return sorted(categories)
