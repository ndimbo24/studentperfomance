"""
train_model.py
---------------
Offline training script for the Exam Score prediction model.

Run this manually whenever the dataset changes:

    python models/train_model.py

It produces three artifacts in this same folder:
    model.joblib     - trained RandomForestRegressor
    scaler.joblib     - StandardScaler fit on the numeric features
    encoders.joblib   - dict of {column: LabelEncoder} for categoricals,
                        plus the exact feature column order used at
                        train time so prediction can reproduce it.

This file is intentionally NOT imported by the Dash app - the app only
loads the saved artifacts (see utils/ml_utils.py). This keeps app
startup fast and keeps training reproducible/versioned separately from
serving.
"""

from __future__ import annotations

import os
import sys

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.data_loader import (  # noqa: E402
    CATEGORICAL_COLUMNS,
    NUMERIC_COLUMNS,
    TARGET_COLUMN,
    load_clean_data,
)

MODEL_DIR = os.path.dirname(os.path.abspath(__file__))


def train() -> None:
    df = load_clean_data()
    if df.empty:
        raise RuntimeError(
            "No data available to train on - check data/StudentPerformanceFactors.csv"
        )

    feature_columns = NUMERIC_COLUMNS + CATEGORICAL_COLUMNS
    X = df[feature_columns].copy()
    y = df[TARGET_COLUMN].copy()

    # Encode categoricals with per-column LabelEncoders. Saved so the
    # prediction pipeline applies the *identical* mapping at inference
    # time instead of re-fitting on whatever the user typed.
    encoders: dict[str, LabelEncoder] = {}
    for col in CATEGORICAL_COLUMNS:
        le = LabelEncoder()
        X[col] = le.fit_transform(X[col].astype(str))
        encoders[col] = le

    # Scale numeric columns only - keeps encoded categoricals as clean
    # integer codes, which tree-based models handle natively.
    scaler = StandardScaler()
    X[NUMERIC_COLUMNS] = scaler.fit_transform(X[NUMERIC_COLUMNS])

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = RandomForestRegressor(
        n_estimators=300,
        max_depth=12,
        min_samples_leaf=3,
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    mae = mean_absolute_error(y_test, preds)
    r2 = r2_score(y_test, preds)
    print(f"Test MAE: {mae:.3f}")
    print(f"Test R^2: {r2:.3f}")

    joblib.dump(model, os.path.join(MODEL_DIR, "model.joblib"))
    joblib.dump(scaler, os.path.join(MODEL_DIR, "scaler.joblib"))
    joblib.dump(
        {
            "encoders": encoders,
            "feature_columns": feature_columns,
            "numeric_columns": NUMERIC_COLUMNS,
            "categorical_columns": CATEGORICAL_COLUMNS,
            "test_mae": mae,
            "test_r2": r2,
        },
        os.path.join(MODEL_DIR, "encoders.joblib"),
    )
    print(f"Saved model artifacts to {MODEL_DIR}")


if __name__ == "__main__":
    train()
