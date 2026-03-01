"""
utils/data_loader.py
Load, merge, and cache all 9 Olist CSV files into a single master DataFrame.
"""

import pandas as pd
import pickle
from pathlib import Path

# ── Path helpers ──────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
CACHE_FILE = ROOT / ".cache" / "master_df.pkl"

# ── Date columns per file ─────────────────────────────────────────────────────
DATE_COLS = {
    "olist_orders_dataset.csv": [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ],
}


# ── Loader ────────────────────────────────────────────────────────────────────
def _read_csv(filename: str, parse_dates=None) -> pd.DataFrame:
    path = DATA_DIR / filename
    if not path.exists():
        raise FileNotFoundError(
            f"Missing dataset file: {path}\n"
            "Please place all 9 Olist CSV files inside the data/ folder."
        )
    kwargs = {}
    if parse_dates:
        kwargs["parse_dates"] = parse_dates
    return pd.read_csv(path, low_memory=False, **kwargs)


def load_master_data(force_reload: bool = False) -> pd.DataFrame:
    """
    Load all 9 Olist CSVs, merge them into a single master DataFrame,
    engineer features, and apply a date filter (2017-01-01 → 2018-08-31).

    Uses a pickle cache; set force_reload=True to ignore the cache.
    """
    # ── Serve from cache if available ─────────────────────────────────────────
    if not force_reload and CACHE_FILE.exists():
        try:
            with open(CACHE_FILE, "rb") as f:
                df = pickle.load(f)
            print("[data_loader] Loaded master DataFrame from cache.")
            return df
        except Exception as e:
            print(f"[data_loader] Cache read failed ({e}), reloading from CSVs.")

    print("[data_loader] Loading CSVs…")

    # ── 1. Orders ─────────────────────────────────────────────────────────────
    orders = _read_csv(
        "olist_orders_dataset.csv",
        parse_dates=DATE_COLS["olist_orders_dataset.csv"],
    )

    # ── 2. Order Items (aggregate per order_id) ───────────────────────────────
    items_raw = _read_csv("olist_order_items_dataset.csv")
    items = (
        items_raw.groupby("order_id")
        .agg(
            item_price=("price", "sum"),
            item_freight=("freight_value", "sum"),
            num_items=("order_item_id", "count"),
            product_id=("product_id", "first"),
            seller_id=("seller_id", "first"),
        )
        .reset_index()
    )
    items["total_order_value"] = items["item_price"] + items["item_freight"]

    # ── 3. Customers ──────────────────────────────────────────────────────────
    customers = _read_csv("olist_customers_dataset.csv")[
        [
            "customer_id",
            "customer_unique_id",
            "customer_city",
            "customer_state",
            "customer_zip_code_prefix",
        ]
    ]

    # ── 4. Products ───────────────────────────────────────────────────────────
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

    # ── 5. Category translations ──────────────────────────────────────────────
    translation = _read_csv("product_category_name_translation.csv")
    products = products.merge(translation, on="product_category_name", how="left")
    products["product_category_name_english"] = (
        products["product_category_name_english"]
        .fillna(products["product_category_name"])
        .str.replace("_", " ")
        .str.title()
    )

    # ── 6. Sellers ────────────────────────────────────────────────────────────
    sellers = _read_csv("olist_sellers_dataset.csv")[
        ["seller_id", "seller_city", "seller_state"]
    ]

    # ── 7. Reviews (aggregate per order_id) ───────────────────────────────────
    reviews_raw = _read_csv("olist_order_reviews_dataset.csv")
    reviews = (
        reviews_raw.groupby("order_id")
        .agg(
            review_score=("review_score", "mean"),
            review_comment=("review_comment_message", "first"),
        )
        .reset_index()
    )

    # ── 8. Payments (aggregate per order_id) ─────────────────────────────────
    payments_raw = _read_csv("olist_order_payments_dataset.csv")
    payments = (
        payments_raw.groupby("order_id")
        .agg(
            payment_value=("payment_value", "sum"),
            payment_type=("payment_type", "first"),
            payment_installments=("payment_installments", "max"),
        )
        .reset_index()
    )

    # ── 9. Geolocation (one row per zip prefix, take first) ───────────────────
    geo = _read_csv("olist_geolocation_dataset.csv")
    geo = (
        geo.groupby("geolocation_zip_code_prefix")
        .first()
        .reset_index()[
            [
                "geolocation_zip_code_prefix",
                "geolocation_lat",
                "geolocation_lng",
                "geolocation_state",
            ]
        ]
    )

    # ── Merge pipeline ────────────────────────────────────────────────────────
    print("[data_loader] Merging tables…")

    df = orders.copy()

    df = df.merge(items, on="order_id", how="left")
    df = df.merge(customers, on="customer_id", how="left")
    df = df.merge(reviews, on="order_id", how="left")
    df = df.merge(payments, on="order_id", how="left")
    df = df.merge(products, on="product_id", how="left")
    df = df.merge(sellers, on="seller_id", how="left")

    # Geolocation by customer zip code
    df = df.merge(
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

    # ── Feature engineering ───────────────────────────────────────────────────
    print("[data_loader] Engineering features…")

    df["delivery_days"] = (
        df["order_delivered_customer_date"] - df["order_purchase_timestamp"]
    ).dt.total_seconds() / 86_400
    df["is_on_time"] = (
        df["order_delivered_customer_date"] <= df["order_estimated_delivery_date"]
    )
    df["month_year"] = df["order_purchase_timestamp"].dt.strftime("%Y-%m")
    df["purchase_year"] = df["order_purchase_timestamp"].dt.year
    df["purchase_month"] = df["order_purchase_timestamp"].dt.month

    # Fill nulls
    df["review_score"] = df["review_score"].fillna(df["review_score"].median())
    df["delivery_days"] = df["delivery_days"].clip(lower=0)
    df["review_comment"] = df["review_comment"].fillna("")

    # ── Date filter (best data window) ────────────────────────────────────────
    mask = (df["order_purchase_timestamp"] >= "2017-01-01") & (
        df["order_purchase_timestamp"] <= "2018-08-31"
    )
    df = df.loc[mask].copy().reset_index(drop=True)

    print(f"[data_loader] Master DataFrame: {len(df):,} rows × {df.shape[1]} columns")

    # ── Save to cache ─────────────────────────────────────────────────────────
    CACHE_FILE.parent.mkdir(exist_ok=True)
    with open(CACHE_FILE, "wb") as f:
        pickle.dump(df, f, protocol=pickle.HIGHEST_PROTOCOL)
    print(f"[data_loader] Cached to {CACHE_FILE}")

    return df


def get_unique_categories(df: pd.DataFrame) -> list[str]:
    """Return sorted list of unique English category names."""
    cats = df["product_category_name_english"].dropna().unique().tolist()
    return sorted(cats)
