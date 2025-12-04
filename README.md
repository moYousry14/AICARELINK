# 🚑 Aicarelink: Intelligent Emergency Response System

> **Bridging the gap between pre-hospital care and specialized treatment during the Golden Hour.**

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=for-the-badge&logo=python)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Streamlit-1.32-red?style=for-the-badge&logo=streamlit)](https://streamlit.io/)
[![AI Engine](https://img.shields.io/badge/TensorFlow-Keras-orange?style=for-the-badge&logo=tensorflow)](https://www.tensorflow.org/)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

## 📖 Overview
**Aicarelink** is an AI-powered triage and resource allocation system designed to optimize emergency response. It utilizes Deep Learning to analyze **12-Lead ECG signals** in real-time, detects critical conditions (like STEMI), and automatically routes the ambulance to the nearest hospital *capable* of treating that specific condition (e.g., finding a facility with an available Cath Lab).

This project aims to reduce "Door-to-Balloon" time and prevent patient transfers between hospitals due to lack of resources.

---

## 🌟 Key Features

### 🧠 1. Clinical-Grade AI Engine
* Powered by a **Deep ResNet-1d** model trained on the **PTB-XL** dataset (21,000+ records).
* Capable of classifying 5 complex cardiac conditions:
    * **MI:** Myocardial Infarction (Heart Attack).
    * **STTC:** Ischemia / ST-T Changes.
    * **CD:** Conduction Disturbance.
    * **HYP:** Hypertrophy.
    * **NORM:** Normal Sinus Rhythm.
* Achieves **77.4% Accuracy** on unseen clinical test data (Fold 10 strict split).

### 🗺️ Intelligent National Grid Routing
* Dynamic routing algorithm that considers:
    * **Distance:** Real-time road distance via OSRM API.
    * **Capability:** Matches patient needs (e.g., Cath Lab) with hospital resources.
    * **Status:** Avoids overloaded/busy hospitals.
* Visualizes the live path on a dark-mode interactive map using **Folium**.

### 📡 Smart Handover Protocol
* Enables **Pre-Arrival Notification**: Sends ECG and vitals to the destination hospital before arrival.
* Reduces admission administrative delays.

### 💻 Cinematic Command Center
* High-end **Dark Mode UI** with Glassmorphism effects.
* Real-time simulation of vital signs (HR, SpO2, BP) correlated with the diagnosis.

---

## 🏗️ Project Architecture (MVC Pattern)

The codebase follows a clean **Model-View-Controller (MVC)** structure for scalability:

```text
Aicarelink/
│
├── models/                  # AI Models & Assets
│   ├── PTBXL_ResNet_Final.h5  # The trained ResNet Model
│   └── classes.npy            # Label encoders
│
├── src/                     # Source Modules
│   ├── ai_engine.py         # (Model) Inference logic & Signal generation
│   ├── routing.py           # (Logic) Distance calc & Hospital database
│   └── ui_components.py     # (View) Streamlit UI widgets & Plots
│
├── app.py                   # (Controller) Main entry point
├── requirements.txt         # Project dependencies
└── README.md                # Documentation