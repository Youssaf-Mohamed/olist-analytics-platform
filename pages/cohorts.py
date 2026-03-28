"""
pages/cohorts.py - Cohort retention and repeat-purchase analytics.
"""

import dash
from dash import html, dcc, callback, Input, Output
import plotly.graph_objects as go

from components.page_helpers import page_section
from utils.cleaner import apply_chart_layout, pct, tooltip
from utils.data_loader import load_data_bundle
from utils.retention import build_retention_matrix, get_retention_kpis


dash.register_page(__name__, path="/cohorts", name="Cohorts", order=6)

DATA_BUNDLE = load_data_bundle()
orders_df = DATA_BUNDLE["orders"]


layout = page_section(
    html.Div(
    [
        html.Div(
            [
                html.H1("Cohort Retention", className="page-title"),
                html.P(
                    "Track whether newly acquired customers come back to buy again over time.",
                    className="page-subtitle",
                ),
            ],
            className="page-header",
        ),
        html.Div(
            "This page follows the global date range in the top bar and focuses on delivered orders only.",
            className="global-filter-note",
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.P(
                            [
                                "Active Customers",
                                tooltip("Unique delivered-order customers in the active date range."),
                            ],
                            className="kpi-label",
                            style={"display": "flex", "alignItems": "center"},
                        ),
                        html.Div(id="cohort-kpi-active", className="kpi-value"),
                        html.P("Customers contributing to retention analysis", className="kpi-delta"),
                    ],
                    className="kpi-card kpi-cyan",
                ),
                html.Div(
                    [
                        html.P(
                            [
                                "Repeat Purchase Rate",
                                tooltip("Share of customers with more than one delivered order."),
                            ],
                            className="kpi-label",
                            style={"display": "flex", "alignItems": "center"},
                        ),
                        html.Div(id="cohort-kpi-repeat", className="kpi-value"),
                        html.P("Customers with 2+ delivered orders", className="kpi-delta"),
                    ],
                    className="kpi-card kpi-green",
                ),
                html.Div(
                    [
                        html.P(
                            [
                                "Avg Orders / Customer",
                                tooltip("Average delivered-order frequency per customer."),
                            ],
                            className="kpi-label",
                            style={"display": "flex", "alignItems": "center"},
                        ),
                        html.Div(id="cohort-kpi-frequency", className="kpi-value"),
                        html.P("Higher values indicate deeper retention", className="kpi-delta"),
                    ],
                    className="kpi-card kpi-purple",
                ),
                html.Div(
                    [
                        html.P(
                            [
                                "Latest M+1 Retention",
                                tooltip("Share of the latest visible cohort that returned one month later."),
                            ],
                            className="kpi-label",
                            style={"display": "flex", "alignItems": "center"},
                        ),
                        html.Div(id="cohort-kpi-m1", className="kpi-value"),
                        html.P("Month-1 cohort retention benchmark", className="kpi-delta"),
                    ],
                    className="kpi-card kpi-amber",
                ),
            ],
            className="kpi-grid",
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.P(
                            ["Retention Heatmap", tooltip("Each row is a cohort month and each column is months since acquisition.")],
                            className="chart-title",
                            style={"display": "flex", "alignItems": "center"},
                        ),
                        html.P(
                            "Percentage of each cohort returning in subsequent months",
                            className="chart-subtitle",
                        ),
                        dcc.Loading(
                            dcc.Graph(id="cohort-heatmap", config={"displayModeBar": False}),
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
        html.Div(
            [
                html.Div(
                    [
                        html.P(
                            ["Retention Curve", tooltip("Average retention by months since first purchase.")],
                            className="chart-title",
                            style={"display": "flex", "alignItems": "center"},
                        ),
                        html.P("Average retention across visible cohorts", className="chart-subtitle"),
                        dcc.Loading(
                            dcc.Graph(id="cohort-curve", config={"displayModeBar": False}),
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
                            ["Cohort Detail Table", tooltip("Customer counts and month-1 retention for each cohort.")],
                            className="chart-title",
                            style={"display": "flex", "alignItems": "center"},
                        ),
                        html.P("Operational view of cohort health", className="chart-subtitle"),
                        dcc.Loading(
                            html.Div(id="cohort-table-wrap"),
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
    ],
        style={"maxWidth": "1600px"},
    ),
)


@callback(
    Output("cohort-kpi-active", "children"),
    Output("cohort-kpi-repeat", "children"),
    Output("cohort-kpi-frequency", "children"),
    Output("cohort-kpi-m1", "children"),
    Output("cohort-heatmap", "figure"),
    Output("cohort-curve", "figure"),
    Output("cohort-table-wrap", "children"),
    Output("cohorts-page-context", "data"),
    Input("global-date-range", "start_date"),
    Input("global-date-range", "end_date"),
    Input("global-compare-toggle", "value"),
    Input("theme-store", "data"),
    Input("app-container", "data-theme"),
)
def update_cohorts(start_date, end_date, compare_values, theme="dark", applied_theme="dark"):
    theme = applied_theme or theme or "dark"
    pct_matrix, count_matrix = build_retention_matrix(orders_df, start_date, end_date)
    kpis = get_retention_kpis(orders_df, start_date, end_date)

    if pct_matrix.empty:
        fig_heatmap = go.Figure()
        fig_curve = go.Figure()
        table = html.Div("No delivered-order cohort data available.", className="global-filter-note")
    else:
        fig_heatmap = go.Figure(
            data=go.Heatmap(
                z=pct_matrix.values,
                x=[f"M+{int(col)}" for col in pct_matrix.columns],
                y=list(pct_matrix.index),
                colorscale=[
                    [0.0, "#1E2433"],
                    [0.35, "#7C3AED"],
                    [0.7, "#34D399"],
                    [1.0, "#00D4FF"],
                ],
                text=[[f"{value:.1f}%" for value in row] for row in pct_matrix.values],
                texttemplate="%{text}",
                hovertemplate="Cohort %{y}<br>%{x}: %{z:.1f}%<extra></extra>",
                colorbar=dict(title="Retention %"),
            )
        )
        apply_chart_layout(fig_heatmap, height=430, theme=theme)
        fig_heatmap.update_layout(
            xaxis_title="Months Since First Purchase",
            yaxis_title="Cohort Month",
        )

        avg_curve = pct_matrix.mean(axis=0).reset_index()
        avg_curve.columns = ["month_number", "retention_pct"]
        fig_curve = go.Figure(
            go.Scatter(
                x=avg_curve["month_number"],
                y=avg_curve["retention_pct"],
                mode="lines+markers",
                line=dict(color="#38BDF8", width=3),
                marker=dict(size=8, color="#A78BFA"),
                hovertemplate="M+%{x}<br>%{y:.1f}%<extra></extra>",
            )
        )
        apply_chart_layout(fig_curve, height=430, theme=theme)
        fig_curve.update_layout(
            xaxis_title="Months Since First Purchase",
            yaxis_title="Average Retention %",
        )

        rows = []
        month_one_col = 1 if 1 in pct_matrix.columns else None
        for cohort_label in pct_matrix.index[-10:]:
            cohort_size = int(count_matrix.loc[cohort_label, 0]) if 0 in count_matrix.columns else 0
            month_one = (
                f"{pct_matrix.loc[cohort_label, month_one_col]:.1f}%"
                if month_one_col is not None
                else "N/A"
            )
            rows.append(
                html.Tr(
                    [
                        html.Td(cohort_label, className="mono"),
                        html.Td(f"{cohort_size:,}", className="mono"),
                        html.Td(month_one, className="mono"),
                        html.Td(
                            f"{pct_matrix.loc[cohort_label].replace(0, float('nan')).count():,}",
                            className="mono",
                        ),
                    ]
                )
            )

        table = html.Div(
            html.Table(
                [
                    html.Thead(
                        html.Tr(
                            [
                                html.Th("Cohort"),
                                html.Th("Customers"),
                                html.Th("M+1 Retention"),
                                html.Th("Observed Months"),
                            ]
                        )
                    ),
                    html.Tbody(rows),
                ],
                className="data-table",
            ),
            className="data-table-wrap",
        )

    context = {
        "page": "cohorts",
        "filters": {
            "start_date": start_date,
            "end_date": end_date,
            "compare_previous": "compare" in (compare_values or []),
        },
        "headline_metrics": {
            "active_customers": f"{int(kpis['active_customers']):,}",
            "repeat_rate": pct(kpis["repeat_rate_pct"] / 100),
            "avg_orders_per_customer": f"{kpis['avg_orders_per_customer']:.2f}",
            "latest_m1_retention": pct(kpis["latest_month_1_retention_pct"] / 100),
        },
    }

    return (
        f"{int(kpis['active_customers']):,}",
        pct(kpis["repeat_rate_pct"] / 100),
        f"{kpis['avg_orders_per_customer']:.2f}",
        pct(kpis["latest_month_1_retention_pct"] / 100),
        fig_heatmap,
        fig_curve,
        table,
        context,
    )
