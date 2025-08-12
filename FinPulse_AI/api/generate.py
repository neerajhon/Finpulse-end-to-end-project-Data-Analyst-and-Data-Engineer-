from fastapi import FastAPI, Query
from faker import Faker
import random, uuid
from datetime import datetime

app = FastAPI()
fake = Faker("en_IN")  # 👈 use Indian locale

card_types = ['Visa', 'MasterCard', 'RuPay', 'AmEx']
genders = ['Male', 'Female', 'Other']
transaction_types = ['Online', 'POS', 'ATM', 'QR Scan']

def generate_transaction():
    return {
        "transaction_id": str(uuid.uuid4()),
        "user_id": random.randint(1000, 9999),
        "user_name": fake.name(),                       # 👈 Indian name
        "user_age": random.randint(18, 70),
        "user_gender": random.choice(genders),
        "card_type": random.choice(card_types),
        "transaction_type": random.choice(transaction_types),
        "amount": round(random.uniform(10, 5000), 2),
        "merchant": fake.company(),
        "location": fake.city(),                        # 👈 Indian city
        "device": fake.user_agent(),
        "timestamp": datetime.now().isoformat(),
        "is_fraud": random.choice([0, 1])
    }

@app.get("/generate-transactions")
def generate_transactions(count: int = Query(10, gt=0, le=10000)):
    return [generate_transaction() for _ in range(count)]
