import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report

# Load dataset
df = pd.read_csv("dataset/features.csv")

# Drop non-feature columns
X = df[["duration_sec", "contains_secret", "is_anomaly"]]
y = df["result"]

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Define and train the model
model = RandomForestClassifier(n_estimators=100, class_weight="balanced", random_state=42)
model.fit(X_train, y_train)

# Evaluate
y_pred = model.predict(X_test)
acc = accuracy_score(y_test, y_pred)
conf = confusion_matrix(y_test, y_pred)
report = classification_report(y_test, y_pred)

print(f"\n✅ Model Accuracy: {acc:.2f}")
print("\n📊 Classification Report:\n", report)
print("📉 Confusion Matrix:\n", conf)

# Save model
joblib.dump(model, "model.pkl")
print("\n💾 Model saved as model.pkl")
