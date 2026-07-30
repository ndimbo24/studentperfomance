"""
pages/reports.py
------------------
Professional report download page.

Lets users download PDF, Excel, and CSV reports based on the currently
filtered dataset. The same filter controls as the Dashboard are provided
so users can refine the report scope before exporting.
"""

from __future__ import annotations

import dash
from dash import Input, Output, State, callback, dcc, html
import dash_bootstrap_components as dbc
import pandas as pd

from components.cards import empty_state, kpi_card
from components.filter_panel import render_filter_panel

from utils.data_loader import (
    compute_kpis,
    filter_dataframe,
    load_clean_data,
)
from utils.report_generator import (
    build_report_insights,
    generate_excel_report,
    generate_pdf_report,
    generate_csv_report,
)

dash.register_page(__name__, path="/reports", name="Reports", order=1.5)


def layout():
    return html.Div(
        [
            html.Div(
                [
                    html.H2("Reports", className="page-title"),
                    html.P(
                        "Download professional reports based on the filtered dataset.",
                        className="page-subtitle",
                    ),
                ],
                className="page-header",
            ),
            render_filter_panel(),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.Div(
                                        [
                                            html.I(className="bi bi-file-earmark-pdf me-2"),
                                            html.Span("PDF Report"),
                                        ],
                                        className="filter-panel-title",
                                    ),
                                    html.P(
                                        "Professional multi-page report with cover page, KPIs, "
                                        "charts, insights, and recommendations.",
                                        className="text-muted mb-3",
                                    ),
                                    dbc.Button(
                                        [
                                            html.I(className="bi bi-download me-2"),
                                            "Download PDF Report",
                                        ],
                                        id="rep-download-pdf-btn",
                                        color="danger",
                                        className="w-100",
                                    ),
                                ]
                            ),
                            className="filter-panel h-100",
                        ),
                        lg=4,
                    ),
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.Div(
                                        [
                                            html.I(className="bi bi-file-earmark-excel me-2"),
                                            html.Span("Excel Report"),
                                        ],
                                        className="filter-panel-title",
                                    ),
                                    html.P(
                                        "Formatted workbook with raw data, statistics, KPIs, "
                                        "and correlation matrix.",
                                        className="text-muted mb-3",
                                    ),
                                    dbc.Button(
                                        [
                                            html.I(className="bi bi-download me-2"),
                                            "Download Excel Report",
                                        ],
                                        id="rep-download-excel-btn",
                                        color="success",
                                        className="w-100",
                                    ),
                                ]
                            ),
                            className="filter-panel h-100",
                        ),
                        lg=4,
                    ),
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.Div(
                                        [
                                            html.I(className="bi bi-file-earmark-arrow-down me-2"),
                                            html.Span("CSV Report"),
                                        ],
                                        className="filter-panel-title",
                                    ),
                                    html.P(
                                        "Raw filtered dataset exported as comma-separated values.",
                                        className="text-muted mb-3",
                                    ),
                                    dbc.Button(
                                        [
                                            html.I(className="bi bi-download me-2"),
                                            "Download CSV Report",
                                        ],
                                        id="rep-download-csv-btn",
                                        color="primary",
                                        className="w-100",
                                    ),
                                ]
                            ),
                            className="filter-panel h-100",
                        ),
                        lg=4,
                    ),
                ],
                className="g-3 mt-1",
            ),
            dbc.Row(id="rep-kpi-row", className="g-3 mt-1"),
            dbc.Card(
                dbc.CardBody(
                    [
                        html.Div(
                            [
                                html.I(className="bi bi-lightbulb"),
                                html.Span("Report Preview - Automatic Insights"),
                            ],
                            className="filter-panel-title",
                        ),
                        html.Div(id="rep-insights"),
                    ]
                ),
                className="filter-panel mt-3",
            ),
            dcc.Download(id="rep-download-pdf"),
            dcc.Download(id="rep-download-excel"),
            dcc.Download(id="rep-download-csv"),
        ]
    )


@callback(
    Output("rep-kpi-row", "children"),
    Output("rep-insights", "children"),
    Input("dash-filter-gender", "value"),
    Input("dash-filter-school-type", "value"),
    Input("dash-filter-income", "value"),
    Input("dash-filter-involvement", "value"),
    Input("dash-filter-hours", "value"),
    Input("dash-filter-attendance", "value"),
)
def update_report_preview(gender, school_type, income, involvement, hours_range, attendance_range):
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
            "Highest Score",
            f"{float(filtered['Exam_Score'].max()):.1f}" if not filtered.empty else "N/A",
            "bi-trophy-fill",
            accent="warning",
        ),
        kpi_card(
            "Lowest Score",
            f"{float(filtered['Exam_Score'].min()):.1f}" if not filtered.empty else "N/A",
            "bi-arrow-down-circle-fill",
            accent="info",
        ),
    ]

    if filtered.empty:
        insights = empty_state("No students match the selected filters.")
        return kpi_cards, insights

    insight_texts = build_report_insights(filtered)
    insights = [
        insight_item(text, accent="info") for text in insight_texts
    ]

    return kpi_cards, insights


def insight_item(text: str, accent: str = "info") -> html.Div:
    """Wrap a plain insight string in the same style used on the dashboard."""
    return html.Div(
        [
            html.I(className="bi bi-graph-up-arrow insight-icon insight-icon-" + accent),
            html.Span(text, className="insight-text"),
        ],
        className="insight-item",
    )


@callback(
    Output("rep-download-pdf", "data"),
    Input("rep-download-pdf-btn", "n_clicks"),
    State("dash-filter-gender", "value"),
    State("dash-filter-school-type", "value"),
    State("dash-filter-income", "value"),
    State("dash-filter-involvement", "value"),
    State("dash-filter-hours", "value"),
    State("dash-filter-attendance", "value"),
    prevent_initial_call=True,
)
def download_pdf(n_clicks, gender, school_type, income, involvement, hours_range, attendance_range):
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

    if filtered.empty:
        return dcc.send_bytes(
            b"No data available for the selected filters.",
            "student_performance_report.pdf",
        )

    filters = {
        "gender": gender or [],
        "school_type": school_type or [],
        "family_income": income or [],
        "parental_involvement": involvement or [],
        "hours_studied_range": list(hours_range) if hours_range else None,
        "attendance_range": list(attendance_range) if attendance_range else None,
    }
    insights = build_report_insights(filtered)
    pdf_bytes = generate_pdf_report(filtered, filters, df, insights)
    return dcc.send_bytes(pdf_bytes, "student_performance_report.pdf")


@callback(
    Output("rep-download-excel", "data"),
    Input("rep-download-excel-btn", "n_clicks"),
    State("dash-filter-gender", "value"),
    State("dash-filter-school-type", "value"),
    State("dash-filter-income", "value"),
    State("dash-filter-involvement", "value"),
    State("dash-filter-hours", "value"),
    State("dash-filter-attendance", "value"),
    prevent_initial_call=True,
)
def download_excel(n_clicks, gender, school_type, income, involvement, hours_range, attendance_range):
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

    if filtered.empty:
        return dcc.send_bytes(
            b"No data available for the selected filters.",
            "student_performance_report.xlsx",
        )

    filters = {
        "gender": gender or [],
        "school_type": school_type or [],
        "family_income": income or [],
        "parental_involvement": involvement or [],
        "hours_studied_range": list(hours_range) if hours_range else None,
        "attendance_range": list(attendance_range) if attendance_range else None,
    }
    excel_bytes = generate_excel_report(filtered, filters, df)
    return dcc.send_bytes(excel_bytes, "student_performance_report.xlsx")


@callback(
    Output("rep-download-csv", "data"),
    Input("rep-download-csv-btn", "n_clicks"),
    State("dash-filter-gender", "value"),
    State("dash-filter-school-type", "value"),
    State("dash-filter-income", "value"),
    State("dash-filter-involvement", "value"),
    State("dash-filter-hours", "value"),
    State("dash-filter-attendance", "value"),
    prevent_initial_call=True,
)
def download_csv(n_clicks, gender, school_type, income, involvement, hours_range, attendance_range):
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
    csv_bytes = generate_csv_report(filtered)
    return dcc.send_bytes(csv_bytes, "student_performance_report.csv")
