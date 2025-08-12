from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import pandas as pd
import joblib
from sqlalchemy import create_engine, text

# Paths
model_dir = "/opt/airflow/data/models"

# DB connection
DB_URI = "postgresql+psycopg2://postgres:postgres@postgres_fp:5432/finpulse"
engine = create_engine(DB_URI)

def predict_fraud():
    # Ensure table exists
    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS fraud_predictions (
                id SERIAL PRIMARY KEY,
                transaction_id VARCHAR(255) UNIQUE NOT NULL,
                prediction INTEGER NOT NULL,
                score FLOAT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """))

    # Load latest model & encoders
    model = joblib.load(f"{model_dir}/fraud_detection_model_latest.pkl")
    encoders = joblib.load(f"{model_dir}/label_encoders_latest.pkl")
    feature_names = list(model.feature_names_in_)

    # Fetch only new transactions
    query = """
        SELECT *
        FROM transactions
        WHERE transaction_id NOT IN (SELECT transaction_id FROM fraud_predictions)
        ORDER BY timestamp DESC
        LIMIT 100;
    """
    df = pd.read_sql(query, engine)

    if df.empty:
        print("⚠️ No new transactions to predict.")
        return

    # Keep original IDs
    original_ids = df["transaction_id"].astype(str).copy()

    # Drop target column if exists
    if "is_fraud" in df.columns:
        df = df.drop(columns=["is_fraud"])

    # Encode features with unseen label handling
    for col, encoder in encoders.items():
        if col in df.columns:
            df[col] = df[col].astype(str).apply(
                lambda val: encoder.transform([val])[0]
                if val in encoder.classes_
                else encoder.transform([encoder.classes_[0]])[0]
            )

    # Ensure correct order
    X = df[feature_names]

    # Predictions
    preds = model.predict(X)
    scores = model.predict_proba(X)[:, 1]

    # Prepare results
    results = pd.DataFrame({
        "transaction_id": original_ids,
        "prediction": preds,
        "score": scores
    })

    # Insert predictions safely
    with engine.begin() as conn:
        for _, row in results.iterrows():
            conn.execute(text("""
                INSERT INTO fraud_predictions (transaction_id, prediction, score)
                VALUES (:transaction_id, :prediction, :score)
                ON CONFLICT (transaction_id) DO NOTHING;
            """), {
                "transaction_id": row["transaction_id"],
                "prediction": int(row["prediction"]),
                "score": float(row["score"])
            })

    print(f"✅ Inserted {len(results)} new predictions into fraud_predictions.")

# Airflow DAG config
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2025, 8, 9),
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    "predict_model_dag",
    default_args=default_args,
    description="Predict fraud using trained model and save results",
    schedule_interval=timedelta(hours=1),
    catchup=False,
) as dag:

    predict_task = PythonOperator(
        task_id="predict_fraud_transactions",
        python_callable=predict_fraud
    )

    predict_task
