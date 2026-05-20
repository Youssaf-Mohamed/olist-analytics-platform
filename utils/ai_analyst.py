"""
AI chatbot helpers for the dashboard using Groq API.
"""

from __future__ import annotations

import os
import requests
from typing import Any

import pandas as pd

_AI_AVAILABLE = False
_API_KEY = os.getenv("GROQ_API_KEY", "")
_API_URL = os.getenv("GROQ_API_URL", "https://api.groq.com/openai/v1/chat/completions")
_MODEL_NAME = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

if _API_KEY:
    _AI_AVAILABLE = True
    print(f"[ai] Groq API ready (model: {_MODEL_NAME}).")
else:
    print("[ai] GROQ_API_KEY not set, using rule-based responses.")


SYSTEM_PROMPT = """You are the 'Olist AI Analyst', a premium business intelligence copilot.
Your goal is to provide high-signal, executive-level insights based on the Olist e-commerce dataset.

GUIDELINES:
1. GOUNDING: Only use the numbers provided in the 'DATA SUMMARY' and 'PAGE CONTEXT'. Do not hallucinate external data.
2. ANALYTICAL DEPTH: When asked for an analysis, follow a 'Reason -> Evidence -> Action' structure.
3. CONCISENESS: Business stakeholders value time. Keep responses punchy and avoid filler.
4. PAGE AWARENESS: If a 'PAGE CONTEXT' is provided, the user is looking at specific charts. Prioritize this context.
5. FORMATTING: Use Markdown (bolding, lists) to make insights easy to scan.
6. LANGUAGE: Always respond in the same language as the user's query.

If you don't have enough data to answer a specific question, state it clearly and suggest what the user should look for in the dashboard.
"""


def _as_bundle(data: Any) -> dict[str, pd.DataFrame]:
    if isinstance(data, dict):
        return data
    return {"orders": data}


def build_data_summary(data: Any) -> str:
    """Builds a rich textual summary of the entire dataset for LLM grounding."""
    bundle = _as_bundle(data)
    orders_df = bundle["orders"]
    items_df = bundle.get("order_items")
    payments_df = bundle.get("payments")

    # Basic KPIs
    total_rev = orders_df["total_order_value"].sum()
    total_orders = orders_df["order_id"].nunique()
    total_customers = orders_df["customer_unique_id"].nunique()
    avg_ticket = total_rev / total_orders if total_orders > 0 else 0
    
    date_min = orders_df["order_purchase_timestamp"].min().strftime("%Y-%m-%d")
    date_max = orders_df["order_purchase_timestamp"].max().strftime("%Y-%m-%d")

    # Product performance
    if items_df is not None:
        cat_rev = (
            items_df.groupby("product_category_name_english")["line_total"]
            .sum()
            .sort_values(ascending=False)
        )
        top5_cats = "\n".join(
            [f"   - {category}: R${value:,.0f}" for category, value in cat_rev.head(5).items()]
        )
    else:
        top5_cats = "   - Category data unavailable"

    # Geographic performance
    state_orders = orders_df["customer_state"].value_counts().head(5)
    top5_states = ", ".join(
        [f"{state} ({count:,} orders)" for state, count in state_orders.items()]
    )

    # Customer Satisfaction
    avg_review = orders_df["review_score"].mean()
    review_dist = orders_df["review_score"].dropna().value_counts().sort_index()
    review_str = ", ".join([f"{score}*: {count:,}" for score, count in review_dist.items()])

    # Logistics
    delivered = orders_df[orders_df["order_status"] == "delivered"]
    on_time_rate = delivered["is_on_time"].mean() * 100 if not delivered.empty else 0
    avg_delivery_days = delivered["delivery_days"].mean() if not delivered.empty else 0

    # Payments
    if payments_df is not None:
        pay_types = (
            payments_df.groupby("payment_type")["payment_value"]
            .sum()
            .sort_values(ascending=False)
        )
        pay_str = ", ".join([f"{ptype}: R${value:,.0f}" for ptype, value in pay_types.head(4).items()])
    else:
        pay_str = "Payment data unavailable"

    # Recent Trend (last 6 months)
    monthly = (
        orders_df.set_index("order_purchase_timestamp")
        .resample("ME")["total_order_value"]
        .sum()
        .tail(6)
    )
    trend_str = ", ".join(
        [f"{date.strftime('%Y-%m')}: R${value:,.0f}" for date, value in monthly.items()]
    )

    return (
        "### OLIST E-COMMERCE DATA SUMMARY\n"
        f"- **Period**: {date_min} to {date_max}\n"
        f"- **Revenue**: R${total_rev:,.0f} (Avg. Ticket: R${avg_ticket:,.2f})\n"
        f"- **Volume**: {total_orders:,} orders from {total_customers:,} unique customers\n"
        f"- **Top Categories**:\n{top5_cats}\n"
        f"- **Top Regions**: {top5_states}\n"
        f"- **Customer CSAT**: {avg_review:.2f}/5.0 ({review_str})\n"
        f"- **Logistics**: {on_time_rate:.1f}% on-time, {avg_delivery_days:.1f} days avg delivery\n"
        f"- **Payments**: {pay_str}\n"
        f"- **Revenue Trend (6m)**: {trend_str}"
    )


def _format_page_context(page_context: dict[str, Any] | None) -> str:
    """Formats the active dashboard page context into a prompt-friendly string."""
    if not page_context:
        return "### ACTIVE PAGE CONTEXT\n- Page: General Dashboard (No specific context)"

    page_name = page_context.get("page", "unknown").replace("_", " ").title()
    filters = page_context.get("filters", {})
    metrics = page_context.get("headline_metrics", {})
    
    filter_list = [f"{k}: {v}" for k, v in filters.items() if v not in (None, "", [], {})]
    metric_list = [f"{k.replace('_', ' ').title()}: {v}" for k, v in metrics.items()]

    return (
        "### ACTIVE PAGE CONTEXT\n"
        f"- **Current View**: {page_name}\n"
        f"- **Active Filters**: {', '.join(filter_list) if filter_list else 'None'}\n"
        f"- **Page KPIs**: {', '.join(metric_list) if metric_list else 'None'}"
    )


def chat_with_data(
    user_message: str,
    data_summary: str,
    history: list[dict[str, str]],
    page_context: dict[str, Any] | None = None,
) -> str:
    """Main entry point for AI chat. Handles API calls with fallback logic."""
    page_summary = _format_page_context(page_context)

    if not _AI_AVAILABLE:
        return _fallback_chat(user_message, data_summary, page_summary)

    messages = [
        {"role": "system", "content": f"{SYSTEM_PROMPT}\n\n{data_summary}\n\n{page_summary}"},
    ]

    # Include recent history (max 10 turns to save context)
    for message in history[-10:]:
        messages.append({"role": message["role"], "content": message["content"]})

    messages.append({"role": "user", "content": user_message})

    try:
        headers = {
            "Authorization": f"Bearer {_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": _MODEL_NAME,
            "messages": messages,
            "temperature": 0.2, # Slightly higher for better analysis, but still grounded
            "max_tokens": 800
        }
        
        response = requests.post(_API_URL, headers=headers, json=payload, timeout=45)
        response.raise_for_status()
        
        return response.json()["choices"][0]["message"]["content"]
    except Exception as exc:
        print(f"[ai] API error: {exc}")
        return _fallback_chat(user_message, data_summary, page_summary, api_configured=True)


def _fallback_chat(
    user_message: str,
    data_summary: str,
    page_summary: str,
    api_configured: bool = False,
) -> str:
    """Provides rule-based responses when the AI service is unavailable."""
    message = user_message.lower()
    response_parts = []

    # If the user is just saying hi
    if any(word in message for word in ["hello", "hi", "hey", "مرحبا", "اهلا", "أهلا", "سلام"]):
        status_msg = "I'm currently running in **Limited Mode** (no API connection)." if not api_configured else "I'm having trouble reaching my brain right now."
        return (
            f"Hi! {status_msg}\n\n"
            "I can still provide core statistics about **Revenue**, **Categories**, **Regions**, **Reviews**, and **Logistics** based on the current data load."
        )

    # Simple keyword extraction from the grounded summary
    summary_clean = data_summary.replace("### ", "").replace("- **", "").replace("**", "")
    lines = summary_clean.split("\n")
    
    keywords = {
        "revenue": ["revenue", "sales", "إيراد", "مبيعات", "money"],
        "categories": ["category", "categories", "product", "منتج"],
        "regions": ["region", "state", "map", "ولاية", "منطقة"],
        "reviews": ["review", "rating", "satisfaction", "تقييم"],
        "logistics": ["delivery", "shipping", "logistics", "توصيل", "شحن"],
    }

    found = False
    for key, words in keywords.items():
        if any(word in message for word in words):
            for line in lines:
                if key.title() in line or (key == "regions" and "Top Regions" in line):
                    response_parts.append(line.strip())
                    found = True

    if not found:
        hint = "\n\n*Note: AI Analyst is temporarily offline. Basic data lookup is active.*" if api_configured else ""
        return (
            "I can help with specific data points. Try asking about:\n"
            "- Overall **Revenue** and growth\n"
            "- **Top Categories** by sales\n"
            "- **Regional performance** (States)\n"
            "- **Customer Satisfaction** (Reviews)\n"
            "- **Delivery performance** and timing"
            + hint
        )

    return "Based on the available data:\n" + "\n".join([f"- {p}" for p in response_parts])


def generate_executive_summary(
    data_summary: str, page_context: dict[str, Any] | None = None
) -> str:
    """Generates a high-level executive summary for the current dashboard view."""
    page_summary = _format_page_context(page_context)
    
    prompt = (
        "Generate a professional Executive Summary for the current dashboard view.\n"
        "Requirements:\n"
        "1. Use 4 bullet points: 'Scope', 'Strongest Signal', 'Risk Area', and 'Strategic Recommendation'.\n"
        "2. Be extremely specific with numbers.\n"
        "3. Tone: Executive, confident, data-driven.\n\n"
        f"{data_summary}\n\n{page_summary}"
    )

    if _AI_AVAILABLE:
        try:
            headers = {
                "Authorization": f"Bearer {_API_KEY}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": _MODEL_NAME,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.1
            }
            
            response = requests.post(_API_URL, headers=headers, json=payload, timeout=45)
            response.raise_for_status()
            
            return response.json()["choices"][0]["message"]["content"]
        except Exception as exc:
            print(f"[ai] Executive summary fallback due to error: {exc}")

    # Manual Fallback Summary
    page_name = page_context.get("page", "Dashboard") if page_context else "Dashboard"
    metrics = page_context.get("headline_metrics", {}) if page_context else {}
    
    metric_text = "\n".join([f"   - {k.replace('_', ' ').title()}: {v}" for k, v in list(metrics.items())[:3]])
    
    # Extract period safely
    period_match = "full range"
    if "Period: " in data_summary:
        try:
            period_match = data_summary.split("Period: ")[1].split("\n")[0]
        except IndexError:
            pass

    return (
        f"**Executive Summary: {page_name.title()}**\n"
        f"- **Scope**: Analyzed dataset from {period_match}\n"
        f"- **Current Signal**: The visible metrics for this view are:\n{metric_text if metric_text else '   - General dataset KPIs active.'}\n"
        f"- **Risk Area**: Need to monitor delivery performance and review scores in underperforming states.\n"
        f"- **Strategic Recommendation**: Optimize logistics in top-volume regions to maintain satisfaction levels."
    )
