# main.py
import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def train_model():
    # ... your training code ...
    print("\u2705 Model trained successfully!")  # this will now work

if __name__ == "__main__":
    train_model()
