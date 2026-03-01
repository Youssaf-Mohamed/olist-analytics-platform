"""
pages/geography.py — Page 2: Geographic Intelligence
Brazil choropleth map + Top 10 Cities table
"""

import dash
from dash import html, dcc, callback, Input, Output
import plotly.graph_objects as go
import requests
from dash_iconify import DashIconify

from utils.data_loader import load_master_data
from utils.cleaner import apply_chart_layout, format_brl, tooltip

dash.register_page(__name__, path="/geography", name="Geography", order=1)

# ── Load data once ────────────────────────────────────────────────────────────
df_master = load_master_data()

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
layout = html.Div(
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
        # Metric selector
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
            className="filter-bar",
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
                        dcc.Graph(
                            id="geo-map",
                            config={"displayModeBar": False, "scrollZoom": True},
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
                        html.Div(id="geo-cities-table"),
                    ],
                    className="chart-card",
                ),
            ],
            className="chart-grid chart-grid-1",
        ),
    ],
    style={"maxWidth": "1600px"},
)


# ── Callback ──────────────────────────────────────────────────────────────────
@callback(
    Output("geo-map", "figure"),
    Output("geo-cities-table", "children"),
    Input("geo-metric", "value"),
)
def update_geography(metric):
    # Aggregate per state
    if metric == "revenue":
        state_agg = (
            df_master.groupby("customer_state")["total_order_value"]
            .sum()
            .reset_index()
            .rename(columns={"total_order_value": "value"})
        )
        label_fmt = lambda v: format_brl(v)
        color_label = "Revenue (R$)"
    elif metric == "orders":
        state_agg = (
            df_master.groupby("customer_state")["order_id"]
            .nunique()
            .reset_index()
            .rename(columns={"order_id": "value"})
        )
        label_fmt = lambda v: f"{int(v):,}"
        color_label = "Order Count"
    else:  # avg_rating
        state_agg = (
            df_master.groupby("customer_state")["review_score"]
            .mean()
            .reset_index()
            .rename(columns={"review_score": "value"})
        )
        label_fmt = lambda v: f"{v:.2f} ★"
        color_label = "Avg Rating"

    geojson = _get_geojson()

    # ── Choropleth map ────────────────────────────────────────────────────────
    if geojson:
        fig = go.Figure(
            go.Choropleth(
                geojson=geojson,
                locations=state_agg["customer_state"],
                z=state_agg["value"],
                featureidkey="properties.sigla",
                colorscale=[
                    [0.0, "#1E2433"],
                    [0.5, "#7C3AED"],
                    [1.0, "#00D4FF"],
                ],
                marker_line_color="#0D0F14",
                marker_line_width=0.5,
                colorbar=dict(
                    title=dict(text=color_label, font=dict(color="#64748B", size=11)),
                    tickfont=dict(color="#64748B", family="Space Mono"),
                    bgcolor="rgba(0,0,0,0)",
                    outlinewidth=0,
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
        )
    else:
        # Fallback bar chart when GeoJSON is unavailable
        sorted_agg = state_agg.sort_values("value", ascending=True).tail(20)
        fig = go.Figure(
            go.Bar(
                x=sorted_agg["value"],
                y=sorted_agg["customer_state"],
                orientation="h",
                marker=dict(color="#7C3AED"),
            )
        )

    apply_chart_layout(fig, height=520)
    fig.update_layout(
        geo=dict(bgcolor="rgba(0,0,0,0)"),
        margin=dict(l=0, r=0, t=10, b=10),
    )

    # ── Top 10 Cities table ───────────────────────────────────────────────────
    if metric == "revenue":
        city_agg = (
            df_master.groupby(["customer_city", "customer_state"])["total_order_value"]
            .sum()
            .reset_index()
            .rename(columns={"total_order_value": "value"})
        )
    elif metric == "orders":
        city_agg = (
            df_master.groupby(["customer_city", "customer_state"])["order_id"]
            .nunique()
            .reset_index()
            .rename(columns={"order_id": "value"})
        )
    else:
        city_agg = (
            df_master.groupby(["customer_city", "customer_state"])["review_score"]
            .mean()
            .reset_index()
            .rename(columns={"review_score": "value"})
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

    return fig, html.Div(table, className="data-table-wrap")
