"""
app.py — Olist E-Commerce Intelligence System
Entry point: Dash multi-page app with fixed sidebar navigation.
Run: venv\\Scripts\\python.exe app.py
Dashboard: http://127.0.0.1:8050
"""

import dash
from dash import html, dcc, callback, Input, Output, State, clientside_callback
import pandas as pd
import json
from dash_iconify import DashIconify
from utils.data_loader import load_master_data
from utils.gemini_analyst import build_data_summary, chat_with_data

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

server = app.server  # expose Flask server for deployment

# ── Pre-compute data summary for chatbot ──────────────────────────────────────
_master = load_master_data()
_data_summary = build_data_summary(_master)

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
    {"icon": "ph:trend-up-bold", "label": "Forecasting", "href": "/forecasting"},
]


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
                            src="/assets/logo.png",
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
                html.Div(id="topbar"),
                dash.page_container,
            ],
        ),
        # ── AI Chatbot Panel ──────────────────────────────────────────────────
        html.Div(
            id="ai-panel",
            className="ai-panel collapsed",
            children=[
                # Header
                html.Div(
                    [
                        html.Div(
                            [
                                DashIconify(
                                    icon="ph:brain-bold", width=20, color="#38BDF8"
                                ),
                                html.Span(
                                    "AI ANALYST",
                                    style={
                                        "fontFamily": "var(--font-heading)",
                                        "fontSize": "11px",
                                        "fontWeight": "800",
                                        "color": "#38BDF8",
                                        "letterSpacing": "2px",
                                        "marginLeft": "8px",
                                    },
                                ),
                            ],
                            style={"display": "flex", "alignItems": "center"},
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
                # Chat messages area
                html.Div(
                    id="chat-messages",
                    className="chat-messages",
                    children=[
                        # Welcome message
                        html.Div(
                            [
                                html.P(
                                    "👋 Hi! I'm your AI data analyst. Ask me anything "
                                    "about the Olist dashboard — sales, categories, "
                                    "deliveries, reviews, and more!",
                                ),
                            ],
                            className="chat-msg chat-msg-ai",
                        ),
                    ],
                ),
                # Input area
                html.Div(
                    [
                        dcc.Input(
                            id="chat-input",
                            type="text",
                            placeholder="Ask about the data...",
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
                    className="chat-input-area",
                ),
                # Hidden store for chat history
                dcc.Store(id="chat-history", data="[]"),
            ],
        ),
    ],
)


# ── Clientside: active nav link highlighting ──────────────────────────────────
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
                if (main) main.style.marginRight = '300px';
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
    Output("chat-messages", "children"),
    Output("chat-input", "value"),
    Output("chat-history", "data"),
    Input("chat-send", "n_clicks"),
    Input("chat-input", "n_submit"),
    State("chat-input", "value"),
    State("chat-history", "data"),
    State("chat-messages", "children"),
    prevent_initial_call=True,
)
def send_chat_message(n_clicks, n_submit, user_msg, history_json, existing_msgs):
    """Handle user chat messages."""
    if not user_msg or not user_msg.strip():
        return dash.no_update, dash.no_update, dash.no_update

    user_msg = user_msg.strip()
    history = json.loads(history_json) if history_json else []

    # Get AI response
    ai_response = chat_with_data(user_msg, _data_summary, history)

    # Update history
    history.append({"role": "user", "content": user_msg})
    history.append({"role": "assistant", "content": ai_response})

    # Keep last 20 messages in history for context window
    if len(history) > 20:
        history = history[-20:]

    # Build message components
    if existing_msgs is None:
        existing_msgs = []

    existing_msgs.append(
        html.Div(user_msg, className="chat-msg chat-msg-user")
    )
    existing_msgs.append(
        html.Div(ai_response, className="chat-msg chat-msg-ai")
    )

    return existing_msgs, "", json.dumps(history)


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
        debug=True,
        host="127.0.0.1",
        port=8050,
    )
