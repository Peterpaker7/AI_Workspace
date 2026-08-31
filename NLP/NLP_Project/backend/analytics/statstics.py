import pandas as pd


def calculate_statistics(df):
    """
    Calculate basic statistics for a WhatsApp chat.
    """

    # --------------------------------------------------
    # Total messages
    # --------------------------------------------------

    total_messages = len(df)

    # --------------------------------------------------
    # Participants
    # --------------------------------------------------

    participants = df["sender"].nunique()

    # --------------------------------------------------
    # Messages per person
    # --------------------------------------------------

    messages_per_person = (
        df["sender"]
        .value_counts()
        .to_dict()
    )

    # --------------------------------------------------
    # Most talkative person
    # --------------------------------------------------

    if messages_per_person:
        most_talkative = max(
            messages_per_person,
            key=messages_per_person.get
        )
    else:
        most_talkative = None

    # --------------------------------------------------
    # Total words
    # --------------------------------------------------

    total_words = int(
        df["word_count"].sum()
    )

    # --------------------------------------------------
    # Words per person
    # --------------------------------------------------

    words_per_person = (
        df.groupby("sender")["word_count"]
        .sum()
        .astype(int)
        .to_dict()
    )

    # --------------------------------------------------
    # Average message length
    # --------------------------------------------------

    average_message_length = (
        df.groupby("sender")["word_count"]
        .mean()
        .round(2)
        .to_dict()
    )

    # --------------------------------------------------
    # Longest message
    # --------------------------------------------------

    if not df.empty:

        longest_index = df["char_count"].idxmax()

        longest_message = {
            "sender": df.loc[
                longest_index, "sender"
            ],
            "message": df.loc[
                longest_index, "message"
            ],
            "word_count": int(
                df.loc[
                    longest_index, "word_count"
                ]
            ),
            "char_count": int(
                df.loc[
                    longest_index, "char_count"
                ]
            )
        }

    else:

        longest_message = None

    # --------------------------------------------------
    # Shortest message
    # --------------------------------------------------

    # Ignore completely empty messages
    non_empty_df = df[
        df["message"].str.strip() != ""
    ]

    if not non_empty_df.empty:

        shortest_index = non_empty_df[
            "char_count"
        ].idxmin()

        shortest_message = {
            "sender": non_empty_df.loc[
                shortest_index, "sender"
            ],
            "message": non_empty_df.loc[
                shortest_index, "message"
            ],
            "word_count": int(
                non_empty_df.loc[
                    shortest_index, "word_count"
                ]
            ),
            "char_count": int(
                non_empty_df.loc[
                    shortest_index, "char_count"
                ]
            )
        }

    else:

        shortest_message = None

    # --------------------------------------------------
    # Final result
    # --------------------------------------------------

    statistics = {
        "total_messages": total_messages,
        "participants": participants,
        "messages_per_person": messages_per_person,
        "most_talkative": most_talkative,
        "total_words": total_words,
        "words_per_person": words_per_person,
        "average_message_length": average_message_length,
        "longest_message": longest_message,
        "shortest_message": shortest_message
    }

    return statistics