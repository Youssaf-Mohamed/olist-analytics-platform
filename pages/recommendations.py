"""
pages/recommendations.py — Page 4: Smart Recommendation Engine
Content-based recommendations + trending products
"""

import dash
from dash import html, dcc, callback, Input, Output, State
from dash_iconify import DashIconify

from components.page_helpers import page_section
from utils.data_loader import get_unique_categories, load_data_bundle
from utils.recommender import get_content_recommendations, get_trending_products
from utils.cleaner import format_brl, tooltip

dash.register_page(__name__, path="/recommendations", name="Recommendations", order=3)

# ── Load data once ────────────────────────────────────────────────────────────
DATA_BUNDLE = load_data_bundle()
order_items_df = DATA_BUNDLE["order_items"]
CATEGORIES = get_unique_categories(order_items_df)


# ── Card builder ──────────────────────────────────────────────────────────────
def _rec_card(rec: dict, accent: str = "cyan") -> html.Div:
    """Build a recommendation result card."""
    return html.Div(
        [
            html.Div(rec.get("category", "—"), className="rec-card-category"),
            html.Div(
                rec.get("product_id", "")[:16] + "…",
                className="rec-card-id",
                title=rec.get("product_id", ""),
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Span("Price", className="rec-stat-label"),
                            html.Span(
                                format_brl(rec.get("avg_price", 0)),
                                className="rec-stat-value",
                            ),
                        ],
                        className="rec-stat",
                    ),
                    html.Div(
                        [
                            html.Span("Rating", className="rec-stat-label"),
                            html.Span(
                                [
                                    DashIconify(
                                        icon="ph:star-fill",
                                        width=12,
                                        style={
                                            "marginRight": "2px",
                                            "color": "var(--amber)",
                                        },
                                    )
                                ]
                                * int(round(rec.get("avg_rating", 0))),
                                className="rec-stat-value rec-stars",
                                style={"display": "flex", "alignItems": "center"},
                            ),
                        ],
                        className="rec-stat",
                    ),
                    html.Div(
                        [
                            html.Span("Sales", className="rec-stat-label"),
                            html.Span(
                                f"{int(rec.get('total_sales', 0)):,}",
                                className="rec-stat-value",
                            ),
                        ],
                        className="rec-stat",
                    ),
                    html.Div(
                        [
                            html.Span("Score", className="rec-stat-label"),
                            html.Span(
                                f"{rec.get('score', 0):.3f}", className="rec-stat-value"
                            ),
                        ],
                        className="rec-stat",
                    ),
                ]
            ),
        ],
        className=f"rec-card rec-{accent}",
    )


def _empty_state(msg="No products found for the selected filters.") -> html.Div:
    return html.Div(
        [
            DashIconify(
                icon="ph:warning-circle",
                width=32,
                style={"marginBottom": "8px", "color": "var(--muted)"},
            ),
            html.Div(msg),
        ],
        style={
            "color": "#64748B",
            "fontFamily": "DM Sans",
            "padding": "32px 0",
            "textAlign": "center",
            "display": "flex",
            "flexDirection": "column",
            "alignItems": "center",
        },
    )


# ── Layout ────────────────────────────────────────────────────────────────────
layout = page_section(
    html.Div(
    [
        html.Div(
            [
                html.H1("Smart Recommendation Engine", className="page-title"),
                html.P(
                    "Discover top products by category and price, or see what's trending now.",
                    className="page-subtitle",
                ),
            ],
            className="page-header",
        ),
        # Controls
        html.Div(
            [
                html.Div(
                    [
                        html.Span(
                            "Category", 
                            className="filter-label", 
                        ),
                        dcc.Dropdown(
                            id="rec-category",
                            options=[{"label": c, "value": c} for c in CATEGORIES],
                            value=CATEGORIES[0] if CATEGORIES else None,
                            clearable=False,
                            className="dash-dropdown",
                            style={"width": "100%"},
                        ),
                    ],
                    style={"flex": "1", "minWidth": "240px"},
                ),
                html.Div(
                    [
                        html.Span(
                            "Price Range (R$)",
                            className="filter-label",
                        ),
                        html.Div(
                            dcc.RangeSlider(
                                id="rec-price",
                                min=0,
                                max=1000,
                                step=10,
                                value=[0, 500],
                                marks={
                                    0: {"label": "0", "style": {"color": "var(--text-soft)"}},
                                    250: {"label": "250", "style": {"color": "var(--text-soft)"}},
                                    500: {"label": "500", "style": {"color": "var(--text-soft)"}},
                                    750: {"label": "750", "style": {"color": "var(--text-soft)"}},
                                    1000: {"label": "1K", "style": {"color": "var(--text-soft)"}}
                                },
                                tooltip={"placement": "bottom", "always_visible": False},
                            ),
                            style={"padding": "10px 10px 0 10px"}
                        )
                    ],
                    style={
                        "flex": "2", 
                        "minWidth": "300px", 
                        "padding": "0 24px", 
                        "borderLeft": "1px solid var(--glass-border)", 
                        "borderRight": "1px solid var(--glass-border)"
                    },
                ),
                html.Div(
                    [
                        html.Button(
                            [
                                DashIconify(
                                    icon="ph:magic-wand-fill",
                                    width=20,
                                ),
                                "Discover Items",
                            ],
                            id="rec-button",
                            n_clicks=0,
                            className="btn-primary",
                            style={
                                "height": "44px",
                                "display": "flex",
                                "alignItems": "center",
                                "justifyContent": "center",
                                "gap": "10px",
                                "width": "100%",
                                "fontSize": "1rem",
                            },
                        ),
                    ],
                    style={"flex": "0 0 220px", "display": "flex", "alignItems": "flex-end", "paddingBottom": "2px"}
                ),
            ],
            className="filter-bar",
            style={"display": "flex", "flexWrap": "wrap", "gap": "20px", "padding": "24px 28px", "alignItems": "flex-end"},
        ),
        # Content recommendations title
        html.Div(
            [
                html.Div(
                    [
                        DashIconify(
                            icon="ph:sparkle-fill",
                            width=26,
                            style={"color": "var(--cyan)"},
                        ),
                        html.Span(
                            [
                                "Content-Based Recommendations",
                                tooltip(
                                    "Suggests 5 similar items to what customers in this category generally purchase based on attributes."
                                ),
                            ]
                        ),
                    ],
                    className="section-title",
                    style={"display": "flex", "alignItems": "center"},
                ),
            ]
        ),
        # Results grid (5 cards)
        html.Div(
            id="rec-results-grid", className="rec-grid", style={"minHeight": "180px"}
        ),
        html.Hr(className="section-divider"),
        # Trending section (always visible, no button required)
        html.Div(
            [
                html.Div(
                    [
                        DashIconify(
                            icon="ph:fire-fill",
                            width=26,
                            style={"color": "var(--amber)"},
                        ),
                        html.Span(
                            [
                                "Trending Now — Last 90 Days",
                                tooltip(
                                    "Machine Learning insight highlighting products with the steepest sales velocity in the most recent 90-day window."
                                ),
                            ]
                        ),
                    ],
                    className="section-title",
                    style={"display": "flex", "alignItems": "center"},
                ),
            ]
        ),
        html.Div(id="rec-trending-grid", className="rec-grid"),
    ],
        style={"maxWidth": "1600px"},
    ),
)


# ── Callbacks ─────────────────────────────────────────────────────────────────


@callback(
    Output("rec-results-grid", "children"),
    Input("rec-button", "n_clicks"),
    State("rec-category", "value"),
    State("rec-price", "value"),
    prevent_initial_call=True,
)
def get_recommendations(n_clicks, category, price_range):
    if not category:
        return _empty_state("Please select a category.")

    min_p = price_range[0] if price_range else 0
    max_p = price_range[1] if price_range else 1000

    results = get_content_recommendations(category, min_p, max_p, top_n=5)

    if not results:
        return _empty_state(
            f"No products found in '{category}' with price R${min_p}–R${max_p}."
        )
    return [_rec_card(r, "cyan") for r in results]


@callback(
    Output("rec-trending-grid", "children"),
    Output("recommendations-page-context", "data"),
    Input("rec-category", "value"),  # any input to trigger on load
)
def load_trending(_):
    results = get_trending_products(days=90, top_n=5)
    if not results:
        context = {
            "page": "recommendations",
            "filters": {"category": _},
            "headline_metrics": {"trending_count": 0},
        }
        return _empty_state("No trending data available."), context
    context = {
        "page": "recommendations",
        "filters": {"category": _},
        "headline_metrics": {
            "trending_count": len(results),
            "top_trending_product": results[0]["product_id"][:16] if results else "N/A",
        },
    }
    return [_rec_card(r, "amber") for r in results], context
