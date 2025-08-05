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

# TODO: Add Telegram support
# https://github.com/ramcarreno/chatscroll/issues/1
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

    def parse_chat(self) -> None:
        """
        Parse the chat file, supporting multi-line messages by splitting on timestamps.
        Groups message timestamps, sender users and message contents, filling chat and users containers.
        Filters system messages, ignoring messages with no text or sender.
        """
        # Create users set to add their names only once
        users: set[str] = set()

        # Start reading
        chat_text = self.chat_file.read()

        # Regex pattern to detect timestamps at the start of a message line
        # Start dividing between timestamp and rest of message
        timestamp_pattern = r'(\d{1,2}[./]\d{1,2}[./]\d{2,4}, \d{1,2}:\d{2}) - '
        parts = re.split(timestamp_pattern, chat_text)

        # Parts structure: ['', timestamp1, message1, timestamp2, message2, ...]
        # So we iterate in steps of 2 starting at index 1 (timestamps) and get messages at index+1
        for i in range(1, len(parts), 2):
            timestamp_str = parts[i]
            message_block = parts[i + 1].strip() if (i + 1) < len(parts) else ""

            # Parse timestamp into possible dates, skipping unparseable timestamps
            try:
                timestamp = parse_timestamp(timestamp_str)
            except ValueError:
                continue

            # Split user name from message, if no separator found skip (system message)
            if ':' not in message_block:
                continue

            user, message = message_block.split(':', 1)
            user = user.strip()
            message = message.strip()

            # Clean system messages such as <Media ommitted> and skip empty messages
            message = re.sub(r'<[^>]+>', '', message)
            if not message:
                continue

            # Store elements in chat and user containers
            users.add(user)
            self.chat.append({
                "time": timestamp,
                "user": user,
                "message": message
            })

        self.users = list(sorted(users))
