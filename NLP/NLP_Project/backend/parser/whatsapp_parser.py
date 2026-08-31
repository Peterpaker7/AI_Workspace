import re
import pandas as pd


def parse_whatsapp_chat(file_path):

    messages = []

    # Common WhatsApp format:
    # 31/08/26, 10:30 pm - Mukesh: Hello bro

    pattern = re.compile(
        r'^(\d{1,2}/\d{1,2}/\d{2,4}),\s*'
        r'(\d{1,2}:\d{2}(?:\s?[APap][Mm])?)\s*-\s*'
        r'([^:]+):\s*(.*)$'
    )

    current_message = None

    with open(file_path, "r", encoding="utf-8") as file:

        for line in file:

            line = line.rstrip("\n")

            match = pattern.match(line)

            if match:

                # Save previous message
                if current_message is not None:
                    messages.append(current_message)

                date, time, name, message = match.groups()

                current_message = {
                    "Date": date,
                    "Time": time,
                    "Name": name.strip(),
                    "Chat": message.strip()
                }

            else:

                # This can be a continuation of a previous message
                if current_message is not None:
                    current_message["Chat"] += " " + line.strip()

    # Add last message
    if current_message is not None:
        messages.append(current_message)

    return pd.DataFrame(messages)





