"""
pages/explorer.py
------------------
Searchable, sortable, filterable DataTable with CSV export. IDs are
prefixed "exp-". Filtering/sorting/pagination are handled natively by
dash_table (page_action='native', filter_action='native') so no
callback is required for basic interaction - only the CSV export uses
a callback (dcc.Download).
"""

from __future__ import annotations

import dash
from dash import Input, Output, State, callback, dcc, html, dash_table
import dash_bootstrap_components as dbc

from utils.data_loader import ALL_FEATURE_COLUMNS, TARGET_COLUMN, load_clean_data

dash.register_page(__name__, path="/explorer", name="Data Explorer", order=2)

_DISPLAY_COLUMNS = ALL_FEATURE_COLUMNS + [TARGET_COLUMN]


def layout():
    df = load_clean_data()
    columns = [{"name": c.replace("_", " "), "id": c} for c in _DISPLAY_COLUMNS if c in df.columns]

    return html.Div(
        [
            html.Div(
                [
                    html.H2("Data Explorer", className="page-title"),
                    html.P(
                        "Search, sort, and filter the full student dataset, then export your view.",
                        className="page-subtitle",
                    ),
                ],
                className="page-header",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        html.Span(
                            f"{len(df):,} total records",
                            className="explorer-record-count",
                        ),
                        md="auto",
                    ),
                    dbc.Col(
                        dbc.Button(
                            [html.I(className="bi bi-download me-2"), "Export CSV"],
                            id="exp-export-btn",
                            color="primary",
                            className="ms-auto",
                        ),
                        md="auto",
                        className="ms-auto",
                    ),
                ],
                className="mb-2 align-items-center",
                justify="between",
            ),
            dbc.Card(
                dbc.CardBody(
                    dash_table.DataTable(
                        id="exp-table",
                        columns=columns,
                        data=df.to_dict("records"),
                        page_action="native",
                        page_size=15,
                        sort_action="native",
                        filter_action="native",
                        style_table={"overflowX": "auto"},
                        style_header={
                            "backgroundColor": "#F8FAFC",
                            "fontWeight": "600",
                            "border": "none",
                            "borderBottom": "2px solid #E2E8F0",
                            "textAlign": "left",
                        },
                        style_cell={
                            "padding": "10px 14px",
                            "fontFamily": "'Inter', sans-serif",
                            "fontSize": "13px",
                            "border": "none",
                            "borderBottom": "1px solid #F1F5F9",
                            "textAlign": "left",
                        },
                        style_data_conditional=[
                            {
                                "if": {"row_index": "odd"},
                                "backgroundColor": "#FAFBFC",
                            }
                        ],
                        style_as_list_view=True,
                        export_format=None,
                    )
                ),
                className="filter-panel",
            ),
            dcc.Download(id="exp-download"),
        ]
    )


@callback(
    Output("exp-download", "data"),
    Input("exp-export-btn", "n_clicks"),
    State("exp-table", "derived_virtual_data"),
    prevent_initial_call=True,
)
def export_csv(n_clicks, filtered_rows):
    """Export exactly what the user currently sees (after their in-table
    search/filter/sort) rather than the full unfiltered dataset."""
    import pandas as pd

    if not filtered_rows:
        df = load_clean_data()
    else:
        df = pd.DataFrame(filtered_rows)

    return dcc.send_data_frame(df.to_csv, "student_performance_export.csv", index=False)
