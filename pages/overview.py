"""
pages/overview.py — Page 1: Sales Overview
KPIs + Revenue Over Time + Orders by Status + Top 10 Categories
"""

import dash
from dash import html, dcc, callback, Input, Output
import plotly.graph_objects as go
import pandas as pd
from dash_iconify import DashIconify

from utils.data_loader import load_master_data
from utils.cleaner import apply_chart_layout, filter_by_date, format_brl, pct, tooltip

dash.register_page(__name__, path="/", name="Overview", order=0)

# ── Load data once at module level ────────────────────────────────────────────
df_master = load_master_data()
DATE_MIN = df_master["order_purchase_timestamp"].min().date()
DATE_MAX = df_master["order_purchase_timestamp"].max().date()


# ── Layout ────────────────────────────────────────────────────────────────────
layout = html.Div(
    [
        # Header
        html.Div(
            [
                html.H1("Sales Overview", className="page-title"),
                html.P(
                    "Monitor revenue, orders, satisfaction, and delivery performance.",
                    className="page-subtitle",
                ),
            ],
            className="page-header",
        ),
        # Date filter
        html.Div(
            [
                html.Span("Date Range:", className="filter-label"),
                dcc.DatePickerRange(
                    id="overview-date-range",
                    min_date_allowed=DATE_MIN,
                    max_date_allowed=DATE_MAX,
                    start_date=DATE_MIN,
                    end_date=DATE_MAX,
                    display_format="YYYY-MM-DD",
                    style={"fontFamily": "Space Mono"},
                ),
            ],
            className="filter-bar",
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
                                        "Total Revenue",
                                        tooltip(
                                            "Gross total of all customer orders in BRL."
                                        ),
                                    ],
                                    className="kpi-label",
                                    style={"display": "flex", "alignItems": "center"},
                                ),
                                DashIconify(
                                    icon="ph:currency-dollar-simple",
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
                        html.Div(id="kpi-revenue", className="kpi-value"),
                        html.P(id="kpi-revenue-delta", className="kpi-delta"),
                    ],
                    className="kpi-card kpi-cyan",
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.P(
                                    [
                                        "Total Orders",
                                        tooltip(
                                            "Count of distinct orders processed during the date range."
                                        ),
                                    ],
                                    className="kpi-label",
                                    style={"display": "flex", "alignItems": "center"},
                                ),
                                DashIconify(
                                    icon="ph:shopping-cart",
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
                        html.Div(id="kpi-orders", className="kpi-value"),
                        html.P(id="kpi-orders-delta", className="kpi-delta"),
                    ],
                    className="kpi-card kpi-purple",
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.P(
                                    [
                                        "Avg Review Score",
                                        tooltip(
                                            "Mean customer satisfaction score ranging from 1 to 5 stars."
                                        ),
                                    ],
                                    className="kpi-label",
                                    style={"display": "flex", "alignItems": "center"},
                                ),
                                DashIconify(
                                    icon="ph:star",
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
                        html.Div(id="kpi-review", className="kpi-value"),
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
                                        "On-Time Delivery",
                                        tooltip(
                                            "Percentage of orders successfully delivered to the customer on or before the estimated delivery date."
                                        ),
                                    ],
                                    className="kpi-label",
                                    style={"display": "flex", "alignItems": "center"},
                                ),
                                DashIconify(
                                    icon="ph:truck",
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
                        html.Div(id="kpi-ontime", className="kpi-value"),
                        html.P(
                            "Delivered on or before estimate", className="kpi-delta"
                        ),
                    ],
                    className="kpi-card kpi-amber",
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.P(
                                    [
                                        "Avg Order Value",
                                        tooltip(
                                            "Average revenue per order (AOV) — total revenue divided by total orders."
                                        ),
                                    ],
                                    className="kpi-label",
                                    style={"display": "flex", "alignItems": "center"},
                                ),
                                DashIconify(
                                    icon="ph:receipt-bold",
                                    width=20,
                                    style={
                                        "color": "var(--indigo)",
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
                        html.Div(id="kpi-aov", className="kpi-value"),
                        html.P("Revenue ÷ Orders (R$)", className="kpi-delta"),
                    ],
                    className="kpi-card kpi-purple",
                ),
            ],
            className="kpi-grid",
            style={"gridTemplateColumns": "repeat(5, 1fr)"},
        ),
        # Revenue over time (full width)
        html.Div(
            [
                html.Div(
                    [
                        html.P("Revenue Over Time", className="chart-title"),
                        html.P(
                            "Monthly revenue trend (R$)", className="chart-subtitle"
                        ),
                        dcc.Loading(
                            dcc.Graph(
                                id="chart-revenue-time", config={"displayModeBar": False}
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
        # Orders by Status + Top 10 Categories
        html.Div(
            [
                html.Div(
                    [
                        html.P("Orders by Status", className="chart-title"),
                        html.P(
                            "Distribution of order statuses", className="chart-subtitle"
                        ),
                        dcc.Loading(
                            dcc.Graph(
                                id="chart-orders-status", config={"displayModeBar": False}
                            ),
                            type="circle",
                            color="#38BDF8",
                            parent_className="chart-loading-wrapper",
                        ),
                    ],
                    className="chart-card",
                ),
                html.Div(
                    [
                        html.P("Top 10 Categories by Revenue", className="chart-title"),
                        html.P(
                            "Sum of item_price + freight per category",
                            className="chart-subtitle",
                        ),
                        dcc.Loading(
                            dcc.Graph(
                                id="chart-top-categories", config={"displayModeBar": False}
                            ),
                            type="circle",
                            color="#38BDF8",
                            parent_className="chart-loading-wrapper",
                        ),
                    ],
                    className="chart-card",
                ),
            ],
            className="chart-grid chart-grid-2",
        ),
        # Revenue Heatmap (full width)
        html.Div(
            [
                html.Div(
                    [
                        html.P(
                            [
                                "Revenue by Weekday & Hour",
                                tooltip(
                                    "Darker and brighter colors indicate higher revenue volumes during that specific hour and day."
                                ),
                            ],
                            className="chart-title",
                            style={"display": "flex", "alignItems": "center"},
                        ),
                        html.P(
                            "Identify peak shopping times (Local Time)", 
                            className="chart-subtitle"
                        ),
                        dcc.Loading(
                            dcc.Graph(
                                id="chart-revenue-heatmap", config={"displayModeBar": False}
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
            style={"marginTop": "20px"},
        ),
    ],
    style={"maxWidth": "1600px"},
)


# ── Callback ──────────────────────────────────────────────────────────────────
@callback(
    Output("kpi-revenue", "children"),
    Output("kpi-orders", "children"),
    Output("kpi-review", "children"),
    Output("kpi-ontime", "children"),
    Output("kpi-aov", "children"),
    Output("kpi-revenue-delta", "children"),
    Output("kpi-orders-delta", "children"),
    Output("chart-revenue-time", "figure"),
    Output("chart-orders-status", "figure"),
    Output("chart-top-categories", "figure"),
    Output("chart-revenue-heatmap", "figure"),
    Input("overview-date-range", "start_date"),
    Input("overview-date-range", "end_date"),
)
def update_overview(start_date, end_date):
    dff = (
        filter_by_date(df_master, start_date, end_date)
        if start_date and end_date
        else df_master.copy()
    )

    # ── KPIs ─────────────────────────────────────────────────────────────────
    total_rev = dff["total_order_value"].sum()
    total_ord = dff["order_id"].nunique()
    avg_review = dff["review_score"].mean()
    on_time = dff["is_on_time"].mean()
    aov = total_rev / max(total_ord, 1)

    # ── MoM Growth ───────────────────────────────────────────────────────────
    # Calculate the selected period length to construct the "previous" window
    sd = pd.Timestamp(start_date) if start_date else dff["order_purchase_timestamp"].min()
    ed = pd.Timestamp(end_date) if end_date else dff["order_purchase_timestamp"].max()
    delta = ed - sd
    prev_start = sd - delta - pd.Timedelta(days=1)
    prev_end = sd - pd.Timedelta(days=1)
    prev = df_master[
        (df_master["order_purchase_timestamp"] >= prev_start)
        & (df_master["order_purchase_timestamp"] <= prev_end)
    ]
    prev_rev = prev["total_order_value"].sum()
    prev_ord = prev["order_id"].nunique()

    def _arrow(current, previous):
        """Return a styled growth/decline element."""
        if previous == 0:
            return "vs. prior period"
        pct_chg = ((current - previous) / previous) * 100
        if pct_chg > 0:
            return html.Span(
                [
                    DashIconify(icon="ph:arrow-up-right-bold", width=14,
                                style={"marginRight": "3px"}),
                    f"+{pct_chg:.1f}% vs prior period",
                ],
                style={"color": "var(--green)", "display": "flex", "alignItems": "center"},
            )
        else:
            return html.Span(
                [
                    DashIconify(icon="ph:arrow-down-right-bold", width=14,
                                style={"marginRight": "3px"}),
                    f"{pct_chg:.1f}% vs prior period",
                ],
                style={"color": "var(--red)", "display": "flex", "alignItems": "center"},
            )

    rev_delta = _arrow(total_rev, prev_rev)
    ord_delta = _arrow(total_ord, prev_ord)

    # ── Revenue Over Time ─────────────────────────────────────────────────────
    monthly = (
        dff.groupby("month_year")["total_order_value"]
        .sum()
        .reset_index()
        .rename(columns={"total_order_value": "revenue", "month_year": "month"})
        .sort_values("month")
    )
    fig_time = go.Figure()
    fig_time.add_trace(
        go.Scatter(
            x=monthly["month"],
            y=monthly["revenue"],
            mode="lines+markers",
            line=dict(color="#00D4FF", width=2.5),
            marker=dict(color="#00D4FF", size=5),
            fill="tozeroy",
            fillcolor="rgba(0,212,255,0.07)",
            hovertemplate="<b>%{x}</b><br>R$ %{y:,.0f}<extra></extra>",
        )
    )
    apply_chart_layout(fig_time, height=280)

    # ── Orders by Status ──────────────────────────────────────────────────────
    status_counts = (
        dff.groupby("order_status")["order_id"]
        .nunique()
        .reset_index()
        .rename(columns={"order_id": "count"})
        .sort_values("count", ascending=False)
    )
    fig_status = go.Figure(
        go.Pie(
            labels=status_counts["order_status"],
            values=status_counts["count"],
            hole=0.75,
            textinfo="none", # Hide text on slices to keep it clean, relying on hover and legend
            marker=dict(
                colors=[
                    "#10B981", # delivered
                    "#00D4FF", # shipped
                    "#A78BFA", # processing/invoiced
                    "#FBBF24", # canceled
                    "#F87171", # unavailable
                    "#8B5CF6", 
                    "#38BDF8",
                ],
                line=dict(color="rgba(19, 23, 42, 0.8)", width=3), # Add a dark gap between slices
            ),
            hovertemplate="<div style='padding:4px;'><b>%{label}</b><br><span style='font-size:16px'>%{value:,} orders</span><br><span style='color:#38BDF8'>%{percent}</span></div><extra></extra>",
        )
    )
    apply_chart_layout(fig_status, height=300)
    fig_status.update_layout(
        showlegend=True,
        legend={
            "orientation": "v",
            "yanchor": "middle",
            "y": 0.5,
            "xanchor": "left",
            "x": 0.85,
            "font": {"family": "Inter", "size": 11, "color": "#94A3B8"},
            "bgcolor": "rgba(0,0,0,0)",
        },
        margin={"l": 0, "r": 120, "t": 10, "b": 10},
        annotations=[
            {
                "text": f"{total_ord:,}",
                "x": 0.38, 
                "y": 0.55, 
                "font": {"size": 24, "family": "Plus Jakarta Sans", "color": "#E2E8F0"},
                "showarrow": False,
            },
            {
                "text": "Total",
                "x": 0.38, 
                "y": 0.43, 
                "font": {"size": 12, "family": "Inter", "color": "#94A3B8"},
                "showarrow": False,
            }
        ]
    )

    # ── Top 10 Categories ─────────────────────────────────────────────────────
    cat_rev = (
        dff.groupby("product_category_name_english")["total_order_value"]
        .sum()
        .nlargest(10)
        .reset_index()
        .rename(
            columns={
                "product_category_name_english": "category",
                "total_order_value": "revenue",
            }
        )
        .sort_values("revenue")
    )
    fig_cat = go.Figure(
        go.Bar(
            x=cat_rev["revenue"],
            y=cat_rev["category"],
            orientation="h",
            marker=dict(
                color=cat_rev["revenue"],
                colorscale=[[0, "#1E2433"], [0.5, "#7C3AED"], [1, "#00D4FF"]],
                line=dict(width=0),
            ),
            hovertemplate="<b>%{y}</b><br>R$ %{x:,.0f}<extra></extra>",
        )
    )
    apply_chart_layout(fig_cat, height=300)
    fig_cat.update_layout(yaxis=dict(tickfont=dict(size=10)))

    # ── Revenue Heatmap ───────────────────────────────────────────────────────
    dow_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    if "purchase_dow" in dff.columns and "purchase_hour" in dff.columns:
        hm_data = (
            dff.groupby(["purchase_dow", "purchase_hour"])["total_order_value"]
            .sum()
            .reset_index()
        )
        hm_pivot = hm_data.pivot(index="purchase_dow", columns="purchase_hour", values="total_order_value").fillna(0)
        # Ensure all hours (0-23) and DOWs are present
        hm_pivot = hm_pivot.reindex(index=dow_order, columns=list(range(24)), fill_value=0)
    else:
        hm_pivot = pd.DataFrame(0, index=dow_order, columns=list(range(24)))

    fig_hm = go.Figure(
        data=go.Heatmap(
            z=hm_pivot.values,
            x=[f"{h:02d}:00" for h in hm_pivot.columns],
            y=hm_pivot.index,
            colorscale=[[0, "#0B0E17"], [0.2, "#1E293B"], [0.5, "#8B5CF6"], [1.0, "#00D4FF"]],
            showscale=False,
            hovertemplate="<b>%{y} at %{x}</b><br>Revenue: R$ %{z:,.0f}<extra></extra>",
            xgap=2,
            ygap=2,
        )
    )
    apply_chart_layout(fig_hm, height=320)
    # Reverse y-axis so Monday is at the top
    fig_hm.update_layout(
        xaxis=dict(gridcolor="rgba(0,0,0,0)", fixedrange=True, tickangle=-45),
        yaxis=dict(gridcolor="rgba(0,0,0,0)", autorange="reversed", fixedrange=True),
        margin=dict(l=80, r=20, t=10, b=20),
    )

    return (
        format_brl(total_rev),
        f"{total_ord:,}",
        html.Div(
            [
                html.Span(f"{avg_review:.2f}"),
                DashIconify(
                    icon="ph:star-fill",
                    width=16,
                    style={"marginLeft": "4px", "color": "var(--green)"},
                ),
            ],
            style={"display": "flex", "alignItems": "center"},
        ),
        pct(on_time),
        format_brl(aov),
        rev_delta,
        ord_delta,
        fig_time,
        fig_status,
        fig_cat,
        fig_hm,
    )
