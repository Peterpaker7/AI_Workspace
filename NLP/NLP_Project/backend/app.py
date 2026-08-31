from flask import Flask, request, jsonify
from flask_cors import CORS

import os
import tempfile

from parser.message_processor import parse_whatsapp_chat, process_dataframe

from analytics.statstics import calculate_statistics
from analytics.activity import calculate_activity
from analytics.media import calculate_media
from analytics.calls import calculate_calls

from model.flirt_model import (
    predict_flirt_probability,
    calculate_conversation_score
)


# ============================================================
# FLASK APP
# ============================================================

app = Flask(__name__)

CORS(app)


# ============================================================
# HOME
# ============================================================

@app.route("/", methods=["GET"])
def home():

    return jsonify({
        "status": "running",
        "message": "WhatsApp Chat Analyzer API"
    })


# ============================================================
# HEALTH CHECK
# ============================================================

@app.route("/health", methods=["GET"])
def health():

    return jsonify({
        "status": "ok"
    })


# ============================================================
# ANALYZE CHAT
# ============================================================

@app.route("/analyze", methods=["POST"])
def analyze_chat():

    # --------------------------------------------------------
    # Check file
    # --------------------------------------------------------

    if "file" not in request.files:

        return jsonify({
            "error": "No chat file provided"
        }), 400

    file = request.files["file"]

    if file.filename == "":

        return jsonify({
            "error": "No file selected"
        }), 400

    # --------------------------------------------------------
    # Validate extension
    # --------------------------------------------------------

    if not file.filename.lower().endswith(".txt"):

        return jsonify({
            "error": "Only .txt WhatsApp exports are supported"
        }), 400

    temp_path = None

    try:

        # ----------------------------------------------------
        # Save uploaded file temporarily
        # ----------------------------------------------------

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".txt"
        ) as temp_file:

            file.save(temp_file.name)

            temp_path = temp_file.name

        # ----------------------------------------------------
        # Parse WhatsApp chat
        # ----------------------------------------------------

        df = parse_whatsapp_chat(
            temp_path
        )

        # ----------------------------------------------------
        # Process messages
        # ----------------------------------------------------

        df = process_dataframe(
            df
        )

        # ----------------------------------------------------
        # Remove system messages
        # ----------------------------------------------------

        if "is_system" in df.columns:

            df = df[
                df["is_system"] == False
            ].copy()

        # ----------------------------------------------------
        # STATISTICS
        # ----------------------------------------------------

        statistics = calculate_statistics(
            df
        )

        # ----------------------------------------------------
        # ACTIVITY
        # ----------------------------------------------------

        activity = calculate_activity(
            df
        )

        # ----------------------------------------------------
        # MEDIA
        # ----------------------------------------------------

        media = calculate_media(
            df
        )

        # ----------------------------------------------------
        # CALLS
        # ----------------------------------------------------

        calls = calculate_calls(
            df
        )

        # ----------------------------------------------------
        # FLIRT ANALYSIS
        # ----------------------------------------------------

        flirt_messages = []

        for _, row in df.iterrows():

            message = row.get(
                "message",
                ""
            )

            # Don't send media/call messages
            # to the text classifier

            if not isinstance(
                message,
                str
            ):
                continue

            message = message.strip()

            if not message:
                continue

            # Skip media
            if row.get(
                "is_media",
                False
            ):
                continue

            # Skip calls
            if row.get(
                "is_call",
                False
            ):
                continue

            score = predict_flirt_probability(
                message
            )

            flirt_messages.append({

                "sender": row.get(
                    "sender"
                ),

                "message": message,

                "flirt_score": score
            })

        # ----------------------------------------------------
        # Conversation flirt score
        # ----------------------------------------------------

        message_scores = [
            item["flirt_score"]
            for item in flirt_messages
        ]

        conversation_flirt_score = (
            calculate_conversation_score(
                [
                    item["message"]
                    for item in flirt_messages
                ]
            )
        )

        flirt = {

            "conversation_flirt_score":
                conversation_flirt_score,

            "messages_analyzed":
                len(message_scores),

            "messages": flirt_messages
        }

        # ----------------------------------------------------
        # Combined response
        # ----------------------------------------------------

        result = {

            "statistics":
                statistics,

            "activity":
                activity,

            "media":
                media,

            "calls":
                calls,

            "flirt":
                flirt
        }

        return jsonify(result)

    except Exception as e:

        print(
            "ERROR:",
            str(e)
        )

        return jsonify({
            "error": str(e)
        }), 500

    finally:

        # ----------------------------------------------------
        # Delete temporary file
        # ----------------------------------------------------

        if temp_path and os.path.exists(
            temp_path
        ):

            os.remove(
                temp_path
            )


# ============================================================
# RUN SERVER
# ============================================================

if __name__ == "__main__":

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )