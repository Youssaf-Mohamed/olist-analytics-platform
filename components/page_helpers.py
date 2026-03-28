"""Shared wrappers for consistent page and chart layout structure."""

from __future__ import annotations

from dash import dcc, html


def page_section(children, *, style: dict | None = None, class_name: str | None = None):
    return dcc.Loading(
        html.Div(children, style=style, className=class_name),
        type="default",
        parent_className="page-section-loading",
    )


def chart_loading(child, *, overlay_style: dict | None = None):
    kwargs = {
        "type": "circle",
        "color": "#38BDF8",
        "parent_className": "chart-loading-wrapper",
    }
    if overlay_style is not None:
        kwargs["overlay_style"] = overlay_style
    return dcc.Loading(child, **kwargs)
