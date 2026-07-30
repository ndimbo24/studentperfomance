"""
app.py
------
Application entry point.

Sets up the Dash app with `use_pages=True`, which auto-discovers every
module in `pages/` that calls `dash.register_page(...)`. The layout
below wraps the routed page content with the shared sidebar, header,
and footer so those persist across navigation without re-rendering.

Run locally:
    python app.py

Run in production (see Procfile):
    gunicorn app:server
"""

from __future__ import annotations

import logging

import dash
from dash import Dash, Input, Output, State, html, dcc
import dash_bootstrap_components as dbc

from components.footer import render_footer
from components.header import render_header
from components.sidebar import render_sidebar

logging.basicConfig(level=logging.INFO)

app = Dash(
    __name__,
    use_pages=True,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.css",
    ],
    suppress_callback_exceptions=True,
    title="Student Performance Dashboard",
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"}
    ],
)

# Exposed for WSGI servers (gunicorn app:server)
server = app.server

app.layout = html.Div(
    [
        dcc.Store(id="shared-filtered-data", storage_type="session"),
        render_sidebar(),
        html.Div(
            [
                render_header(),
                html.Div(dash.page_container, className="page-content"),
                render_footer(),
            ],
            className="main-column",
        ),
    ],
    className="app-shell",
)


@app.callback(
    Output("sidebar", "className"),
    Input("sidebar-toggle", "n_clicks"),
    State("sidebar", "className"),
    prevent_initial_call=True,
)
def toggle_sidebar(n_clicks, current_class):
    """Mobile-only sidebar toggle. On desktop the sidebar is always
    visible via CSS; this only matters below the 992px breakpoint."""
    current_class = current_class or "sidebar"
    if "sidebar-open" in current_class:
        return "sidebar"
    return "sidebar sidebar-open"


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8050)
