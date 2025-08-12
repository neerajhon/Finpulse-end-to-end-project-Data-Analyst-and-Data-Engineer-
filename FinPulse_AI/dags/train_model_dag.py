from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime
import pandas as pd
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

# Paths inside Docker
processed_data_dir = "/opt/airflow/data/processed"
model_dir = "/opt/airflow/data/models"

def train_model():
    # Get latest processed file
    files = [f for f in os.listdir(processed_data_dir) if f.endswith(".csv")]
    if not files:
        raise FileNotFoundError("No processed data files found.")
    latest_file = max(files, key=lambda x: os.path.getctime(os.path.join(processed_data_dir, x)))
    file_path = os.path.join(processed_data_dir, latest_file)

    print(f"📂 Using dataset: {file_path}")

    # Load dataset
    df = pd.read_csv(file_path)

    # Example: Assume target is 'is_fraud' and rest are features
    target_col = "is_fraud"
    X = df.drop(columns=[target_col])
    y = df[target_col]

    # Encode categorical variables
    encoders = {}
    for col in X.select_dtypes(include=['object']).columns:
        le = LabelEncoder()
        X[col] = le.fit_transform(X[col])
        encoders[col] = le

    # Store feature order for prediction DAG
    feature_cols = list(X.columns)

    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Train model
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # Create model directory if not exists
    os.makedirs(model_dir, exist_ok=True)

    # Timestamp for versioning
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Save timestamped versions
    joblib.dump(model, f"{model_dir}/fraud_detection_model_{timestamp}.pkl")
    joblib.dump(encoders, f"{model_dir}/label_encoders_{timestamp}.pkl")
    joblib.dump(feature_cols, f"{model_dir}/model_features_{timestamp}.pkl")

    # Save "latest" versions (for prediction DAG)
    joblib.dump(model, f"{model_dir}/fraud_detection_model_latest.pkl")
    joblib.dump(encoders, f"{model_dir}/label_encoders_latest.pkl")
    joblib.dump(feature_cols, f"{model_dir}/model_features_latest.pkl")

    print(f"✅ Model saved: fraud_detection_model_{timestamp}.pkl and _latest.pkl")
    print(f"✅ Encoders saved: label_encoders_{timestamp}.pkl and _latest.pkl")
    print(f"✅ Features saved: model_features_{timestamp}.pkl and _latest.pkl")

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2025, 8, 8),
    'retries': 1,
}

with DAG(
    dag_id='train_model_dag',
    default_args=default_args,
    schedule_interval='@daily',
    catchup=False
) as dag:

    train_task = PythonOperator(
        task_id='train_fraud_detection_model',
        python_callable=train_model
    )
