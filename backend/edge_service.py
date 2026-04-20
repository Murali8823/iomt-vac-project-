from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Iterable

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest


BASE_DIR = Path(__file__).resolve().parent.parent
DATASET_PATH = BASE_DIR / "data" / "processed_vitals_full.csv"
MODEL_PATH = BASE_DIR / "models" / "edge" / "edge_model.pkl"
STATUS_PATH = BASE_DIR / "project_status.json"

MODEL_CONFIG = {
    "contamination": 0.05,
    "n_estimators": 100,
    "random_state": 42,
}

_MODEL_BUNDLE: dict[str, Any] | None = None


def _select_feature_frame(dataframe: pd.DataFrame) -> pd.DataFrame:
    numeric_frame = dataframe.select_dtypes(include=[np.number]).copy()
    excluded_columns = {
        "time_idx",
        "timestamp",
        "index",
        "row_id",
        "target",
        "label",
        "anomaly",
    }
    feature_columns = [
        column for column in numeric_frame.columns if column.lower() not in excluded_columns
    ]
    return numeric_frame[feature_columns].dropna()


def _load_dataset() -> pd.DataFrame | None:
    if not DATASET_PATH.exists():
        print(
            f"Error: dataset not found at '{DATASET_PATH}'. "
            "Expected data/processed_vitals_full.csv."
        )
        return None

    dataframe = pd.read_csv(DATASET_PATH)
    numeric_frame = _select_feature_frame(dataframe)

    if numeric_frame.empty:
        print(
            f"Error: dataset '{DATASET_PATH}' does not contain usable numeric rows "
            "for edge model training."
        )
        return None

    return numeric_frame


def _update_project_status(edge_ready: bool) -> None:
    status_payload: dict[str, Any] = {}

    if STATUS_PATH.exists():
        try:
            with STATUS_PATH.open("r", encoding="utf-8") as status_file:
                existing = json.load(status_file)
                if isinstance(existing, dict):
                    status_payload = existing
        except (json.JSONDecodeError, OSError):
            status_payload = {}

    status_payload["edge_ready"] = edge_ready

    with STATUS_PATH.open("w", encoding="utf-8") as status_file:
        json.dump(status_payload, status_file, indent=2)
        status_file.write("\n")


def train_and_save_model() -> dict[str, Any] | None:
    dataset = _load_dataset()
    if dataset is None:
        return None

    start_time = time.perf_counter()

    model = IsolationForest(
        contamination=MODEL_CONFIG["contamination"],
        n_estimators=MODEL_CONFIG["n_estimators"],
        random_state=MODEL_CONFIG["random_state"],
        n_jobs=-1,
    )
    model.fit(dataset)

    training_time_seconds = time.perf_counter() - start_time

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    model_bundle = {
        "model": model,
        "feature_columns": list(dataset.columns),
        "training_time_seconds": training_time_seconds,
        "dataset_path": str(DATASET_PATH),
    }
    joblib.dump(model_bundle, MODEL_PATH)

    _update_project_status(edge_ready=True)
    print(f"Edge model trained in {training_time_seconds:.4f} seconds")
    print(f"Edge model saved to '{MODEL_PATH}'")

    global _MODEL_BUNDLE
    _MODEL_BUNDLE = model_bundle
    return model_bundle


def _load_model_bundle() -> dict[str, Any] | None:
    global _MODEL_BUNDLE

    if _MODEL_BUNDLE is not None:
        return _MODEL_BUNDLE

    if MODEL_PATH.exists():
        _MODEL_BUNDLE = joblib.load(MODEL_PATH)
        return _MODEL_BUNDLE

    return train_and_save_model()


def _normalize_input(
    vitals_array: Iterable[float] | np.ndarray | pd.Series | pd.DataFrame,
    feature_columns: list[str],
) -> np.ndarray:
    if isinstance(vitals_array, pd.DataFrame):
        if list(vitals_array.columns) != feature_columns:
            missing = [column for column in feature_columns if column not in vitals_array.columns]
            extra = [column for column in vitals_array.columns if column not in feature_columns]
            details = []
            if missing:
                details.append(f"missing columns: {missing}")
            if extra:
                details.append(f"unexpected columns: {extra}")
            raise ValueError("Input DataFrame columns do not match trained model features: " + ", ".join(details))
        frame = vitals_array[feature_columns]
        return frame.to_numpy(dtype=float)

    if isinstance(vitals_array, pd.Series):
        values = vitals_array.to_numpy(dtype=float)
    else:
        values = np.asarray(vitals_array, dtype=float)

    if values.ndim == 1:
        if values.shape[0] != len(feature_columns):
            raise ValueError(
                f"Expected {len(feature_columns)} values, received {values.shape[0]}."
            )
        values = values.reshape(1, -1)
    elif values.ndim == 2:
        if values.shape[1] != len(feature_columns):
            raise ValueError(
                f"Expected {len(feature_columns)} features per row, received {values.shape[1]}."
            )
    else:
        raise ValueError("Input must be a 1D or 2D array-like structure.")

    return values


def predict(vitals_array: Iterable[float] | np.ndarray | pd.Series | pd.DataFrame) -> dict[str, Any]:
    model_bundle = _load_model_bundle()
    if model_bundle is None:
        raise FileNotFoundError(
            f"Unable to load or train edge model because dataset '{DATASET_PATH}' is unavailable."
        )

    model: IsolationForest = model_bundle["model"]
    feature_columns: list[str] = model_bundle["feature_columns"]
    inputs = _normalize_input(vitals_array, feature_columns)
    input_frame = pd.DataFrame(inputs, columns=feature_columns)

    scores = -model.score_samples(input_frame)
    predictions = model.predict(input_frame)
    labels = np.where(predictions == -1, "anomaly", "normal")

    results = [
        {
            "anomaly_score": float(score),
            "label": str(label),
        }
        for score, label in zip(scores, labels, strict=False)
    ]

    if len(results) == 1:
        return results[0]

    return {"predictions": results}


if __name__ == "__main__":
    train_and_save_model()
