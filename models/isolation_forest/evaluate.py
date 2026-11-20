#!/usr/bin/env python3
"""Evaluate the saved Isolation Forest model on the labeled PROFINET dataset.

Run using the command:
    python3 models/isolation_forest/evaluate.py

The script writes three plots into models/isolation_forest/.
Note: the current model was trained on all normal rows in this dataset, so
normal-class evaluation here is in-sample, not an independent test result.
"""

from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    RocCurveDisplay,
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODEL_PATH = PROJECT_ROOT / "models" / "isolation_forest" / "saved_model.pkl"
DATASET_PATH = PROJECT_ROOT / "dataset" / "labeled_dataset.csv"
OUTPUT_DIR = PROJECT_ROOT / "models" / "isolation_forest"

FEATURES = ["iat", "frame_size", "src_mac_known", "payload_entropy"]
ATTACK_TYPES = ["replay", "spoof", "malformed"]


def load_model(model_path=MODEL_PATH):
    """Load the fitted Isolation Forest model from disk."""
    if not Path(model_path).is_file():
        raise FileNotFoundError(f"Trained model not found: {model_path}")
    return joblib.load(model_path)


def load_full_dataset(csv_path=DATASET_PATH):
    """Load all scenarios and create binary ground-truth labels."""
    if not Path(csv_path).is_file():
        raise FileNotFoundError(f"Labeled dataset not found: {csv_path}")

    df = pd.read_csv(csv_path)
    required_columns = FEATURES + ["label", "attack_type"]
    missing_columns = [column for column in required_columns if column not in df.columns]
    if missing_columns:
        raise ValueError(
            "Dataset is missing required columns: " + ", ".join(missing_columns)
        )
    if df.empty:
        raise ValueError("The labeled dataset is empty.")

    # Convert the feature columns to numeric values. The MAC feature may be Boolean.
    for column in FEATURES:
        if pd.api.types.is_bool_dtype(df[column]):
            df[column] = df[column].astype(int)
        df[column] = pd.to_numeric(df[column], errors="raise")

    if df[FEATURES].isnull().any().any():
        bad_columns = df[FEATURES].columns[df[FEATURES].isnull().any()].tolist()
        raise ValueError("Feature data contains missing values in: " + ", ".join(bad_columns))

    # Dataset convention: 0 = normal, 1/2/3 = attack.
    df["binary_label"] = (df["label"] != 0).astype(int)
    return df


def evaluate_model(model, df):
    """Generate binary predictions and continuous anomaly scores."""
    df = df.copy()
    X_all = df[FEATURES]

    model_features = getattr(model, "feature_names_in_", None)
    if model_features is not None and list(model_features) != FEATURES:
        raise ValueError(
            "Feature mismatch between saved model and evaluation data. "
            f"Model expects {list(model_features)}, script supplies {FEATURES}."
        )

    raw_predictions = model.predict(X_all)  # -1 = anomaly, +1 = normal
    df["predicted"] = (raw_predictions == -1).astype(int)  # 1 = attack, 0 = normal

    # score_samples: lower values are more abnormal. Negate so higher means more anomalous.
    df["anomaly_score"] = -model.score_samples(X_all)
    return df


def print_metrics(df):
    """Print binary metrics, false-positive rate, and attack-specific detection."""
    y_true = df["binary_label"]
    y_pred = df["predicted"]
    anomaly_scores = df["anomaly_score"]

    cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
    tn, fp, fn, tp = cm.ravel()

    precision = precision_score(y_true, y_pred, pos_label=1, zero_division=0)
    recall = recall_score(y_true, y_pred, pos_label=1, zero_division=0)
    f1 = f1_score(y_true, y_pred, pos_label=1, zero_division=0)
    accuracy = accuracy_score(y_true, y_pred)
    fpr = fp / (fp + tn) if (fp + tn) else 0.0
    auc = roc_auc_score(y_true, anomaly_scores)

    print("=" * 64)
    print("ISOLATION FOREST EVALUATION: NORMAL VS ANY ATTACK")
    print("=" * 64)
    print("Evaluation scope: complete labeled dataset")
    print("WARNING: normal rows were also used to fit this model.")
    print("The normal-class results are therefore in-sample, not an independent test.")
    print("Attack rows were not used during training.")
    print("\nClassification report:")
    print(
        classification_report(
            y_true,
            y_pred,
            labels=[0, 1],
            target_names=["normal", "attack"],
            zero_division=0,
        )
    )

    print("Confusion matrix counts (actual rows, predicted columns):")
    print(f"TN={tn:,}  FP={fp:,}  FN={fn:,}  TP={tp:,}")
    print("\nOverall metrics:")
    print(f"Accuracy:              {accuracy:.4f} ({accuracy:.2%})")
    print(f"Attack precision:      {precision:.4f}")
    print(f"Attack recall:         {recall:.4f}")
    print(f"Attack F1-score:       {f1:.4f}")
    print(f"False positive rate:   {fpr:.4f} ({fpr:.2%})")
    print(f"ROC AUC:               {auc:.4f}")

    normal_rows = df[df["attack_type"].astype(str).str.lower() == "normal"]
    normal_false_alarms = int(normal_rows["predicted"].sum())
    normal_total = len(normal_rows)
    print("\nNormal traffic false alarms:")
    print(
        f"{normal_false_alarms:,}/{normal_total:,} flagged as anomalies "
        f"({normal_false_alarms / normal_total:.2%})"
        if normal_total else "No normal rows found."
    )

    print("\nDetection rate per attack type:")
    print("-" * 64)
    for attack_type in ATTACK_TYPES:
        subset = df[df["attack_type"].astype(str).str.lower() == attack_type]
        total = len(subset)
        detected = int(subset["predicted"].sum())
        missed = total - detected
        rate = detected / total if total else 0.0
        print(
            f"{attack_type:10s}: {detected:,}/{total:,} detected "
            f"({rate:.2%}), missed={missed:,}"
        )
        if total == 0:
            print(f"WARNING: no rows found for attack_type '{attack_type}'.")

    return {
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "fpr": fpr,
        "roc_auc": auc,
        "tn": int(tn),
        "fp": int(fp),
        "fn": int(fn),
        "tp": int(tp),
    }


def plot_confusion_matrix(df, save_path):
    cm = confusion_matrix(df["binary_label"], df["predicted"], labels=[0, 1])
    display = ConfusionMatrixDisplay(
        confusion_matrix=cm,
        display_labels=["normal", "attack"],
    )
    display.plot(cmap="Blues", values_format="d")
    plt.title("Isolation Forest: Confusion Matrix")
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {save_path}")


def plot_roc_curve(df, save_path):
    RocCurveDisplay.from_predictions(
        df["binary_label"],
        df["anomaly_score"],
        name="Isolation Forest",
    )
    plt.plot([0, 1], [0, 1], linestyle="--", label="Random baseline")
    plt.title("Isolation Forest: ROC Curve")
    plt.legend()
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {save_path}")


def plot_score_distribution(df, save_path):
    plt.figure(figsize=(9, 5))
    bin_edges = 50
    for traffic_type in ["normal", *ATTACK_TYPES]:
        subset = df[df["attack_type"].astype(str).str.lower() == traffic_type]
        if subset.empty:
            continue
        plt.hist(
            subset["anomaly_score"],
            bins=bin_edges,
            density=True,
            alpha=0.45,
            label=f"{traffic_type} (n={len(subset):,})",
        )

    plt.xlabel("Anomaly score (higher = more anomalous)")
    plt.ylabel("Density")
    plt.title("Isolation Forest: Anomaly Score Distribution")
    plt.legend()
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {save_path}")


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    model = load_model()
    df = load_full_dataset()
    evaluated_df = evaluate_model(model, df)
    print_metrics(evaluated_df)

    plot_confusion_matrix(
        evaluated_df,
        OUTPUT_DIR / "confusion_matrix.png",
    )
    plot_roc_curve(
        evaluated_df,
        OUTPUT_DIR / "roc_curve.png",
    )
    plot_score_distribution(
        evaluated_df,
        OUTPUT_DIR / "anomaly_score_distribution.png",
    )

    print("\nEvaluation completed.")
    print("Review the in-sample normal evaluation limitation before interpreting results.")


if __name__ == "__main__":
    main()
