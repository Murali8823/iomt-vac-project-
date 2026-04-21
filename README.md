# 🩺 VitalGuard AI: Real-Time IoMT Health Monitoring System

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![PyTorch](https://img.shields.io/badge/PyTorch-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white)](https://pytorch.org/)
[![Scikit-Learn](https://img.shields.io/badge/scikit_learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

**VitalGuard AI** is a state-of-the-art, multi-model AI framework designed for real-time monitoring and anomaly detection in Medical Internet of Things (IoMT) ecosystems. By fusing time-series forecasting, edge-based anomaly detection, and deep learning, VitalGuard ensures patient safety through continuous, intelligent oversight.

---

## 🚀 Key Features

-   **📡 Real-Time Simulation:** Dynamically generates vital sign data (Heart Rate, SpO2, Respiratory Rate) for 50+ virtual devices.
-   **🤖 Tri-Model AI Architecture:**
    -   **Edge Intelligence:** Instant anomaly detection using Isolation Forests.
    -   **Predictive Forecasting:** Temporal Fusion Transformers (TFT) for future health trend analysis.
    -   **Diagnostic Vision:** ResNet50-based CNN for medical image (X-ray) integration.
-   **📊 Interactive Dashboard:** A modern, responsive UI providing live updates and instant health alerts.
-   **⚡ High Performance:** Built on FastAPI for low-latency inference and high-concurrency data handling.

---

## 🏗️ Architecture Overview

The system operates as a distributed intelligence network:
1.  **Data Layer:** Ingests live streams from simulated IoT medical sensors.
2.  **Service Layer:** Orchestrates three AI models to analyze data from different perspectives.
3.  **Inference Engine:** Aggregates model outputs into a unified "Final Health Decision."
4.  **Presentation Layer:** Delivers actionable insights to healthcare providers via a real-time web dashboard.

---

## 🛠️ Tech Stack

-   **Backend:** FastAPI, Python 3.10+, Uvicorn
-   **Machine Learning:** PyTorch, Scikit-learn, Pandas, NumPy
-   **Frontend:** HTML5, CSS3 (Modern UI/UX), Vanilla JavaScript
-   **Serialization:** Joblib, Pickle

---

## 📂 Project Structure

```bash
├── backend/            # FastAPI core, AI service logic, and simulation engine
├── models/             # Pre-trained model weights (CNN, Edge, TFT)
├── data/               # Healthcare datasets and processed vital records
├── frontend/           # Web-based monitoring dashboard
├── report.md           # Detailed architectural and operational report
└── README.md           # Project documentation
```

---

## ⚙️ Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Murali8823/iomt-vac-project-.git
   cd iomt-vac-project-
   ```

2. **Set up a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Launch the system:**
   ```bash
   python backend/main.py
   ```

---

## 📸 Dashboard Preview

*The dashboard displays 20 active devices with real-time vitals and a color-coded status (Normal vs. Anomaly).*

---

## 🛡️ Security & Integrity

-   **Data Privacy:** All patient data is anonymized during simulation.
-   **Modular Design:** Easily swap or upgrade individual AI models without disrupting the system.

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

---
*Developed with ❤️ for the future of Smart Healthcare.*
