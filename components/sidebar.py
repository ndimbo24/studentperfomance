"""
sidebar.py
----------
Left-hand navigation sidebar, shared by every page via app.py's layout.

Uses `dash.page_registry` so nav links are generated automatically from
whatever pages are registered - adding a new page file to `pages/`
is enough for it to appear here, no manual edits needed.
"""

import dash
from dash import html
import dash_bootstrap_components as dbc

# Maps a page's module path to a Bootstrap icon class so each nav link
# gets a matching icon without hardcoding page order.
_ICONS = {
    "pages.dashboard": "bi-speedometer2",
    "pages.analytics": "bi-graph-up",
    "pages.explorer": "bi-table",
    "pages.ml_prediction": "bi-cpu",
    "pages.reports": "bi-file-earmark-text",
    "pages.about": "bi-info-circle",
}


def render_sidebar() -> html.Div:
    nav_links = []
    for page in dash.page_registry.values():
        icon_class = _ICONS.get(page["module"], "bi-circle")
        nav_links.append(
            dbc.NavLink(
                [
                    html.I(className=f"bi {icon_class} sidebar-icon"),
                    html.Span(page["name"], className="sidebar-label"),
                ],
                href=page["path"],
                active="exact",
                className="sidebar-link",
            )
        )

    return html.Div(
        [
            html.Div(
                [
                    html.I(className="bi bi-mortarboard-fill brand-icon"),
                    html.Span("EduAnalytics", className="brand-text"),
                ],
                className="sidebar-brand",
            ),
            html.Hr(className="sidebar-divider"),
            dbc.Nav(nav_links, vertical=True, pills=True, className="sidebar-nav"),
            html.Div(
                [
                    html.Hr(className="sidebar-divider"),
                    html.P(
                        "Student Performance Analytics",
                        className="sidebar-footer-text",
                    ),
                    html.P("v1.0.0", className="sidebar-footer-version"),
                ],
                className="sidebar-footer",
            ),
        ],
        className="sidebar",
        id="sidebar",
    )
