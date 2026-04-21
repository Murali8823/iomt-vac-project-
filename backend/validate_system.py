import os
import pickle
import sys

import joblib
import torch

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "models")

EDGE_MODEL_PATH = os.path.join(MODEL_DIR, "edge", "edge_model.pkl")
CNN_MODEL_PATH = os.path.join(MODEL_DIR, "cnn", "cnn_model.pth")
TFT_MODEL_PATH = os.path.join(MODEL_DIR, "tft", "tft_model.pth")
TFT_DATASET_PATH = os.path.join(MODEL_DIR, "tft", "tft_dataset.pkl")


def print_ok(message):
    print(f"[OK] {message}")


def print_fail(message):
    print(f"[FAIL] {message}")


def check_file(path):
    if not os.path.exists(path):
        print_fail(f"Missing file: {path}")
        return False
    return True


def load_torch_artifact(path):
    try:
        torch.load(path, map_location="cpu", weights_only=False)
    except TypeError:
        torch.load(path, map_location="cpu")


def load_tft_dataset(path):
    errors = []

    try:
        with open(path, "rb") as dataset_file:
            pickle.load(dataset_file)
        return
    except Exception as pickle_error:
        errors.append(f"pickle load failed: {pickle_error}")

        try:
            load_torch_artifact(path)
            return
        except Exception as torch_error:
            errors.append(f"torch load failed: {torch_error}")

        try:
            from pytorch_forecasting import TimeSeriesDataSet

            TimeSeriesDataSet.load(path)
            return
        except Exception as forecasting_error:
            errors.append(f"pytorch_forecasting load failed: {forecasting_error}")
            raise RuntimeError("; ".join(errors)) from forecasting_error


def main():
    file_checks = {
        "Edge model": EDGE_MODEL_PATH,
        "CNN model": CNN_MODEL_PATH,
        "TFT model": TFT_MODEL_PATH,
        "TFT dataset": TFT_DATASET_PATH,
    }

    all_present = True
    for _, path in file_checks.items():
        all_present = check_file(path) and all_present

    if not all_present:
        return 1

    try:
        joblib.load(EDGE_MODEL_PATH)
        print_ok("Edge model loaded")
    except Exception as exc:
        print_fail(f"Edge model failed to load: {exc}")
        return 1

    try:
        load_torch_artifact(CNN_MODEL_PATH)
        print_ok("CNN model loaded")
    except Exception as exc:
        print_fail(f"CNN model failed to load: {exc}")
        return 1

    try:
        load_tft_dataset(TFT_DATASET_PATH)
        print_ok("TFT dataset loaded")
    except Exception as exc:
        print_fail(f"TFT dataset failed to load: {exc}")
        return 1

    print_ok("All required model artifacts are present")
    return 0


if __name__ == "__main__":
    sys.exit(main())
