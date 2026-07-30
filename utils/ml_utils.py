"""
ml_utils.py
-----------
Serving-side machine learning helpers.

This module ONLY loads pre-trained artifacts produced by
`models/train_model.py` - it never trains at request time. That keeps
predictions fast and guarantees every prediction uses the exact same
encoders/scaler that were fit during training (no train/serve skew).
"""

from __future__ import annotations

import logging
import os

import joblib
import pandas as pd

logger = logging.getLogger(__name__)

_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_DIR = os.path.join(_BASE_DIR, "models")

MODEL_PATH = os.path.join(MODEL_DIR, "model.joblib")
SCALER_PATH = os.path.join(MODEL_DIR, "scaler.joblib")
ENCODERS_PATH = os.path.join(MODEL_DIR, "encoders.joblib")


class PredictionArtifacts:
    """Lazily-loaded, cached bundle of everything needed to predict.

    Loading is wrapped in try/except so a missing or corrupt model
    directory degrades to `is_ready() == False` instead of crashing the
    whole Dash app on import.
    """

    def __init__(self) -> None:
        self.model = None
        self.scaler = None
        self.encoders: dict = {}
        self.feature_columns: list[str] = []
        self.numeric_columns: list[str] = []
        self.categorical_columns: list[str] = []
        self.test_mae: float | None = None
        self.test_r2: float | None = None
        self._load()

    def _load(self) -> None:
        try:
            self.model = joblib.load(MODEL_PATH)
            self.scaler = joblib.load(SCALER_PATH)
            meta = joblib.load(ENCODERS_PATH)
            self.encoders = meta["encoders"]
            self.feature_columns = meta["feature_columns"]
            self.numeric_columns = meta["numeric_columns"]
            self.categorical_columns = meta["categorical_columns"]
            self.test_mae = meta.get("test_mae")
            self.test_r2 = meta.get("test_r2")
        except FileNotFoundError:
            logger.warning(
                "Model artifacts not found in %s - run models/train_model.py",
                MODEL_DIR,
            )
        except Exception:  # noqa: BLE001
            logger.exception("Failed to load model artifacts")

    def is_ready(self) -> bool:
        return self.model is not None and self.scaler is not None and bool(
            self.encoders
        )


# Single shared instance - loaded once when the app process starts.
ARTIFACTS = PredictionArtifacts()


def predict_exam_score(input_values: dict) -> dict:
    """Predict an exam score from a dict of raw feature values.

    `input_values` keys must match the training feature columns
    (see ARTIFACTS.feature_columns). Unknown categorical values that
    were never seen during training are safely mapped to the most
    common training category instead of raising, so a slightly odd
    user input never crashes the app.

    Returns a dict with either:
        {"success": True, "prediction": float}
        {"success": False, "error": str}
    """
    if not ARTIFACTS.is_ready():
        return {"success": False, "error": "Model is not available. Please train the model first."}

    try:
        # Build a plain dict of fully-numeric encoded values first, then
        # construct the DataFrame in one shot. Mutating cells of an
        # already-typed mixed DataFrame (e.g. assigning an int into a
        # pandas StringDtype column) raises under pandas' modern strict
        # string dtype, so we deliberately avoid that pattern here.
        encoded_row: dict = {}

        for col in ARTIFACTS.categorical_columns:
            if col not in input_values or input_values[col] in (None, ""):
                return {"success": False, "error": f"Missing value for '{col}'."}
            encoder = ARTIFACTS.encoders[col]
            raw_value = str(input_values[col])
            known_classes = set(encoder.classes_)
            if raw_value not in known_classes:
                # Fall back gracefully to the first known class rather
                # than raising a ValueError from LabelEncoder.
                logger.warning(
                    "Unseen category '%s' for column '%s' - falling back to '%s'",
                    raw_value,
                    col,
                    encoder.classes_[0],
                )
                raw_value = encoder.classes_[0]
            encoded_row[col] = int(encoder.transform([raw_value])[0])

        for col in ARTIFACTS.numeric_columns:
            if col not in input_values or input_values[col] in (None, ""):
                return {"success": False, "error": f"Missing value for '{col}'."}
            numeric_value = pd.to_numeric(pd.Series([input_values[col]]), errors="coerce").iloc[0]
            if pd.isna(numeric_value):
                return {"success": False, "error": f"Invalid numeric value for '{col}'."}
            encoded_row[col] = float(numeric_value)

        df = pd.DataFrame([encoded_row], columns=ARTIFACTS.feature_columns)

        df[ARTIFACTS.numeric_columns] = ARTIFACTS.scaler.transform(
            df[ARTIFACTS.numeric_columns]
        )

        prediction = float(ARTIFACTS.model.predict(df)[0])
        prediction = max(0.0, min(100.0, prediction))
        return {"success": True, "prediction": round(prediction, 1)}

    except Exception as exc:  # noqa: BLE001
        logger.exception("Prediction failed")
        return {"success": False, "error": f"Prediction failed: {exc}"}


def get_feature_importance() -> pd.DataFrame:
    """Return feature importances as a tidy DataFrame for charting."""
    if not ARTIFACTS.is_ready() or not hasattr(ARTIFACTS.model, "feature_importances_"):
        return pd.DataFrame(columns=["Feature", "Importance"])

    importances = ARTIFACTS.model.feature_importances_
    data = sorted(
        zip(ARTIFACTS.feature_columns, importances), key=lambda x: x[1], reverse=True
    )
    return pd.DataFrame(data, columns=["Feature", "Importance"])
