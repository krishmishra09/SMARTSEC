# SMARTSEC 🛡️

> An AI-powered real-time system monitor and intrusion detection system (IDS) built with Python and Machine Learning.

This project is designed to provide real-time monitoring of system and network activities to detect and flag potential security threats using both anomaly-based and signature-based detection methods.


## 📖 About The Project

SMARTSEC is a system-monitoring and intrusion detection system that actively monitors a machine's processes and network traffic. It leverages machine learning models to distinguish between normal and malicious activities. The system features a web-based dashboard for visualizing alerts and system status in real-time. This project was developed as a comprehensive tool to apply machine learning concepts to the practical field of cybersecurity.

---

## ✨ Key Features

* **Real-Time Monitoring**: Agents continuously collect data on running processes and network packets.
* **Anomaly Detection**: Uses an Isolation Forest model (`isolation_forest_model.joblib`) to detect unusual patterns that deviate from the norm.
* **Signature-Based Detection**: Employs a Random Forest model (`random_forest_model.joblib`) to identify known malicious patterns.
* **Web Dashboard**: A Flask-powered user interface (`index.html`) for easy monitoring and viewing of alerts.
* **Modular Design**: A decoupled agent-server architecture for scalability and maintenance.

---

## 💻 Tech Stack

* **Backend**: Python, Flask
* **Machine Learning**: Scikit-learn, Pandas, NumPy
* **Data Collection**: Psutil (for system processes), Scapy (for network packets)
* **Frontend**: HTML, CSS, JavaScript
* **Deployment**: Local server environment

---

## 🏗️ Software Architecture

The system is designed with a central server and multiple agents that can be deployed on hosts to be monitored.

1.  **Agents (`host_agent.py`, `network_agent.py`)**:
    * These are lightweight Python scripts that run on the target machine.
    * The `host_agent` collects data about running processes, CPU usage, and memory consumption.
    * The `network_agent` captures and analyzes network traffic.
    * Both agents send the collected data to the central server via HTTP requests.

2.  **Central Server (`app.py`)**:
    * This is a Flask web server that acts as the core of the system.
    * It exposes an API endpoint (`/api/data`) to receive data from the agents.
    * It passes the received data to the Detection Engine for analysis.
    * It serves the web dashboard to the user.

3.  **Detection Engine (`detection_engine.py`)**:
    * This component contains the core logic for threat detection.
    * It preprocesses the data and feeds it into the pre-trained machine learning models (Isolation Forest and Random Forest).
    * If a threat is detected, it generates an alert that is displayed on the dashboard.



---

## 🚀 Getting Started

Follow these steps to get a local copy up and running.

### Prerequisites

* Python 3.10+
* Git

### Installation

1.  **Clone the repository**
    ```bash
    git clone [https://github.com/krishmishra09/SMARTSEC.git](https://github.com/krishmishra09/SMARTSEC.git)
    cd SMARTSEC
    ```

2.  **Create and activate a virtual environment**
    ```bash
    # For Windows
    python -m venv venv
    .\venv\Scripts\activate
    ```

3.  **Install the required packages**
    ```bash
    pip install -r requirements.txt
    ```

---
Krish Mishra - [https://www.linkedin.com/in/krish-mishra-b0aa27295/]

Project Link: [https://github.com/krishmishra09/SMARTSEC]
