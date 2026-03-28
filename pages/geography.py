"""
pages/geography.py — Page 2: Geographic Intelligence
Brazil choropleth map + Top 10 Cities table
"""

import dash
from dash import html, dcc, callback, Input, Output
import plotly.graph_objects as go
import requests
from dash_iconify import DashIconify

from components.page_helpers import page_section
from utils.data_loader import load_data_bundle
from utils.cleaner import (
    apply_chart_layout,
    filter_by_date_column,
    format_brl,
    get_chart_theme,
    tooltip,
)

dash.register_page(__name__, path="/geography", name="Geography", order=1)

# ── Load data once ────────────────────────────────────────────────────────────
DATA_BUNDLE = load_data_bundle()
orders_df = DATA_BUNDLE["orders"]
state_daily_df = DATA_BUNDLE["agg_state_daily"]
city_daily_df = DATA_BUNDLE["agg_city_daily"]
DATE_MIN = orders_df["order_purchase_timestamp"].min().date()
DATE_MAX = orders_df["order_purchase_timestamp"].max().date()

# ── Brazil GeoJSON ────────────────────────────────────────────────────────────
GEOJSON_URL = (
    "https://raw.githubusercontent.com/codeforamerica/click_that_hood"
    "/master/public/data/brazil-states.geojson"
)

_geojson_cache = {}


def _get_geojson():
    if "data" not in _geojson_cache:
        try:
            r = requests.get(GEOJSON_URL, timeout=10)
            _geojson_cache["data"] = r.json()
        except Exception:
            _geojson_cache["data"] = None
    return _geojson_cache["data"]


METRIC_OPTIONS = [
    {
        "label": html.Div(
            [
                DashIconify(icon="ph:coin", width=16, style={"marginRight": "8px"}),
                "Revenue (R$)",
            ],
            style={"display": "flex", "alignItems": "center"},
        ),
        "value": "revenue",
    },
    {
        "label": html.Div(
            [
                DashIconify(icon="ph:package", width=16, style={"marginRight": "8px"}),
                "Order Count",
            ],
            style={"display": "flex", "alignItems": "center"},
        ),
        "value": "orders",
    },
    {
        "label": html.Div(
            [
                DashIconify(icon="ph:star", width=16, style={"marginRight": "8px"}),
                "Avg Review Score",
            ],
            style={"display": "flex", "alignItems": "center"},
        ),
        "value": "avg_rating",
    },
]

# ── Layout ────────────────────────────────────────────────────────────────────
layout = page_section(
    html.Div(
    [
        html.Div(
            [
                html.H1("Geographic Intelligence", className="page-title"),
                html.P(
                    "Explore how orders, revenue, and satisfaction vary across Brazilian states.",
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
                        html.Span("Metric:", className="filter-label"),
                        dcc.Dropdown(
                            id="geo-metric",
                            options=METRIC_OPTIONS,
                            value="revenue",
                            clearable=False,
                            className="dash-dropdown",
                            style={"minWidth": "240px"},
                        ),
                    ],
                ),
            ],
            className="filter-bar",
            style={"display": "flex", "flexWrap": "wrap", "gap": "24px", "alignItems": "flex-end"},
        ),
        # Map
        html.Div(
            [
                html.Div(
                    [
                        html.P(
                            [
                                "Brazil State Choropleth",
                                tooltip(
                                    "Interactive map of Brazil displaying the selected metric for each individual state."
                                ),
                            ],
                            className="chart-title",
                            style={"display": "flex", "alignItems": "center"},
                        ),
                        html.P(
                            "Color intensity reflects the selected metric per state.",
                            className="chart-subtitle",
                        ),
                        dcc.Loading(
                            dcc.Graph(
                                id="geo-map",
                                config={"displayModeBar": False, "scrollZoom": True},
                            ),
                            type="circle",
                            color="#38BDF8",
                            parent_className="chart-loading-wrapper",
                        ),
                    ],
                    className="chart-card",
                ),
            ],
            className="chart-grid chart-grid-1",
        ),
        # Top 10 cities table
        html.Div(
            [
                html.Div(
                    [
                        html.P(
                            [
                                "Top 10 Cities",
                                tooltip(
                                    "Leaderboard of the top municipalities nationwide according to the active metric filter."
                                ),
                            ],
                            className="chart-title",
                            style={"display": "flex", "alignItems": "center"},
                        ),
                        html.P("Ranked by selected metric", className="chart-subtitle"),
                        dcc.Loading(
                            html.Div(id="geo-cities-table"),
                            type="circle",
                            color="#38BDF8",
                            parent_className="chart-loading-wrapper",
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
    Output("geo-map", "figure"),
    Output("geo-cities-table", "children"),
    Output("geography-page-context", "data"),
    Input("geo-metric", "value"),
    Input("global-date-range", "start_date"),
    Input("global-date-range", "end_date"),
    Input("global-compare-toggle", "value"),
    Input("theme-store", "data"),
    Input("app-container", "data-theme"),
)
def update_geography(metric, start_date, end_date, compare_values, theme="dark", applied_theme="dark"):
    theme = applied_theme or theme or "dark"
    palette = get_chart_theme(theme)
    state_dff = (
        filter_by_date_column(state_daily_df, "order_date", start_date, end_date)
        if start_date and end_date
        else state_daily_df.copy()
    )
    city_dff = (
        filter_by_date_column(city_daily_df, "order_date", start_date, end_date)
        if start_date and end_date
        else city_daily_df.copy()
    )
    # Aggregate per state
    if metric == "revenue":
        state_agg = (
            state_dff.groupby("customer_state")["revenue_sum"]
            .sum()
            .reset_index()
            .rename(columns={"revenue_sum": "value"})
        )
        label_fmt = lambda v: format_brl(v)
        color_label = "Revenue (R$)"
    elif metric == "orders":
        state_agg = (
            state_dff.groupby("customer_state")["order_count"]
            .sum()
            .reset_index()
            .rename(columns={"order_count": "value"})
        )
        label_fmt = lambda v: f"{int(v):,}"
        color_label = "Order Count"
    else:  # avg_rating
        state_agg = (
            state_dff.groupby("customer_state", as_index=False)
            .agg(review_sum=("review_sum", "sum"), review_count=("review_count", "sum"))
            .assign(value=lambda df: df["review_sum"] / df["review_count"].clip(lower=1))
        )
        label_fmt = lambda v: f"{v:.2f} ★"
        color_label = "Avg Rating"

    geojson = _get_geojson()
    choropleth_scale = (
        [
            [0.0, "#E0F2FE"],
            [0.35, "#7DD3FC"],
            [0.7, "#38BDF8"],
            [1.0, "#2563EB"],
        ]
        if theme == "light"
        else [
            [0.0, "#1E2433"],
            [0.5, "#7C3AED"],
            [1.0, "#00D4FF"],
        ]
    )
    state_border_color = "#E2E8F0" if theme == "light" else "#0D0F14"

    # ── Choropleth map ────────────────────────────────────────────────────────
    if geojson:
        fig = go.Figure(
            go.Choropleth(
                geojson=geojson,
                locations=state_agg["customer_state"],
                z=state_agg["value"],
                featureidkey="properties.sigla",
                colorscale=choropleth_scale,
                marker_line_color=state_border_color,
                marker_line_width=0.8 if theme == "light" else 0.5,
                colorbar=dict(
                    title=dict(text=color_label, font=dict(color=palette["tick_color"], size=11)),
                    tickfont=dict(color=palette["tick_color"], family="Space Mono"),
                    bgcolor="rgba(255,255,255,0.78)" if theme == "light" else "rgba(0,0,0,0)",
                    outlinewidth=1 if theme == "light" else 0,
                    outlinecolor="rgba(203, 213, 225, 0.9)" if theme == "light" else "rgba(0,0,0,0)",
                    thickness=14,
                ),
                hovertemplate="<b>%{location}</b><br>"
                + color_label
                + ": %{z}<extra></extra>",
            )
        )
        fig.update_geos(
            fitbounds="locations",
            visible=False,
            bgcolor="rgba(0,0,0,0)",
            showlakes=False,
        )
    else:
        # Fallback bar chart when GeoJSON is unavailable
        sorted_agg = state_agg.sort_values("value", ascending=True).tail(20)
        fig = go.Figure(
            go.Bar(
                x=sorted_agg["value"],
                y=sorted_agg["customer_state"],
                orientation="h",
                marker=dict(color=palette["colorway"][0]),
            )
        )

    apply_chart_layout(fig, height=520, theme=theme)
    fig.update_layout(
        geo=dict(bgcolor="rgba(0,0,0,0)"),
        margin=dict(l=0, r=0, t=10, b=10),
    )

    # ── Top 10 Cities table ───────────────────────────────────────────────────
    if metric == "revenue":
        city_agg = (
            city_dff.groupby(["customer_city", "customer_state"])["revenue_sum"]
            .sum()
            .reset_index()
            .rename(columns={"revenue_sum": "value"})
        )
    elif metric == "orders":
        city_agg = (
            city_dff.groupby(["customer_city", "customer_state"])["order_count"]
            .sum()
            .reset_index()
            .rename(columns={"order_count": "value"})
        )
    else:
        city_agg = (
            city_dff.groupby(["customer_city", "customer_state"], as_index=False)
            .agg(review_sum=("review_sum", "sum"), review_count=("review_count", "sum"))
            .assign(value=lambda df: df["review_sum"] / df["review_count"].clip(lower=1))
        )

    top10 = city_agg.nlargest(10, "value").reset_index(drop=True)

    rows = []
    for i, row in top10.iterrows():
        rows.append(
            html.Tr(
                [
                    html.Td(str(i + 1), className="mono"),
                    html.Td(row["customer_city"].title()),
                    html.Td(
                        html.Span(row["customer_state"], className="badge badge-cyan"),
                    ),
                    html.Td(label_fmt(row["value"]), className="mono"),
                ]
            )
        )

    table = html.Table(
        [
            html.Thead(
                html.Tr(
                    [
                        html.Th("#"),
                        html.Th("City"),
                        html.Th("State"),
                        html.Th(color_label),
                    ]
                )
            ),
            html.Tbody(rows),
        ],
        className="data-table",
    )

    context = {
        "page": "geography",
        "filters": {
            "metric": metric,
            "start_date": start_date,
            "end_date": end_date,
            "compare_previous": "compare" in (compare_values or []),
        },
        "headline_metrics": {
            "top_state": state_agg.nlargest(1, "value").to_dict(orient="records"),
            "top_cities": top10.head(3).to_dict(orient="records"),
        },
    }

    return fig, html.Div(table, className="data-table-wrap"), context
