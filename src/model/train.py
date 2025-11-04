# src/model/train.py
import os
import joblib
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier

def train_model():
    os.makedirs("src/model", exist_ok=True)
    print("Starting training...")
    data = load_iris()
    X, y = data.data, data.target
    clf = RandomForestClassifier(n_estimators=50, random_state=42)
    clf.fit(X, y)
    joblib.dump(clf, "src/model/model.pkl")
    print("Saved model to src/model/model.pkl")

if __name__ == "__main__":
    train_model()
