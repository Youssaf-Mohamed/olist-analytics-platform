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


CHART_THEME = {
    "dark": {
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(0,0,0,0)",
        "font_color": "#E2E8F0",
        "tick_color": "#7F8EA8",
        "gridcolor": "rgba(148, 163, 184, 0.16)",
        "legend_color": "#94A3B8",
        "hover_bg": "#11182B",
        "hover_border": "#27314D",
        "title_color": "#F8FAFC",
        "colorway": [
            "#38BDF8",
            "#A78BFA",
            "#34D399",
            "#FBBF24",
            "#F87171",
            "#22D3EE",
            "#818CF8",
        ],
    },
    "light": {
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(0,0,0,0)",
        "font_color": "#0F172A",
        "tick_color": "#64748B",
        "gridcolor": "rgba(148, 163, 184, 0.26)",
        "legend_color": "#475569",
        "hover_bg": "#FFFFFF",
        "hover_border": "#CBD5E1",
        "title_color": "#0F172A",
        "colorway": [
            "#0284C7",
            "#7C3AED",
            "#059669",
            "#D97706",
            "#DC2626",
            "#0F766E",
            "#4F46E5",
        ],
    },
}


def get_chart_theme(theme: str = "dark") -> dict:
    return CHART_THEME["light" if theme == "light" else "dark"].copy()


def apply_chart_layout(fig, title: str = "", height: int = 320, theme: str = "dark"):
    """Apply the shared Plotly layout using the active UI theme."""
    palette = get_chart_theme(theme)
    update = dict(
        paper_bgcolor=palette["paper_bgcolor"],
        plot_bgcolor=palette["plot_bgcolor"],
        font=dict(
            family="Inter, sans-serif",
            color=palette["font_color"],
            size=12,
        ),
        xaxis=dict(
            gridcolor=palette["gridcolor"],
            linecolor=palette["gridcolor"],
            tickfont=dict(
                color=palette["tick_color"],
                family="Inter, sans-serif",
                size=11,
            ),
            zeroline=False,
        ),
        yaxis=dict(
            gridcolor=palette["gridcolor"],
            linecolor=palette["gridcolor"],
            tickfont=dict(
                color=palette["tick_color"],
                family="Inter, sans-serif",
                size=11,
            ),
            zeroline=False,
        ),
        margin=dict(l=40, r=20, t=20, b=40),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(
                color=palette["legend_color"],
                family="Inter, sans-serif",
                size=11,
            ),
            bordercolor="rgba(0,0,0,0)",
        ),
        colorway=palette["colorway"],
        hoverlabel=dict(
            bgcolor=palette["hover_bg"],
            bordercolor=palette["hover_border"],
            font=dict(
                family="Inter, sans-serif",
                color=palette["font_color"],
                size=12,
            ),
        ),
        height=height,
    )
    if title:
        update["title"] = dict(
            text=title,
            font=dict(
                family="Plus Jakarta Sans, sans-serif",
                size=14,
                color=palette["title_color"],
            ),
            x=0,
            xanchor="left",
        )
        update["margin"]["t"] = 44
    fig.update_layout(**update)
    return fig


def filter_by_date_column(
    df: pd.DataFrame, column: str, start: str, end: str
) -> pd.DataFrame:
    """Slice a DataFrame to an inclusive calendar-date range using any datetime column."""
    start_ts = pd.Timestamp(start)
    end_exclusive = pd.Timestamp(end) + pd.Timedelta(days=1)
    mask = (df[column] >= start_ts) & (df[column] < end_exclusive)
    return df.loc[mask].copy()


def filter_by_date(df: pd.DataFrame, start: str, end: str) -> pd.DataFrame:
    """Slice a DataFrame to an inclusive calendar-date range."""
    return filter_by_date_column(df, "order_purchase_timestamp", start, end)


def format_brl(value: float) -> str:
    """Format a number as Brazilian Real."""
    if pd.isna(value):
        return "R$ -"
    if value >= 1_000_000:
        return f"R$ {value/1_000_000:.1f}M"
    if value >= 1_000:
        return f"R$ {value/1_000:.1f}K"
    return f"R$ {value:,.0f}"


def stars(rating: float) -> str:
    """Convert a 1-5 rating to star string."""
    full = int(round(rating))
    full = max(1, min(5, full))
    return "*" * full + "-" * (5 - full)


def pct(value: float, decimals: int = 1) -> str:
    """Format a 0-1 fraction as percentage string."""
    return f"{value * 100:.{decimals}f}%"
