import re
import pandas as pd


# ============================================================
# 1. WHATSAPP MESSAGE PATTERN
# ============================================================

MESSAGE_PATTERN = re.compile(
    r"^(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}),\s*"
    r"(\d{1,2}:\d{2}(?::\d{2})?\s*(?:[APap][Mm])?)\s*-\s*"
    r"(.*)$"
)


# ============================================================
# 2. SYSTEM MESSAGE DETECTION
# ============================================================

SYSTEM_PATTERNS = [
    r"Messages are end-to-end encrypted",
    r"You added .+",
    r"You removed .+",
    r".+ added .+",
    r".+ removed .+",
    r".+ left",
    r".+ joined using this group's invite link",
    r".+ changed the group subject",
    r".+ changed the group icon",
    r".+ changed this group's settings",
    r".+ changed the group description",
    r"You changed the group subject",
    r"You changed the group icon",
    r"You changed this group's settings",
    r"You changed the group description",
    r"Waiting for this message",
]


def is_system_message(text):
    """
    Check whether a line is a WhatsApp system message.
    """

    for pattern in SYSTEM_PATTERNS:

        if re.search(pattern, text, re.IGNORECASE):
            return True

    return False


# ============================================================
# 3. MEDIA DETECTION
# ============================================================

MEDIA_PATTERNS = [
    r"<Media omitted>",
    r"<attached:.*\.(jpg|jpeg|png|gif|webp)>",
    r"<attached:.*\.(mp4|mov|avi|mkv)>",
    r"<attached:.*\.(mp3|wav|m4a|ogg)>",
    r"<attached:.*\.(pdf|doc|docx|xls|xlsx|ppt|pptx)>",
]


def detect_media(text):

    for pattern in MEDIA_PATTERNS:

        if re.search(pattern, text, re.IGNORECASE):
            return True

    return False


# ============================================================
# 4. CALL DETECTION
# ============================================================

CALL_PATTERNS = [
    r"missed voice call",
    r"missed video call",
    r"voice call",
    r"video call",
    r"call ended",
    r"call declined",
    r"call started",
]


def detect_call(text):

    for pattern in CALL_PATTERNS:

        if re.search(pattern, text, re.IGNORECASE):
            return True

    return False


def detect_missed_call(text):

    if re.search(r"missed .*call", text, re.IGNORECASE):
        return True

    return False


# ============================================================
# 5. DELETED MESSAGE DETECTION
# ============================================================

DELETED_PATTERNS = [
    "This message was deleted",
    "You deleted this message"
]


def detect_deleted_message(text):

    for pattern in DELETED_PATTERNS:

        if pattern.lower() in text.lower():
            return True

    return False


# ============================================================
# 6. MESSAGE TYPE
# ============================================================

def get_message_type(
    message,
    is_media,
    is_call,
    is_missed_call,
    is_deleted,
    is_system
):

    if is_system:
        return "system"

    if is_missed_call:
        return "missed_call"

    if is_call:
        return "call"

    if is_media:
        return "media"

    if is_deleted:
        return "deleted"

    if message.strip() == "":
        return "empty"

    return "text"


# ============================================================
# 7. CLEAN MESSAGE
# ============================================================

def clean_message(text):

    if not isinstance(text, str):
        return ""

    # Remove unnecessary whitespace
    text = re.sub(r"\s+", " ", text)

    return text.strip()


# ============================================================
# 8. PARSE WHATSAPP CHAT
# ============================================================

def parse_whatsapp_chat(file_path):

    messages = []

    current_message = None

    with open(
        file_path,
        "r",
        encoding="utf-8"
    ) as file:

        for raw_line in file:

            line = raw_line.rstrip("\n\r")

            match = MESSAGE_PATTERN.match(line)

            # ------------------------------------------------
            # New WhatsApp message
            # ------------------------------------------------

            if match:

                # Save previous message
                if current_message is not None:
                    messages.append(current_message)

                date = match.group(1)
                time = match.group(2)
                content = match.group(3)

                # --------------------------------------------
                # Separate sender and message
                # --------------------------------------------

                if ": " in content:

                    sender, message = content.split(
                        ": ",
                        1
                    )

                elif ":" in content:

                    sender, message = content.split(
                        ":",
                        1
                    )

                else:

                    # System message
                    sender = None
                    message = content

                current_message = {
                    "date": date,
                    "time": time,
                    "sender": (
                        sender.strip()
                        if sender
                        else None
                    ),
                    "message": clean_message(message)
                }

            # ------------------------------------------------
            # Multiline message
            # ------------------------------------------------

            else:

                if current_message is not None:

                    continuation = clean_message(line)

                    if continuation:

                        current_message["message"] += (
                            " " + continuation
                        )

        # Save final message
        if current_message is not None:
            messages.append(current_message)

    return pd.DataFrame(messages)


# ============================================================
# 9. PROCESS DATAFRAME
# ============================================================

def process_dataframe(df):

    # --------------------------------------------------------
    # Clean message
    # --------------------------------------------------------

    df["message"] = (
        df["message"]
        .fillna("")
        .apply(clean_message)
    )

    # --------------------------------------------------------
    # System message
    # --------------------------------------------------------

    df["is_system"] = (
        df["sender"]
        .isna()
    )

    # Also check message text
    df.loc[
        df["message"].apply(is_system_message),
        "is_system"
    ] = True

    # --------------------------------------------------------
    # Media
    # --------------------------------------------------------

    df["is_media"] = (
        df["message"]
        .apply(detect_media)
    )

    # --------------------------------------------------------
    # Calls
    # --------------------------------------------------------

    df["is_call"] = (
        df["message"]
        .apply(detect_call)
    )

    # --------------------------------------------------------
    # Missed calls
    # --------------------------------------------------------

    df["is_missed_call"] = (
        df["message"]
        .apply(detect_missed_call)
    )

    # --------------------------------------------------------
    # Deleted messages
    # --------------------------------------------------------

    df["is_deleted"] = (
        df["message"]
        .apply(detect_deleted_message)
    )

    # --------------------------------------------------------
    # Message type
    # --------------------------------------------------------

    df["message_type"] = df.apply(
        lambda row: get_message_type(
            row["message"],
            row["is_media"],
            row["is_call"],
            row["is_missed_call"],
            row["is_deleted"],
            row["is_system"]
        ),
        axis=1
    )

    # --------------------------------------------------------
    # Datetime
    # --------------------------------------------------------

    df["datetime"] = pd.to_datetime(
        df["date"] + " " + df["time"],
        dayfirst=True,
        errors="coerce"
    )

    # --------------------------------------------------------
    # Word count
    # --------------------------------------------------------

    df["word_count"] = (
        df["message"]
        .apply(
            lambda x: len(x.split())
            if x.strip()
            else 0
        )
    )

    # --------------------------------------------------------
    # Character count
    # --------------------------------------------------------

    df["char_count"] = (
        df["message"]
        .apply(len)
    )

    return df


# ============================================================
# 10. MAIN
# ============================================================

if __name__ == "__main__":

    file_path = "whatsapp_chat_sridhar_kasc.txt"

    # Parse raw WhatsApp file
    whatsapp_data_chat = parse_whatsapp_chat(
        file_path
    )

    # Process DataFrame
    whatsapp_data_chat = process_dataframe(
        whatsapp_data_chat
    )

    # --------------------------------------------------------
    # Remove system messages
    # --------------------------------------------------------

    whatsapp_data_chat = whatsapp_data_chat[
        whatsapp_data_chat["is_system"] == False
    ].copy()

    # --------------------------------------------------------
    # Final columns
    # --------------------------------------------------------

    whatsapp_data_chat = whatsapp_data_chat[
        [
            "date",
            "time",
            "datetime",
            "sender",
            "message",
            "message_type",
            "is_media",
            "is_call",
            "is_missed_call",
            "is_deleted",
            "word_count",
            "char_count"
        ]
    ]

    # --------------------------------------------------------
    # Display
    # --------------------------------------------------------

    print("\n========== FIRST 10 MESSAGES ==========\n")

    print(
        whatsapp_data_chat.head(10).to_string(
            index=False
        )
    )

    print(
        "\n========== DATASET INFO ==========\n"
    )

    print(
        whatsapp_data_chat.info()
    )

    print(
        "\n========== MESSAGE TYPES ==========\n"
    )

    print(
        whatsapp_data_chat[
            "message_type"
        ].value_counts()
    )

    print(
        "\n========== MESSAGES PER PERSON ==========\n"
    )

    print(
        whatsapp_data_chat[
            "sender"
        ].value_counts()
    )

    print(
        "\n========== MEDIA COUNT ==========\n"
    )

    print(
        whatsapp_data_chat[
            "is_media"
        ].sum()
    )

    print(
        "\n========== CALL COUNT ==========\n"
    )

    print(
        whatsapp_data_chat[
            "is_call"
        ].sum()
    )

    print(
        "\n========== MISSED CALL COUNT ==========\n"
    )

    print(
        whatsapp_data_chat[
            "is_missed_call"
        ].sum()
    )