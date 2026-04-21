import os

import joblib
import pandas as pd
from sklearn.ensemble import IsolationForest

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "models", "edge", "edge_model.pkl")
DATA_PATH = os.path.join(BASE_DIR, "data", "processed_vitals_full.csv")


def train_edge_model():
    print("Loading data...")

    df = pd.read_csv(DATA_PATH)

    # Remove non-feature columns before training.
    features = [col for col in df.columns if col not in ["patient_id", "time_idx"]]
    X = df[features]

    print("Training Isolation Forest...")

    model = IsolationForest(
        n_estimators=100,
        contamination=0.05,
        random_state=42,
    )
    model.fit(X)

    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    joblib.dump(model, MODEL_PATH)

    print("[OK] Edge model trained and saved")


def load_edge_model():
    if not os.path.exists(MODEL_PATH):
        print("Model not found. Training...")
        train_edge_model()

    model = joblib.load(MODEL_PATH)
    print("[OK] Edge model loaded")
    return model


edge_model = load_edge_model()


def predict_edge(vitals_array):
    """
    vitals_array = [heart_rate, temp, resp_rate]
    """

    score = edge_model.decision_function([vitals_array])[0]
    label = edge_model.predict([vitals_array])[0]

    # Convert label: -1 means anomaly.
    label = 1 if label == -1 else 0

    return {
        "score": float(score),
        "anomaly": label,
    }


def predict(vitals_array):
    result = predict_edge(vitals_array)
    result["label"] = "anomaly" if result["anomaly"] == 1 else "normal"
    return result
