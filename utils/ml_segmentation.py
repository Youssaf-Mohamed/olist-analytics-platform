"""
utils/ml_segmentation.py
RFM computation + K-Means clustering for Customer Segmentation page.
Pure functions — no Dash/Plotly imports here (keep ML separate from views).
"""

import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score, davies_bouldin_score

# ── Reference date (last date in dataset) ────────────────────────────────────
REFERENCE_DATE = pd.Timestamp("2018-09-01")

# ── Segment label mapping (based on RFM quintiles) ───────────────────────────
SEGMENT_NAMES = {
    0: "Champions",
    1: "Loyal Customers",
    2: "At Risk",
    3: "Hibernating",
    4: "Potential Loyalists",
    5: "New Customers",
}

SEGMENT_COLORS = {
    "Champions": "#38BDF8",  # cyan
    "Loyal Customers": "#A78BFA",  # purple
    "Potential Loyalists": "#34D399",  # green
    "New Customers": "#FBBF24",  # amber
    "At Risk": "#F87171",  # red
    "Hibernating": "#64748B",  # muted
}


def compute_rfm(df: pd.DataFrame) -> pd.DataFrame:
    """
    Build a per-customer RFM DataFrame from the master order dataframe.

    Returns columns: customer_unique_id, recency, frequency, monetary
    """
    rfm = (
        df.dropna(
            subset=[
                "customer_unique_id",
                "order_purchase_timestamp",
                "total_order_value",
            ]
        )
        .groupby("customer_unique_id")
        .agg(
            last_purchase=("order_purchase_timestamp", "max"),
            frequency=("order_id", "nunique"),
            monetary=("total_order_value", "sum"),
        )
        .reset_index()
    )

    rfm["recency"] = (REFERENCE_DATE - rfm["last_purchase"]).dt.days
    rfm = rfm.drop(columns=["last_purchase"])

    # Remove outliers (top 1%)
    for col in ["recency", "frequency", "monetary"]:
        cap = rfm[col].quantile(0.99)
        rfm[col] = rfm[col].clip(upper=cap)

    return rfm


def cluster_customers(rfm_df: pd.DataFrame, n_clusters: int = 4) -> pd.DataFrame:
    """
    Scale RFM features and apply K-Means clustering.
    Returns rfm_df enriched with 'segment_id', 'segment', and 'color' columns.
    Also adds 'pc1' and 'pc2' for 2D visualization.
    """
    rfm = rfm_df.copy()
    features = rfm[["recency", "frequency", "monetary"]].values

    # Scale
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(features)

    # K-Means
    km = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labels = km.fit_predict(X_scaled)
    rfm["segment_id"] = labels

    sil_score = silhouette_score(X_scaled, labels, sample_size=5000, random_state=42)
    db_score = davies_bouldin_score(X_scaled, labels)

    # ── Label clusters by RFM profile ─────────────────────────────────────────
    # Champions  = low recency (bought recently), high freq, high monetary
    # Hibernating = high recency (old), low freq, low monetary
    # Sort cluster centroids by composite score: -recency + freq + monetary (normalised)
    centers = pd.DataFrame(
        scaler.inverse_transform(km.cluster_centers_),
        columns=["recency", "frequency", "monetary"],
    )
    centers["score"] = (
        -centers["recency"]  # lower recency → better
        + centers["frequency"] * 3
        + centers["monetary"] / 100
    )
    rank_map = centers["score"].rank(ascending=False).sub(1).astype(int).to_dict()

    # Map ranks to predefined labels
    label_map = {
        orig_id: SEGMENT_NAMES[rank_map[orig_id]] for orig_id in range(n_clusters)
    }
    rfm["segment"] = rfm["segment_id"].map(label_map)
    rfm["color"] = rfm["segment"].map(SEGMENT_COLORS)

    # ── 2D PCA for scatter ─────────────────────────────────────────────────────
    pca = PCA(n_components=2, random_state=42)
    pcs = pca.fit_transform(X_scaled)
    rfm["pc1"] = pcs[:, 0]
    rfm["pc2"] = pcs[:, 1]

    metrics = {"silhouette": float(sil_score), "davies_bouldin": float(db_score)}
    return rfm, metrics


def get_segment_summary(rfm_df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate mean RFM stats per segment.
    Returns: segment, count, pct, avg_recency, avg_frequency, avg_monetary
    """
    total = len(rfm_df)
    summary = (
        rfm_df.groupby("segment")
        .agg(
            count=("customer_unique_id", "count"),
            avg_recency=("recency", "mean"),
            avg_frequency=("frequency", "mean"),
            avg_monetary=("monetary", "mean"),
        )
        .reset_index()
    )
    summary["pct"] = (summary["count"] / total * 100).round(1)
    
    INSIGHTS = {
        "Champions": "Reward them with early access or exclusive offers. Can be brand promoters.",
        "Loyal Customers": "Upsell higher value products. Ask for reviews and encourage referrals.",
        "Potential Loyalists": "Offer a loyalty program and recommend complementary products.",
        "New Customers": "Provide excellent onboarding. Give early discount to encourage repeat purchase.",
        "At Risk": "Send personalized win-back emails with helpful resources or aggressive discounts.",
        "Hibernating": "Don't spend too much. Send standard promotional campaigns periodically.",
    }
    summary["insight"] = summary["segment"].map(INSIGHTS).fillna("Standard engagement.")
    
    return summary.sort_values("avg_monetary", ascending=False)
