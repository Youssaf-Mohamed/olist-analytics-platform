"""
app.py — Olist E-Commerce Intelligence System
Entry point: Dash multi-page app with fixed sidebar navigation.
Run: venv\\Scripts\\python.exe app.py
Dashboard: http://127.0.0.1:8050
"""

import os
import dash
from dash import html, dcc, callback, Input, Output, State, clientside_callback
import json
from dash_iconify import DashIconify
from components.ai_panel import (
    brief_context_meta,
    build_chat_messages,
    build_suggested_prompts,
    page_label,
)
from components.shell import build_root_layout
from utils.data_loader import load_data_bundle
from utils.gemini_analyst import (
    build_data_summary,
    chat_with_data,
    generate_executive_summary,
)

# ── App initialisation ────────────────────────────────────────────────────────
app = dash.Dash(
    __name__,
    use_pages=True,
    suppress_callback_exceptions=True,
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"},
        {
            "name": "description",
            "content": "Olist E-Commerce Intelligence Dashboard — Big Data & Analytics",
        },
    ],
    title="Olist BI Dashboard",
)

app.index_string = """
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        <script>
            (function() {
                function normalizeTheme(value) {
                    if (value === "light" || value === "dark") {
                        return value;
                    }
                    if (typeof value === "string") {
                        try {
                            var parsed = JSON.parse(value);
                            if (parsed === "light" || parsed === "dark") {
                                return parsed;
                            }
                            if (parsed && typeof parsed === "object" && (parsed.data === "light" || parsed.data === "dark")) {
                                return parsed.data;
                            }
                        } catch (e) {}
                    }
                    if (value && typeof value === "object" && (value.data === "light" || value.data === "dark")) {
                        return value.data;
                    }
                    return null;
                }

                function readStoredTheme() {
                    try {
                        var direct = normalizeTheme(window.localStorage.getItem("olist-theme"));
                        if (direct) return direct;

                        var dashStore = normalizeTheme(window.localStorage.getItem("theme-store"));
                        if (dashStore) return dashStore;

                        var keys = Object.keys(window.localStorage || {});
                        for (var i = 0; i < keys.length; i++) {
                            if (keys[i].indexOf("theme-store") !== -1) {
                                var candidate = normalizeTheme(window.localStorage.getItem(keys[i]));
                                if (candidate) return candidate;
                            }
                        }
                    } catch (e) {}

                    return (
                        window.matchMedia &&
                        window.matchMedia("(prefers-color-scheme: light)").matches
                    ) ? "light" : "dark";
                }

                function applyTheme(theme) {
                    document.documentElement.setAttribute("data-theme", theme);
                    if (document.body) {
                        document.body.setAttribute("data-theme", theme);
                    }
                    var root = document.getElementById("app-container");
                    if (root) {
                        root.setAttribute("data-theme", theme);
                    }
                }

                var initialTheme = readStoredTheme();
                applyTheme(initialTheme);

                var observer = new MutationObserver(function() {
                    var root = document.getElementById("app-container");
                    if (root) {
                        applyTheme(readStoredTheme());
                        observer.disconnect();
                    }
                });

                observer.observe(document.documentElement, { childList: true, subtree: true });
            })();
        </script>
        {%css%}
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
"""

server = app.server  # expose Flask server for deployment

# ── Pre-compute data summary for chatbot ──────────────────────────────────────
_data_bundle = load_data_bundle()
_data_summary = build_data_summary(_data_bundle)
GLOBAL_DATE_MIN = _data_bundle["orders"]["order_purchase_timestamp"].min().date()
GLOBAL_DATE_MAX = _data_bundle["orders"]["order_purchase_timestamp"].max().date()

# ── Navigation items ──────────────────────────────────────────────────────────
NAV_ITEMS = [
    {"icon": "ph:chart-line-up-bold", "label": "Sales Overview", "href": "/"},
    {"icon": "ph:map-trifold-bold", "label": "Geography", "href": "/geography"},
    {"icon": "ph:chat-teardrop-text-bold", "label": "Reviews", "href": "/reviews"},
    {"icon": "ph:sparkle-bold", "label": "Recommendations", "href": "/recommendations"},
    {
        "icon": "ph:credit-card-bold",
        "label": "Payments & Delivery",
        "href": "/payments",
    },
    {"icon": "ph:users-three-bold", "label": "Segmentation", "href": "/segmentation"},
    {"icon": "ph:arrows-clockwise-bold", "label": "Cohorts", "href": "/cohorts"},
    {"icon": "ph:trend-up-bold", "label": "Forecasting", "href": "/forecasting"},
    {"icon": "ph:storefront-bold", "label": "Sellers", "href": "/sellers"},
]

PAGE_LABELS = {
    "overview": "Sales Overview",
    "geography": "Geography",
    "reviews": "Reviews",
    "recommendations": "Recommendations",
    "payments": "Payments & Delivery",
    "segmentation": "Segmentation",
    "cohorts": "Cohorts",
    "forecasting": "Forecasting",
    "sellers": "Sellers",
}


def _page_label(page_key: str | None) -> str:
    return page_label(page_key)


def _brief_context_meta(page_context: dict | None) -> str:
    return brief_context_meta(page_context)


def _build_suggested_prompts(page_context: dict | None) -> list[dict[str, str]]:
    return build_suggested_prompts(page_context)
    page_key = (page_context or {}).get("page", "overview")
    prompt_map = {
        "overview": [
            {
                "label": "Strongest Signal",
                "prompt": "What is the strongest business signal on the current overview page and why?",
            },
            {
                "label": "Revenue Drivers",
                "prompt": "Explain the main revenue drivers visible in the current overview context.",
            },
            {
                "label": "Next Action",
                "prompt": "Based on this overview page, what should the business investigate next?",
            },
        ],
        "geography": [
            {
                "label": "Top Regions",
                "prompt": "Which regions are leading in the current geography view, and what stands out?",
            },
            {
                "label": "Regional Risk",
                "prompt": "What geographic risk or underperforming region should I pay attention to here?",
            },
            {
                "label": "Expansion Idea",
                "prompt": "What expansion or optimization action would you recommend from this geography view?",
            },
        ],
        "reviews": [
            {
                "label": "Satisfaction Read",
                "prompt": "Summarize customer satisfaction on the current reviews page.",
            },
            {
                "label": "Pain Points",
                "prompt": "What are the likely customer pain points suggested by this reviews view?",
            },
            {
                "label": "CX Action",
                "prompt": "What is the best next action to improve customer experience from this page?",
            },
        ],
        "recommendations": [
            {
                "label": "Cross-Sell Insight",
                "prompt": "What cross-sell or affinity insight is most important on this recommendations page?",
            },
            {
                "label": "Category Opportunity",
                "prompt": "Which category opportunity is most visible in the current recommendations context?",
            },
            {
                "label": "Decision Support",
                "prompt": "What business decision would you support using this recommendations page?",
            },
        ],
        "payments": [
            {
                "label": "Payment Mix",
                "prompt": "Explain the payment mix and delivery performance on the current payments page.",
            },
            {
                "label": "Delivery Risk",
                "prompt": "What delivery or fulfillment risk stands out on this page?",
            },
            {
                "label": "Ops Action",
                "prompt": "What operational action should the team take based on this page?",
            },
        ],
        "segmentation": [
            {
                "label": "Best Segment",
                "prompt": "Which customer segment looks most valuable in the current segmentation view?",
            },
            {
                "label": "At-Risk Customers",
                "prompt": "What segment appears most at risk or least engaged here?",
            },
            {
                "label": "Retention Move",
                "prompt": "What retention or marketing action would you recommend from this segmentation page?",
            },
        ],
        "cohorts": [
            {
                "label": "Retention Read",
                "prompt": "Summarize retention performance in the current cohorts page.",
            },
            {
                "label": "Drop-Off Point",
                "prompt": "Where does customer retention weaken the most in this cohort view?",
            },
            {
                "label": "Lifecycle Action",
                "prompt": "What lifecycle action should be taken based on this cohort analysis?",
            },
        ],
        "forecasting": [
            {
                "label": "Forecast Read",
                "prompt": "Interpret the forecast and explain what it implies for near-term performance.",
            },
            {
                "label": "Confidence Check",
                "prompt": "What risk or uncertainty should stakeholders keep in mind with this forecast?",
            },
            {
                "label": "Planning Move",
                "prompt": "What planning action should the business take using this forecast page?",
            },
        ],
        "sellers": [
            {
                "label": "Top Sellers",
                "prompt": "Which seller signal matters most in the current sellers page?",
            },
            {
                "label": "Seller Risk",
                "prompt": "What seller performance risk or weakness appears on this page?",
            },
            {
                "label": "Partner Action",
                "prompt": "What action should the marketplace team take based on the sellers view?",
            },
        ],
    }
    return prompt_map.get(page_key, prompt_map["overview"])


def _chat_message_component(role: str, text: str, label: str | None = None) -> html.Div:
    is_user = role == "user"
    avatar_icon = "ph:user-bold" if is_user else "ph:brain-bold"
    avatar_label = "You" if is_user else "AI Analyst"
    bubble_label = label or avatar_label
    return html.Div(
        [
            html.Div(
                DashIconify(icon=avatar_icon, width=16),
                className=f"chat-avatar {'chat-avatar-user' if is_user else 'chat-avatar-ai'}",
            ),
            html.Div(
                [
                    html.Div(bubble_label, className="chat-msg-meta"),
                    dcc.Markdown(
                        text,
                        className="chat-msg-copy",
                        link_target="_blank",
                    ),
                ],
                className=f"chat-msg chat-msg-{'user' if is_user else 'ai'}",
            ),
        ],
        className=f"chat-row chat-row-{'user' if is_user else 'ai'}",
    )


def _build_chat_messages(history: list[dict[str, str]] | None) -> list[html.Div]:
    return build_chat_messages(history)
    messages = [
        _chat_message_component(
            "assistant",
            (
                "Welcome to your context-aware analyst.\n\n"
                "- Ask for trends, anomalies, risks, or next actions.\n"
                "- Answers follow the active page filters and visible KPIs.\n"
                "- Use the quick actions below for faster analysis."
            ),
            label="AI Analyst",
        )
    ]

    for item in history or []:
        messages.append(
            _chat_message_component(
                item.get("role", "assistant"),
                item.get("content", ""),
                label="You" if item.get("role") == "user" else "AI Analyst",
            )
        )

    return messages


def _nav_link(item: dict) -> html.A:
    return html.A(
        [
            html.Span(
                DashIconify(icon=item["icon"], width=18),
                className="nav-icon",
            ),
            html.Span(item["label"], className="nav-label"),
        ],
        href=item["href"],
        className="nav-link",
        title=item["label"],  # native tooltip
        **{"data-label": item["label"]},  # CSS tooltip for collapsed mode
    )


def _build_topbar() -> html.Div:
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
                                min_date_allowed=GLOBAL_DATE_MIN,
                                max_date_allowed=GLOBAL_DATE_MAX,
                                start_date=GLOBAL_DATE_MIN,
                                end_date=GLOBAL_DATE_MAX,
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


# ── Root layout ───────────────────────────────────────────────────────────────
app.layout = html.Div(
    id="app-container",
    **{"data-theme": "dark"},  # initial theme
    children=[
        # ── Sidebar ──────────────────────────────────────────────────────────
        html.Nav(
            id="sidebar",
            children=[
                # Logo
                html.Div(
                    [
                        html.Img(
                            src=app.get_asset_url("logo.svg"),
                            className="logo-icon",
                        ),
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
                # Navigation links
                html.Div(
                    [_nav_link(item) for item in NAV_ITEMS],
                    id="sidebar-nav",
                ),
                # AI Analyst sidebar button
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
                # Collapse / expand toggle
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
                # Footer
                html.Div("v1.0 · Big Data & Analytics", id="sidebar-footer"),
            ],
        ),
        # ── Main content area ─────────────────────────────────────────────────
        html.Main(
            id="main-content",
            children=[
                # Top bar
                html.Div(id="topbar", children=_build_topbar()),
                dcc.Loading(
                    html.Div(id="page-shell", children=[dash.page_container]),
                    type="default",
                    parent_className="page-shell-loading",
                ),
            ],
        ),
        dcc.Store(id="theme-store", storage_type="local", data=None),
        dcc.Store(
            id="active-page-context",
            data={"page": "overview", "filters": {}, "headline_metrics": {}},
        ),
        dcc.Store(id="overview-page-context"),
        dcc.Store(id="geography-page-context"),
        dcc.Store(id="reviews-page-context"),
        dcc.Store(id="recommendations-page-context"),
        dcc.Store(id="payments-page-context"),
        dcc.Store(id="segmentation-page-context"),
        dcc.Store(id="cohorts-page-context"),
        dcc.Store(id="forecasting-page-context"),
        dcc.Store(id="sellers-page-context"),
        # AI Chatbot Panel
        html.Div(
            id="ai-panel",
            className="ai-panel collapsed",
            children=[
                html.Div(
                    [
                        html.Div(
                            [
                                html.Div(
                                    DashIconify(icon="ph:brain-bold", width=20),
                                    className="ai-panel-orb",
                                ),
                                html.Div(
                                    [
                                        html.Span("AI ANALYST", className="ai-panel-eyebrow"),
                                        html.Div("Dashboard Copilot", className="ai-panel-title"),
                                        html.Div(
                                            "Premium analysis grounded in the active page context.",
                                            className="ai-panel-subtitle",
                                        ),
                                    ],
                                    className="ai-panel-title-wrap",
                                ),
                            ],
                            className="ai-panel-title-block",
                        ),
                        html.Button(
                            DashIconify(
                                icon="ph:x-bold",
                                width=14,
                                color="rgba(255,255,255,0.4)",
                            ),
                            id="ai-panel-close",
                            n_clicks=0,
                            className="ai-close-btn",
                        ),
                    ],
                    className="ai-panel-header",
                ),
                html.Div(
                    [
                        html.Div("Live Context", className="ai-context-eyebrow"),
                        html.Div(
                            "Sales Overview",
                            id="ai-context-title",
                            className="ai-context-title",
                        ),
                        html.Div(
                            "0 active filters • 0 headline metrics • Context-aware answers",
                            id="ai-context-meta",
                            className="ai-context-meta",
                        ),
                    ],
                    className="ai-context-card",
                ),
                html.Div(
                    [
                        html.Button(
                            [
                                DashIconify(icon="ph:file-text-bold", width=15),
                                html.Span("Executive Summary"),
                            ],
                            id="chat-summary-btn",
                            n_clicks=0,
                            className="chat-action-btn chat-action-btn-primary",
                        ),
                        html.Button(
                            "Strongest Signal",
                            id="chat-suggest-1",
                            n_clicks=0,
                            className="chat-action-btn",
                        ),
                        html.Button(
                            "Revenue Drivers",
                            id="chat-suggest-2",
                            n_clicks=0,
                            className="chat-action-btn",
                        ),
                        html.Button(
                            "Next Action",
                            id="chat-suggest-3",
                            n_clicks=0,
                            className="chat-action-btn",
                        ),
                        html.Button(
                            [
                                DashIconify(icon="ph:broom-bold", width=14),
                                html.Span("Clear"),
                            ],
                            id="chat-clear-btn",
                            n_clicks=0,
                            className="chat-action-btn chat-action-btn-secondary",
                        ),
                    ],
                    className="chat-quick-actions",
                ),
                dcc.Loading(
                    html.Div(
                        id="chat-messages",
                        className="chat-messages",
                        children=_build_chat_messages([]),
                    ),
                    type="default",
                    parent_className="chat-loading-shell",
                ),
                html.Div(
                    [
                        html.Div(
                            "Ask for trends, anomalies, root causes, opportunities, or the best next action.",
                            className="chat-input-hint",
                        ),
                        html.Div(
                            [
                                dcc.Input(
                                    id="chat-input",
                                    type="text",
                                    placeholder="Ask about the current page, filters, and KPIs...",
                                    className="chat-input",
                                    debounce=False,
                                    n_submit=0,
                                ),
                                html.Button(
                                    DashIconify(icon="ph:paper-plane-right-fill", width=16),
                                    id="chat-send",
                                    n_clicks=0,
                                    className="chat-send-btn",
                                ),
                            ],
                            className="chat-composer",
                        ),
                    ],
                    className="chat-input-area",
                ),
                dcc.Store(id="chat-history", data="[]"),
                dcc.Store(id="chat-suggestions-store", data="[]"),
            ],
        ),
    ],
)


# ── Clientside: active nav link highlighting ──────────────────────────────────
app.layout = build_root_layout(
    nav_items=NAV_ITEMS,
    date_min=GLOBAL_DATE_MIN,
    date_max=GLOBAL_DATE_MAX,
    logo_src=app.get_asset_url("logo.svg"),
    page_container=dash.page_container,
)


clientside_callback(
    """
    function(pathname) {
        const links = document.querySelectorAll('.nav-link:not(.ai-nav-link)');
        links.forEach(function(link) {
            const href = link.getAttribute('href');
            const isActive = (href === pathname) || (href === '/' && pathname === '/');
            link.classList.toggle('active', isActive);
        });
        return '';
    }
    """,
    Output("app-container", "data-pathname"),
    Input("_pages_location", "pathname"),
)


clientside_callback(
    """
    function(n_clicks, currentTheme) {
        const preferred = (
            window.matchMedia &&
            window.matchMedia('(prefers-color-scheme: light)').matches
        ) ? 'light' : 'dark';

        if (!n_clicks) {
            return currentTheme || preferred;
        }

        const baseTheme = currentTheme || preferred;
        return baseTheme === 'dark' ? 'light' : 'dark';
    }
    """,
    Output("theme-store", "data"),
    Input("theme-toggle-btn", "n_clicks"),
    State("theme-store", "data"),
)


clientside_callback(
    """
    function(theme) {
        const activeTheme = theme || 'dark';
        const nextLabel = activeTheme === 'dark' ? 'Light Mode' : 'Dark Mode';
        const title = activeTheme === 'dark'
            ? 'Switch to light mode'
            : 'Switch to dark mode';
        if (document && document.documentElement) {
            document.documentElement.setAttribute('data-theme', activeTheme);
        }
        if (document && document.body) {
            document.body.setAttribute('data-theme', activeTheme);
        }
        if (window && window.localStorage) {
            window.localStorage.setItem('olist-theme', activeTheme);
        }
        const root = document.getElementById('app-container');
        if (root) {
            root.setAttribute('data-theme', activeTheme);
        }
        return [activeTheme, nextLabel, title];
    }
    """,
    Output("app-container", "data-theme"),
    Output("theme-toggle-copy", "children"),
    Output("theme-toggle-btn", "title"),
    Input("theme-store", "data"),
)


# ── Clientside: sidebar collapse toggle ──────────────────────────────────────
clientside_callback(
    """
    function(n_clicks) {
        if (!n_clicks) return window.dash_clientside.no_update;
        const sidebar = document.getElementById('sidebar');
        const icon = document.getElementById('toggle-icon');
        if (sidebar) {
            sidebar.classList.toggle('collapsed');
        }
        if (icon && sidebar) {
            const isCollapsed = sidebar.classList.contains('collapsed');
            icon.style.transform = isCollapsed ? 'rotate(180deg)' : 'rotate(0deg)';
        }
        
        // Force Plotly charts to resize after the sidebar transition completes
        setTimeout(function() {
            window.dispatchEvent(new Event('resize'));
        }, 250);
        
        return window.dash_clientside.no_update;
    }
    """,
    Output("sidebar-toggle-btn", "data-dummy"),
    Input("sidebar-toggle-btn", "n_clicks"),
    prevent_initial_call=True,
)


# ── Clientside: AI panel toggle (close button + sidebar button) ──────────────
clientside_callback(
    """
    function(nClose, nSidebar) {
        var panel = document.getElementById('ai-panel');
        var main = document.getElementById('main-content');
        if (!panel) return window.dash_clientside.no_update;
        var ctx = dash_clientside.callback_context;
        if (!ctx.triggered.length) return window.dash_clientside.no_update;
        var who = ctx.triggered[0]['prop_id'].split('.')[0];
        if (who === 'ai-panel-close') {
            panel.classList.add('collapsed');
            if (main) main.style.marginRight = '0px';
        } else {
            var isCollapsed = panel.classList.contains('collapsed');
            if (isCollapsed) {
                panel.classList.remove('collapsed');
                if (main) main.style.marginRight = '380px';
            } else {
                panel.classList.add('collapsed');
                if (main) main.style.marginRight = '0px';
            }
        }
        setTimeout(function() {
            window.dispatchEvent(new Event('resize'));
        }, 300);
        return window.dash_clientside.no_update;
    }
    """,
    Output("ai-panel", "data-toggle"),
    Input("ai-panel-close", "n_clicks"),
    Input("sidebar-ai-btn", "n_clicks"),
    prevent_initial_call=True,
)


# ── Server: Chat callback ────────────────────────────────────────────────────
@callback(
    Output("active-page-context", "data"),
    Input("_pages_location", "pathname"),
    Input("overview-page-context", "data"),
    Input("geography-page-context", "data"),
    Input("reviews-page-context", "data"),
    Input("recommendations-page-context", "data"),
    Input("payments-page-context", "data"),
    Input("segmentation-page-context", "data"),
    Input("cohorts-page-context", "data"),
    Input("forecasting-page-context", "data"),
    Input("sellers-page-context", "data"),
)
def update_active_page_context(
    pathname,
    overview_context,
    geography_context,
    reviews_context,
    recommendations_context,
    payments_context,
    segmentation_context,
    cohorts_context,
    forecasting_context,
    sellers_context,
):
    context_by_path = {
        "/": overview_context,
        "/geography": geography_context,
        "/reviews": reviews_context,
        "/recommendations": recommendations_context,
        "/payments": payments_context,
        "/segmentation": segmentation_context,
        "/cohorts": cohorts_context,
        "/forecasting": forecasting_context,
        "/sellers": sellers_context,
    }
    return context_by_path.get(pathname or "/", overview_context) or {
        "page": "overview",
        "filters": {},
        "headline_metrics": {},
    }


@callback(
    Output("ai-context-title", "children"),
    Output("ai-context-meta", "children"),
    Output("chat-suggest-1", "children"),
    Output("chat-suggest-2", "children"),
    Output("chat-suggest-3", "children"),
    Output("chat-suggestions-store", "data"),
    Input("active-page-context", "data"),
)
def update_ai_panel_context(active_page_context):
    page_key = (active_page_context or {}).get("page", "overview")
    prompts = _build_suggested_prompts(active_page_context)
    return (
        _page_label(page_key),
        _brief_context_meta(active_page_context),
        prompts[0]["label"],
        prompts[1]["label"],
        prompts[2]["label"],
        json.dumps(prompts),
    )


@callback(
    Output("chat-messages", "children"),
    Output("chat-input", "value"),
    Output("chat-history", "data"),
    Input("chat-summary-btn", "n_clicks"),
    Input("chat-suggest-1", "n_clicks"),
    Input("chat-suggest-2", "n_clicks"),
    Input("chat-suggest-3", "n_clicks"),
    Input("chat-clear-btn", "n_clicks"),
    Input("chat-send", "n_clicks"),
    Input("chat-input", "n_submit"),
    State("chat-input", "value"),
    State("chat-history", "data"),
    State("chat-suggestions-store", "data"),
    State("active-page-context", "data"),
    prevent_initial_call=True,
)
def send_chat_message(
    n_summary,
    n_suggest_1,
    n_suggest_2,
    n_suggest_3,
    n_clear,
    n_clicks,
    n_submit,
    user_msg,
    history_json,
    suggestions_json,
    active_page_context,
):
    """Handle AI panel interactions and chat messages."""
    ctx = dash.callback_context
    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0] if ctx.triggered else None

    history = json.loads(history_json) if history_json else []
    suggestions = json.loads(suggestions_json) if suggestions_json else []

    if trigger_id == "chat-clear-btn":
        return _build_chat_messages([]), "", "[]"

    prompt_text = (user_msg or "").strip()
    assistant_response = None

    if trigger_id == "chat-summary-btn":
        prompt_text = "Generate an executive summary for the current view."
        assistant_response = generate_executive_summary(_data_summary, active_page_context)
    elif trigger_id in {"chat-suggest-1", "chat-suggest-2", "chat-suggest-3"}:
        index = int(trigger_id[-1]) - 1
        if 0 <= index < len(suggestions):
            prompt_text = suggestions[index]["prompt"]
    elif not prompt_text:
        return dash.no_update, dash.no_update, dash.no_update

    if not prompt_text:
        return dash.no_update, dash.no_update, dash.no_update

    if assistant_response is None:
        assistant_response = chat_with_data(
            prompt_text,
            _data_summary,
            history,
            page_context=active_page_context,
        )

    history.append({"role": "user", "content": prompt_text})
    history.append({"role": "assistant", "content": assistant_response})

    if len(history) > 24:
        history = history[-24:]

    return _build_chat_messages(history), "", json.dumps(history)


# ── Clientside: auto-scroll chat to bottom ───────────────────────────────────
clientside_callback(
    """
    function(children) {
        setTimeout(function() {
            var el = document.getElementById('chat-messages');
            if (el) el.scrollTop = el.scrollHeight;
        }, 100);
        return window.dash_clientside.no_update;
    }
    """,
    Output("chat-messages", "data-scroll"),
    Input("chat-messages", "children"),
)


# ── Run ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(
        debug=os.getenv("DASH_DEBUG", "").lower() in {"1", "true", "yes"},
        host="127.0.0.1",
        port=8050,
    )
