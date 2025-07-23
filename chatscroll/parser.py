import datetime
import re

from io import StringIO
from typing import Any


# Timestamp parsing utils
_TIMESTAMP_FORMATS = [
    '%d.%m.%Y, %H:%M',
    '%d/%m/%Y, %H:%M',
    '%d/%m/%y, %H:%M',
]

def parse_timestamp(timestamp_str: str) -> datetime.datetime:
    for fmt in _TIMESTAMP_FORMATS:
        try:
            return datetime.datetime.strptime(timestamp_str.strip(), fmt)
        except ValueError:
            continue
    raise ValueError(f"Unrecognized timestamp format: {timestamp_str}")


class ChatParser:
    """
    A parser for exported chat logs from messaging apps like WhatsApp or Telegram.

    After initialization, the parsed messages and users (users) are available via
    the `chat` and `users` attributes.
    """
    def __init__(self, chat_file: StringIO, app=None) -> None:
        """
        Args:
            chat_file (StringIO):
                A text file in string format.
            app (str):
                Name of the app from where the chat log was exported. Whatsapp by default; Telegram support to be
                implemented.
        """
        self.chat_file: StringIO = chat_file  # TODO: unzip if chat is uploaded zipped
        self.app: str | Any = app
        self.chat: list[dict[str, Any]] = []
        self.users: list[str] = []
        self.parse_chat()

    def parse_chat(self) -> None:  # TODO: telegram support
        """
        Parse the chat file and extract timestamped messages and user names.

        Ignores lines that don't match the expected format (e.g., system messages,
        broken lines).
        """
        # Init user container
        users: set[str] = set()

        # Iterate over file object
        lines = self.chat_file.readlines()
        for line in lines:
            line = line.strip()

            try:
                # Separate timestamp from the rest; cast to datetime
                timestamp_str, rest = line.split(" - ", 1)
                timestamp = parse_timestamp(timestamp_str)

                # Process user & message fields
                # TODO: manage line breaks as part of a single message
                user, message = rest.split(":", 1)
                user = user.strip()
                message = re.sub(r'<[^>]+>', '', message.strip()).strip()

                # Skip empty messages
                if not message:
                    continue

                # Store elements in chat and user containers
                users.add(user)
                self.chat.append({
                    "time": timestamp,
                    "user": user,
                    "message": message
                })
            except ValueError:
                continue

        self.users = list(sorted(users))

