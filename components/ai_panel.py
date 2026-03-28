"""AI panel UI helpers and context-aware prompt builders."""

from __future__ import annotations

from dash import dcc, html
from dash_iconify import DashIconify

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


def page_label(page_key: str | None) -> str:
    return PAGE_LABELS.get(page_key or "overview", "Dashboard")


def brief_context_meta(page_context: dict | None) -> str:
    if not page_context:
        return "Synced to the dashboard. No page-specific context available yet."

    filters = page_context.get("filters", {}) or {}
    metrics = page_context.get("headline_metrics", {}) or {}
    active_filters = sum(1 for value in filters.values() if value not in (None, "", [], {}))
    metric_count = len(metrics)
    return (
        f"{active_filters} active filters • {metric_count} headline metrics "
        "• Context-aware answers"
    )


def build_suggested_prompts(page_context: dict | None) -> list[dict[str, str]]:
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


def chat_message_component(role: str, text: str, label: str | None = None) -> html.Div:
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
                    dcc.Markdown(text, className="chat-msg-copy", link_target="_blank"),
                ],
                className=f"chat-msg chat-msg-{'user' if is_user else 'ai'}",
            ),
        ],
        className=f"chat-row chat-row-{'user' if is_user else 'ai'}",
    )


def build_chat_messages(history: list[dict[str, str]] | None) -> list[html.Div]:
    messages = [
        chat_message_component(
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
            chat_message_component(
                item.get("role", "assistant"),
                item.get("content", ""),
                label="You" if item.get("role") == "user" else "AI Analyst",
            )
        )

    return messages


def build_ai_panel() -> html.Div:
    return html.Div(
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
                    html.Div("Sales Overview", id="ai-context-title", className="ai-context-title"),
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
                    children=build_chat_messages([]),
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
    )
