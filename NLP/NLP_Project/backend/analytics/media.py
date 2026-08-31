import re
import pandas as pd


def detect_media_type(message):
    """
    Identify the type of media in a WhatsApp message.
    """

    if not isinstance(message, str):
        return "text"

    message = message.lower().strip()

    # --------------------------------------------
    # Media omitted
    # --------------------------------------------

    if "<media omitted>" in message:
        return "media"

    # --------------------------------------------
    # Images
    # --------------------------------------------

    image_extensions = (
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
        ".webp",
        ".heic"
    )

    if any(
        extension in message
        for extension in image_extensions
    ):
        return "image"

    # --------------------------------------------
    # Videos
    # --------------------------------------------

    video_extensions = (
        ".mp4",
        ".mov",
        ".avi",
        ".mkv",
        ".3gp",
        ".webm"
    )

    if any(
        extension in message
        for extension in video_extensions
    ):
        return "video"

    # --------------------------------------------
    # Audio / Voice messages
    # --------------------------------------------

    audio_extensions = (
        ".mp3",
        ".wav",
        ".m4a",
        ".ogg",
        ".opus",
        ".aac"
    )

    if any(
        extension in message
        for extension in audio_extensions
    ):
        return "audio"

    # --------------------------------------------
    # Documents
    # --------------------------------------------

    document_extensions = (
        ".pdf",
        ".doc",
        ".docx",
        ".xls",
        ".xlsx",
        ".ppt",
        ".pptx",
        ".txt",
        ".csv",
        ".zip"
    )

    if any(
        extension in message
        for extension in document_extensions
    ):
        return "document"

    # --------------------------------------------
    # Stickers
    # --------------------------------------------

    if (
        "sticker" in message
        or ".webp" in message
    ):
        return "sticker"

    # --------------------------------------------
    # GIF
    # --------------------------------------------

    if (
        ".gif" in message
        or "gif" in message
    ):
        return "gif"

    # --------------------------------------------
    # Normal text
    # --------------------------------------------

    return "text"


def calculate_media(df):
    """
    Calculate media statistics from a processed
    WhatsApp DataFrame.

    Required columns:
        sender
        message
    """

    df = df.copy()

    # --------------------------------------------
    # Detect media type
    # --------------------------------------------

    df["media_type"] = (
        df["message"]
        .apply(detect_media_type)
    )

    # --------------------------------------------
    # Is media?
    # --------------------------------------------

    media_types = [
        "media",
        "image",
        "video",
        "audio",
        "document",
        "sticker",
        "gif"
    ]

    df["is_media"] = (
        df["media_type"]
        .isin(media_types)
    )

    # --------------------------------------------
    # Total media
    # --------------------------------------------

    total_media = int(
        df["is_media"].sum()
    )

    # --------------------------------------------
    # Media by type
    # --------------------------------------------

    media_counts = (
        df[df["is_media"]]["media_type"]
        .value_counts()
        .to_dict()
    )

    # Make sure all requested types exist
    media_by_type = {
        "images": int(
            media_counts.get("image", 0)
        ),

        "videos": int(
            media_counts.get("video", 0)
        ),

        "audio": int(
            media_counts.get("audio", 0)
        ),

        "documents": int(
            media_counts.get("document", 0)
        ),

        "stickers": int(
            media_counts.get("sticker", 0)
        ),

        "gifs": int(
            media_counts.get("gif", 0)
        ),

        "other_media": int(
            media_counts.get("media", 0)
        )
    }

    # --------------------------------------------
    # Media sent by each person
    # --------------------------------------------

    media_by_person = (
        df[df["is_media"]]
        .groupby("sender")
        .size()
        .to_dict()
    )

    media_by_person = {
        person: int(count)
        for person, count
        in media_by_person.items()
    }

    # --------------------------------------------
    # Total messages per participant
    # --------------------------------------------

    messages_by_person = (
        df.groupby("sender")
        .size()
    )

    # --------------------------------------------
    # Media percentage per participant
    # --------------------------------------------

    media_percentage_per_person = {}

    for person, total_messages in (
        messages_by_person.items()
    ):

        person_media = media_by_person.get(
            person,
            0
        )

        percentage = (
            person_media / total_messages
        ) * 100

        media_percentage_per_person[person] = round(
            percentage,
            2
        )

    # --------------------------------------------
    # Final result
    # --------------------------------------------

    media_statistics = {

        "total_media": total_media,

        "media_by_person": media_by_person,

        "media_by_type": media_by_type,

        "media_percentage_per_person":
            media_percentage_per_person
    }

    return media_statistics