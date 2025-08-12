# 🛡️ FinPulse – AI-Powered Fraud Detection Data Pipeline

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)](https://www.python.org/)
[![Apache Kafka](https://img.shields.io/badge/Kafka-2.8%2B-black?logo=apachekafka)](https://kafka.apache.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13%2B-blue?logo=postgresql)](https://www.postgresql.org/)
[![Airflow](https://img.shields.io/badge/Apache%20Airflow-2.5%2B-green?logo=apacheairflow)](https://airflow.apache.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.20%2B-ff4b4b?logo=streamlit)](https://streamlit.io/)
[![Docker](https://img.shields.io/badge/Docker-20.10%2B-blue?logo=docker)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**End-to-end real-time + batch processing pipeline for detecting fraudulent transactions, with automated ML model training and interactive dashboards.**

---

## 📌 Overview

FinPulse is a **Fraud Detection Data Pipeline** that simulates real-world payment transactions, processes them in real-time, and predicts fraud using a trained ML model.  
It integrates **FastAPI, Kafka, PostgreSQL, Airflow, Scikit-learn, and Streamlit** into a fully automated system.

The architecture is designed for **scalability, automation, and real-time decision making**, and can be adapted for other fraud detection or streaming analytics use cases.

---

## ⚙️ Tech Stack

| Component             | Technology Used |
|-----------------------|-----------------|
| **Data Generation**   | FastAPI + Faker |
| **Streaming**         | Apache Kafka |
| **Storage**           | PostgreSQL |
| **Workflow Orchestration** | Apache Airflow |
| **Machine Learning**  | Scikit-learn (Random Forest) |
| **Visualization**     | Streamlit |
| **Deployment**        | Docker + Docker Compose |

---

## 🚀 Features

- ✅ **Synthetic Transaction Data** – Generated using FastAPI with realistic fields like card type, location, merchant, amount, etc.
- ✅ **Real-Time Ingestion** – Data streamed from API → Kafka → PostgreSQL.
- ✅ **Data Preprocessing** – Automated cleaning & label encoding before training.
- ✅ **Automated Model Training** – Airflow DAG trains a Random Forest model daily.
- ✅ **Fraud Prediction DAG** – Predicts fraud for new transactions every hour.
- ✅ **Prediction Storage** – Results stored in `fraud_predictions` table with scores.
- ✅ **Interactive Dashboard** – Streamlit app shows KPIs, trends, and charts.
- ✅ **Modular & Scalable** – Easy to extend to Spark or cloud services.

---

## 🗂 Project Structure

![Project_Structure](pro_stru.png)

---

## 🔄 Workflow

1. **Data Generation**
   - FastAPI (`generation.py`) generates synthetic transaction data (UUID, user details, card info, amount, timestamp, etc.).
   - Data can be requested in batches via `/generate-transactions` endpoint.

2. **Streaming with Kafka**
   - `producer.py` fetches transactions from API and sends them to Kafka topic `transactions`.
   - `consumer.py` listens to Kafka topic and inserts into PostgreSQL table `transactions`.

3. **Data Preprocessing & Model Training (Airflow DAG 1)**
   - Airflow `train_model_dag` reads processed data.
   - Encodes categorical variables.
   - Trains a **Random Forest Classifier** to detect fraud.
   - Saves **model**, **label encoders**, and **feature list** (timestamped + latest versions).

4. **Fraud Prediction (Airflow DAG 2)**
   - Fetches **unseen transactions** from PostgreSQL.
   - Applies **saved encoders** to match model format.
   - Predicts fraud probability and stores results in `fraud_predictions` table.

5. **Visualization**
   - Streamlit dashboard fetches data from PostgreSQL.
   - Displays **KPIs, fraud trend charts, transaction patterns**, and a searchable fraud table.

---

## 🖥 Architecture Diagram

![Workflow Diagram](workflow.png)  


---

## 📊 Example Dashboard Screenshots

**Main Dashboard**  
![Dashboard Screenshot](dashboard.png)

---

## 🛠 Setup & Installation

### 1️⃣ Clone the repo
```bash
git clone https://github.com/neerajhon/finpulse.git
cd finpulse

│
├── docker-compose.yml       # Multi-container setup for all services
├── Dockerfile               # Docker build instructions
├── requirements.txt         # Python dependencies
└── README.md                # Project documentation (this file)

