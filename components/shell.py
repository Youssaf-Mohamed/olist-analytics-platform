"""App shell helpers: sidebar, top bar, shared stores, and root layout."""

from __future__ import annotations

from dash import dcc, html
from dash_iconify import DashIconify

from components.ai_panel import build_ai_panel

PAGE_CONTEXT_STORE_IDS = [
    "overview-page-context",
    "geography-page-context",
    "reviews-page-context",
    "recommendations-page-context",
    "payments-page-context",
    "segmentation-page-context",
    "cohorts-page-context",
    "forecasting-page-context",
    "sellers-page-context",
]


def nav_link(item: dict) -> html.A:
    return html.A(
        [
            html.Span(DashIconify(icon=item["icon"], width=18), className="nav-icon"),
            html.Span(item["label"], className="nav-label"),
        ],
        href=item["href"],
        className="nav-link",
        title=item["label"],
        **{"data-label": item["label"]},
    )


def build_topbar(date_min, date_max) -> html.Div:
    return html.Div(
        [
            html.Div(
                [
                    html.Span("Global View", className="topbar-eyebrow"),
                    html.Div("Unified Date Filter Across Pages", className="topbar-title"),
                    html.Div(
                        "Overview, geography, reviews, payments, sellers, and cohorts stay in sync.",
                        className="topbar-subtitle",
                    ),
                ],
                className="topbar-copy",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Span("Date Range", className="topbar-label"),
                            dcc.DatePickerRange(
                                id="global-date-range",
                                min_date_allowed=date_min,
                                max_date_allowed=date_max,
                                start_date=date_min,
                                end_date=date_max,
                                display_format="YYYY-MM-DD",
                                className="topbar-date-range",
                            ),
                        ],
                        className="topbar-control",
                    ),
                    html.Div(
                        [
                            html.Span("Comparison", className="topbar-label"),
                            dcc.Checklist(
                                id="global-compare-toggle",
                                options=[
                                    {
                                        "label": "Compare against previous period",
                                        "value": "compare",
                                    }
                                ],
                                value=[],
                                className="topbar-checklist",
                            ),
                        ],
                        className="topbar-control topbar-control-compact",
                    ),
                    html.Div(
                        [
                            html.Span("Theme", className="topbar-label"),
                            html.Button(
                                [
                                    DashIconify(
                                        icon="ph:sun-dim-bold",
                                        width=16,
                                        className="theme-toggle-icon",
                                    ),
                                    html.Span(
                                        "Light Mode",
                                        id="theme-toggle-copy",
                                        className="theme-toggle-copy",
                                    ),
                                ],
                                id="theme-toggle-btn",
                                n_clicks=0,
                                className="theme-toggle-btn",
                                title="Switch to light mode",
                            ),
                        ],
                        className="topbar-control topbar-control-compact",
                    ),
                ],
                className="topbar-controls",
            ),
        ],
        className="global-topbar-shell",
    )


def build_sidebar(nav_items: list[dict], logo_src: str) -> html.Nav:
    return html.Nav(
        id="sidebar",
        children=[
            html.Div(
                [
                    html.Img(src=logo_src, className="logo-icon"),
                    html.Div(
                        [
                            html.Span("OLIST BI", className="logo-text"),
                            html.Span("Intelligence System", className="logo-sub"),
                        ],
                        className="logo-text-wrap",
                    ),
                ],
                id="sidebar-logo",
            ),
            html.Div([nav_link(item) for item in nav_items], id="sidebar-nav"),
            html.Div(
                html.A(
                    [
                        html.Span(
                            DashIconify(icon="ph:brain-bold", width=18),
                            className="nav-icon",
                        ),
                        html.Span("AI Analyst", className="nav-label"),
                    ],
                    id="sidebar-ai-btn",
                    className="nav-link ai-nav-link",
                    title="AI Analyst",
                    **{"data-label": "AI Analyst"},
                ),
                style={
                    "borderTop": "1px solid rgba(255,255,255,0.06)",
                    "paddingTop": "6px",
                    "marginTop": "auto",
                },
            ),
            html.Div(
                [
                    html.Button(
                        DashIconify(
                            icon="ph:caret-left-bold",
                            width=14,
                            id="toggle-icon",
                            color="rgba(255,255,255,0.55)",
                        ),
                        id="sidebar-toggle-btn",
                        title="Collapse sidebar",
                        n_clicks=0,
                        style={
                            "background": "rgba(255,255,255,0.06)",
                            "border": "1px solid rgba(255,255,255,0.1)",
                            "borderRadius": "6px",
                            "width": "30px",
                            "height": "30px",
                            "cursor": "pointer",
                            "display": "flex",
                            "alignItems": "center",
                            "justifyContent": "center",
                            "transition": "all 0.22s ease",
                        },
                    ),
                ],
                id="sidebar-toggle",
                style={
                    "padding": "10px 14px",
                    "borderTop": "1px solid rgba(255,255,255,0.07)",
                    "display": "flex",
                    "justifyContent": "flex-end",
                },
            ),
            html.Div("v1.0 · Big Data & Analytics", id="sidebar-footer"),
        ],
    )


def build_shared_stores() -> list:
    stores = [
        dcc.Store(id="theme-store", storage_type="local", data=None),
        dcc.Store(
            id="active-page-context",
            data={"page": "overview", "filters": {}, "headline_metrics": {}},
        ),
    ]
    stores.extend(dcc.Store(id=store_id) for store_id in PAGE_CONTEXT_STORE_IDS)
    return stores


def build_root_layout(nav_items: list[dict], date_min, date_max, logo_src: str, page_container) -> html.Div:
    return html.Div(
        id="app-container",
        **{"data-theme": "dark"},
        children=[
            build_sidebar(nav_items, logo_src),
            html.Main(
                id="main-content",
                children=[
                    html.Div(id="topbar", children=build_topbar(date_min, date_max)),
                    dcc.Loading(
                        html.Div(id="page-shell", children=[page_container]),
                        type="default",
                        parent_className="page-shell-loading",
                    ),
                ],
            ),
            *build_shared_stores(),
            build_ai_panel(),
        ],
    )
