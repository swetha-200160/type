from sklearn.linear_model import LinearRegression
import numpy as np

def train_model():
    X = np.array([[1], [2], [3], [4], [5]])
    y = np.array([2, 4, 6, 8, 10])
    model = LinearRegression()
    model.fit(X, y)
    print("✅ Model trained successfully!")
    print("Prediction for 6:", model.predict([[6]])[0])

if __name__ == "__main__":
    train_model()
