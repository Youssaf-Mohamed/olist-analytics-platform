"""
pages/sellers.py — Page 8: Seller Performance Analytics
Top sellers, geographic distribution, delivery speed, customer satisfaction.
"""

import dash
from dash import html, dcc, callback, Input, Output
import plotly.graph_objects as go
from dash_iconify import DashIconify

from components.page_helpers import page_section
from utils.data_loader import load_data_bundle
from utils.cleaner import apply_chart_layout, filter_by_date, format_brl, pct, tooltip

dash.register_page(__name__, path="/sellers", name="Sellers", order=7)

# ── Load data once ────────────────────────────────────────────────────────────
DATA_BUNDLE = load_data_bundle()
seller_orders_df = DATA_BUNDLE["seller_orders"]
DATE_MIN = seller_orders_df["order_purchase_timestamp"].min().date()
DATE_MAX = seller_orders_df["order_purchase_timestamp"].max().date()


# ── Layout ────────────────────────────────────────────────────────────────────
layout = page_section(
    html.Div(
    [
        # Header
        html.Div(
            [
                html.H1("Seller Performance Analytics", className="page-title"),
                html.P(
                    "Analyse seller performance, geographic reach, delivery efficiency, and customer satisfaction.",
                    className="page-subtitle",
                ),
            ],
            className="page-header",
        ),
        html.Div(
            "This page follows the global date range in the top bar so seller comparisons stay aligned with the rest of the dashboard.",
            className="global-filter-note",
        ),
        # KPI cards
        html.Div(
            [
                html.Div(
                    [
                        html.Div(
                            [
                                html.P(
                                    [
                                        "Active Sellers",
                                        tooltip(
                                            "Total unique sellers who made at least one sale in the selected period."
                                        ),
                                    ],
                                    className="kpi-label",
                                    style={"display": "flex", "alignItems": "center"},
                                ),
                                DashIconify(
                                    icon="ph:storefront-bold",
                                    width=20,
                                    style={
                                        "color": "var(--cyan)",
                                        "marginBottom": "8px",
                                    },
                                ),
                            ],
                            style={
                                "display": "flex",
                                "justifyContent": "space-between",
                                "alignItems": "flex-start",
                            },
                        ),
                        html.Div(id="sellers-kpi-total", className="kpi-value"),
                        html.P("Unique sellers with sales", className="kpi-delta"),
                    ],
                    className="kpi-card kpi-cyan",
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.P(
                                    [
                                        "Avg Revenue / Seller",
                                        tooltip(
                                            "Mean revenue generated per active seller in the selected period."
                                        ),
                                    ],
                                    className="kpi-label",
                                    style={"display": "flex", "alignItems": "center"},
                                ),
                                DashIconify(
                                    icon="ph:currency-dollar-simple",
                                    width=20,
                                    style={
                                        "color": "var(--purple)",
                                        "marginBottom": "8px",
                                    },
                                ),
                            ],
                            style={
                                "display": "flex",
                                "justifyContent": "space-between",
                                "alignItems": "flex-start",
                            },
                        ),
                        html.Div(id="sellers-kpi-avg-rev", className="kpi-value"),
                        html.P("Average per seller (R$)", className="kpi-delta"),
                    ],
                    className="kpi-card kpi-purple",
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.P(
                                    [
                                        "Avg Seller Rating",
                                        tooltip(
                                            "Mean customer review score for orders handled by sellers in this period."
                                        ),
                                    ],
                                    className="kpi-label",
                                    style={"display": "flex", "alignItems": "center"},
                                ),
                                DashIconify(
                                    icon="ph:star-bold",
                                    width=20,
                                    style={
                                        "color": "var(--green)",
                                        "marginBottom": "8px",
                                    },
                                ),
                            ],
                            style={
                                "display": "flex",
                                "justifyContent": "space-between",
                                "alignItems": "flex-start",
                            },
                        ),
                        html.Div(id="sellers-kpi-rating", className="kpi-value"),
                        html.P("Scale: 1 (worst) — 5 (best)", className="kpi-delta"),
                    ],
                    className="kpi-card kpi-green",
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.P(
                                    [
                                        "Avg Delivery Speed",
                                        tooltip(
                                            "Average number of days sellers take to fulfil and deliver orders."
                                        ),
                                    ],
                                    className="kpi-label",
                                    style={"display": "flex", "alignItems": "center"},
                                ),
                                DashIconify(
                                    icon="ph:truck-bold",
                                    width=20,
                                    style={
                                        "color": "var(--amber)",
                                        "marginBottom": "8px",
                                    },
                                ),
                            ],
                            style={
                                "display": "flex",
                                "justifyContent": "space-between",
                                "alignItems": "flex-start",
                            },
                        ),
                        html.Div(id="sellers-kpi-speed", className="kpi-value"),
                        html.P("From purchase to delivery", className="kpi-delta"),
                    ],
                    className="kpi-card kpi-amber",
                ),
            ],
            className="kpi-grid",
        ),
        # Top 10 Sellers by Revenue + Seller State Distribution
        html.Div(
            [
                html.Div(
                    [
                        html.P(
                            [
                                "Top 10 Sellers by Revenue",
                                tooltip(
                                    "Leaderboard of the top-performing sellers ranked by total revenue generated."
                                ),
                            ],
                            className="chart-title",
                            style={"display": "flex", "alignItems": "center"},
                        ),
                        html.P(
                            "Sum of order values per seller (R$)",
                            className="chart-subtitle",
                        ),
                        dcc.Loading(
                            dcc.Graph(
                                id="sellers-top-revenue",
                                config={"displayModeBar": False},
                            ),
                            type="circle",
                            color="#38BDF8",
                            parent_className="chart-loading-wrapper",
                            overlay_style={
                                "visibility": "visible",
                                "opacity": 0.6,
                                "backgroundColor": "rgba(11,14,23,0.7)",
                            },
                        ),
                    ],
                    className="chart-card",
                ),
                html.Div(
                    [
                        html.P(
                            [
                                "Seller Distribution by State",
                                tooltip(
                                    "Geographic distribution showing which Brazilian states have the most active sellers."
                                ),
                            ],
                            className="chart-title",
                            style={"display": "flex", "alignItems": "center"},
                        ),
                        html.P(
                            "Number of unique sellers per state",
                            className="chart-subtitle",
                        ),
                        dcc.Loading(
                            dcc.Graph(
                                id="sellers-state-dist",
                                config={"displayModeBar": False},
                            ),
                            type="circle",
                            color="#38BDF8",
                            parent_className="chart-loading-wrapper",
                            overlay_style={
                                "visibility": "visible",
                                "opacity": 0.6,
                                "backgroundColor": "rgba(11,14,23,0.7)",
                            },
                        ),
                    ],
                    className="chart-card",
                ),
            ],
            className="chart-grid chart-grid-2",
        ),
        # Seller Rating vs Delivery Days Scatter + On-Time Rate by State
        html.Div(
            [
                html.Div(
                    [
                        html.P(
                            [
                                "Seller Rating vs Delivery Speed",
                                tooltip(
                                    "Correlation between average delivery days and customer satisfaction per seller. Faster delivery → higher ratings?"
                                ),
                            ],
                            className="chart-title",
                            style={"display": "flex", "alignItems": "center"},
                        ),
                        html.P(
                            "Each dot = one seller  |  colour = on-time rate",
                            className="chart-subtitle",
                        ),
                        dcc.Loading(
                            dcc.Graph(
                                id="sellers-scatter",
                                config={"displayModeBar": False},
                            ),
                            type="circle",
                            color="#38BDF8",
                            parent_className="chart-loading-wrapper",
                            overlay_style={
                                "visibility": "visible",
                                "opacity": 0.6,
                                "backgroundColor": "rgba(11,14,23,0.7)",
                            },
                        ),
                    ],
                    className="chart-card",
                ),
                html.Div(
                    [
                        html.P(
                            [
                                "Seller On-Time Delivery by State",
                                tooltip(
                                    "Average on-time delivery rate of sellers grouped by their home state."
                                ),
                            ],
                            className="chart-title",
                            style={"display": "flex", "alignItems": "center"},
                        ),
                        html.P(
                            "Top 15 states — percentage of on-time deliveries",
                            className="chart-subtitle",
                        ),
                        dcc.Loading(
                            dcc.Graph(
                                id="sellers-ontime-state",
                                config={"displayModeBar": False},
                            ),
                            type="circle",
                            color="#38BDF8",
                            parent_className="chart-loading-wrapper",
                            overlay_style={
                                "visibility": "visible",
                                "opacity": 0.6,
                                "backgroundColor": "rgba(11,14,23,0.7)",
                            },
                        ),
                    ],
                    className="chart-card",
                ),
            ],
            className="chart-grid chart-grid-2",
        ),
        # Top 10 Sellers Table
        html.Div(
            [
                html.Div(
                    [
                        html.P(
                            [
                                "Seller Performance Leaderboard",
                                tooltip(
                                    "Detailed breakdown of top sellers with revenue, orders, average rating, and on-time delivery rate."
                                ),
                            ],
                            className="chart-title",
                            style={"display": "flex", "alignItems": "center"},
                        ),
                        html.P(
                            "Top 10 sellers ranked by total revenue",
                            className="chart-subtitle",
                        ),
                        dcc.Loading(
                            html.Div(id="sellers-table-wrap"),
                            type="circle",
                            color="#38BDF8",
                            parent_className="chart-loading-wrapper",
                            overlay_style={
                                "visibility": "visible",
                                "opacity": 0.6,
                                "backgroundColor": "rgba(11,14,23,0.7)",
                            },
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
    Output("sellers-kpi-total", "children"),
    Output("sellers-kpi-avg-rev", "children"),
    Output("sellers-kpi-rating", "children"),
    Output("sellers-kpi-speed", "children"),
    Output("sellers-top-revenue", "figure"),
    Output("sellers-state-dist", "figure"),
    Output("sellers-scatter", "figure"),
    Output("sellers-ontime-state", "figure"),
    Output("sellers-table-wrap", "children"),
    Output("sellers-page-context", "data"),
    Input("global-date-range", "start_date"),
    Input("global-date-range", "end_date"),
    Input("global-compare-toggle", "value"),
    Input("theme-store", "data"),
    Input("app-container", "data-theme"),
)
def update_sellers(start_date, end_date, compare_values, theme="dark", applied_theme="dark"):
    theme = applied_theme or theme or "dark"
    dff = (
        filter_by_date(seller_orders_df, start_date, end_date)
        if start_date and end_date
        else seller_orders_df.copy()
    )

    # ── Seller-level aggregation ──────────────────────────────────────────────
    seller_stats = (
        dff.dropna(subset=["seller_id"])
        .groupby("seller_id")
        .agg(
            revenue=("seller_revenue", "sum"),
            orders=("order_id", "nunique"),
            avg_rating=("review_score", "mean"),
            avg_delivery=("delivery_days", "mean"),
            on_time_rate=("is_on_time", "mean"),
            seller_state=("seller_state", "first"),
            seller_city=("seller_city", "first"),
        )
        .reset_index()
    )

    # ── KPIs ──────────────────────────────────────────────────────────────────
    n_sellers = seller_stats["seller_id"].nunique()
    avg_rev = seller_stats["revenue"].mean() if not seller_stats.empty else 0
    avg_rating = seller_stats["avg_rating"].mean() if not seller_stats.empty else 0
    avg_speed = seller_stats["avg_delivery"].mean() if not seller_stats.empty else 0

    # ── Top 10 Sellers by Revenue ─────────────────────────────────────────────
    top10 = seller_stats.nlargest(10, "revenue").copy()
    top10["label"] = top10["seller_id"].str[:8] + "…"
    top10 = top10.sort_values("revenue")

    fig_top = go.Figure(
        go.Bar(
            x=top10["revenue"],
            y=top10["label"],
            orientation="h",
            marker=dict(
                color=top10["revenue"],
                colorscale=[[0, "#1E2433"], [0.5, "#7C3AED"], [1, "#00D4FF"]],
                line=dict(width=0),
            ),
            hovertemplate=(
                "<b>Seller: %{customdata[0]}</b><br>"
                "Revenue: R$ %{x:,.0f}<br>"
                "Orders: %{customdata[1]:,}<br>"
                "Rating: %{customdata[2]:.2f} ★"
                "<extra></extra>"
            ),
            customdata=list(
                zip(
                    top10["seller_id"],
                    top10["orders"],
                    top10["avg_rating"],
                )
            ),
        )
    )
    apply_chart_layout(fig_top, height=320, theme=theme)
    fig_top.update_layout(yaxis=dict(tickfont=dict(size=10)))

    # ── Seller Distribution by State ──────────────────────────────────────────
    state_dist = (
        seller_stats.groupby("seller_state")["seller_id"]
        .nunique()
        .reset_index()
        .rename(columns={"seller_id": "count"})
        .sort_values("count", ascending=False)
        .head(15)
    )

    fig_state = go.Figure(
        go.Bar(
            x=state_dist["seller_state"],
            y=state_dist["count"],
            marker=dict(
                color=state_dist["count"],
                colorscale=[[0, "#1E2433"], [0.5, "#A78BFA"], [1, "#38BDF8"]],
                line=dict(width=0),
            ),
            hovertemplate="<b>%{x}</b><br>%{y} sellers<extra></extra>",
        )
    )
    apply_chart_layout(fig_state, height=320, theme=theme)
    fig_state.update_layout(xaxis_title="State", yaxis_title="Sellers")

    # ── Seller Rating vs Delivery Speed Scatter ───────────────────────────────
    scatter_df = seller_stats.dropna(
        subset=["avg_delivery", "avg_rating", "on_time_rate"]
    ).copy()
    if len(scatter_df) > 2_000:
        scatter_df = scatter_df.sample(2_000, random_state=42)

    fig_scatter = go.Figure(
        go.Scatter(
            x=scatter_df["avg_delivery"],
            y=scatter_df["avg_rating"],
            mode="markers",
            marker=dict(
                color=scatter_df["on_time_rate"],
                colorscale=[
                    [0.0, "#EF4444"],
                    [0.5, "#FBBF24"],
                    [1.0, "#10B981"],
                ],
                size=6,
                opacity=0.7,
                colorbar=dict(
                    title=dict(
                        text="On-Time %",
                        font=dict(color="#64748B", size=11),
                    ),
                    tickfont=dict(color="#64748B", family="Space Mono"),
                    bgcolor="rgba(0,0,0,0)",
                    outlinewidth=0,
                    thickness=12,
                    tickformat=".0%",
                ),
                cmin=0,
                cmax=1,
            ),
            hovertemplate=(
                "Delivery: %{x:.1f} days<br>"
                "Rating: %{y:.2f} ★<br>"
                "On-Time: %{marker.color:.0%}"
                "<extra></extra>"
            ),
        )
    )
    apply_chart_layout(fig_scatter, height=320, theme=theme)
    fig_scatter.update_layout(
        xaxis_title="Avg Delivery Days",
        yaxis_title="Avg Review Score",
    )

    # ── On-Time Rate by Seller State ──────────────────────────────────────────
    state_ontime = (
        seller_stats.groupby("seller_state")["on_time_rate"]
        .mean()
        .reset_index()
        .sort_values("on_time_rate")
        .head(15)
    )

    fig_ontime = go.Figure(
        go.Bar(
            x=state_ontime["on_time_rate"],
            y=state_ontime["seller_state"],
            orientation="h",
            marker=dict(
                color=state_ontime["on_time_rate"],
                colorscale=[[0, "#EF4444"], [0.5, "#FBBF24"], [1, "#10B981"]],
                line=dict(width=0),
            ),
            hovertemplate="<b>%{y}</b><br>On-Time: %{x:.1%}<extra></extra>",
        )
    )
    apply_chart_layout(fig_ontime, height=320, theme=theme)
    fig_ontime.update_layout(
        xaxis=dict(title="On-Time Rate", tickformat=".0%"),
    )

    # ── Seller Performance Table ──────────────────────────────────────────────
    table_data = seller_stats.nlargest(10, "revenue").reset_index(drop=True)
    rows = []
    for i, row in table_data.iterrows():
        # Rating badge colour
        rating = row["avg_rating"]
        if rating >= 4.0:
            badge_cls = "badge badge-green"
        elif rating >= 3.0:
            badge_cls = "badge badge-amber"
        else:
            badge_cls = "badge badge-red"

        # On-time badge colour
        ot = row["on_time_rate"]
        if ot >= 0.9:
            ot_cls = "badge badge-green"
        elif ot >= 0.75:
            ot_cls = "badge badge-amber"
        else:
            ot_cls = "badge badge-red"

        rows.append(
            html.Tr(
                [
                    html.Td(str(i + 1), className="mono"),
                    html.Td(
                        row["seller_id"][:12] + "…",
                        title=row["seller_id"],
                        style={"fontFamily": "var(--font-mono)", "fontSize": "0.84rem"},
                    ),
                    html.Td(
                        html.Span(row["seller_state"], className="badge badge-cyan")
                    ),
                    html.Td(format_brl(row["revenue"]), className="mono"),
                    html.Td(f"{int(row['orders']):,}", className="mono"),
                    html.Td(
                        html.Span(f"{rating:.2f} ★", className=badge_cls)
                    ),
                    html.Td(
                        html.Span(pct(ot), className=ot_cls)
                    ),
                ]
            )
        )

    table = html.Table(
        [
            html.Thead(
                html.Tr(
                    [
                        html.Th("#"),
                        html.Th("Seller ID"),
                        html.Th("State"),
                        html.Th("Revenue"),
                        html.Th("Orders"),
                        html.Th("Rating"),
                        html.Th("On-Time"),
                    ]
                )
            ),
            html.Tbody(rows),
        ],
        className="data-table",
    )

    context = {
        "page": "sellers",
        "filters": {
            "start_date": start_date,
            "end_date": end_date,
            "compare_previous": "compare" in (compare_values or []),
        },
        "headline_metrics": {
            "seller_count": int(n_sellers),
            "avg_seller_revenue": format_brl(avg_rev),
            "avg_seller_rating": f"{avg_rating:.2f}" if avg_rating == avg_rating else "N/A",
        },
    }

    return (
        f"{n_sellers:,}",
        format_brl(avg_rev),
        html.Div(
            [
                html.Span(f"{avg_rating:.2f}"),
                DashIconify(
                    icon="ph:star-fill",
                    width=16,
                    style={"marginLeft": "4px", "color": "var(--green)"},
                ),
            ],
            style={"display": "flex", "alignItems": "center"},
        ),
        f"{avg_speed:.1f} days",
        fig_top,
        fig_state,
        fig_scatter,
        fig_ontime,
        html.Div(table, className="data-table-wrap"),
        context,
    )
