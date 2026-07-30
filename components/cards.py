"""
cards.py
--------
Small presentational helpers for KPI cards used across pages.
Kept as pure functions (no callbacks) so they're trivial to test and
reuse - each page just calls kpi_card(...) with fresh numbers.
"""

from dash import html
import dash_bootstrap_components as dbc


def kpi_card(
    title: str,
    value: str,
    icon_class: str,
    accent: str = "primary",
    subtitle: str | None = None,
) -> dbc.Col:
    """A single KPI stat card.

    Parameters
    ----------
    title: label shown above the number, e.g. "Average Exam Score"
    value: the big number/string, e.g. "67.2"
    icon_class: a Bootstrap Icons class, e.g. "bi-mortarboard"
    accent: one of "primary", "success", "warning", "info" - controls
        the icon badge color via CSS classes defined in style.css
    subtitle: optional small helper text under the value
    """
    return dbc.Col(
        html.Div(
            [
                html.Div(
                    html.I(className=f"bi {icon_class}"),
                    className=f"kpi-icon kpi-icon-{accent}",
                ),
                html.Div(
                    [
                        html.P(title, className="kpi-title"),
                        html.H3(value, className="kpi-value"),
                        html.P(subtitle, className="kpi-subtitle") if subtitle else None,
                    ],
                    className="kpi-text",
                ),
            ],
            className="kpi-card",
        ),
        xs=12,
        sm=6,
        lg=3,
        className="kpi-col",
    )


def insight_card(icon_class: str, text: str, accent: str = "info") -> html.Div:
    """A single row in the 'Automatic Insights' list."""
    return html.Div(
        [
            html.I(className=f"bi {icon_class} insight-icon insight-icon-{accent}"),
            html.Span(text, className="insight-text"),
        ],
        className="insight-item",
    )


def empty_state(message: str = "No data available for the selected filters.") -> html.Div:
    """Shown instead of a chart/table when a filter combination yields
    zero rows, so the app never shows a blank confusing chart."""
    return html.Div(
        [
            html.I(className="bi bi-inbox empty-state-icon"),
            html.P(message, className="empty-state-text"),
        ],
        className="empty-state",
    )
