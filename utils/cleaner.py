"""
utils/cleaner.py
Extra cleaning helpers and the shared chart layout template.
Imported by all page modules.
"""

import pandas as pd

from dash import html
from dash_iconify import DashIconify


def tooltip(text: str) -> html.Span:
    """Returns a CSS-driven info tooltip icon."""
    return html.Span(
        [
            DashIconify(icon="ph:info", width=16),
            html.Span(text, className="tooltip-text"),
        ],
        className="tooltip-container",
    )


# ── Plotly chart template (apply to EVERY figure) ────────────────────────────
CHART_LAYOUT = dict(
    paper_bgcolor="#13172A",
    plot_bgcolor="#0B0E17",
    font=dict(family="Inter, sans-serif", color="#E2E8F0", size=12),
    xaxis=dict(
        gridcolor="#252D47",
        linecolor="#252D47",
        tickfont=dict(color="#4B5A7A", family="Inter, sans-serif", size=11),
        zeroline=False,
    ),
    yaxis=dict(
        gridcolor="#252D47",
        linecolor="#252D47",
        tickfont=dict(color="#4B5A7A", family="Inter, sans-serif", size=11),
        zeroline=False,
    ),
    margin=dict(l=40, r=20, t=20, b=40),
    legend=dict(
        bgcolor="rgba(0,0,0,0)",
        font=dict(color="#94A3B8", family="Inter, sans-serif", size=11),
        bordercolor="rgba(0,0,0,0)",
    ),
    colorway=[
        "#38BDF8",
        "#A78BFA",
        "#34D399",
        "#FBBF24",
        "#F87171",
        "#22D3EE",
        "#818CF8",
    ],
    hoverlabel=dict(
        bgcolor="#1A1F35",
        bordercolor="#252D47",
        font=dict(family="Inter, sans-serif", color="#E2E8F0", size=12),
    ),
)


def apply_chart_layout(fig, title: str = "", height: int = 320):
    """Apply the standard dark-theme layout to a Plotly figure."""
    update = dict(**CHART_LAYOUT, height=height)
    if title:
        update["title"] = dict(
            text=title,
            font=dict(family="Plus Jakarta Sans, sans-serif", size=14, color="#E2E8F0"),
            x=0,
            xanchor="left",
        )
        update["margin"]["t"] = 44
    fig.update_layout(**update)
    return fig


# ── Data helpers ──────────────────────────────────────────────────────────────


def filter_by_date(df: pd.DataFrame, start: str, end: str) -> pd.DataFrame:
    """Slice master DataFrame to a date range (inclusive)."""
    mask = (df["order_purchase_timestamp"] >= pd.Timestamp(start)) & (
        df["order_purchase_timestamp"] <= pd.Timestamp(end)
    )
    return df.loc[mask].copy()


def format_brl(value: float) -> str:
    """Format a number as Brazilian Real."""
    if pd.isna(value):
        return "R$ —"
    if value >= 1_000_000:
        return f"R$ {value/1_000_000:.1f}M"
    if value >= 1_000:
        return f"R$ {value/1_000:.1f}K"
    return f"R$ {value:,.0f}"


def stars(rating: float) -> str:
    """Convert a 1–5 rating to star emoji string."""
    full = int(round(rating))
    full = max(1, min(5, full))
    return "★" * full + "☆" * (5 - full)


def pct(value: float, decimals: int = 1) -> str:
    """Format a 0–1 fraction as percentage string."""
    return f"{value * 100:.{decimals}f}%"
