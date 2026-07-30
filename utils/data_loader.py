"""
data_loader.py
---------------
Central data-access layer for the Student Performance Dashboard.

Responsibilities:
    * Load the raw CSV exactly once (cached).
    * Clean the data (missing values, duplicates, dtype fixes).
    * Expose small helper functions used across every page so that no
      page ever talks to the raw CSV directly.

Keeping all data logic in one module means every page/callback sees an
identical, already-cleaned DataFrame - this avoids subtle bugs where
one page filters NaNs and another doesn't.
"""

from __future__ import annotations

import functools
import logging
import os

import pandas as pd

logger = logging.getLogger(__name__)

# Path to the CSV, resolved relative to this file so the app works
# regardless of the working directory it is launched from.
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(_BASE_DIR, "data", "StudentPerformanceFactors.csv")

# Columns that are categorical (object/string) in the raw dataset.
CATEGORICAL_COLUMNS = [
    "Parental_Involvement",
    "Access_to_Resources",
    "Extracurricular_Activities",
    "Motivation_Level",
    "Internet_Access",
    "Family_Income",
    "Teacher_Quality",
    "School_Type",
    "Peer_Influence",
    "Learning_Disabilities",
    "Parental_Education_Level",
    "Distance_from_Home",
    "Gender",
]

# Columns that are numeric in the raw dataset.
NUMERIC_COLUMNS = [
    "Hours_Studied",
    "Attendance",
    "Sleep_Hours",
    "Previous_Scores",
    "Tutoring_Sessions",
    "Physical_Activity",
]

TARGET_COLUMN = "Exam_Score"

ALL_FEATURE_COLUMNS = NUMERIC_COLUMNS + CATEGORICAL_COLUMNS


@functools.lru_cache(maxsize=1)
def load_raw_data() -> pd.DataFrame:
    """Read the CSV from disk exactly once per process.

    Returns an empty, correctly-columned DataFrame instead of raising if
    the file is missing, so the rest of the app can render a friendly
    "no data" state instead of crashing on import.
    """
    if not os.path.exists(DATA_PATH):
        logger.error("Dataset not found at %s", DATA_PATH)
        return pd.DataFrame(columns=ALL_FEATURE_COLUMNS + [TARGET_COLUMN])

    try:
        df = pd.read_csv(DATA_PATH)
    except Exception:  # noqa: BLE001 - we want to catch any parse error
        logger.exception("Failed to read dataset at %s", DATA_PATH)
        return pd.DataFrame(columns=ALL_FEATURE_COLUMNS + [TARGET_COLUMN])

    return df


@functools.lru_cache(maxsize=1)
def load_clean_data() -> pd.DataFrame:
    """Return a cleaned copy of the dataset.

    Cleaning steps:
        1. Drop exact duplicate rows.
        2. Impute missing categorical values with the column mode.
        3. Impute missing numeric values with the column median.
        4. Coerce dtypes so numeric columns are numeric and categorical
           columns are clean strings (no leading/trailing whitespace).
        5. Clip a small number of implausible values (e.g. Exam_Score
           over 100) is intentionally NOT done - outliers are kept and
           surfaced in Analytics instead of being silently hidden.
    """
    df = load_raw_data().copy()
    if df.empty:
        return df

    before_rows = len(df)
    df = df.drop_duplicates()
    duplicates_removed = before_rows - len(df)
    if duplicates_removed:
        logger.info("Removed %d duplicate rows", duplicates_removed)

    for col in CATEGORICAL_COLUMNS:
        if col not in df.columns:
            continue
        df[col] = df[col].astype("string").str.strip()
        if df[col].isnull().any():
            mode = df[col].mode(dropna=True)
            fill_value = mode.iloc[0] if not mode.empty else "Unknown"
            df[col] = df[col].fillna(fill_value)

    for col in NUMERIC_COLUMNS + [TARGET_COLUMN]:
        if col not in df.columns:
            continue
        df[col] = pd.to_numeric(df[col], errors="coerce")
        if df[col].isnull().any():
            df[col] = df[col].fillna(df[col].median())

    df = df.reset_index(drop=True)
    return df


def get_categorical_options(column: str) -> list[str]:
    """Sorted unique values for a categorical column, for dropdowns."""
    df = load_clean_data()
    if column not in df.columns:
        return []
    return sorted(df[column].dropna().unique().tolist())


def get_numeric_range(column: str) -> tuple[float, float]:
    """(min, max) for a numeric column, used to size sliders."""
    df = load_clean_data()
    if column not in df.columns or df.empty:
        return (0.0, 1.0)
    return (float(df[column].min()), float(df[column].max()))


def filter_dataframe(
    df: pd.DataFrame,
    gender: list[str] | None = None,
    school_type: list[str] | None = None,
    family_income: list[str] | None = None,
    parental_involvement: list[str] | None = None,
    hours_studied_range: tuple[float, float] | None = None,
    attendance_range: tuple[float, float] | None = None,
) -> pd.DataFrame:
    """Apply the shared set of dashboard filters to a DataFrame.

    Every argument is optional; an empty/None filter is a no-op so pages
    can reuse this function with only the filters they expose.
    """
    if df.empty:
        return df

    filtered = df

    def _isin(frame: pd.DataFrame, col: str, values) -> pd.DataFrame:
        if values and col in frame.columns:
            return frame[frame[col].isin(values)]
        return frame

    filtered = _isin(filtered, "Gender", gender)
    filtered = _isin(filtered, "School_Type", school_type)
    filtered = _isin(filtered, "Family_Income", family_income)
    filtered = _isin(filtered, "Parental_Involvement", parental_involvement)

    if hours_studied_range and "Hours_Studied" in filtered.columns:
        lo, hi = hours_studied_range
        filtered = filtered[
            (filtered["Hours_Studied"] >= lo) & (filtered["Hours_Studied"] <= hi)
        ]

    if attendance_range and "Attendance" in filtered.columns:
        lo, hi = attendance_range
        filtered = filtered[
            (filtered["Attendance"] >= lo) & (filtered["Attendance"] <= hi)
        ]

    return filtered


def compute_kpis(df: pd.DataFrame) -> dict:
    """Compute the headline KPI numbers shown as cards on the Dashboard."""
    if df.empty:
        return {
            "total_students": 0,
            "avg_exam_score": 0.0,
            "avg_hours_studied": 0.0,
            "avg_attendance": 0.0,
        }
    return {
        "total_students": int(len(df)),
        "avg_exam_score": round(float(df["Exam_Score"].mean()), 1),
        "avg_hours_studied": round(float(df["Hours_Studied"].mean()), 1),
        "avg_attendance": round(float(df["Attendance"].mean()), 1),
    }
