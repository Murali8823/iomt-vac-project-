# 🩺 VitalGuard AI: Real-Time IoMT Health Monitoring System

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![PyTorch](https://img.shields.io/badge/PyTorch-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white)](https://pytorch.org/)
[![Scikit-Learn](https://img.shields.io/badge/scikit_learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)

**VitalGuard AI** is a sophisticated, production-ready multi-model AI ecosystem designed to revolutionize patient monitoring in the Medical Internet of Things (IoMT) landscape. By integrating three distinct artificial intelligence architectures, the system provides a fail-safe, high-fidelity analysis of patient health in real-time.

---

## 📑 Table of Contents
1. [System Architecture](#-system-architecture)
2. [Deep Dive: The Tri-Model AI Engine](#-deep-dive-the-tri-model-ai-engine)
3. [Data Engineering & Pipeline](#-data-engineering--pipeline)
4. [How to Use & Quick Start](#-how-to-use--quick-start)
5. [API Specification](#-api-specification)
6. [Frontend & Real-Time Visualization](#-frontend--real-time-visualization)
7. [Deployment & Scaling](#-deployment--scaling)
8. [Research & Mathematical Foundation](#-research--mathematical-foundation)

---

## 🏗️ System Architecture

VitalGuard AI operates on a distributed intelligence model. Unlike traditional monitoring systems that rely on simple threshold alerts (e.g., "Heart rate > 100"), VitalGuard analyzes the *relationship* between multiple vitals and their historical context.

### The Logic Flow:
1.  **Ingestion:** The `Simulator` engine streams synthetic yet medically-accurate vitals from a high-resolution dataset.
2.  **Edge Processing:** Data is first hit by the Isolation Forest model to catch immediate physical anomalies.
3.  **Temporal Analysis:** The TFT model looks back at the last 24-48 hours of data to predict the next 6 hours, identifying "silent" degradations.
4.  **Diagnostic Cross-Check:** For high-risk flags, the system triggers the CNN-ResNet50 service to simulate the analysis of recent medical imaging (X-rays/MRIs).
5.  **Consensus Engine:** A weighted voting algorithm combines these outputs into a single "Health Score."

---

## 🤖 Deep Dive: The Tri-Model AI Engine

### 1. Edge Intelligence (Isolation Forest)
*   **Role:** Immediate Anomaly Detection.
*   **Logic:** Instead of modeling "normal" behavior, the Isolation Forest isolates anomalies. It builds random trees; anomalies are "easy" to isolate and thus have shorter path lengths in the trees.
*   **Parameters:**
    -   `n_estimators`: 100
    -   `contamination`: 0.05 (Optimized for medical sensitivity)
    -   `max_features`: Heart Rate, SpO2, Respiratory Rate, Blood Pressure.

### 2. Temporal Fusion Transformer (TFT)
*   **Role:** Long-term Trend Forecasting.
*   **Mechanism:** Uses multi-head attention to identify which past events (e.g., a spike in temperature 4 hours ago) are most relevant to current health.
*   **Capabilities:**
    -   Handles multi-horizon forecasting.
    -   Incorporates static metadata (Patient Age, History) and time-varying vitals.
    -   Provides "Quantile Forecasts" to show the uncertainty range of future vitals.

### 3. Diagnostic Vision (ResNet50)
*   **Role:** Image-Based Clinical Support.
*   **Transfer Learning:** Uses a ResNet50 backbone pre-trained on ImageNet and fine-tuned on a specialized Medical Imaging dataset.
*   **Implementation:** The service processes 224x224 RGB inputs, outputting probability scores across various diagnostic categories (e.g., Pneumonia, Cardiomegaly).

---

## 🧬 Data Engineering & Pipeline

VitalGuard's robustness comes from its data treatment. The system utilizes `Data_Entry_2017.csv` and `healthcare_iot_target_dataset.csv` to build a realistic patient profile database.

### Preprocessing Steps:
-   **Normalization:** Vitals are scaled using `StandardScaler` to ensure the CNN and TFT models don't over-index on high-magnitude numbers (like Heart Rate vs. Temperature).
-   **Windowing:** Data is transformed into sliding windows of 10-50 time steps for the TFT model.
-   **Synthetic Generation:** The `Simulator` uses Gaussian noise and trend-injection to mimic real-world sensor jitter and medical emergencies.

---

## 🛠️ How to Use & Quick Start

### 1. Start the AI Backend
Launch the FastAPI server which orchestrates the AI models and the IoT simulation:
```bash
python backend/main.py
```
*The server will start at `http://localhost:8000`.*

### 2. Access the Real-Time Dashboard
The dashboard is a static web interface that polls the backend. You can open it directly in your browser:
-   **Path:** `frontend/dashboard.html`
-   **Action:** Double-click the file or serve it via a local web server.
-   **Interaction:** Once open, you will see 20 device cards. If a patient's vitals become abnormal, the card will turn **Red** and move to the top of the list for immediate triage.

### 3. Explore the API (Swagger UI)
VitalGuard provides a fully interactive API documentation page:
-   **URL:** [http://localhost:8000/docs](http://localhost:8000/docs)
-   **Usage:** You can test individual model inferences, manually trigger simulations, or check system health directly from the browser.

### 4. Running a Diagnostic Check
If you want to manually verify the CNN or TFT services:
-   Use the `/diagnostics/{device_id}` endpoint in Swagger.
-   The system will return a JSON payload containing the individual confidence scores of all three models.

---

## 🔌 API Specification

The backend is built with FastAPI, providing an auto-documented (Swagger/OpenAPI) interface for hospital systems integration.

### `GET /devices`
Returns the current state of all 50 monitored devices.
**Response Format:**
```json
{
  "device_id": "DEV-001",
  "vitals": {
    "heart_rate": 72,
    "oxygen": 98,
    "temp": 98.6
  },
  "status": "Normal",
  "alerts": [],
  "ai_confidence": 0.94
}
```

### `POST /train/edge`
Triggers a re-training of the Edge model using the latest 10,000 data points to adapt to shifting patient demographics.

### `GET /diagnostics/{device_id}`
Retrieves a detailed AI breakdown, including the attention maps from the TFT model and the heatmap from the ResNet50 vision service.

---

## 📊 Frontend & Real-Time Visualization

The **VitalGuard Dashboard** is designed for high-stress environments like ICU command centers.

### UI Features:
-   **Dynamic Triage:** Devices are automatically sorted by risk level. Anomaly-detected devices jump to the top and pulse in Red.
-   **Trend Sparklines:** Every device card features a micro-graph showing the last 30 seconds of activity.
-   **Latency Optimization:** Polling is optimized with `RequestAnimationFrame` logic to ensure a smooth 60fps experience even with 50 devices updating simultaneously.

---

## 🚀 Deployment & Scaling

### Local Setup
1.  **Python Environment:** 3.10+ recommended.
2.  **Dependencies:** Managed via `requirements.txt`.
3.  **Execution:** `uvicorn backend.main:app --reload`

### Containerization (Production)
The system is ready for Docker deployment:
```dockerfile
FROM python:3.10-slim
COPY . /app
RUN pip install -r requirements.txt
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "80"]
```

---

## 📓 Research & Mathematical Foundation

### The "Fusion" Logic
VitalGuard uses a Late Fusion approach for AI consensus. The Final Decision $D$ is calculated as:
$$D = w_1 \cdot E + w_2 \cdot T + w_3 \cdot C$$
Where:
-   $E$ = Edge Model Score
-   $T$ = TFT Forecast Deviation
-   $C$ = CNN Diagnostic Probability
-   $w$ = Dynamically adjusted weights based on sensor reliability.

### Anomaly Thresholding
The Isolation Forest score $s$ is normalized to $[0,1]$. A patient is flagged if:
$$s > \tau + \delta$$
where $\tau$ is the static threshold and $\delta$ is a dynamic offset based on the patient's age-specific baseline vitals.

---

## 📂 Project Directory Structure

```text
iomt-ai-system/
├── backend/
│   ├── main.py            # FastAPI Entry Point
│   ├── simulator.py       # IoT Data Generation
│   ├── edge_service.py    # Scikit-Learn Inference
│   ├── tft_service.py     # PyTorch Time-Series
│   └── cnn_service.py     # ResNet50 Vision logic
├── models/
│   ├── edge/              # Isolation Forest (.pkl)
│   ├── tft/               # TFT Transformer (.pth)
│   └── cnn/               # ResNet50 Weights (.pth)
├── data/
│   ├── processed/         # Cleaned training data
│   └── raw/               # Source CSV files
└── frontend/
    └── dashboard.html     # Real-time Web UI
```
