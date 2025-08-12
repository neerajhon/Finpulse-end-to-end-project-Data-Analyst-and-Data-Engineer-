import psycopg2
import pandas as pd

# DB connection
conn = psycopg2.connect(
    dbname="finpulse",
    user="postgres",
    password="postgres",
    host="localhost",  # or 'postgres_fp' if using Docker PostgreSQL
    port="5432"
)

# Load data
df = pd.read_sql("SELECT * FROM transactions", conn)
df.to_csv("data/transactions.csv", index=False)
print("✅ Exported transactions to data/transactions.csv")

conn.close()
