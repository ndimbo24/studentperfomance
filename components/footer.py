"""footer.py - simple app-wide footer."""

from datetime import datetime

from dash import html


def render_footer() -> html.Footer:
    return html.Footer(
        html.P(
            f"\u00a9 {datetime.now().year} EduAnalytics \u2014 Student Performance "
            "Dashboard. Built with Dash & Plotly.",
            className="footer-text",
        ),
        className="app-footer",
    )
