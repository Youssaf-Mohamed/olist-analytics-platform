"""
pages/payments.py — Page 5: Payments & Delivery Analytics
2 KPIs + Payment Distribution + Delivery by State + Scatter (Value vs Days)
"""

import dash
from dash import html, dcc, callback, Input, Output
import plotly.graph_objects as go
from dash_iconify import DashIconify

from components.page_helpers import page_section
from utils.data_loader import load_data_bundle
from utils.cleaner import (
    apply_chart_layout,
    filter_by_date,
    filter_by_date_column,
    format_brl,
    get_chart_theme,
    pct,
    tooltip,
)

dash.register_page(__name__, path="/payments", name="Payments & Delivery", order=4)

# ── Load data once ────────────────────────────────────────────────────────────
DATA_BUNDLE = load_data_bundle()
orders_df = DATA_BUNDLE["orders"]
payments_df = DATA_BUNDLE["payments"]
payments_daily_df = DATA_BUNDLE["agg_payments_daily"]
delivery_state_daily_df = DATA_BUNDLE["agg_delivery_state_daily"]
cancellations_daily_df = DATA_BUNDLE["agg_cancellations_daily"]
scatter_sample_df = DATA_BUNDLE["agg_scatter_orders_sample"]
DATE_MIN = orders_df["order_purchase_timestamp"].min().date()
DATE_MAX = orders_df["order_purchase_timestamp"].max().date()

# ── Layout ────────────────────────────────────────────────────────────────────
layout = page_section(
    html.Div(
    [
        html.Div(
            [
                html.H1("Payments & Delivery Analytics", className="page-title"),
                html.P(
                    "Full-dataset view of payment methods, delivery performance, and order value distribution.",
                    className="page-subtitle",
                ),
            ],
            className="page-header",
        ),
        html.Div(
            "This page follows the global date range in the top bar for synchronized payment and delivery analysis.",
            className="global-filter-note",
        ),
        # 2 KPI cards
        html.Div(
            [
                html.Div(
                    [
                        html.Div(
                            [
                                html.P(
                                    [
                                        "On-Time Delivery Rate",
                                        tooltip(
                                            "Percentage of orders successfully delivered before or on their estimated date."
                                        ),
                                    ],
                                    className="kpi-label",
                                    style={"display": "flex", "alignItems": "center"},
                                ),
                                DashIconify(
                                    icon="ph:check-circle",
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
                        html.Div(id="pay-kpi-ontime", className="kpi-value"),
                        html.P("Delivered ≤ estimated date", className="kpi-delta"),
                    ],
                    className="kpi-card kpi-green",
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.P(
                                    [
                                        "Avg Delivery Days",
                                        tooltip(
                                            "Calculated mean of elapsed days between order purchase and actual delivery to customer."
                                        ),
                                    ],
                                    className="kpi-label",
                                    style={"display": "flex", "alignItems": "center"},
                                ),
                                DashIconify(
                                    icon="ph:clock",
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
                        html.Div(id="pay-kpi-days", className="kpi-value"),
                        html.P("From purchase to delivery", className="kpi-delta"),
                    ],
                    className="kpi-card kpi-amber",
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.P(
                                    [
                                        "Total Payment Volume",
                                        tooltip(
                                            "Sum total of all payment transactions including credit cards, boletos, vouchers, and debit cards."
                                        ),
                                    ],
                                    className="kpi-label",
                                    style={"display": "flex", "alignItems": "center"},
                                ),
                                DashIconify(
                                    icon="ph:coins",
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
                        html.Div(id="pay-kpi-volume", className="kpi-value"),
                        html.P("Sum of all payment values (R$)", className="kpi-delta"),
                    ],
                    className="kpi-card kpi-cyan",
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.P(
                                    [
                                        "Avg Installments",
                                        tooltip(
                                            "Mean number of split payments (installments) chosen by customers."
                                        ),
                                    ],
                                    className="kpi-label",
                                    style={"display": "flex", "alignItems": "center"},
                                ),
                                DashIconify(
                                    icon="ph:list-numbers",
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
                        html.Div(id="pay-kpi-install", className="kpi-value"),
                        html.P(
                            "Mean payment installments count", className="kpi-delta"
                        ),
                    ],
                    className="kpi-card kpi-purple",
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.P(
                                    [
                                        "Cancellation Rate",
                                        tooltip(
                                            "Percentage of total orders that were canceled."
                                        ),
                                    ],
                                    className="kpi-label",
                                    style={"display": "flex", "alignItems": "center"},
                                ),
                                DashIconify(
                                    icon="ph:x-circle-bold",
                                    width=20,
                                    style={
                                        "color": "var(--red)",
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
                        html.Div(id="pay-kpi-cancel", className="kpi-value"),
                        html.P(
                            "Proportion of canceled orders", className="kpi-delta"
                        ),
                    ],
                    className="kpi-card kpi-red",
                ),
            ],
            className="kpi-grid",
            style={"gridTemplateColumns": "repeat(5, 1fr)"},
        ),
        # Payment distribution + Delivery by State
        html.Div(
            [
                html.Div(
                    [
                        html.P(
                            [
                                "Payment Type Distribution",
                                tooltip(
                                    "Breakdown of order volume by the type of payment method applied."
                                ),
                            ],
                            className="chart-title",
                            style={"display": "flex", "alignItems": "center"},
                        ),
                        html.P(
                            "Proportion of each payment method",
                            className="chart-subtitle",
                        ),
                        dcc.Loading(
                            dcc.Graph(
                                id="pay-chart-types", config={"displayModeBar": False}
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
                        html.P(
                            [
                                "Avg Delivery Days by State",
                                tooltip(
                                    "Logistics efficiency sorted showing which states have the quickest and slowest deliveries."
                                ),
                            ],
                            className="chart-title",
                            style={"display": "flex", "alignItems": "center"},
                        ),
                        html.P(
                            "Top 15 states — sorted ascending",
                            className="chart-subtitle",
                        ),
                        dcc.Loading(
                            dcc.Graph(
                                id="pay-chart-states", config={"displayModeBar": False}
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
        # Scatter: order value vs delivery days
        html.Div(
            [
                html.Div(
                    [
                        html.P(
                            [
                                "Order Value vs Delivery Days",
                                tooltip(
                                    "Correlation visualization measuring whether expensive orders take longer or are prioritized for delivery. Color acts as review score proxy."
                                ),
                            ],
                            className="chart-title",
                            style={"display": "flex", "alignItems": "center"},
                        ),
                        html.P(
                            "Scatter plot — color = review score  |  sample of 5,000 orders",
                            className="chart-subtitle",
                        ),
                        dcc.Loading(
                            dcc.Graph(
                                id="pay-chart-scatter", config={"displayModeBar": False}
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
        # Cancellations over time
        html.Div(
            [
                html.Div(
                    [
                        html.P(
                            [
                                "Cancellations Over Time",
                                tooltip(
                                    "Monthly volume of orders with a 'canceled' status."
                                ),
                            ],
                            className="chart-title",
                            style={"display": "flex", "alignItems": "center"},
                        ),
                        html.P(
                            "Track order cancellations month by month",
                            className="chart-subtitle",
                        ),
                        dcc.Loading(
                            dcc.Graph(
                                id="pay-chart-cancellations", config={"displayModeBar": False}
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
    ),
)


# ── Callback (triggered once on load — no inputs needed) ─────────────────────
@callback(
    Output("pay-kpi-ontime", "children"),
    Output("pay-kpi-days", "children"),
    Output("pay-kpi-volume", "children"),
    Output("pay-kpi-install", "children"),
    Output("pay-kpi-cancel", "children"),
    Output("pay-chart-types", "figure"),
    Output("pay-chart-states", "figure"),
    Output("pay-chart-scatter", "figure"),
    Output("pay-chart-cancellations", "figure"),
    Output("payments-page-context", "data"),
    Input("global-date-range", "start_date"),
    Input("global-date-range", "end_date"),
    Input("global-compare-toggle", "value"),
    Input("theme-store", "data"),
    Input("app-container", "data-theme"),
)
def update_payments(start_date, end_date, compare_values, theme="dark", applied_theme="dark"):
    theme = applied_theme or theme or "dark"
    palette = get_chart_theme(theme)
    dff = (
        filter_by_date(orders_df, start_date, end_date)
        if start_date and end_date
        else orders_df.copy()
    )
    payments_dff = (
        filter_by_date_column(payments_daily_df, "order_date", start_date, end_date)
        if start_date and end_date
        else payments_daily_df.copy()
    )
    delivered_dff = dff[dff["order_status"] == "delivered"].copy()
    delivery_state_dff = (
        filter_by_date_column(delivery_state_daily_df, "order_date", start_date, end_date)
        if start_date and end_date
        else delivery_state_daily_df.copy()
    )
    cancel_dff = (
        filter_by_date_column(cancellations_daily_df, "order_date", start_date, end_date)
        if start_date and end_date
        else cancellations_daily_df.copy()
    )
    scatter_df = (
        filter_by_date(scatter_sample_df, start_date, end_date)
        if start_date and end_date
        else scatter_sample_df.copy()
    )

    # ── KPIs ─────────────────────────────────────────────────────────────────
    on_time_rate = delivered_dff["is_on_time"].mean()
    avg_days = delivered_dff["delivery_days"].mean()
    total_pay = payments_dff["payment_value_sum"].sum()
    avg_install = dff["payment_installments"].mean()
    cancel_rate = len(dff[dff["order_status"] == "canceled"]) / max(len(dff["order_id"].unique()), 1)

    # Format KPIs
    def _brl(v):
        if v >= 1e6:
            return f"R$ {v/1e6:.1f}M"
        if v >= 1e3:
            return f"R$ {v/1e3:.1f}K"
        return f"R$ {v:,.0f}"

    kpi_ontime = pct(on_time_rate) if on_time_rate == on_time_rate else "N/A"
    kpi_days = f"{avg_days:.1f} days" if avg_days == avg_days else "N/A"
    kpi_volume = _brl(total_pay)
    kpi_install = f"{avg_install:.1f}×"
    kpi_cancel = pct(cancel_rate)

    # ── Payment type donut ────────────────────────────────────────────────────
    pay_counts = (
        payments_dff.groupby("payment_type")["payment_value_sum"]
        .sum()
        .reset_index()
        .rename(columns={"payment_value_sum": "value"})
        .sort_values("value", ascending=False)
    )
    COLORS = ["#00D4FF", "#7C3AED", "#10B981", "#F59E0B", "#EF4444", "#06B6D4"]
    fig_types = go.Figure(
        go.Pie(
            labels=pay_counts["payment_type"],
            values=pay_counts["value"],
            hole=0.55,
            textinfo="label+percent",
            textfont=dict(family="DM Sans", size=11),
            marker=dict(
                colors=COLORS[: len(pay_counts)],
                line=dict(color="rgba(0,0,0,0)", width=0),
            ),
            hovertemplate="<b>%{label}</b><br>R$ %{value:,.0f} (%{percent})<extra></extra>",
        )
    )
    apply_chart_layout(fig_types, height=320, theme=theme)

    # ── Delivery days by state ────────────────────────────────────────────────
    state_days = (
        delivery_state_dff.groupby("customer_state", as_index=False)
        .agg(
            delivery_days_sum=("delivery_days_sum", "sum"),
            delivered_count=("delivered_count", "sum"),
        )
        .assign(
            delivery_days=lambda df: df["delivery_days_sum"]
            / df["delivered_count"].clip(lower=1)
        )
        .reset_index()
        .sort_values("delivery_days")
        .head(15)
    )
    fig_states = go.Figure(
        go.Bar(
            x=state_days["delivery_days"],
            y=state_days["customer_state"],
            orientation="h",
            marker=dict(
                color=state_days["delivery_days"],
                colorscale=[[0, "#10B981"], [0.5, "#7C3AED"], [1, "#EF4444"]],
                line=dict(width=0),
            ),
            hovertemplate="<b>%{y}</b><br>Avg %{x:.1f} days<extra></extra>",
        )
    )
    apply_chart_layout(fig_states, height=320, theme=theme)
    fig_states.update_layout(xaxis_title="Days")

    # ── Scatter: Order Value vs Delivery Days ─────────────────────────────────
    fig_scatter = go.Figure(
        go.Scatter(
            x=scatter_df["total_order_value"],
            y=scatter_df["delivery_days"],
            mode="markers",
            marker=dict(
                color=scatter_df["review_score"],
                colorscale=[
                    [0.0, "#EF4444"],
                    [0.25, "#F59E0B"],
                    [0.5, "#7C3AED"],
                    [0.75, "#10B981"],
                    [1.0, "#00D4FF"],
                ],
                size=4,
                opacity=0.6,
                colorbar=dict(
                    title=dict(
                        text="Review Score",
                        font=dict(color=palette["tick_color"], size=11),
                    ),
                    tickfont=dict(color=palette["tick_color"], family="Space Mono"),
                    bgcolor="rgba(0,0,0,0)",
                    outlinewidth=0,
                    thickness=12,
                ),
                cmin=1,
                cmax=5,
            ),
            hovertemplate=(
                "Order Value: R$ %{x:,.0f}<br>"
                "Delivery: %{y:.0f} days<br>"
                "Score: %{marker.color:.1f}<extra></extra>"
            ),
        )
    )
    apply_chart_layout(fig_scatter, height=360, theme=theme)
    fig_scatter.update_layout(
        xaxis_title="Order Value (R$)",
        yaxis_title="Delivery Days",
    )

    # ── Cancellations Over Time ──────────────────────────────────────────────
    cancel_monthly = (
        cancel_dff.assign(month=cancel_dff["order_date"].dt.to_period("M").astype(str))
        .groupby("month")["canceled_orders"]
        .sum()
        .reset_index()
        .rename(columns={"canceled_orders": "cancellations"})
        .sort_values("month")
    )
    if not cancel_monthly.empty:
        fig_cancel = go.Figure(
            go.Bar(
                x=cancel_monthly["month"],
                y=cancel_monthly["cancellations"],
                marker_color="#F87171",
                hovertemplate="<b>%{x}</b><br>%{y} canceled orders<extra></extra>",
            )
        )
    else:
        fig_cancel = go.Figure()
    apply_chart_layout(fig_cancel, height=300, theme=theme)
    fig_cancel.update_layout(
        xaxis=dict(tickangle=-45),
        yaxis=dict(title="Canceled Orders"),
    )

    context = {
        "page": "payments",
        "filters": {
            "start_date": start_date,
            "end_date": end_date,
            "compare_previous": "compare" in (compare_values or []),
        },
        "headline_metrics": {
            "payment_volume": _brl(total_pay),
            "on_time_rate": kpi_ontime,
            "cancel_rate": kpi_cancel,
        },
    }

    return (
        kpi_ontime,
        kpi_days,
        kpi_volume,
        kpi_install,
        kpi_cancel,
        fig_types,
        fig_states,
        fig_scatter,
        fig_cancel,
        context,
    )
