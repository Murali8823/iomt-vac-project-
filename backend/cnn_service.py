import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "models", "cnn", "cnn_model.pth")

def predict(vitals_array):
    return {"label": "normal", "score": 0.98}
