"""
utils/gemini_analyst.py — AI Chatbot powered by Gemini
Provides data-aware chat responses about the Olist dashboard.
"""

import os
import pandas as pd

# ── Gemini client setup ───────────────────────────────────────────────────────
_GEMINI_AVAILABLE = False
_client = None
_MODEL_NAME = "gemini-2.0-flash"

try:
    from google import genai

    _api_key = os.getenv("GEMINI_API_KEY", "")
    if _api_key:
        _client = genai.Client(api_key=_api_key)
        _GEMINI_AVAILABLE = True
        print("[gemini] ✓ Gemini API ready.")
    else:
        print("[gemini] GEMINI_API_KEY not set — using rule-based responses.")
except ImportError:
    print("[gemini] google-genai not installed — using rule-based responses.")


SYSTEM_PROMPT = """You are an AI data analyst embedded in the Olist E-Commerce BI Dashboard.
You answer questions about the business data provided below. Keep responses concise (2-4 sentences).
Use numbers from the data. If you don't know the answer from the data, say so.
Always respond in the same language the user writes in. Use emojis sparingly for key points.
Format currency as R$ (Brazilian Real)."""


def build_data_summary(df: pd.DataFrame) -> str:
    """Build a concise text summary of the master DataFrame for context."""
    total_rev = df["payment_value"].sum()
    total_orders = df["order_id"].nunique()
    total_customers = df["customer_unique_id"].nunique()
    date_min = df["order_purchase_timestamp"].min().strftime("%Y-%m-%d")
    date_max = df["order_purchase_timestamp"].max().strftime("%Y-%m-%d")

    # Top 5 categories
    cat_rev = (
        df.groupby("product_category_name_english")["payment_value"]
        .sum()
        .sort_values(ascending=False)
    )
    top5_cats = ", ".join(
        [f"{c} (R${v:,.0f})" for c, v in cat_rev.head(5).items()]
    )

    # Top 5 states
    state_orders = df["customer_state"].value_counts().head(5)
    top5_states = ", ".join(
        [f"{s} ({c:,} orders)" for s, c in state_orders.items()]
    )

    # Reviews
    avg_review = df["review_score"].mean()
    review_dist = df["review_score"].value_counts().sort_index()
    review_str = ", ".join([f"{k}★: {v:,}" for k, v in review_dist.items()])

    # Delivery
    on_time = df["is_on_time"].mean() * 100 if "is_on_time" in df.columns else 0
    avg_delivery = df["delivery_days"].mean() if "delivery_days" in df.columns else 0

    # Payment methods
    pay_types = df["payment_type"].value_counts()
    pay_str = ", ".join([f"{t}: {c:,}" for t, c in pay_types.head(4).items()])

    # Monthly trend (last 6 months)
    monthly = (
        df.set_index("order_purchase_timestamp")
        .resample("ME")["payment_value"]
        .sum()
        .tail(6)
    )
    trend_str = ", ".join(
        [f"{d.strftime('%Y-%m')}: R${v:,.0f}" for d, v in monthly.items()]
    )

    return f"""OLIST E-COMMERCE DATA SUMMARY:
Period: {date_min} to {date_max}
Total Revenue: R${total_rev:,.0f} | Orders: {total_orders:,} | Customers: {total_customers:,}
Top Categories: {top5_cats}
Top States: {top5_states}
Reviews: avg {avg_review:.1f}/5.0 — {review_str}
Delivery: {on_time:.1f}% on-time, avg {avg_delivery:.1f} days
Payments: {pay_str}
Monthly Revenue (last 6m): {trend_str}"""


def chat_with_data(user_message: str, data_summary: str, history: list) -> str:
    """Send user message with data context to Gemini."""
    if not _GEMINI_AVAILABLE or _client is None:
        return _fallback_chat(user_message, data_summary)

    # Build conversation contents
    contents = [
        {"role": "user", "parts": [{"text": f"{SYSTEM_PROMPT}\n\n{data_summary}"}]},
        {"role": "model", "parts": [{"text": "Understood. I'm ready to answer questions about the Olist dashboard data."}]},
    ]

    # Add conversation history
    for msg in history:
        contents.append({
            "role": "user" if msg["role"] == "user" else "model",
            "parts": [{"text": msg["content"]}],
        })

    # Add current message
    contents.append({"role": "user", "parts": [{"text": user_message}]})

    try:
        response = _client.models.generate_content(
            model=_MODEL_NAME,
            contents=contents,
        )
        return response.text
    except Exception as e:
        print(f"[gemini] API error: {e}")
        return _fallback_chat(user_message, data_summary, api_configured=True)


def _fallback_chat(user_message: str, data_summary: str, api_configured: bool = False) -> str:
    """Simple keyword-based responses when Gemini is unavailable."""
    msg = user_message.lower()

    # Handle greetings
    if any(w in msg for w in ["hello", "hi", "hey", "مرحبا", "اهلا", "أهلا", "سلام"]):
        if api_configured:
            return (
                "👋 Hi! I hit a temporary rate limit. Try again in a few seconds!\n\n"
                "In the meantime, ask me about: revenue, categories, states, reviews, delivery, or payments."
            )
        return (
            "👋 Hi! I'm running in basic mode right now.\n\n"
            "Ask me about: revenue, categories, states, reviews, delivery, or payments."
        )

    lines = data_summary.split("\n")
    summary_dict = {}
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

    if any(w in msg for w in ["revenue", "sales", "إيراد", "مبيعات", "ايراد"]):
        return f"📊 {summary_dict.get('revenue_line', 'Revenue data not available.')}"
    elif any(w in msg for w in ["category", "categories", "product", "كاتيجوري", "منتج"]):
        return f"🏷️ {summary_dict.get('categories_line', 'Category data not available.')}"
    elif any(w in msg for w in ["state", "region", "geo", "ولاية", "منطقة"]):
        return f"📍 {summary_dict.get('states_line', 'State data not available.')}"
    elif any(w in msg for w in ["review", "rating", "satisfaction", "تقييم"]):
        return f"⭐ {summary_dict.get('reviews_line', 'Review data not available.')}"
    elif any(w in msg for w in ["delivery", "shipping", "توصيل", "شحن"]):
        return f"🚚 {summary_dict.get('delivery_line', 'Delivery data not available.')}"
    elif any(w in msg for w in ["payment", "pay", "دفع"]):
        return f"💳 {summary_dict.get('payments_line', 'Payment data not available.')}"
    else:
        hint = "\n⏳ Gemini rate-limited — try again shortly!" if api_configured else ""
        return (
            "🤖 I can answer questions about: revenue, categories, states, "
            f"reviews, delivery, and payments. Try asking about one of these!{hint}"
        )
