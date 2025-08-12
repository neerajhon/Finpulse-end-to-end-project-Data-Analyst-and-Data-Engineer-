from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime
import pandas as pd
import os
import psycopg2

RAW_DIR = "/opt/airflow/data/raw"
PROCESSED_DIR = "/opt/airflow/data/processed"

def export_transaction_data():
    # Ensure directories exist
    os.makedirs(RAW_DIR, exist_ok=True)
    os.makedirs(PROCESSED_DIR, exist_ok=True)

    # Connect to PostgreSQL
    conn = psycopg2.connect(
        dbname="finpulse",
        user="postgres",
        password="postgres",
        host="postgres_fp",
        port="5432"
    )
    
    # Export raw data
    df = pd.read_sql("SELECT * FROM transactions", conn)
    raw_path = os.path.join(RAW_DIR, f"transactions_raw_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
    df.to_csv(raw_path, index=False)
    print(f"✅ Raw data saved: {raw_path}")

    # Process data
    df.drop_duplicates(inplace=True)
    df.dropna(inplace=True)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['amount'] = df['amount'].astype(float)

    # Save processed data
    processed_path = os.path.join(PROCESSED_DIR, f"transactions_processed_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
    df.to_csv(processed_path, index=False)
    print(f"✅ Processed data saved: {processed_path}")

    conn.close()

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2025, 8, 8),
    'retries': 1,
}

with DAG(
    dag_id='export_transaction_data_dag',
    default_args=default_args,
    schedule_interval='@daily',
    catchup=False
) as dag:
    
    export_task = PythonOperator(
        task_id='export_and_process_data',
        python_callable=export_transaction_data
    )
