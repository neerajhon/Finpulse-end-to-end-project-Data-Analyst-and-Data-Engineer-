import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
import pickle
import os

# Step 1: Load data
df = pd.read_csv("data/transactions.csv")

# Step 2: Drop non-useful columns (like IDs, timestamps, free-text device info)
df = df.drop(columns=["transaction_id", "timestamp", "device"], errors='ignore')

# Step 3: Encode categorical variables
df = pd.get_dummies(df, drop_first=True)

# Step 4: Split into features and target
X = df.drop("is_fraud", axis=1)
y = df["is_fraud"]

# Step 5: Split into train/test
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Step 6: Train RandomForest
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Step 7: Evaluate the model
y_pred = model.predict(X_test)
print("✅ Accuracy:", accuracy_score(y_test, y_pred))
print("📊 Classification Report:\n", classification_report(y_test, y_pred))

# Step 8: Save model
os.makedirs("ml", exist_ok=True)
with open("ml/fraud_model.pkl", "wb") as f:
    pickle.dump(model, f)

print("✅ Trained model saved as ml/fraud_model.pkl")
