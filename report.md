# IoMT AI System - Architectural & Operational Report

## 1. System Overview
The **VitalGuard AI** (iomt-ai-system) is a production-grade multi-model AI framework designed for real-time anomaly detection in medical Internet of Things (IoMT) devices. The system monitors critical patient vital signs (heart rate, temperature, respiratory rate) and provides a consolidated health status "Final Decision" by leveraging three specialized AI models.

## 2. Technical Stack
*   **Backend:** Python 3.x, FastAPI (REST API), Uvicorn (ASGI server).
*   **AI/ML Frameworks:** PyTorch (CNN and TFT), Scikit-learn (Isolation Forest), Pandas, and Joblib.
*   **Frontend:** HTML5, CSS3, and Vanilla JavaScript (Fetch API for real-time polling).
*   **Data Strategy:** CSV-based datasets for simulation, preprocessing, and model training.

## 3. AI/ML Model Architecture
The system employs a "tri-model" approach for robust health monitoring:
*   **Edge Model (`edge_service.py`):** Utilizes an **Isolation Forest** (Scikit-learn) for immediate, low-latency anomaly detection on vital sign vectors.
*   **TFT Model (`tft_service.py`):** Implements a **Temporal Fusion Transformer** (PyTorch) for advanced time-series forecasting, predicting future health trends based on historical data.
*   **CNN Model (`cnn_service.py`):** A **ResNet50** (PyTorch) architecture designed for medical image analysis (e.g., X-ray anomaly detection), integrated as a service stub ready for weight loading.

## 4. Data Flow & Backend Logic
1.  **Simulation (`simulator.py`):** Generates real-time synthetic vital signs for 50 virtual devices, sourced from `healthcare_iot_target_dataset.csv`.
2.  **Orchestration (`main.py`):** The FastAPI application manages the simulation lifecycle and exposes endpoints (e.g., `/devices`) that aggregate live data and model predictions.
3.  **Inference Pipeline:** When the frontend requests status updates, the backend passes current vitals through the Edge, TFT, and CNN services to determine if an anomaly exists.
4.  **Consolidated Decision:** A logic layer aggregates model outputs to produce a finalized "Normal" or "Anomaly Detected" status.

## 5. Frontend & Visualization
*   **`dashboard.html`:** A modern, real-time monitoring interface displaying status cards for 20 devices simultaneously.
*   **Polling Mechanism:** The UI utilizes a polling strategy (every 3 seconds) to the `/devices` endpoint to ensure the dashboard reflects the most recent vitals and health indicators.

## 6. Project Structure
*   **`/models`:** Contains trained artifacts (`.pth`, `.pkl`).
*   **`/data`:** Source and processed CSV files.
*   **`/backend`:** Core FastAPI logic and AI service implementations.
*   **`/frontend`:** Dashboard and user interface components.
