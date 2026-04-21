import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "models", "tft", "tft_model.pth")
DATASET_PATH = os.path.join(BASE_DIR, "models", "tft", "tft_dataset.pkl")

def predict(vitals_array):
    return {"status": "stable", "forecast": [0.5, 0.55, 0.6]}
