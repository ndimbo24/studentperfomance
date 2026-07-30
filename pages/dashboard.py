"""
pages/dashboard.py
-------------------
Landing page: KPI cards, global-style filters, and the most important
overview charts + automatic text insights.

All IDs on this page are prefixed with "dash-" so they never collide
with IDs on other pages (Dash requires globally unique component IDs
across the whole multi-page app).
"""

from __future__ import annotations

import dash
import pandas as pd
from dash import Input, Output, callback, dcc, html
import dash_bootstrap_components as dbc
import plotly.express as px

from components.cards import empty_state, insight_card, kpi_card
from components.filter_panel import render_filter_panel
from utils.chart_theme import apply_theme, empty_figure
from utils.data_loader import (
    compute_kpis,
    filter_dataframe,
    get_categorical_options,
    get_numeric_range,
    load_clean_data,
)

dash.register_page(__name__, path="/", name="Dashboard", order=0)


def layout():
    return html.Div(
        [
            html.Div(
                [
                    html.H2("Dashboard", className="page-title"),
                    html.P(
                        "Overview of student performance across the full survey population.",
                        className="page-subtitle",
                    ),
                ],
                className="page-header",
            ),
            render_filter_panel(),
            dbc.Row(id="dash-kpi-row", className="g-3 mt-1"),
            dbc.Row(
                [
                    dbc.Col(dcc.Graph(id="dash-chart-distribution"), lg=6),
                    dbc.Col(dcc.Graph(id="dash-chart-hours-vs-score"), lg=6),
                ],
                className="g-3 mt-1",
            ),
            dbc.Row(
                [
                    dbc.Col(dcc.Graph(id="dash-chart-by-involvement"), lg=6),
                    dbc.Col(dcc.Graph(id="dash-chart-by-income"), lg=6),
                ],
                className="g-3 mt-1",
            ),
            dbc.Card(
                dbc.CardBody(
                    [
                        html.Div(
                            [html.I(className="bi bi-lightbulb"), html.Span("Automatic Insights")],
                            className="filter-panel-title",
                        ),
                        html.Div(id="dash-insights"),
                    ]
                ),
                className="filter-panel mt-3",
            ),
        ]
    )


@callback(
    Output("dash-kpi-row", "children"),
    Output("dash-chart-distribution", "figure"),
    Output("dash-chart-hours-vs-score", "figure"),
    Output("dash-chart-by-involvement", "figure"),
    Output("dash-chart-by-income", "figure"),
    Output("dash-insights", "children"),
    Output("shared-filtered-data", "data"),
    Input("dash-filter-gender", "value"),
    Input("dash-filter-school-type", "value"),
    Input("dash-filter-income", "value"),
    Input("dash-filter-involvement", "value"),
    Input("dash-filter-hours", "value"),
    Input("dash-filter-attendance", "value"),
)
def update_dashboard(gender, school_type, income, involvement, hours_range, attendance_range):
    df = load_clean_data()
    filtered = filter_dataframe(
        df,
        gender=gender,
        school_type=school_type,
        family_income=income,
        parental_involvement=involvement,
        hours_studied_range=tuple(hours_range) if hours_range else None,
        attendance_range=tuple(attendance_range) if attendance_range else None,
    )

    kpis = compute_kpis(filtered)
    kpi_cards = [
        kpi_card(
            "Total Students",
            f"{kpis['total_students']:,}",
            "bi-people-fill",
            accent="primary",
        ),
        kpi_card(
            "Average Exam Score",
            f"{kpis['avg_exam_score']}",
            "bi-mortarboard-fill",
            accent="success",
        ),
        kpi_card(
            "Average Hours Studied",
            f"{kpis['avg_hours_studied']} hrs/wk",
            "bi-clock-fill",
            accent="warning",
        ),
        kpi_card(
            "Average Attendance",
            f"{kpis['avg_attendance']}%",
            "bi-calendar-check-fill",
            accent="info",
        ),
    ]

    if filtered.empty:
        empty = empty_figure()
        insights = empty_state("No students match the selected filters.")
        filter_state = {
            "gender": gender or [],
            "school_type": school_type or [],
            "family_income": income or [],
            "parental_involvement": involvement or [],
            "hours_studied_range": list(hours_range) if hours_range else None,
            "attendance_range": list(attendance_range) if attendance_range else None,
        }
        return kpi_cards, empty, empty, empty, empty, insights, filter_state

    fig_dist = px.histogram(
        filtered,
        x="Exam_Score",
        nbins=25,
        labels={"Exam_Score": "Exam Score"},
    )
    fig_dist.update_traces(marker_line_width=0)
    apply_theme(fig_dist, title="Exam Score Distribution")

    fig_scatter = px.scatter(
        filtered,
        x="Hours_Studied",
        y="Exam_Score",
        color="Parental_Involvement",
        opacity=0.6,
        labels={"Hours_Studied": "Hours Studied / week", "Exam_Score": "Exam Score"},
        hover_data=["Attendance", "Sleep_Hours"],
    )
    apply_theme(fig_scatter, title="Hours Studied vs. Exam Score")

    by_involvement = (
        filtered.groupby("Parental_Involvement", observed=True)["Exam_Score"]
        .mean()
        .reindex(["Low", "Medium", "High"])
        .dropna()
        .reset_index()
    )
    fig_involvement = px.bar(
        by_involvement,
        x="Parental_Involvement",
        y="Exam_Score",
        text_auto=".1f",
        labels={"Parental_Involvement": "Parental Involvement", "Exam_Score": "Avg. Exam Score"},
    )
    apply_theme(fig_involvement, title="Average Score by Parental Involvement")

    by_income = (
        filtered.groupby("Family_Income", observed=True)["Exam_Score"]
        .mean()
        .reindex(["Low", "Medium", "High"])
        .dropna()
        .reset_index()
    )
    fig_income = px.bar(
        by_income,
        x="Family_Income",
        y="Exam_Score",
        text_auto=".1f",
        color_discrete_sequence=["#22C55E"],
        labels={"Family_Income": "Family Income", "Exam_Score": "Avg. Exam Score"},
    )
    apply_theme(fig_income, title="Average Score by Family Income")

    insights = _build_insights(filtered)

    filter_state = {
        "gender": gender or [],
        "school_type": school_type or [],
        "family_income": income or [],
        "parental_involvement": involvement or [],
        "hours_studied_range": list(hours_range) if hours_range else None,
        "attendance_range": list(attendance_range) if attendance_range else None,
    }

    return kpi_cards, fig_dist, fig_scatter, fig_involvement, fig_income, insights, filter_state


def _build_insights(df) -> list:
    """Generate a handful of plain-English, data-driven insight rows."""
    items = []

    corr = df[["Hours_Studied", "Exam_Score"]].corr().iloc[0, 1]
    direction = "positively" if corr > 0 else "negatively"
    items.append(
        insight_card(
            "bi-graph-up-arrow",
            f"Hours studied is {direction} correlated with exam score "
            f"(r = {corr:.2f}).",
            accent="primary",
        )
    )

    by_inv = df.groupby("Parental_Involvement", observed=True)["Exam_Score"].mean()
    if len(by_inv) > 1:
        best = by_inv.idxmax()
        worst = by_inv.idxmin()
        gap = by_inv.max() - by_inv.min()
        items.append(
            insight_card(
                "bi-people",
                f"Students with '{best}' parental involvement score "
                f"{gap:.1f} points higher on average than those with '{worst}'.",
                accent="success",
            )
        )

    top_attendance = df["Attendance"].quantile(0.75)
    high_att_avg = df.loc[df["Attendance"] >= top_attendance, "Exam_Score"].mean()
    low_att_avg = df.loc[df["Attendance"] < top_attendance, "Exam_Score"].mean()
    if pd.notna(high_att_avg) and pd.notna(low_att_avg):
        items.append(
            insight_card(
                "bi-calendar-check",
                f"Students in the top attendance quartile average "
                f"{high_att_avg - low_att_avg:.1f} points higher than the rest.",
                accent="warning",
            )
        )

    if (df["Exam_Score"] > 95).any():
        n_top = int((df["Exam_Score"] > 95).sum())
        items.append(
            insight_card(
                "bi-star-fill",
                f"{n_top} student(s) scored above 95, suggesting a small "
                "high-performing outlier group worth investigating.",
                accent="info",
            )
        )

    return items if items else [empty_state("Not enough data to generate insights.")]
