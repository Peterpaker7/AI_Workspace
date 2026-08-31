from pathlib import Path
import joblib


# ============================================================
# LOAD TRAINED MODEL
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

MODEL_PATH = BASE_DIR / "model.pkl"

model = joblib.load(MODEL_PATH)


# ============================================================
# SINGLE MESSAGE FLIRT SCORE
# ============================================================

def predict_flirt_probability(text):

    if not isinstance(text, str):
        text = str(text)

    text = text.strip()

    if not text:
        return 0.0

    probabilities = model.predict_proba([text])[0]

    # Assumes:
    # 0 = non-flirt
    # 1 = flirt

    flirt_probability = probabilities[1]

    return round(
        float(flirt_probability * 100),
        2
    )


# ============================================================
# CONVERSATION FLIRT SCORE
# ============================================================

def calculate_conversation_score(messages):

    if not messages:
        return 0.0

    scores = []

    for message in messages:

        if not isinstance(message, str):
            continue

        message = message.strip()

        if not message:
            continue

        score = predict_flirt_probability(
            message
        )

        scores.append(score)

    if not scores:
        return 0.0

    conversation_score = sum(scores) / len(scores)

    return round(
        conversation_score,
        2
    )