"""
header.py
---------
Top header bar: page context, live "as of" timestamp, and a mobile
sidebar toggle button. Kept intentionally content-light - each page is
responsible for its own title beneath the header.
"""

from datetime import datetime

from dash import html
import dash_bootstrap_components as dbc


def render_header() -> html.Div:
    return html.Div(
        [
            dbc.Button(
                html.I(className="bi bi-list"),
                id="sidebar-toggle",
                className="sidebar-toggle-btn",
                n_clicks=0,
            ),
            html.Div(
                [
                    html.Span("Student Performance Dashboard", className="header-title"),
                ],
                className="header-title-wrap",
            ),
            html.Div(
                [
                    html.I(className="bi bi-clock header-clock-icon"),
                    html.Span(
                        datetime.now().strftime("Data as of %B %d, %Y"),
                        className="header-timestamp",
                    ),
                ],
                className="header-meta",
            ),
        ],
        className="app-header",
    )
