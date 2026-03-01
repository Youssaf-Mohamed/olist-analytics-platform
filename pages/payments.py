"""
pages/payments.py — Page 5: Payments & Delivery Analytics
2 KPIs + Payment Distribution + Delivery by State + Scatter (Value vs Days)
"""

import dash
from dash import html, dcc, callback, Input, Output
import plotly.graph_objects as go
from dash_iconify import DashIconify

from utils.data_loader import load_master_data
from utils.cleaner import apply_chart_layout, pct, tooltip

dash.register_page(__name__, path="/payments", name="Payments & Delivery", order=4)

# ── Load data once ────────────────────────────────────────────────────────────
df_master = load_master_data()

# ── Layout ────────────────────────────────────────────────────────────────────
layout = html.Div(
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
            ],
            className="kpi-grid",
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
                        dcc.Graph(
                            id="pay-chart-types", config={"displayModeBar": False}
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
                        dcc.Graph(
                            id="pay-chart-states", config={"displayModeBar": False}
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
                        dcc.Graph(
                            id="pay-chart-scatter", config={"displayModeBar": False}
                        ),
                    ],
                    className="chart-card",
                ),
            ],
            className="chart-grid chart-grid-1",
        ),
    ],
    style={"maxWidth": "1600px"},
)


# ── Callback (triggered once on load — no inputs needed) ─────────────────────
@callback(
    Output("pay-kpi-ontime", "children"),
    Output("pay-kpi-days", "children"),
    Output("pay-kpi-volume", "children"),
    Output("pay-kpi-install", "children"),
    Output("pay-chart-types", "figure"),
    Output("pay-chart-states", "figure"),
    Output("pay-chart-scatter", "figure"),
    Input("pay-chart-types", "id"),  # dummy trigger — fires on page load
)
def update_payments(_):
    dff = df_master.copy()

    # ── KPIs ─────────────────────────────────────────────────────────────────
    on_time_rate = dff["is_on_time"].mean()
    avg_days = dff["delivery_days"].mean()
    total_pay = dff["payment_value"].sum()
    avg_install = dff["payment_installments"].mean()

    # Format KPIs
    def _brl(v):
        if v >= 1e6:
            return f"R$ {v/1e6:.1f}M"
        if v >= 1e3:
            return f"R$ {v/1e3:.1f}K"
        return f"R$ {v:,.0f}"

    kpi_ontime = pct(on_time_rate)
    kpi_days = f"{avg_days:.1f} days"
    kpi_volume = _brl(total_pay)
    kpi_install = f"{avg_install:.1f}×"

    # ── Payment type donut ────────────────────────────────────────────────────
    pay_counts = (
        dff.groupby("payment_type")["payment_value"]
        .sum()
        .reset_index()
        .rename(columns={"payment_value": "value"})
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
    apply_chart_layout(fig_types, height=320)

    # ── Delivery days by state ────────────────────────────────────────────────
    state_days = (
        dff.groupby("customer_state")["delivery_days"]
        .mean()
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
    apply_chart_layout(fig_states, height=320)
    fig_states.update_layout(xaxis_title="Days")

    # ── Scatter: Order Value vs Delivery Days ─────────────────────────────────
    scatter_df = dff.dropna(subset=["total_order_value", "delivery_days"]).copy()
    if len(scatter_df) > 5_000:
        scatter_df = scatter_df.sample(5_000, random_state=42)

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
                        text="Review Score", font=dict(color="#64748B", size=11)
                    ),
                    tickfont=dict(color="#64748B", family="Space Mono"),
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
    apply_chart_layout(fig_scatter, height=360)
    fig_scatter.update_layout(
        xaxis_title="Order Value (R$)",
        yaxis_title="Delivery Days",
    )

    return (
        kpi_ontime,
        kpi_days,
        kpi_volume,
        kpi_install,
        fig_types,
        fig_states,
        fig_scatter,
    )
