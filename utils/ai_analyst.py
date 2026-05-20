"""
AI chatbot helpers for the dashboard using Groq API.
"""

from __future__ import annotations

import os
import requests
import json
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


SYSTEM_PROMPT = """You are the 'Olist AI Business Intelligence Analyst'. You operate within a high-performance analytics dashboard.

### CORE OPERATING PROTOCOL: CHAIN OF THOUGHT (CoT)
When you receive a query, you MUST follow these internal reasoning steps before providing your final answer:
1. **Data Internalization**: Review the 'DATA SUMMARY' and 'PAGE CONTEXT'. Identify the specific metrics relevant to the query.
2. **Context Synthesis**: Determine if the user is asking about the entire dataset or just the current visible view.
3. **Analytical Reasoning**: Look for correlations, trends, or anomalies. Ask yourself: "Why is this number high/low?"
4. **Insight Generation**: Formulate a grounded response based on steps 1-3.

### RESPONSE STRUCTURE:
- **Direct Answer**: Provide the primary insight or number requested immediately.
- **Data Evidence**: Cite the specific numbers from the context that support your answer.
- **Business Action**: Suggest a practical 'Next Step' or 'Optimization' based on the insight.

### GUIDELINES:
- **Grounding**: Never invent data. If the data is missing, suggest where the user might find it in the dashboard.
- **Language**: Respond in the same language as the user.
- **Conciseness**: Avoid conversational filler. Be precise, professional, and analytical.
"""


def _as_bundle(data: Any) -> dict[str, pd.DataFrame]:
    if isinstance(data, dict):
        return data
    return {"orders": data}


def build_data_summary(data: Any) -> str:
    """Builds a hierarchical, multi-dimensional textual summary of the dataset."""
    bundle = _as_bundle(data)
    orders_df = bundle["orders"]
    items_df = bundle.get("order_items")
    payments_df = bundle.get("payments")

    # 1. High-Level Performance (Revenue & Volume)
    total_rev = orders_df["total_order_value"].sum()
    total_orders = orders_df["order_id"].nunique()
    total_customers = orders_df["customer_unique_id"].nunique()
    avg_order_val = total_rev / total_orders if total_orders > 0 else 0
    
    date_min = orders_df["order_purchase_timestamp"].min().strftime("%Y-%m-%d")
    date_max = orders_df["order_purchase_timestamp"].max().strftime("%Y-%m-%d")

    # 2. Product & Category Hierarchy
    if items_df is not None:
        cat_perf = items_df.groupby("product_category_name_english").agg({
            "line_total": "sum",
            "order_id": "nunique"
        }).sort_values("line_total", ascending=False)
        
        top_cats = []
        for cat, row in cat_perf.head(5).iterrows():
            top_cats.append(f"   - {cat}: R${row['line_total']:,.0f} ({row['order_id']:,} orders)")
        top_cats_str = "\n".join(top_cats)
    else:
        top_cats_str = "   - Product data unavailable"

    # 3. Logistics & Fulfillment Efficiency
    delivered = orders_df[orders_df["order_status"] == "delivered"]
    if not delivered.empty:
        on_time_rate = delivered["is_on_time"].mean() * 100
        avg_lead_time = delivered["delivery_days"].mean()
        # Calculate delay for late orders if columns exist
        if "order_delivered_customer_date" in delivered.columns and "order_estimated_delivery_date" in delivered.columns:
            late_orders = delivered[delivered["is_on_time"] == False]
            avg_delay = (late_orders["order_delivered_customer_date"] - late_orders["order_estimated_delivery_date"]).dt.total_seconds().mean() / 86400 if not late_orders.empty else 0
        else:
            avg_delay = 0
    else:
        on_time_rate, avg_lead_time, avg_delay = 0, 0, 0

    # 4. Customer Sentiment & Loyalty
    avg_review = orders_df["review_score"].mean()
    promoters_rate = (orders_df["review_score"] >= 4).mean() * 100
    detractors_rate = (orders_df["review_score"] <= 2).mean() * 100

    # 5. Financial & Payment Mix
    if payments_df is not None:
        pay_mix = payments_df["payment_type"].value_counts(normalize=True).head(3) * 100
        pay_str = ", ".join([f"{ptype}: {val:.1f}%" for ptype, val in pay_mix.items()])
    else:
        pay_str = "Unknown"

    # 6. Temporal Revenue Momentum (Last 4 Months)
    monthly = orders_df.set_index("order_purchase_timestamp").resample("ME")["total_order_value"].sum().tail(4)
    momentum_str = " -> ".join([f"{val/1000:,.0f}k" for val in monthly.values])

    return (
        "## DATA SUMMARY (Grounded Facts)\n"
        f"### 1. Ecosystem Scale\n"
        f"- **Period**: {date_min} to {date_max}\n"
        f"- **Total Revenue**: R${total_rev:,.0f} | **Avg. Order**: R${avg_order_val:,.2f}\n"
        f"- **Network**: {total_orders:,} orders | {total_customers:,} unique customers\n"
        f"### 2. Top Performing Categories\n"
        f"{top_cats_str}\n"
        f"### 3. Fulfillment & Logistics\n"
        f"- **SLA Compliance**: {on_time_rate:.1f}% on-time delivery\n"
        f"- **Lead Time**: {avg_lead_time:.1f} days avg | **Avg. Delay**: {avg_delay:.1f} days\n"
        f"### 4. Customer Satisfaction (CSAT)\n"
        f"- **Avg. Score**: {avg_review:.2f}/5.0\n"
        f"- **Sentiment**: {promoters_rate:.1f}% Promoters (4-5*) | {detractors_rate:.1f}% Detractors (1-2*)\n"
        f"### 5. Payments & Trends\n"
        f"- **Method Mix**: {pay_str}\n"
        f"- **Revenue Momentum (Last 4m)**: {momentum_str} (in R$k)"
    )


def _format_page_context(page_context: dict[str, Any] | None) -> str:
    """Formats the active dashboard page context for maximum signal-to-noise ratio."""
    if not page_context:
        return "## ACTIVE PAGE CONTEXT\n- View: Global Overview (No page-specific filters active)"

    page_name = page_context.get("page", "unknown").replace("_", " ").upper()
    filters = page_context.get("filters", {})
    metrics = page_context.get("headline_metrics", {})
    
    active_filters = {k: v for k, v in filters.items() if v not in (None, "", [], {})}
    
    filter_str = "\n".join([f"   - {k}: {v}" for k, v in active_filters.items()]) if active_filters else "   - No active filters"
    metric_str = "\n".join([f"   - {k.replace('_', ' ').title()}: {v}" for k, v in metrics.items()]) if metrics else "   - No metrics available"

    return (
        "## ACTIVE PAGE CONTEXT\n"
        f"### Current View: {page_name}\n"
        f"#### Applied Filters:\n{filter_str}\n"
        f"#### Visible Page Metrics:\n{metric_str}"
    )


def chat_with_data(
    user_message: str,
    data_summary: str,
    history: list[dict[str, str]],
    page_context: dict[str, Any] | None = None,
) -> str:
    """Handles AI chat with intelligent history management and CoT prompting."""
    page_summary = _format_page_context(page_context)

    if not _AI_AVAILABLE:
        return _fallback_chat(user_message, data_summary, page_summary)

    # --- History Management ---
    # We maintain a sliding window of the last 6 turns (12 messages) to keep context fresh
    # while preventing token bloat. We also prune repetitive greetings from history.
    managed_history = []
    for msg in history[-12:]:
        content = msg.get("content", "").lower()
        # Skip simple greetings in history to focus on analytical turns
        if len(content) < 15 and any(h in content for h in ["hi", "hello", "hey", "مرحبا"]):
            continue
        managed_history.append(msg)

    messages = [
        {"role": "system", "content": f"{SYSTEM_PROMPT}\n\n{data_summary}\n\n{page_summary}"},
    ]
    messages.extend(managed_history)
    messages.append({"role": "user", "content": user_message})

    try:
        headers = {
            "Authorization": f"Bearer {_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": _MODEL_NAME,
            "messages": messages,
            "temperature": 0.1,  # Low temperature for highly grounded analytical responses
            "max_tokens": 1024,
            "top_p": 0.95
        }
        
        response = requests.post(_API_URL, headers=headers, json=payload, timeout=50)
        response.raise_for_status()
        
        return response.json()["choices"][0]["message"]["content"]
    except Exception as exc:
        print(f"[ai] Analytical engine error: {exc}")
        return _fallback_chat(user_message, data_summary, page_summary, api_configured=True)


def _fallback_chat(
    user_message: str,
    data_summary: str,
    page_summary: str,
    api_configured: bool = False,
) -> str:
    """Robust fallback logic with improved keyword-to-section mapping."""
    message = user_message.lower()
    
    if any(word in message for word in ["hello", "hi", "hey", "مرحبا", "اهلا"]):
        return (
            "Hi! I'm the **Olist AI Analyst** (Fallback Mode).\n\n"
            "I can provide direct lookups for **Ecosystem Scale**, **Top Categories**, **Logistics**, **Satisfaction (CSAT)**, and **Payments**."
        )

    # Mapping keywords to summary sections
    mapping = {
        "scale": ["revenue", "sales", "volume", "total", "orders", "customers", "scale"],
        "categories": ["category", "categories", "product", "top items"],
        "logistics": ["delivery", "shipping", "logistics", "delay", "on-time", "lead time"],
        "csat": ["review", "rating", "satisfaction", "csat", "score", "promoter", "detractor"],
        "trends": ["trend", "momentum", "history", "monthly", "growth"]
    }

    relevant_sections = []
    summary_sections = data_summary.split("### ")
    
    for section_key, keywords in mapping.items():
        if any(kw in message for kw in keywords):
            for section in summary_sections:
                # Basic header matching
                header = section.split("\n")[0].lower()
                if any(kw in header for kw in keywords) or \
                   (section_key == "scale" and "scale" in header) or \
                   (section_key == "csat" and "satisfaction" in header):
                    relevant_sections.append(f"**{section.strip()}**")

    if not relevant_sections:
        status = "*AI engine is currently offline. Showing grounded lookup results.*" if api_configured else ""
        return (
            "I couldn't find a direct analytical match for your query in my local cache.\n"
            "Try asking about **Revenue**, **Top Categories**, **Fulfillment (SLA)**, or **Customer Scores**.\n\n"
            + status
        )

    return "### Local Data Lookup Results\n" + "\n\n".join(relevant_sections)


def generate_executive_summary(
    data_summary: str, page_context: dict[str, Any] | None = None
) -> str:
    """Generates a structured executive summary using explicit CoT constraints."""
    page_summary = _format_page_context(page_context)
    
    prompt = (
        "ACT AS: Senior Business Consultant.\n"
        "TASK: Generate a high-impact Executive Summary for the current dashboard view.\n"
        "CONSTRAINTS:\n"
        "1. Identify the 'CORE PERFORMANCE STORY' (The 'What').\n"
        "2. Identify the 'CRITICAL DRIVER' (The 'Why').\n"
        "3. Identify the 'IMMEDIATE RISK' (The 'So What').\n"
        "4. Provide a 'STRATEGIC RECOMMENDATION' (The 'Now What').\n"
        "Use bullet points and bold numbers. Be concise.\n\n"
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
            
            response = requests.post(_API_URL, headers=headers, json=payload, timeout=50)
            response.raise_for_status()
            
            return response.json()["choices"][0]["message"]["content"]
        except Exception as exc:
            print(f"[ai] Executive summary generation failed: {exc}")

    # Manual Fallback with structured CoT logic
    page_name = page_context.get("page", "Dashboard") if page_context else "Global"
    filters = page_context.get("filters", {}) if page_context else {}
    metrics = page_context.get("headline_metrics", {}) if page_context else {}
    
    filter_desc = ", ".join([f"{k}={v}" for k, v in filters.items()]) if filters else "no active filters"
    metric_desc = ", ".join([f"{k}={v}" for k, v in metrics.items()]) if metrics else "no specific metrics"
    
    return (
        f"### Executive Summary: {page_name.title()} View\n"
        f"- **Performance Story**: Analyzing the {page_name.title()} dataset with {filter_desc}. Key metrics: {metric_desc}.\n"
        "- **Critical Driver**: Performance is heavily concentrated in top categories and key economic hubs.\n"
        "- **Immediate Risk**: Logistics SLA compliance and extreme sentiment detractors require attention.\n"
        "- **Strategic Recommendation**: Target optimization efforts toward the most active segments identified in this view."
    )
