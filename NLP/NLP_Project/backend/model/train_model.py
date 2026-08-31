import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

from sklearn.pipeline import Pipeline

from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)

import joblib


# ============================================================
# 1. LOAD DATASET
# ============================================================

DATASET_PATH = "C:\\Users\\USER\\OneDrive\\Desktop\\Full Stack AI Development\\NLP\\NLP_Project\\dataset\\flirting_rated.csv"

df = pd.read_csv(DATASET_PATH)


print("\n========== DATASET ==========\n")

print(df.head())

print("\nDataset shape:")
print(df.shape)

print("\nClass distribution:")
print(df["label"].value_counts())


# ============================================================
# 2. CLEAN DATA
# ============================================================

df = df.dropna(
    subset=["text", "label"]
)

df["text"] = (
    df["text"]
    .astype(str)
    .str.strip()
)

df["label"] = (
    df["label"]
    .astype(int)
)


# ============================================================
# 3. FEATURES AND TARGET
# ============================================================

X = df["text"]

y = df["label"]


# ============================================================
# 4. TRAIN / TEST SPLIT
# ============================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)


print("\nTraining samples:", len(X_train))
print("Testing samples:", len(X_test))


# ============================================================
# 5. TF-IDF + LOGISTIC REGRESSION
# ============================================================

model = Pipeline([

    (
        "tfidf",

        TfidfVectorizer(
            lowercase=True,
            ngram_range=(1, 2),
            max_features=10000,
            sublinear_tf=True
        )
    ),

    (
        "classifier",

        LogisticRegression(
            max_iter=1000,
            class_weight="balanced"
        )
    )
])


# ============================================================
# 6. TRAIN
# ============================================================

print("\nTraining model...")

model.fit(
    X_train,
    y_train
)


# ============================================================
# 7. PREDICTION
# ============================================================

y_pred = model.predict(
    X_test
)


# ============================================================
# 8. EVALUATION
# ============================================================

accuracy = accuracy_score(
    y_test,
    y_pred
)

print("\n========== MODEL PERFORMANCE ==========\n")

print(
    f"Accuracy: {accuracy:.4f}"
)

print("\nClassification Report:")

print(
    classification_report(
        y_test,
        y_pred,
        target_names=[
            "Non-Flirt",
            "Flirt"
        ]
    )
)

print("\nConfusion Matrix:")

print(
    confusion_matrix(
        y_test,
        y_pred
    )
)


# ============================================================
# 9. SAVE MODEL
# ============================================================

MODEL_PATH = "model.pkl"

joblib.dump(
    model,
    MODEL_PATH
)

print(
    f"\nModel saved to: {MODEL_PATH}"
)