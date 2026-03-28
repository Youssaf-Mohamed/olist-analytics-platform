"""
pages/reviews.py — Page 3: Customer Sentiment Analysis
Gauge + Histogram + Box Plot + WordCloud
"""

import base64
from io import BytesIO

import dash
from dash import html, dcc, callback, Input, Output
import plotly.graph_objects as go
import pandas as pd
from dash_iconify import DashIconify

from components.page_helpers import chart_loading, page_section
from utils.data_loader import get_unique_categories, load_data_bundle
from utils.cleaner import apply_chart_layout, filter_by_date, tooltip

try:
    from wordcloud import WordCloud
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    _WC_AVAILABLE = True
except ImportError:
    _WC_AVAILABLE = False

dash.register_page(__name__, path="/reviews", name="Reviews", order=2)

# ── Load data once ────────────────────────────────────────────────────────────
DATA_BUNDLE = load_data_bundle()
orders_df = DATA_BUNDLE["orders"]
order_items_df = DATA_BUNDLE["order_items"]
DATE_MIN = orders_df["order_purchase_timestamp"].min().date()
DATE_MAX = orders_df["order_purchase_timestamp"].max().date()
CATEGORIES = ["All Categories"] + get_unique_categories(order_items_df)


def _make_wordcloud(comments: pd.Series) -> str | None:
    """Generate a base64-encoded WordCloud PNG, or None if unavailable."""
    if not _WC_AVAILABLE:
        return None
    text = " ".join(comments.dropna().astype(str).tolist())
    if len(text.strip()) < 20:
        return None
    try:
        wc = WordCloud(
            width=800,
            height=320,
            background_color="#161A23",
            colormap="cool",
            max_words=150,
            collocations=False,
        ).generate(text)
        buf = BytesIO()
        plt.figure(figsize=(10, 4), facecolor="#161A23")
        plt.imshow(wc, interpolation="bilinear")
        plt.axis("off")
        plt.tight_layout(pad=0)
        plt.savefig(
            buf, format="png", bbox_inches="tight", facecolor="#161A23", dpi=120
        )
        plt.close("all")
        buf.seek(0)
        return "data:image/png;base64," + base64.b64encode(buf.read()).decode()
    except Exception:
        return None


# ── Layout ────────────────────────────────────────────────────────────────────
layout = page_section(
    html.Div(
    [
        html.Div(
            [
                html.H1("Customer Sentiment Analysis", className="page-title"),
                html.P(
                    "Explore review scores and customer feedback across product categories.",
                    className="page-subtitle",
                ),
            ],
            className="page-header",
        ),
        # Filters
        html.Div(
            [
                html.Div(
                    "Using the global date range from the top bar.",
                    className="global-filter-note global-filter-note-inline",
                ),
                html.Div(
                    [
                        html.Span("Category:", className="filter-label"),
                        dcc.Dropdown(
                            id="reviews-category",
                            options=[{"label": c, "value": c} for c in CATEGORIES],
                            value="All Categories",
                            clearable=False,
                            className="dash-dropdown",
                            style={"minWidth": "300px"},
                        ),
                    ],
                ),
            ],
            className="filter-bar",
            style={"display": "flex", "flexWrap": "wrap", "gap": "24px", "alignItems": "flex-end"},
        ),
        # Gauge + Histogram
        html.Div(
            [
                html.Div(
                    [
                        html.P(
                            [
                                "Avg Review Score",
                                tooltip(
                                    "The mean sentiment gauge indicating overall customer satisfaction on a 1-5 scale."
                                ),
                            ],
                            className="chart-title",
                            style={"display": "flex", "alignItems": "center"},
                        ),
                        html.P(
                            "Sentiment gauge (1–5 scale)", className="chart-subtitle"
                        ),
                        chart_loading(
                            dcc.Graph(id="reviews-gauge", config={"displayModeBar": False}),
                        ),
                    ],
                    className="chart-card",
                ),
                html.Div(
                    [
                        html.P(
                            [
                                "Review Score Distribution",
                                tooltip(
                                    "Frequency distribution of each star rating given by customers."
                                ),
                            ],
                            className="chart-title",
                            style={"display": "flex", "alignItems": "center"},
                        ),
                        html.P(
                            "Histogram of review scores", className="chart-subtitle"
                        ),
                        chart_loading(
                            dcc.Graph(
                                id="reviews-histogram", config={"displayModeBar": False}
                            ),
                        ),
                    ],
                    className="chart-card",
                ),
            ],
            className="chart-grid chart-grid-2",
        ),
        # Box plot
        html.Div(
            [
                html.Div(
                    [
                        html.P(
                            [
                                "Review Score by Category",
                                tooltip(
                                    "Boxplot displaying the variance and median score across different product categories."
                                ),
                            ],
                            className="chart-title",
                            style={"display": "flex", "alignItems": "center"},
                        ),
                        html.P(
                            "Top 10 categories — score spread",
                            className="chart-subtitle",
                        ),
                        chart_loading(
                            dcc.Graph(
                                id="reviews-boxplot", config={"displayModeBar": False}
                            ),
                        ),
                    ],
                    className="chart-card",
                ),
            ],
            className="chart-grid chart-grid-1",
        ),
        # WordCloud
        html.Div(
            [
                html.Div(
                    [
                        html.P(
                            [
                                "Customer Comment WordCloud",
                                tooltip(
                                    "NLP visualization where larger words indicate higher frequency in customer review messages."
                                ),
                            ],
                            className="chart-title",
                            style={"display": "flex", "alignItems": "center"},
                        ),
                        html.P(
                            "Generated from review_comment_message (Portuguese text)",
                            className="chart-subtitle",
                        ),
                        chart_loading(
                            html.Div(id="reviews-wordcloud-wrap"),
                        ),
                    ],
                    className="chart-card",
                ),
            ],
            className="chart-grid chart-grid-1",
        ),
    ],
        style={"maxWidth": "1600px"},
    ),
)


# ── Callback ──────────────────────────────────────────────────────────────────
@callback(
    Output("reviews-gauge", "figure"),
    Output("reviews-histogram", "figure"),
    Output("reviews-boxplot", "figure"),
    Output("reviews-wordcloud-wrap", "children"),
    Output("reviews-page-context", "data"),
    Input("reviews-category", "value"),
    Input("global-date-range", "start_date"),
    Input("global-date-range", "end_date"),
    Input("global-compare-toggle", "value"),
    Input("theme-store", "data"),
    Input("app-container", "data-theme"),
)
def update_reviews(category, start_date, end_date, compare_values, theme="dark", applied_theme="dark"):
    theme = applied_theme or theme or "dark"
    orders_dff = (
        filter_by_date(orders_df, start_date, end_date)
        if start_date and end_date
        else orders_df.copy()
    )
    items_dff = (
        filter_by_date(order_items_df, start_date, end_date)
        if start_date and end_date
        else order_items_df.copy()
    )
    category_reviews = items_dff.drop_duplicates(["order_id", "product_category_name_english"])

    if category and category != "All Categories":
        dff = category_reviews[
            category_reviews["product_category_name_english"] == category
        ].copy()
    else:
        dff = orders_dff.drop_duplicates("order_id").copy()

    avg_score = dff["review_score"].mean() if not dff.empty else 3.0

    # ── Gauge ─────────────────────────────────────────────────────────────────
    fig_gauge = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=avg_score,
            number={"font": {"family": "Space Mono", "size": 36}, "valueformat": ".2f"},
            gauge=dict(
                axis=dict(
                    range=[1, 5],
                    tickvals=[1, 2, 3, 4, 5],
                    tickfont=dict(family="Space Mono", size=11),
                ),
                bar=dict(color="#00D4FF", thickness=0.25),
                steps=[
                    dict(range=[1, 2], color="#EF4444"),
                    dict(range=[2, 3], color="#F59E0B"),
                    dict(range=[3, 4], color="#7C3AED"),
                    dict(range=[4, 5], color="#10B981"),
                ],
                threshold=dict(
                    line=dict(color="#00D4FF", width=2),
                    value=avg_score,
                ),
                bgcolor="rgba(0,0,0,0)",
                bordercolor="rgba(0,0,0,0)",
                borderwidth=0,
            ),
        )
    )
    apply_chart_layout(fig_gauge, height=280, theme=theme)

    # ── Histogram ─────────────────────────────────────────────────────────────
    score_counts = dff["review_score"].round().value_counts().sort_index()
    colors_hist = {1: "#EF4444", 2: "#F59E0B", 3: "#7C3AED", 4: "#10B981", 5: "#00D4FF"}

    fig_hist = go.Figure()
    for score in range(1, 6):
        cnt = score_counts.get(float(score), 0)
        fig_hist.add_trace(
            go.Bar(
                x=[str(int(score))],
                y=[cnt],
                name=f"{score}★",
                marker_color=colors_hist.get(score, "#00D4FF"),
                hovertemplate=f"Score {score}: {cnt:,}<extra></extra>",
            )
        )
    apply_chart_layout(fig_hist, height=280, theme=theme)
    fig_hist.update_layout(
        barmode="group",
        showlegend=True,
        xaxis_title="Review Score",
        yaxis_title="Count",
    )

    # ── Box Plot (Top 10 categories) ──────────────────────────────────────────
    if category and category != "All Categories":
        top_cats = [category]
    else:
        top_cats = (
            category_reviews.groupby("product_category_name_english")["order_id"]
            .nunique()
            .nlargest(10)
            .index.tolist()
        )
    box_df = category_reviews[
        category_reviews["product_category_name_english"].isin(top_cats)
    ]
    fig_box = go.Figure()
    colors_box = [
        "#00D4FF",
        "#7C3AED",
        "#10B981",
        "#F59E0B",
        "#EF4444",
        "#06B6D4",
        "#8B5CF6",
        "#34D399",
        "#FCD34D",
        "#F87171",
    ]
    for i, cat in enumerate(top_cats):
        sub = box_df[box_df["product_category_name_english"] == cat]["review_score"]
        fig_box.add_trace(
            go.Box(
                y=sub,
                name=cat,
                marker=dict(color=colors_box[i % len(colors_box)]),
                line=dict(color=colors_box[i % len(colors_box)]),
                fillcolor=f"rgba({int(colors_box[i%len(colors_box)][1:3],16)},"
                f"{int(colors_box[i%len(colors_box)][3:5],16)},"
                f"{int(colors_box[i%len(colors_box)][5:7],16)},0.15)",
                hovertemplate="<b>%{x}</b><br>Score: %{y:.1f}<extra></extra>",
            )
        )
    apply_chart_layout(fig_box, height=340, theme=theme)
    fig_box.update_layout(showlegend=False)

    # ── WordCloud ─────────────────────────────────────────────────────────────
    wc_src = _make_wordcloud(dff["review_comment"])
    if wc_src:
        wc_content = html.Img(
            src=wc_src,
            style={
                "width": "100%",
                "borderRadius": "6px",
                "display": "block",
                "margin": "0 auto",
            },
        )
    else:
        wc_content = html.Div(
            [
                DashIconify(
                    icon="ph:warning-circle",
                    width=32,
                    style={"marginBottom": "8px", "color": "var(--muted)"},
                ),
                html.Div(
                    "WordCloud unavailable — install the 'wordcloud' library or no comments in the selected category.",
                    style={"fontSize": "0.95rem", "fontWeight": "500"},
                ),
            ],
            style={
                "color": "var(--text-soft)",
                "fontFamily": "var(--font-body)",
                "padding": "32px",
                "textAlign": "center",
                "display": "flex",
                "flexDirection": "column",
                "alignItems": "center",
                "backgroundColor": "var(--surface3)",
                "borderRadius": "var(--radius-sm)",
                "border": "1px dashed var(--border2)",
            },
        )

    context = {
        "page": "reviews",
        "filters": {
            "category": category,
            "start_date": start_date,
            "end_date": end_date,
            "compare_previous": "compare" in (compare_values or []),
        },
        "headline_metrics": {
            "avg_review_score": f"{avg_score:.2f}",
            "reviewed_orders": int(dff["order_id"].nunique()) if not dff.empty else 0,
        },
    }

    return fig_gauge, fig_hist, fig_box, wc_content, context
