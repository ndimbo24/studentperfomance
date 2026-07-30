"""
components/filter_panel.py
--------------------------
Shared dashboard filter panel used by both the Dashboard and Reports pages.
"""

from __future__ import annotations

import dash_bootstrap_components as dbc
from dash import dcc, html

from utils.data_loader import get_categorical_options, get_numeric_range


def render_filter_panel() -> dbc.Card:
    """Return the standard global filter panel."""
    hours_lo, hours_hi = get_numeric_range("Hours_Studied")
    att_lo, att_hi = get_numeric_range("Attendance")
    return dbc.Card(
        dbc.CardBody(
            [
                html.Div(
                    [html.I(className="bi bi-funnel"), html.Span("Filters")],
                    className="filter-panel-title",
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.Label("Gender", className="filter-label"),
                                dcc.Dropdown(
                                    id="dash-filter-gender",
                                    options=get_categorical_options("Gender"),
                                    multi=True,
                                    placeholder="All genders",
                                    className="filter-dropdown",
                                ),
                            ],
                            md=3,
                        ),
                        dbc.Col(
                            [
                                html.Label("School Type", className="filter-label"),
                                dcc.Dropdown(
                                    id="dash-filter-school-type",
                                    options=get_categorical_options("School_Type"),
                                    multi=True,
                                    placeholder="All school types",
                                    className="filter-dropdown",
                                ),
                            ],
                            md=3,
                        ),
                        dbc.Col(
                            [
                                html.Label("Family Income", className="filter-label"),
                                dcc.Dropdown(
                                    id="dash-filter-income",
                                    options=get_categorical_options("Family_Income"),
                                    multi=True,
                                    placeholder="All income levels",
                                    className="filter-dropdown",
                                ),
                            ],
                            md=3,
                        ),
                        dbc.Col(
                            [
                                html.Label("Parental Involvement", className="filter-label"),
                                dcc.Dropdown(
                                    id="dash-filter-involvement",
                                    options=get_categorical_options("Parental_Involvement"),
                                    multi=True,
                                    placeholder="All levels",
                                    className="filter-dropdown",
                                ),
                            ],
                            md=3,
                        ),
                    ],
                    className="g-3",
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.Label("Hours Studied (weekly)", className="filter-label"),
                                dcc.RangeSlider(
                                    id="dash-filter-hours",
                                    min=hours_lo,
                                    max=hours_hi,
                                    value=[hours_lo, hours_hi],
                                    tooltip={"placement": "bottom", "always_visible": False},
                                    className="filter-slider",
                                ),
                            ],
                            md=6,
                        ),
                        dbc.Col(
                            [
                                html.Label("Attendance (%)", className="filter-label"),
                                dcc.RangeSlider(
                                    id="dash-filter-attendance",
                                    min=att_lo,
                                    max=att_hi,
                                    value=[att_lo, att_hi],
                                    tooltip={"placement": "bottom", "always_visible": False},
                                    className="filter-slider",
                                ),
                            ],
                            md=6,
                        ),
                    ],
                    className="g-3 mt-1",
                ),
            ]
        ),
        className="filter-panel",
    )
