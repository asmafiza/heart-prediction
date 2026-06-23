"""
Train a Random Forest classifier on the UCI Heart Disease dataset.
Saves the model to models/model.pkl for use by the GUI app.

Usage:
    python src/train_model.py
    python src/train_model.py --data data/heart.csv
"""

import argparse
import os
import pickle
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix


FEATURE_COLS = [
    "age", "sex", "bmi", "trestbps", "chol", "thalach",
    "thalach_max", "oldpeak", "fbs", "exang", "ca",
    "diabetes", "famhist", "cp", "restecg", "slope", "thal", "smoking"
]
TARGET_COL = "target"


def load_and_preprocess(csv_path: str) -> tuple:
    """Load CSV, encode categoricals, return X, y."""
    df = pd.read_csv(csv_path)

    # Encode any string columns
    for col in df.select_dtypes(include="object").columns:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col].astype(str))

    available = [c for c in FEATURE_COLS if c in df.columns]
    X = df[available]
    y = df[TARGET_COL]
    return X, y


def train(csv_path: str, model_output: str):
    print(f"[Train] Loading data from: {csv_path}")
    X, y = load_and_preprocess(csv_path)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"[Train] {len(X_train)} train | {len(X_test)} test samples")

    clf = RandomForestClassifier(
        n_estimators=200,
        max_depth=8,
        min_samples_leaf=4,
        random_state=42,
        n_jobs=-1
    )
    clf.fit(X_train, y_train)

    # Cross-validation
    cv_scores = cross_val_score(clf, X, y, cv=5, scoring="roc_auc")
    print(f"[Train] 5-fold CV AUC: {cv_scores.mean():.3f} ± {cv_scores.std():.3f}")

    # Test set report
    y_pred = clf.predict(X_test)
    print("\n[Train] Classification Report:")
    print(classification_report(y_test, y_pred))
    print("[Train] Confusion Matrix:")
    print(confusion_matrix(y_test, y_pred))

    # Feature importance
    importances = sorted(
        zip(X.columns, clf.feature_importances_),
        key=lambda x: x[1], reverse=True
    )
    print("\n[Train] Feature importances:")
    for name, imp in importances:
        print(f"  {name:<20} {imp:.4f}")

    # Save
    os.makedirs(os.path.dirname(model_output), exist_ok=True)
    with open(model_output, "wb") as f:
        pickle.dump(clf, f)
    print(f"\n[Train] Model saved to: {model_output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data",  default="data/heart.csv",
                        help="Path to training CSV")
    parser.add_argument("--model", default="models/model.pkl",
                        help="Output path for trained model")
    args = parser.parse_args()
    train(args.data, args.model)
