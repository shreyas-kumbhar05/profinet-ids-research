#!/usr/bin/env python3
"""Train an Isolation Forest using normal PROFINET traffic only.

Run using:
    python3 models/isolation_forest/train.py

The script reads "dataset/labeled_dataset.csv", and writes to "saved_model.pkl" 
"""

from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import IsolationForest


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATASET_PATH = PROJECT_ROOT / "dataset" / "labeled_dataset.csv"
MODEL_PATH = PROJECT_ROOT / "models" / "isolation_forest" / "saved_model.pkl"

FEATURES = ["iat", "frame_size", "src_mac_known", "payload_entropy"]


def load_normal_data(csv_path):

    # Loads the dataset and returns only normal traffic feature columns where label value is 0
    csv_path = Path(csv_path)

    if not csv_path.is_file():
        raise FileNotFoundError(f"Dataset file not found: {csv_path}")

    data = pd.read_csv(csv_path)

    required_columns = FEATURES + ["label"]
    missing_columns = [column for column in required_columns if column not in data.columns]
    if missing_columns:
        raise ValueError(
            "Dataset is missing required columns: " + ", ".join(missing_columns)
        )

    normal_data = data.loc[data["label"] == 0, FEATURES].copy()

    if normal_data.empty:
        raise ValueError("No normal samples were found where label == 0")

    # Converts boolean features to integers for a consistent numeric input.
    for column in normal_data.select_dtypes(include=["bool"]).columns:
        normal_data[column] = normal_data[column].astype(int)

    #Checks whether all selected features are numeric and contain no missing values.
    for column in FEATURES:
        normal_data[column] = pd.to_numeric(normal_data[column], errors="raise")

    if normal_data.isnull().any().any():
        missing_features = normal_data.columns[normal_data.isnull().any()].tolist()
        raise ValueError(
            "Normal training data contains missing values in: "
            + ", ".join(missing_features)
        )

    return normal_data


def train_model(X_normal, contamination=0.05, random_state=42):
    # Fit Isolation Forest using normal-traffic features only.
    if X_normal.empty:
        raise ValueError("X_normal is empty; There is no data to train on.")

    model = IsolationForest(
        contamination=contamination,
        random_state=random_state,
    )
    model.fit(X_normal)

    return model


def save_model(model, path):
    # Saves the fitted model so it can be used later for evaluation
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, path)


def main():
    X_normal = load_normal_data(DATASET_PATH)
    model = train_model(X_normal)
    save_model(model, MODEL_PATH)

    print("Isolation Forest training completed.")
    print(f"Normal samples used for training: {len(X_normal):,}")
    print(f"Features used: {', '.join(FEATURES)}")
    print(f"Trained model saved to: {MODEL_PATH.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
