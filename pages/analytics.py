"""
pages/analytics.py
-------------------
Deeper statistical view: correlation heatmap of numeric features, a
selectable box plot across categorical factors, and the ML model's
feature-importance ranking. IDs are prefixed "an-".
"""

from __future__ import annotations

import dash
import plotly.express as px
from dash import Input, Output, callback, dcc, html
import dash_bootstrap_components as dbc

from components.cards import empty_state
from utils.chart_theme import apply_theme, empty_figure
from utils.data_loader import CATEGORICAL_COLUMNS, NUMERIC_COLUMNS, load_clean_data
from utils.ml_utils import ARTIFACTS, get_feature_importance

dash.register_page(__name__, path="/analytics", name="Analytics", order=1)

_CATEGORY_OPTIONS = [
    {"label": c.replace("_", " "), "value": c} for c in CATEGORICAL_COLUMNS
]


def layout():
    return html.Div(
        [
            html.Div(
                [
                    html.H2("Analytics", className="page-title"),
                    html.P(
                        "Statistical relationships between student factors and exam performance.",
                        className="page-subtitle",
                    ),
                ],
                className="page-header",
            ),
            dbc.Row(
                [
                    dbc.Col(dcc.Graph(id="an-correlation-heatmap", figure=_correlation_figure()), lg=6),
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.Div(
                                        [
                                            html.I(className="bi bi-bar-chart-steps"),
                                            html.Span("Score by Category"),
                                        ],
                                        className="filter-panel-title",
                                    ),
                                    dcc.Dropdown(
                                        id="an-category-select",
                                        options=_CATEGORY_OPTIONS,
                                        value="Parental_Involvement",
                                        clearable=False,
                                        className="filter-dropdown mb-2",
                                    ),
                                    dcc.Graph(id="an-category-boxplot"),
                                ]
                            ),
                            className="filter-panel h-100",
                        ),
                        lg=6,
                    ),
                ],
                className="g-3",
            ),
            dbc.Row(
                [
                    dbc.Col(dcc.Graph(id="an-feature-importance", figure=_feature_importance_figure()), lg=6),
                    dbc.Col(dcc.Graph(id="an-scatter-previous"), lg=6),
                ],
                className="g-3 mt-1",
            ),
        ]
    )


def _correlation_figure():
    df = load_clean_data()
    if df.empty:
        return empty_figure()
    corr = df[NUMERIC_COLUMNS + ["Exam_Score"]].corr().round(2)
    fig = px.imshow(
        corr,
        text_auto=True,
        color_continuous_scale="RdBu_r",
        zmin=-1,
        zmax=1,
        aspect="auto",
    )
    return apply_theme(fig, title="Correlation Between Numeric Factors", height=420)


def _feature_importance_figure():
    importance_df = get_feature_importance()
    if importance_df.empty:
        return empty_figure("Feature importance unavailable - model not trained yet.")
    top = importance_df.head(10).sort_values("Importance")
    fig = px.bar(
        top,
        x="Importance",
        y="Feature",
        orientation="h",
    )
    return apply_theme(fig, title="What Predicts Exam Score Most? (ML Model)", height=420)


@callback(
    Output("an-category-boxplot", "figure"),
    Input("an-category-select", "value"),
)
def update_category_boxplot(category):
    df = load_clean_data()
    if df.empty or not category:
        return empty_figure()
    fig = px.box(
        df,
        x=category,
        y="Exam_Score",
        color=category,
        points=False,
        labels={category: category.replace("_", " "), "Exam_Score": "Exam Score"},
    )
    fig.update_layout(showlegend=False)
    return apply_theme(fig, title=f"Exam Score by {category.replace('_', ' ')}")


@callback(
    Output("an-scatter-previous", "figure"),
    Input("an-category-select", "value"),
)
def update_previous_scores_scatter(_category):
    df = load_clean_data()
    if df.empty:
        return empty_figure()
    fig = px.scatter(
        df,
        x="Previous_Scores",
        y="Exam_Score",
        trendline="ols",
        opacity=0.4,
        labels={"Previous_Scores": "Previous Scores", "Exam_Score": "Exam Score"},
    )
    return apply_theme(fig, title="Previous Scores vs. Current Exam Score")
