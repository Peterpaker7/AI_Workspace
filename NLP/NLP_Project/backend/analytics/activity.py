import pandas as pd


def calculate_activity(df):
    """
    Calculate activity patterns from a WhatsApp chat DataFrame.

    Required columns:
        datetime

    Returns:
        Dictionary containing:
        - most_active_day
        - most_active_date
        - most_active_hour
        - messages_per_day
        - messages_per_hour
        - messages_by_weekday
        - activity_by_period
    """

    # --------------------------------------------------
    # Create a copy
    # --------------------------------------------------

    df = df.copy()

    # --------------------------------------------------
    # Make sure datetime is datetime
    # --------------------------------------------------

    df["datetime"] = pd.to_datetime(
        df["datetime"],
        errors="coerce"
    )

    # Remove invalid datetime rows
    df = df.dropna(subset=["datetime"])

    # If there is no valid data
    if df.empty:
        return {
            "most_active_day": None,
            "most_active_date": None,
            "most_active_hour": None,
            "messages_per_day": {},
            "messages_per_hour": {},
            "messages_by_weekday": {},
            "activity_by_period": {}
        }

    # --------------------------------------------------
    # Extract useful time information
    # --------------------------------------------------

    df["date"] = df["datetime"].dt.date

    df["day"] = df["datetime"].dt.day_name()

    df["hour"] = df["datetime"].dt.hour

    # --------------------------------------------------
    # 1. Messages per day
    # --------------------------------------------------

    messages_per_day = (
        df["date"]
        .value_counts()
        .sort_index()
        .to_dict()
    )

    messages_per_day = {
        str(date): int(count)
        for date, count in messages_per_day.items()
    }

    # --------------------------------------------------
    # 2. Messages per hour
    # --------------------------------------------------

    messages_per_hour = (
        df["hour"]
        .value_counts()
        .sort_index()
        .to_dict()
    )

    messages_per_hour = {
        int(hour): int(count)
        for hour, count in messages_per_hour.items()
    }

    # --------------------------------------------------
    # 3. Messages by weekday
    # --------------------------------------------------

    weekday_order = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday"
    ]

    weekday_counts = (
        df["day"]
        .value_counts()
    )

    messages_by_weekday = {
        day: int(
            weekday_counts.get(day, 0)
        )
        for day in weekday_order
    }

    # --------------------------------------------------
    # 4. Most active date
    # --------------------------------------------------

    most_active_date = max(
        messages_per_day,
        key=messages_per_day.get
    )

    # --------------------------------------------------
    # 5. Most active day
    # --------------------------------------------------

    most_active_day = max(
        messages_by_weekday,
        key=messages_by_weekday.get
    )

    # --------------------------------------------------
    # 6. Most active hour
    # --------------------------------------------------

    most_active_hour = max(
        messages_per_hour,
        key=messages_per_hour.get
    )

    # --------------------------------------------------
    # 7. Optional time periods
    #
    # 05:00 - 11:59 → Morning
    # 12:00 - 16:59 → Afternoon
    # 17:00 - 20:59 → Evening
    # 21:00 - 04:59 → Night
    # --------------------------------------------------

    def get_time_period(hour):

        if 5 <= hour < 12:
            return "morning"

        elif 12 <= hour < 17:
            return "afternoon"

        elif 17 <= hour < 21:
            return "evening"

        else:
            return "night"

    df["period"] = df["hour"].apply(
        get_time_period
    )

    period_order = [
        "morning",
        "afternoon",
        "evening",
        "night"
    ]

    period_counts = (
        df["period"]
        .value_counts()
    )

    activity_by_period = {
        period: int(
            period_counts.get(period, 0)
        )
        for period in period_order
    }

    # --------------------------------------------------
    # Final result
    # --------------------------------------------------

    activity = {

        "most_active_day":
            most_active_day,

        "most_active_date":
            str(most_active_date),

        "most_active_hour":
            int(most_active_hour),

        "messages_per_day":
            messages_per_day,

        "messages_per_hour":
            messages_per_hour,

        "messages_by_weekday":
            messages_by_weekday,

        "activity_by_period":
            activity_by_period
    }

    return activity