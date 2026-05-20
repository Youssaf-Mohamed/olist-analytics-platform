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


SYSTEM_PROMPT = """You are an AI data analyst embedded in the Olist BI dashboard.
You answer questions using the provided dataset summary and the currently active page context.
Keep responses concise and grounded in the given numbers.
If the active page context is present, prioritize it over the dataset-wide summary.
Always answer in the same language as the user."""


def _as_bundle(data: Any) -> dict[str, pd.DataFrame]:
    if isinstance(data, dict):
        return data
    return {"orders": data}


def build_data_summary(data: Any) -> str:
    bundle = _as_bundle(data)
    orders_df = bundle["orders"]
    items_df = bundle.get("order_items")
    payments_df = bundle.get("payments")

    total_rev = orders_df["total_order_value"].sum()
    total_orders = orders_df["order_id"].nunique()
    total_customers = orders_df["customer_unique_id"].nunique()
    date_min = orders_df["order_purchase_timestamp"].min().strftime("%Y-%m-%d")
    date_max = orders_df["order_purchase_timestamp"].max().strftime("%Y-%m-%d")

    if items_df is not None:
        cat_rev = (
            items_df.groupby("product_category_name_english")["line_total"]
            .sum()
            .sort_values(ascending=False)
        )
        top5_cats = ", ".join(
            [f"{category} (R${value:,.0f})" for category, value in cat_rev.head(5).items()]
        )
    else:
        top5_cats = "Category data unavailable"

    state_orders = orders_df["customer_state"].value_counts().head(5)
    top5_states = ", ".join(
        [f"{state} ({count:,} orders)" for state, count in state_orders.items()]
    )

    avg_review = orders_df["review_score"].mean()
    review_dist = orders_df["review_score"].dropna().value_counts().sort_index()
    review_str = ", ".join([f"{score}*: {count:,}" for score, count in review_dist.items()])

    delivered = orders_df[orders_df["order_status"] == "delivered"]
    on_time = delivered["is_on_time"].mean() * 100 if not delivered.empty else 0
    avg_delivery = delivered["delivery_days"].mean() if not delivered.empty else 0

    if payments_df is not None:
        pay_types = (
            payments_df.groupby("payment_type")["payment_value"]
            .sum()
            .sort_values(ascending=False)
        )
        pay_str = ", ".join([f"{ptype}: R${value:,.0f}" for ptype, value in pay_types.head(4).items()])
    else:
        pay_str = "Payment data unavailable"

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
        "OLIST E-COMMERCE DATA SUMMARY:\n"
        f"Period: {date_min} to {date_max}\n"
        f"Total Revenue: R${total_rev:,.0f} | Orders: {total_orders:,} | Customers: {total_customers:,}\n"
        f"Top Categories: {top5_cats}\n"
        f"Top States: {top5_states}\n"
        f"Reviews: avg {avg_review:.1f}/5.0 - {review_str}\n"
        f"Delivery: {on_time:.1f}% on-time, avg {avg_delivery:.1f} days\n"
        f"Payments: {pay_str}\n"
        f"Monthly Revenue (last 6m): {trend_str}"
    )


def _format_page_context(page_context: dict[str, Any] | None) -> str:
    if not page_context:
        return "Active page context: not available."

    page_name = page_context.get("page", "unknown")
    filters = page_context.get("filters", {})
    metrics = page_context.get("headline_metrics", {})
    return (
        f"Active page: {page_name}\n"
        f"Filters: {filters}\n"
        f"Visible headline metrics: {metrics}"
    )


def chat_with_data(
    user_message: str,
    data_summary: str,
    history: list[dict[str, str]],
    page_context: dict[str, Any] | None = None,
) -> str:
    page_summary = _format_page_context(page_context)

    if not _AI_AVAILABLE:
        return _fallback_chat(user_message, data_summary, page_summary)

    messages = [
        {"role": "system", "content": f"{SYSTEM_PROMPT}\n\n{data_summary}\n\n{page_summary}"},
    ]

    for message in history:
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
            "temperature": 0.1
        }
        
        response = requests.post(_API_URL, headers=headers, json=payload, timeout=30)
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
    message = user_message.lower()
    response_parts = []

    if "Active page:" in page_summary and "not available" not in page_summary:
        response_parts.append(page_summary)

    lines = data_summary.split("\n")
    summary_dict: dict[str, str] = {}
    for line in lines:
        if "Total Revenue" in line:
            summary_dict["revenue_line"] = line.strip()
        elif "Top Categories" in line:
            summary_dict["categories_line"] = line.strip()
        elif "Top States" in line:
            summary_dict["states_line"] = line.strip()
        elif "Reviews" in line:
            summary_dict["reviews_line"] = line.strip()
        elif "Delivery" in line:
            summary_dict["delivery_line"] = line.strip()
        elif "Payments" in line:
            summary_dict["payments_line"] = line.strip()

    if any(word in message for word in ["hello", "hi", "hey", "مرحبا", "اهلا", "أهلا", "سلام"]):
        if api_configured:
            return (
                "Hi! I hit a temporary rate limit. Try again in a few seconds.\n\n"
                "I can still help with revenue, categories, states, reviews, delivery, or payments."
            )
        return (
            "Hi! I am running in basic mode right now.\n\n"
            "Ask me about revenue, categories, states, reviews, delivery, or payments."
        )

    if any(word in message for word in ["revenue", "sales", "إيراد", "مبيعات", "ايراد"]):
        response_parts.append(summary_dict.get("revenue_line", "Revenue data not available."))
    elif any(word in message for word in ["category", "categories", "product", "كاتيجوري", "منتج"]):
        response_parts.append(summary_dict.get("categories_line", "Category data not available."))
    elif any(word in message for word in ["state", "region", "geo", "ولاية", "منطقة"]):
        response_parts.append(summary_dict.get("states_line", "State data not available."))
    elif any(word in message for word in ["review", "rating", "satisfaction", "تقييم"]):
        response_parts.append(summary_dict.get("reviews_line", "Review data not available."))
    elif any(word in message for word in ["delivery", "shipping", "توصيل", "شحن"]):
        response_parts.append(summary_dict.get("delivery_line", "Delivery data not available."))
    elif any(word in message for word in ["payment", "pay", "دفع"]):
        response_parts.append(summary_dict.get("payments_line", "Payment data not available."))
    else:
        hint = "\nAI Assistant is temporarily unavailable." if api_configured else ""
        response_parts.append(
            "I can answer questions about revenue, categories, states, reviews, delivery, and payments."
            + hint
        )

    return "\n".join(response_parts)


def generate_executive_summary(
    data_summary: str, page_context: dict[str, Any] | None = None
) -> str:
    page_summary = _format_page_context(page_context)
    prompt = (
        "Write a short executive summary for a business stakeholder. "
        "Use 4 compact bullet points covering current scope, strongest signal, risk/opportunity, and next action.\n\n"
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
            
            response = requests.post(_API_URL, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            
            return response.json()["choices"][0]["message"]["content"]
        except Exception as exc:
            print(f"[ai] Executive summary fallback due to error: {exc}")

    page_name = page_context.get("page", "dashboard") if page_context else "dashboard"
    filters = page_context.get("filters", {}) if page_context else {}
    metrics = page_context.get("headline_metrics", {}) if page_context else {}

    metric_lines = []
    for key, value in list(metrics.items())[:4]:
        metric_lines.append(f"- {key.replace('_', ' ').title()}: {value}")

    filter_line = (
        f"Period: {filters.get('start_date', 'full range')} to {filters.get('end_date', 'full range')}"
    )
    compare_line = (
        "Previous-period comparison is enabled."
        if filters.get("compare_previous")
        else "Previous-period comparison is disabled."
    )

    return "\n".join(
        [
            f"Executive summary for {page_name.title()}",
            f"- Scope: {filter_line}",
            f"- Current view: {compare_line}",
            *(metric_lines or ["- Metrics: No page-specific metrics were available."]),
            "- Action: Review the strongest metric on this page and investigate any weak retention, delivery, or satisfaction signal before the next reporting cycle.",
        ]
    )
