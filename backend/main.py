import json
from pathlib import Path
from typing import Any, List

import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

try:
    from . import cnn_service, edge_service, tft_service
except ImportError:
    import cnn_service
    import edge_service
    import tft_service

app = FastAPI(title="IoMT AI System Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent.parent
STATUS_PATH = BASE_DIR / "project_status.json"
DATA_PATH = BASE_DIR / "data" / "processed_vitals_full.csv"

def get_status() -> dict:
    if not STATUS_PATH.exists():
        return {}
    try:
        with STATUS_PATH.open("r") as f:
            return json.load(f)
    except Exception:
        return {}

def update_status(key: str, value: Any):
    status = get_status()
    status[key] = value
    with STATUS_PATH.open("w") as f:
        json.dump(status, f, indent=2)

@app.on_event("startup")
async def startup_event():
    update_status("backend_ready", True)

@app.get("/devices")
async def get_devices() -> List[dict]:
    status = get_status()
    
    edge_ready = status.get("edge_ready", False)
    tft_ready = status.get("tft_ready", False)
    cnn_ready = status.get("cnn_ready", False)

    if not DATA_PATH.exists():
        return []

    # Load data and get latest record for each device
    df = pd.read_csv(DATA_PATH)
    latest_vitals = df.sort_values("time_idx").groupby("patient_id").last().reset_index()
    
    # Take first 20 for performance in response
    devices_to_process = latest_vitals.head(20)

    results = []
    for _, row in devices_to_process.iterrows():
        device_id = str(row["patient_id"])
        heart_rate = float(row["heart_rate"])
        temp = float(row["temp"])
        time_idx = float(row["time_idx"])
        resp_rate = float(row.get("resp_rate", 0.0))
        
        # Prepare inputs for models (4 features based on processed_vitals_full.csv numeric columns)
        vitals_input = [time_idx, heart_rate, temp, resp_rate]
        
        edge_status = "N/A"
        if edge_ready:
            try:
                edge_res = edge_service.predict(vitals_input)
                edge_status = edge_res.get("label", "unknown")
            except Exception:
                edge_status = "error"

        tft_status = "N/A"
        if tft_ready:
            try:
                tft_res = tft_service.predict(vitals_input)
                tft_status = tft_res.get("status", "unknown")
            except Exception:
                tft_status = "error"

        cnn_status = "N/A"
        if cnn_ready:
            try:
                cnn_res = cnn_service.predict(vitals_input)
                cnn_status = cnn_res.get("label", "unknown")
            except Exception:
                cnn_status = "error"

        # Simple final status logic
        final_status = "Healthy"
        if edge_status == "anomaly" or tft_status == "warning" or cnn_status == "abnormal":
            final_status = "Requires Attention"

        results.append({
            "device_id": device_id,
            "heart_rate": heart_rate,
            "temp": temp,
            "edge_status": edge_status,
            "tft_status": tft_status,
            "cnn_status": cnn_status,
            "final_status": final_status
        })

    return results

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
