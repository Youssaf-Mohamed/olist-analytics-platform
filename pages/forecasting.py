"""
pages/forecasting.py — Sales Forecasting (Time-Series ML)
Revenue forecast using Ridge regression + Fourier seasonal features.
"""

import dash
from dash import html, dcc, callback, Input, Output
import plotly.graph_objects as go
import pandas as pd

from dash_iconify import DashIconify
from utils.data_loader import load_master_data
from utils.cleaner import apply_chart_layout, format_brl, tooltip
from utils.ml_forecasting import build_time_series, forecast_revenue

dash.register_page(__name__, path="/forecasting", name="Forecasting", order=6)

# ── Pre-compute time series once ──────────────────────────────────────────────
df_master = load_master_data()
ts_df = build_time_series(df_master)


# ── Layout ────────────────────────────────────────────────────────────────────
layout = html.Div(
    [
        # Header
        html.Div(
            [
                html.H1("Sales Forecasting", className="page-title"),
                html.P(
                    "AI-powered revenue prediction using time-series regression with seasonal decomposition.",
                    className="page-subtitle",
                ),
            ],
            className="page-header",
        ),
        # Controls
        html.Div(
            [
                html.Span("Forecast Horizon:", className="filter-label"),
                html.Div(
                    [
                        html.Button(
                            "30 Days",
                            id="fc-btn-30",
                            n_clicks=0,
                            className="btn-horizon",
                            **{"data-days": "30"},
                        ),
                        html.Button(
                            "60 Days",
                            id="fc-btn-60",
                            n_clicks=0,
                            className="btn-horizon",
                            **{"data-days": "60"},
                        ),
                        html.Button(
                            "90 Days",
                            id="fc-btn-90",
                            n_clicks=0,
                            className="btn-horizon active",
                            **{"data-days": "90"},
                        ),
                    ],
                    style={"display": "flex", "gap": "8px"},
                ),
            ],
            className="filter-bar",
            style={"alignItems": "center", "gap": "20px"},
        ),
        # KPI row
        html.Div(
            [
                html.Div(
                    [
                        html.Div(
                            [
                                html.P(
                                    [
                                        "Forecasted Revenue",
                                        tooltip(
                                            "Total predicted revenue over the selected horizon period (R$)."
                                        ),
                                    ],
                                    className="kpi-label",
                                    style={"display": "flex", "alignItems": "center"},
                                ),
                                DashIconify(
                                    icon="ph:trend-up-bold",
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
                        html.Div(id="fc-kpi-total", className="kpi-value"),
                        html.P("Projected gross revenue (R$)", className="kpi-delta"),
                    ],
                    className="kpi-card kpi-cyan",
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.P(
                                    [
                                        "Growth Rate",
                                        tooltip(
                                            "Expected growth rate compared to the previous equivalent period."
                                        ),
                                    ],
                                    className="kpi-label",
                                    style={"display": "flex", "alignItems": "center"},
                                ),
                                DashIconify(
                                    icon="ph:arrow-up-right-bold",
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
                        html.Div(id="fc-kpi-growth", className="kpi-value"),
                        html.P("vs. previous equivalent period", className="kpi-delta"),
                    ],
                    className="kpi-card kpi-green",
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.P(
                                    [
                                        "Peak Month",
                                        tooltip(
                                            "The month with the highest predicted revenue in the forecast window."
                                        ),
                                    ],
                                    className="kpi-label",
                                    style={"display": "flex", "alignItems": "center"},
                                ),
                                DashIconify(
                                    icon="ph:calendar-check-bold",
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
                        html.Div(id="fc-kpi-peak", className="kpi-value"),
                        html.P(id="fc-kpi-peak-val", className="kpi-delta"),
                    ],
                    className="kpi-card kpi-purple",
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.P(
                                    [
                                        "Avg Daily Revenue",
                                        tooltip(
                                            "Mean predicted daily revenue across the entire forecast window."
                                        ),
                                    ],
                                    className="kpi-label",
                                    style={"display": "flex", "alignItems": "center"},
                                ),
                                DashIconify(
                                    icon="ph:currency-dollar-simple",
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
                        html.Div(id="fc-kpi-daily", className="kpi-value"),
                        html.P("95% confidence interval", className="kpi-delta"),
                    ],
                    className="kpi-card kpi-amber",
                ),
            ],
            className="kpi-grid",
        ),
        # Main area chart
        html.Div(
            [
                html.H3(
                    [
                        "Revenue Timeline & Forecast",
                        tooltip(
                            "Blue = historical actual revenue. Cyan = predicted future revenue with ±95% confidence band."
                        ),
                    ],
                    className="chart-title",
                    style={"display": "flex", "alignItems": "center"},
                ),
                html.P(
                    "Actual vs Predicted daily revenue with confidence interval",
                    className="chart-subtitle",
                ),
                dcc.Loading(
                    dcc.Graph(
                        id="fc-area-chart",
                        config={"displayModeBar": False},
                        style={"height": "420px"},
                    ),
                    type="circle",
                    color="#38BDF8",
                    parent_className="chart-loading-wrapper",
                    overlay_style={"visibility": "visible", "opacity": 0.6, "backgroundColor": "rgba(11,14,23,0.7)"},
                ),
            ],
            className="chart-card",
            style={"marginBottom": "18px"},
        ),
        # Monthly breakdown
        html.Div(
            [
                html.H3(
                    [
                        "Monthly Revenue Breakdown",
                        tooltip(
                            "Aggregated actual revenue by month alongside predicted months in the forecast horizon."
                        ),
                    ],
                    className="chart-title",
                    style={"display": "flex", "alignItems": "center"},
                ),
                html.P(
                    "Historical actuals + forecasted months side by side",
                    className="chart-subtitle",
                ),
                dcc.Loading(
                    dcc.Graph(
                        id="fc-monthly-bar",
                        config={"displayModeBar": False},
                        style={"height": "320px"},
                    ),
                    type="circle",
                    color="#38BDF8",
                    parent_className="chart-loading-wrapper",
                    overlay_style={"visibility": "visible", "opacity": 0.6, "backgroundColor": "rgba(11,14,23,0.7)"},
                ),
            ],
            className="chart-card",
        ),
        # Store
        dcc.Store(id="fc-horizon-store", data=90),
    ],
    className="page-content",
)


# ── Clientside: horizon button active state ───────────────────────────────────
from dash import clientside_callback

clientside_callback(
    """
    function(n30, n60, n90) {
        var ctx = dash_clientside.callback_context;
        if (!ctx.triggered.length) return 90;
        var triggered_id = ctx.triggered[0]['prop_id'].split('.')[0];
        var buttons = ['fc-btn-30', 'fc-btn-60', 'fc-btn-90'];
        var days    = {'fc-btn-30': 30, 'fc-btn-60': 60, 'fc-btn-90': 90};
        buttons.forEach(function(id) {
            var el = document.getElementById(id);
            if (el) {
                el.classList.toggle('active', id === triggered_id);
            }
        });
        return days[triggered_id] || 90;
    }
    """,
    Output("fc-horizon-store", "data"),
    [
        Input("fc-btn-30", "n_clicks"),
        Input("fc-btn-60", "n_clicks"),
        Input("fc-btn-90", "n_clicks"),
    ],
)


# ── Callbacks ─────────────────────────────────────────────────────────────────
@callback(
    Output("fc-kpi-total", "children"),
    Output("fc-kpi-growth", "children"),
    Output("fc-kpi-peak", "children"),
    Output("fc-kpi-peak-val", "children"),
    Output("fc-kpi-daily", "children"),
    Output("fc-area-chart", "figure"),
    Output("fc-monthly-bar", "figure"),
    Input("fc-horizon-store", "data"),
)
def _update_forecast(horizon_days):
    horizon_days = int(horizon_days or 90)
    hist, fc, metrics, monthly = forecast_revenue(ts_df, horizon_days=horizon_days)

    # ── KPIs
    total_str = format_brl(metrics["total_forecast_brl"])
    growth_str = f"{metrics['growth_pct']:+.1f}%"
    peak_str = metrics["peak_month"]
    peak_val = format_brl(metrics["peak_month_value"])
    daily_str = format_brl(metrics["avg_daily"])

    # ── Area chart ─────────────────────────────────────────────────────────────
    # Show only last 180 days of history for readability
    hist_plot = hist.tail(180).copy()

    fig_area = go.Figure()

    # Confidence band
    fig_area.add_trace(
        go.Scatter(
            x=pd.concat([fc["date"], fc["date"].iloc[::-1]]),
            y=pd.concat([fc["upper"], fc["lower"].iloc[::-1]]),
            fill="toself",
            fillcolor="rgba(56,189,248,0.10)",
            line=dict(color="rgba(0,0,0,0)"),
            showlegend=True,
            name="95% Confidence",
            hoverinfo="skip",
        )
    )

    # Forecast line
    fig_area.add_trace(
        go.Scatter(
            x=fc["date"],
            y=fc["predicted"],
            mode="lines",
            line=dict(color="#38BDF8", width=2.5, dash="dot"),
            name="Predicted",
            hovertemplate="%{x|%b %d, %Y}<br>R$ %{y:,.0f}<extra>Predicted</extra>",
        )
    )

    # Historical actual
    fig_area.add_trace(
        go.Scatter(
            x=hist_plot["date"],
            y=hist_plot["revenue"],
            mode="lines",
            line=dict(color="#A78BFA", width=1.5),
            name="Actual Revenue",
            hovertemplate="%{x|%b %d, %Y}<br>R$ %{y:,.0f}<extra>Actual</extra>",
        )
    )

    # Historical smoothed
    fig_area.add_trace(
        go.Scatter(
            x=hist_plot["date"],
            y=hist_plot["revenue_smooth"],
            mode="lines",
            line=dict(color="#818CF8", width=2.5),
            name="7-day Average",
            hovertemplate="%{x|%b %d, %Y}<br>R$ %{y:,.0f}<extra>7-day avg</extra>",
        )
    )

    # Vertical divider at forecast start
    split_date = hist["date"].max()
    fig_area.add_shape(
        type="line",
        x0=split_date,
        x1=split_date,
        y0=0,
        y1=1,
        yref="paper",
        line=dict(color="#38BDF8", width=1, dash="dash"),
    )
    fig_area.add_annotation(
        x=split_date,
        y=0.95,
        yref="paper",
        text="Forecast →",
        showarrow=False,
        font=dict(color="#38BDF8", size=11, family="Inter, sans-serif"),
        xanchor="left",
        xshift=6,
    )

    apply_chart_layout(fig_area, height=410)
    fig_area.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(11,14,23,0.4)",
        xaxis=dict(gridcolor="#1A1F35"),
        yaxis=dict(title="Revenue (R$)", gridcolor="#1A1F35"),
        legend=dict(orientation="h", y=1.06, x=0),
        hovermode="x unified",
    )

    # ── Monthly bar chart ──────────────────────────────────────────────────────
    # Historical monthly actuals
    hist_monthly = (
        hist.assign(month=lambda x: x["date"].dt.strftime("%Y-%m"))
        .groupby("month")["revenue"]
        .sum()
        .reset_index()
    )

    fig_bar = go.Figure()
    fig_bar.add_trace(
        go.Bar(
            x=hist_monthly["month"],
            y=hist_monthly["revenue"],
            name="Actual",
            marker_color="#A78BFA",
            opacity=0.8,
            hovertemplate="Month: %{x}<br>R$ %{y:,.0f}<extra>Actual</extra>",
        )
    )
    fig_bar.add_trace(
        go.Bar(
            x=monthly["month"],
            y=monthly["predicted"],
            name="Forecast",
            marker_color="#38BDF8",
            opacity=0.85,
            hovertemplate="Month: %{x}<br>R$ %{y:,.0f}<extra>Forecast</extra>",
        )
    )

    apply_chart_layout(fig_bar, height=310)
    fig_bar.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(11,14,23,0.4)",
        barmode="overlay",
        xaxis=dict(gridcolor="#1A1F35"),
        yaxis=dict(title="Revenue (R$)", gridcolor="#1A1F35"),
        legend=dict(orientation="h", y=1.06, x=0),
    )

    return total_str, growth_str, peak_str, peak_val, daily_str, fig_area, fig_bar
