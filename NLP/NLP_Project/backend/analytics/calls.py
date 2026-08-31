import re
import pandas as pd


# ============================================================
# CALL DETECTION
# ============================================================

def detect_call_type(message):
    """
    Detect the type of WhatsApp call from message text.

    Returns:
        missed
        incoming
        outgoing
        call
        None
    """

    if not isinstance(message, str):
        return None

    text = message.lower().strip()

    # --------------------------------------------------------
    # Missed calls
    # --------------------------------------------------------

    if "missed voice call" in text:
        return "missed"

    if "missed video call" in text:
        return "missed"

    if "missed call" in text:
        return "missed"

    # --------------------------------------------------------
    # Outgoing calls
    # --------------------------------------------------------

    outgoing_patterns = [
        "outgoing voice call",
        "outgoing video call",
        "you made a voice call",
        "you made a video call",
        "voice call, outgoing",
        "video call, outgoing"
    ]

    for pattern in outgoing_patterns:

        if pattern in text:
            return "outgoing"

    # --------------------------------------------------------
    # Incoming calls
    # --------------------------------------------------------

    incoming_patterns = [
        "incoming voice call",
        "incoming video call",
        "voice call, incoming",
        "video call, incoming"
    ]

    for pattern in incoming_patterns:

        if pattern in text:
            return "incoming"

    # --------------------------------------------------------
    # Generic calls
    # --------------------------------------------------------

    if "voice call" in text:
        return "call"

    if "video call" in text:
        return "call"

    if "call ended" in text:
        return "call"

    if "call declined" in text:
        return "call"

    if "call started" in text:
        return "call"

    return None


# ============================================================
# CALL ANALYTICS
# ============================================================

def calculate_calls(df):
    """
    Calculate WhatsApp call statistics.

    Required columns:
        sender
        message
        datetime

    Returns:
        Dictionary containing call statistics.
    """

    df = df.copy()

    # --------------------------------------------------------
    # Detect call type
    # --------------------------------------------------------

    df["call_type"] = (
        df["message"]
        .apply(detect_call_type)
    )

    # --------------------------------------------------------
    # Keep only calls
    # --------------------------------------------------------

    calls_df = df[
        df["call_type"].notna()
    ].copy()

    # --------------------------------------------------------
    # Total calls
    # --------------------------------------------------------

    total_calls = len(calls_df)

    # --------------------------------------------------------
    # Missed calls
    # --------------------------------------------------------

    missed_calls = int(
        (calls_df["call_type"] == "missed").sum()
    )

    # --------------------------------------------------------
    # Incoming calls
    # --------------------------------------------------------

    incoming_calls = int(
        (calls_df["call_type"] == "incoming").sum()
    )

    # --------------------------------------------------------
    # Outgoing calls
    # --------------------------------------------------------

    outgoing_calls = int(
        (calls_df["call_type"] == "outgoing").sum()
    )

    # --------------------------------------------------------
    # Generic calls
    # --------------------------------------------------------

    generic_calls = int(
        (calls_df["call_type"] == "call").sum()
    )

    # --------------------------------------------------------
    # Calls per participant
    # --------------------------------------------------------

    calls_per_participant = (
        calls_df
        .groupby("sender")
        .size()
        .to_dict()
    )

    calls_per_participant = {
        person: int(count)
        for person, count
        in calls_per_participant.items()
    }

    # --------------------------------------------------------
    # Missed calls per participant
    # --------------------------------------------------------

    missed_calls_df = calls_df[
        calls_df["call_type"] == "missed"
    ]

    missed_calls_per_participant = (
        missed_calls_df
        .groupby("sender")
        .size()
        .to_dict()
    )

    missed_calls_per_participant = {
        person: int(count)
        for person, count
        in missed_calls_per_participant.items()
    }

    # --------------------------------------------------------
    # Calls by day
    # --------------------------------------------------------

    calls_by_day = {}

    if not calls_df.empty:

        calls_df["date"] = (
            calls_df["datetime"].dt.date
        )

        calls_by_day = (
            calls_df["date"]
            .value_counts()
            .sort_index()
            .to_dict()
        )

        calls_by_day = {
            str(date): int(count)
            for date, count
            in calls_by_day.items()
        }

    # --------------------------------------------------------
    # Calls by hour
    # --------------------------------------------------------

    calls_by_hour = {}

    if not calls_df.empty:

        calls_df["hour"] = (
            calls_df["datetime"].dt.hour
        )

        calls_by_hour = (
            calls_df["hour"]
            .value_counts()
            .sort_index()
            .to_dict()
        )

        calls_by_hour = {
            int(hour): int(count)
            for hour, count
            in calls_by_hour.items()
        }

    # --------------------------------------------------------
    # Most active calling day
    # --------------------------------------------------------

    if calls_by_day:

        most_active_calling_day = max(
            calls_by_day,
            key=calls_by_day.get
        )

    else:

        most_active_calling_day = None

    # --------------------------------------------------------
    # Most active calling hour
    # --------------------------------------------------------

    if calls_by_hour:

        most_active_calling_hour = max(
            calls_by_hour,
            key=calls_by_hour.get
        )

    else:

        most_active_calling_hour = None

    # --------------------------------------------------------
    # Final result
    # --------------------------------------------------------

    call_statistics = {

        "total_calls":
            total_calls,

        "missed_calls":
            missed_calls,

        "incoming_calls":
            incoming_calls,

        "outgoing_calls":
            outgoing_calls,

        "generic_calls":
            generic_calls,

        "calls_per_participant":
            calls_per_participant,

        "missed_calls_per_participant":
            missed_calls_per_participant,

        "calls_by_day":
            calls_by_day,

        "calls_by_hour":
            calls_by_hour,

        "most_active_calling_day":
            most_active_calling_day,

        "most_active_calling_hour":
            most_active_calling_hour
    }

    return call_statistics