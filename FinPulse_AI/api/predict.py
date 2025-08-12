from fastapi import FastAPI
from pydantic import BaseModel
import pickle
import pandas as pd

# Load the trained model
with open("ml/fraud_model.pkl", "rb") as f:
    model = pickle.load(f)

# Define input schema
class Transaction(BaseModel):
    amount: float
    merchant: str
    location: str

# Create FastAPI app
app = FastAPI()

@app.post("/predict")
def predict(tx: Transaction):
    # Convert input to DataFrame
    input_df = pd.DataFrame([{
        "amount": tx.amount,
        "merchant": tx.merchant,
        "location": tx.location
    }])

    # One-hot encode like training
    input_df = pd.get_dummies(input_df)

    # Align with model features (handle missing columns)
    model_features = model.feature_names_in_
    for col in model_features:
        if col not in input_df:
            input_df[col] = 0
    input_df = input_df[model_features]

    # Predict
    prediction = model.predict(input_df)[0]
    return { "is_fraud": int(prediction) }
