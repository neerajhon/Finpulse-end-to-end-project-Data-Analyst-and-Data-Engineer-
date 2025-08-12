from kafka import KafkaConsumer
import json
import psycopg2

# PostgreSQL connection
conn = psycopg2.connect(
    dbname="finpulse",
    user="postgres",
    password="postgres",
    host="localhost",  # or 'db' if running PostgreSQL in Docker
    port="5432"
)
cursor = conn.cursor()

# ✅ Create table if it doesn't exist
cursor.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        transaction_id TEXT PRIMARY KEY,
        user_id INTEGER,
        user_name TEXT,
        user_age INTEGER,
        user_gender TEXT,
        card_type TEXT,
        transaction_type TEXT,
        amount FLOAT,
        merchant TEXT,
        location TEXT,
        device TEXT,
        timestamp TIMESTAMP,
        is_fraud INTEGER
    );
""")
conn.commit()
print("✅ Table 'transactions' checked/created.")

# Kafka consumer setup
consumer = KafkaConsumer(
    'transactions',
    bootstrap_servers='localhost:9092',
    auto_offset_reset='latest',
    group_id='finpulse-group',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

print("✅ Kafka consumer started and listening to topic 'transactions'...")

# Process messages
for message in consumer:
    txn = message.value
    try:
        cursor.execute("""
            INSERT INTO transactions (
                transaction_id, user_id, user_name, user_age, user_gender, card_type,
                transaction_type, amount, merchant, location, device, timestamp, is_fraud
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (transaction_id) DO NOTHING
        """, (
            txn["transaction_id"], txn["user_id"], txn["user_name"], txn["user_age"], txn["user_gender"],
            txn["card_type"], txn["transaction_type"], txn["amount"], txn["merchant"], txn["location"],
            txn["device"], txn["timestamp"], txn["is_fraud"]
        ))
        conn.commit()
        print(f"🛬 Inserted transaction: {txn['transaction_id']}")
    except Exception as e:
        print(f"❌ Error inserting transaction: {e}")
        conn.rollback()
