# kafka/producer.py

from kafka import KafkaProducer
import requests
import json
import time

print("🚀 Kafka Producer started...")

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

while True:
    res = requests.get("http://localhost:8000/generate-transactions?count=1")
    transactions = res.json()

    for txn in transactions:
        producer.send("transactions", value=txn)
        print("✅ Sent to Kafka:", txn)

    time.sleep(1)  # send one transaction per second
