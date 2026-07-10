"""Train the match prediction model and save the artifact bundle."""

import joblib

from src.config import MODEL_FILE, MODELS_DIR
from src.data_loader import load_matches
from src.model import engineer_features, train_model

def main():
    print("Loading data...")
    df = load_matches()

    print("Engineering features (rolling win rates take ~a minute)...")
    engineered, fill_values = engineer_features(df)

    print("Training...")
    bundle = train_model(engineered)
    bundle["fill_values"] = fill_values

    m, b = bundle["metrics"], bundle["metrics"]["baseline"]
    print(f"\nBaseline:  accuracy {b['accuracy']*100:.2f}%, AUC {b['auc']:.4f}")
    print(f"XGBoost:   accuracy {m['accuracy']*100:.2f}%, AUC {m['auc']:.4f}")
    print(f"Train/test rows: {m['train_rows']} / {m['test_rows']}")

    MODELS_DIR.mkdir(exist_ok=True)
    joblib.dump(bundle, MODEL_FILE)
    print(f"\nSaved bundle -> {MODEL_FILE}")

if __name__ == "__main__":
    main()