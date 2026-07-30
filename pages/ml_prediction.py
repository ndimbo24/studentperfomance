"""
pages/ml_prediction.py
-----------------------
Form-driven exam score prediction using the pre-trained RandomForest
model (see models/train_model.py + utils/ml_utils.py). IDs prefixed
"ml-". The prediction pipeline here mirrors training exactly: same
column order, same LabelEncoders, same StandardScaler - all loaded
from the saved joblib artifacts rather than re-derived, so there is no
train/serve mismatch.
"""

from __future__ import annotations

import dash
from dash import Input, Output, State, callback, dcc, html
import dash_bootstrap_components as dbc

from utils.data_loader import (
    CATEGORICAL_COLUMNS,
    NUMERIC_COLUMNS,
    get_categorical_options,
    get_numeric_range,
)
from utils.ml_utils import ARTIFACTS, predict_exam_score

dash.register_page(__name__, path="/predict", name="ML Prediction", order=3)

_NUMERIC_LABELS = {
    "Hours_Studied": ("Hours Studied / week", "bi-clock"),
    "Attendance": ("Attendance (%)", "bi-calendar-check"),
    "Sleep_Hours": ("Sleep Hours / night", "bi-moon-stars"),
    "Previous_Scores": ("Previous Scores", "bi-journal-check"),
    "Tutoring_Sessions": ("Tutoring Sessions / month", "bi-person-video3"),
    "Physical_Activity": ("Physical Activity (hrs/wk)", "bi-bicycle"),
}

_CATEGORICAL_LABELS = {c: c.replace("_", " ") for c in CATEGORICAL_COLUMNS}


def _numeric_inputs():
    fields = []
    for col in NUMERIC_COLUMNS:
        label, icon = _NUMERIC_LABELS.get(col, (col.replace("_", " "), "bi-input-cursor"))
        lo, hi = get_numeric_range(col)
        default = round((lo + hi) / 2)
        fields.append(
            dbc.Col(
                [
                    html.Label(
                        [html.I(className=f"bi {icon} me-1"), label],
                        className="filter-label",
                    ),
                    dbc.Input(
                        id={"type": "ml-numeric-input", "index": col},
                        type="number",
                        min=lo,
                        max=hi * 1.5 if hi else 100,
                        value=default,
                        className="ml-input",
                    ),
                ],
                md=4,
                className="mb-3",
            )
        )
    return fields


def _categorical_inputs():
    fields = []
    for col in CATEGORICAL_COLUMNS:
        options = get_categorical_options(col)
        default = options[0] if options else None
        fields.append(
            dbc.Col(
                [
                    html.Label(_CATEGORICAL_LABELS[col], className="filter-label"),
                    dcc.Dropdown(
                        id={"type": "ml-categorical-input", "index": col},
                        options=options,
                        value=default,
                        clearable=False,
                        className="filter-dropdown",
                    ),
                ],
                md=4,
                className="mb-3",
            )
        )
    return fields


def layout():
    if not ARTIFACTS.is_ready():
        return html.Div(
            [
                html.H2("ML Prediction", className="page-title"),
                dbc.Alert(
                    [
                        html.I(className="bi bi-exclamation-triangle me-2"),
                        "The prediction model isn't available. Run ",
                        html.Code("python models/train_model.py"),
                        " to generate it, then reload this page.",
                    ],
                    color="warning",
                    className="mt-3",
                ),
            ]
        )

    accuracy_note = ""
    if ARTIFACTS.test_mae is not None and ARTIFACTS.test_r2 is not None:
        accuracy_note = (
            f"Model validation: MAE {ARTIFACTS.test_mae:.2f} points, "
            f"R\u00b2 {ARTIFACTS.test_r2:.2f} on held-out test data."
        )

    return html.Div(
        [
            html.Div(
                [
                    html.H2("ML Prediction", className="page-title"),
                    html.P(
                        "Enter a student's profile to predict their exam score.",
                        className="page-subtitle",
                    ),
                ],
                className="page-header",
            ),
            dbc.Card(
                dbc.CardBody(
                    [
                        html.H5("Academic & Lifestyle Factors", className="mb-3"),
                        dbc.Row(_numeric_inputs(), className="g-3"),
                        html.Hr(),
                        html.H5("Background Factors", className="mb-3"),
                        dbc.Row(_categorical_inputs(), className="g-3"),
                        html.Div(
                            [
                                dbc.Button(
                                    [html.I(className="bi bi-cpu me-2"), "Predict Exam Score"],
                                    id="ml-predict-btn",
                                    color="primary",
                                    size="lg",
                                    className="mt-3",
                                    n_clicks=0,
                                ),
                            ],
                            className="text-center",
                        ),
                    ]
                ),
                className="filter-panel",
            ),
            html.Div(id="ml-result", className="mt-3"),
            html.P(accuracy_note, className="ml-accuracy-note mt-2") if accuracy_note else None,
        ]
    )


@callback(
    Output("ml-result", "children"),
    Input("ml-predict-btn", "n_clicks"),
    State({"type": "ml-numeric-input", "index": dash.ALL}, "value"),
    State({"type": "ml-numeric-input", "index": dash.ALL}, "id"),
    State({"type": "ml-categorical-input", "index": dash.ALL}, "value"),
    State({"type": "ml-categorical-input", "index": dash.ALL}, "id"),
    prevent_initial_call=True,
)
def run_prediction(n_clicks, numeric_values, numeric_ids, categorical_values, categorical_ids):
    input_values = {}
    for value, id_dict in zip(numeric_values, numeric_ids):
        input_values[id_dict["index"]] = value
    for value, id_dict in zip(categorical_values, categorical_ids):
        input_values[id_dict["index"]] = value

    result = predict_exam_score(input_values)

    if not result["success"]:
        return dbc.Alert(
            [html.I(className="bi bi-x-circle me-2"), result["error"]],
            color="danger",
        )

    score = result["prediction"]
    if score >= 80:
        tier, color, icon = "Excellent", "success", "bi-emoji-smile-fill"
    elif score >= 65:
        tier, color, icon = "Good", "info", "bi-emoji-neutral-fill"
    else:
        tier, color, icon = "Needs Support", "warning", "bi-emoji-frown-fill"

    return dbc.Card(
        dbc.CardBody(
            [
                html.I(className=f"bi {icon} ml-result-icon text-{color}"),
                html.H2(f"{score}", className="ml-result-score"),
                html.P("Predicted Exam Score", className="ml-result-label"),
                dbc.Badge(tier, color=color, className="ml-result-badge"),
            ],
            className="text-center",
        ),
        className="filter-panel ml-result-card",
    )
