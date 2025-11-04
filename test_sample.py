from main import train_model

def test_training_runs():
    # train_model prints output and returns None; test that it runs without raising
    assert train_model() is None
