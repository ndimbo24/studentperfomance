"""pages/about.py - static project/dataset info page."""

from __future__ import annotations

import dash
from dash import html
import dash_bootstrap_components as dbc

from utils.data_loader import load_clean_data
from utils.ml_utils import ARTIFACTS

dash.register_page(__name__, path="/about", name="About", order=4)

_TECH_STACK = [
    ("Dash", "Web application framework"),
    ("Plotly", "Interactive charting library"),
    ("Pandas", "Data loading & cleaning"),
    ("Scikit-learn", "Machine learning model"),
    ("Joblib", "Model persistence"),
    ("Dash Bootstrap Components", "UI layout & styling"),
]


def layout():
    df = load_clean_data()
    model_status = "Ready" if ARTIFACTS.is_ready() else "Not trained"
    model_color = "success" if ARTIFACTS.is_ready() else "warning"

    return html.Div(
        [
            html.Div(
                [
                    html.H2("About", className="page-title"),
                    html.P("Project background, dataset, and technology.", className="page-subtitle"),
                ],
                className="page-header",
            ),
            dbc.Card(
                dbc.CardBody(
                    [
                        html.H5("Student Performance Dashboard", className="mb-2"),
                        html.P(
                            "An analytics dashboard exploring how study habits, attendance, "
                            "family background, and school factors relate to exam performance. "
                            "Built to help educators and analysts spot patterns and estimate "
                            "outcomes for individual students.",
                        ),
                        html.Div(
                            [
                                html.Span("Dataset size: ", className="fw-semibold"),
                                html.Span(f"{len(df):,} student records, {df.shape[1]} columns"),
                            ],
                            className="mb-1",
                        ),
                        html.Div(
                            [
                                html.Span("Prediction model status: ", className="fw-semibold"),
                                dbc.Badge(model_status, color=model_color),
                            ],
                        ),
                    ]
                ),
                className="filter-panel mb-3",
            ),
            dbc.Card(
                dbc.CardBody(
                    [
                        html.H5("Technology Stack", className="mb-3"),
                        html.Ul(
                            [
                                html.Li([html.B(name), f" \u2014 {desc}"])
                                for name, desc in _TECH_STACK
                            ]
                        ),
                    ]
                ),
                className="filter-panel mb-3",
            ),
            dbc.Card(
                dbc.CardBody(
                    [
                        html.H5("Disclaimer", className="mb-2"),
                        html.P(
                            "Predictions are statistical estimates based on historical survey "
                            "data and should support, not replace, professional educational "
                            "judgment.",
                            className="mb-0 text-muted",
                        ),
                    ]
                ),
                className="filter-panel",
            ),
        ]
    )
