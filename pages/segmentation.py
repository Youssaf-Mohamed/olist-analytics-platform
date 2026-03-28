"""
pages/segmentation.py — Customer Segmentation (ML)
RFM Analysis + K-Means clustering dashboard.
"""

import dash
from dash import html, dcc, callback, Input, Output
from io import StringIO
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from dash_iconify import DashIconify
from utils.data_loader import load_master_data
from utils.cleaner import apply_chart_layout, tooltip
from utils.ml_segmentation import (
    compute_rfm,
    cluster_customers,
    get_segment_summary,
    SEGMENT_COLORS,
)

dash.register_page(__name__, path="/segmentation", name="Segmentation", order=5)

# ── Pre-compute RFM once at module level ──────────────────────────────────────
df_master = load_master_data()
rfm_base = compute_rfm(df_master)




# ── Layout ────────────────────────────────────────────────────────────────────
layout = html.Div(
    [
        # Header
        html.Div(
            [
                html.H1("Customer Segmentation", className="page-title"),
                html.P(
                    "RFM-based K-Means clustering — identify high-value, at-risk, and dormant customers.",
                    className="page-subtitle",
                ),
            ],
            className="page-header",
        ),
        # Controls
        html.Div(
            [
                html.Span("Clusters:", className="filter-label"),
                dcc.Slider(
                    id="seg-cluster-slider",
                    min=3,
                    max=6,
                    step=1,
                    value=4,
                    marks={i: {"label": str(i), "style": {"color": "#E2E8F0"}} for i in range(3, 7)},
                    tooltip={"placement": "bottom", "always_visible": False},
                    className="seg-slider",
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
                                        "Total Customers",
                                        tooltip(
                                            "Unique customers with at least one completed order."
                                        ),
                                    ],
                                    className="kpi-label",
                                    style={"display": "flex", "alignItems": "center"},
                                ),
                                DashIconify(
                                    icon="ph:users-three-bold",
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
                        html.Div(id="seg-kpi-total", className="kpi-value"),
                    ],
                    className="kpi-card kpi-cyan",
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.P(
                                    [
                                        "🏆 Champions",
                                        tooltip(
                                            "Customers who bought recently, often, and spent the most."
                                        ),
                                    ],
                                    className="kpi-label",
                                    style={"display": "flex", "alignItems": "center"},
                                ),
                                DashIconify(
                                    icon="ph:trophy-bold",
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
                        html.Div(id="seg-kpi-champions", className="kpi-value"),
                    ],
                    className="kpi-card kpi-cyan",
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.P(
                                    [
                                        "⚠️ At Risk",
                                        tooltip(
                                            "Customers who used to buy but haven't recently. Require re-engagement."
                                        ),
                                    ],
                                    className="kpi-label",
                                    style={"display": "flex", "alignItems": "center"},
                                ),
                                DashIconify(
                                    icon="ph:warning-bold",
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
                        html.Div(id="seg-kpi-atrisk", className="kpi-value"),
                    ],
                    className="kpi-card kpi-red",
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.P(
                                    [
                                        "😴 Hibernating",
                                        tooltip(
                                            "Customers with low recency, frequency, and monetary value — likely lost."
                                        ),
                                    ],
                                    className="kpi-label",
                                    style={"display": "flex", "alignItems": "center"},
                                ),
                                DashIconify(
                                    icon="ph:moon-stars-bold",
                                    width=20,
                                    style={
                                        "color": "var(--muted)",
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
                        html.Div(id="seg-kpi-hibernating", className="kpi-value"),
                    ],
                    className="kpi-card kpi-amber",
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.P(
                                    [
                                        "Clustering Quality",
                                        tooltip(
                                            "Silhouette Score (closer to 1 is better) and Davies-Bouldin Index (lower is better)."
                                        ),
                                    ],
                                    className="kpi-label",
                                    style={"display": "flex", "alignItems": "center"},
                                ),
                                DashIconify(
                                    icon="ph:chart-polar-bold",
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
                        html.Div(id="seg-kpi-metrics", className="kpi-value", style={"fontSize": "1.3rem"}),
                        html.P(id="seg-kpi-metrics-info", className="kpi-delta", style={"fontSize": "0.75rem"}),
                    ],
                    className="kpi-card",
                ),
            ],
            className="kpi-grid",
        ),
        # Main charts row
        html.Div(
            [
                # Scatter plot
                html.Div(
                    [
                        html.H3(
                            [
                                "RFM Cluster Map",
                                tooltip(
                                    "2D PCA projection of all 3 RFM dimensions. Each dot = one customer."
                                ),
                            ],
                            className="chart-title",
                            style={"display": "flex", "alignItems": "center"},
                        ),
                        html.P(
                            "Recency · Frequency · Monetary projected into 2D (PCA)",
                            className="chart-subtitle",
                        ),
                        dcc.Loading(
                            dcc.Graph(
                                id="seg-scatter",
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
                    style={"flex": "1.7"},
                ),
                # Donut chart
                html.Div(
                    [
                        html.H3(
                            [
                                "Segment Distribution",
                                tooltip(
                                    "Percentage of customers in each clustering segment."
                                ),
                            ],
                            className="chart-title",
                            style={"display": "flex", "alignItems": "center"},
                        ),
                        html.P("Customer count by segment", className="chart-subtitle"),
                        dcc.Loading(
                            dcc.Graph(
                                id="seg-donut",
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
                    style={"flex": "1"},
                ),
            ],
            style={"display": "flex", "gap": "18px", "marginBottom": "18px"},
        ),
        # Metrics table
        html.Div(
            [
                html.H3(
                    [
                        "Segment Profiles",
                        tooltip(
                            "Mean RFM values per cluster. Lower recency = more recent buyer."
                        ),
                    ],
                    className="chart-title",
                    style={"display": "flex", "alignItems": "center"},
                ),
                html.P(
                    "Average Recency (days), Frequency (orders), Monetary (R$) per segment",
                    className="chart-subtitle",
                ),
                dcc.Loading(
                    dcc.Graph(
                        id="seg-heatmap",
                        config={"displayModeBar": False},
                        style={"height": "280px"},
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
        # Store for clustered data removed for performance
    ],
    className="page-content",
)


# ── Callbacks ─────────────────────────────────────────────────────────────────
@callback(
    Output("seg-kpi-total", "children"),
    Output("seg-kpi-champions", "children"),
    Output("seg-kpi-atrisk", "children"),
    Output("seg-kpi-hibernating", "children"),
    Output("seg-kpi-metrics", "children"),
    Output("seg-kpi-metrics-info", "children"),
    Output("seg-scatter", "figure"),
    Output("seg-donut", "figure"),
    Output("seg-heatmap", "figure"),
    Input("seg-cluster-slider", "value"),
)
def _update_segmentation(n_clusters):
    # Cluster locally in memory without serialising huge JSON back to client
    rfm, metrics = cluster_customers(rfm_base, n_clusters=int(n_clusters))
    
    # ── KPIs ──────────────────────────────────────────────────────────────────
    total = len(rfm)
    seg_counts = rfm["segment"].value_counts()
    champions = seg_counts.get("Champions", 0)
    at_risk = seg_counts.get("At Risk", 0)
    hibernating = seg_counts.get("Hibernating", 0)
    
    kpi_total = f"{total:,}"
    kpi_champ = f"{champions:,}"
    kpi_risk = f"{at_risk:,}"
    kpi_hib = f"{hibernating:,}"
    kpi_met_val = f"Sil: {metrics['silhouette']:.2f}"
    kpi_met_info = f"DB: {metrics['davies_bouldin']:.2f}"
    
    # ── Scatter Plot ──────────────────────────────────────────────────────────
    fig_scatter = px.scatter(
        rfm,
        x="pc1",
        y="pc2",
        color="segment",
        color_discrete_map=SEGMENT_COLORS,
        hover_data={
            "recency": True,
            "frequency": True,
            "monetary": ":.0f",
            "pc1": False,
            "pc2": False,
        },
        labels={
            "pc1": "PC 1 (Trend)",
            "pc2": "PC 2 (Variation)",
            "recency": "Recency (days)",
            "frequency": "Orders",
            "monetary": "Revenue (R$)",
        },
        opacity=0.72,
    )
    fig_scatter.update_traces(marker=dict(size=5))
    apply_chart_layout(fig_scatter, height=400)
    fig_scatter.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(11,14,23,0.4)",
        legend=dict(title="Segment"),
    )
    
    # Summary for Donut & Heatmap
    summary = get_segment_summary(rfm)
    
    # ── Donut Chart ───────────────────────────────────────────────────────────
    colors = [SEGMENT_COLORS.get(s, "#64748B") for s in summary["segment"]]
    fig_donut = go.Figure(
        go.Pie(
            labels=summary["segment"],
            values=summary["count"],
            hole=0.55,
            marker=dict(colors=colors, line=dict(color="#0B0E17", width=2)),
            textinfo="label+percent",
            hovertemplate="<b>%{label}</b><br>Count: %{value:,}<br>%{percent}<extra></extra>",
        )
    )
    fig_donut.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        margin=dict(l=10, r=10, t=10, b=10),
        height=400,
        font=dict(family="Inter, sans-serif", color="#E2E8F0", size=12),
    )
    
    # ── Heatmap/Table ─────────────────────────────────────────────────────────
    fig_table = go.Figure(
        go.Table(
            header=dict(
                values=[
                    "<b>Segment</b>",
                    "<b>Customers</b>",
                    "<b>Share %</b>",
                    "<b>Avg Recency (days)</b>",
                    "<b>Avg Orders</b>",
                    "<b>Avg Revenue (R$)</b>",
                    "<b>Actionable Insight</b>",
                ],
                fill_color="#1A1F35",
                font=dict(
                    color="#38BDF8", size=12, family="Plus Jakarta Sans, sans-serif"
                ),
                align="left",
                line_color="#252D47",
                height=36,
            ),
            cells=dict(
                values=[
                    summary["segment"],
                    summary["count"].apply(lambda v: f"{v:,}"),
                    summary["pct"].apply(lambda v: f"{v:.1f}%"),
                    summary["avg_recency"].apply(lambda v: f"{v:.0f}"),
                    summary["avg_frequency"].apply(lambda v: f"{v:.1f}"),
                    summary["avg_monetary"].apply(lambda v: f"R$ {v:,.0f}"),
                    summary["insight"],
                ],
                fill_color=[["#13172A", "#0B0E17"] * len(summary)],
                font=dict(color="#94A3B8", size=12, family="Inter, sans-serif"),
                align="left",
                line_color="#252D47",
                height=32,
            ),
        )
    )
    fig_table.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=0, b=0),
        height=260,
        font=dict(family="Inter, sans-serif"),
    )

    return (
        kpi_total,
        kpi_champ,
        kpi_risk,
        kpi_hib,
        kpi_met_val,
        kpi_met_info,
        fig_scatter,
        fig_donut,
        fig_table,
    )
