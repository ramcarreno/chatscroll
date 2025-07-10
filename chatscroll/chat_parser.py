import datetime
import pathlib
import re

from typing import Any


class ChatParser:
    """
    A parser for exported chat logs from messaging apps like WhatsApp or Telegram.

    After initialization, the parsed messages and participants (users) are available via
    the `chat` and `participants` attributes.
    """
    def __init__(self, path_to_chat: pathlib.Path, app) -> None:
        """
        Args:
            path_to_chat (pathlib.Path):
                A path to a chat log.
            app (str):
                Name of the app from where the chat log was exported. Whatsapp by default; Telegram support to be
                implemented.
        """
        self.path_to_chat: pathlib.Path = path_to_chat  # TODO: unzip if chat is uploaded zipped
        self.app: str = app
        self.chat: list[dict[str, Any]] = []
        self.participants: list[str] = []
        self.parse_chat()

    def parse_chat(self) -> None:  # TODO: telegram support
        """
        Parse the chat file and extract timestamped messages and participant names.

        Ignores lines that don't match the expected format (e.g., system messages,
        broken lines).
        """
        participants: set[str] = set()
        with open(self.path_to_chat, "r", encoding="utf-8") as f:
            lines = f.readlines()
            for line in lines:
                line = line.strip()

                try:
                    # Separate timestamp from the rest; cast to datetime
                    timestamp_str, rest = line.split(" - ", 1)
                    timestamp = datetime.datetime.strptime(timestamp_str, '%d.%m.%Y, %H:%M')

                    # Process participant & message fields
                    participant, message = rest.split(":", 1)
                    participant = participant.strip()
                    message = re.sub(r'<[^>]+>', '', message.strip()).strip()

                    # Skip empty messages
                    if not message:
                        continue

                    # Store elements in chat and participant containers
                    participants.add(participant)
                    self.chat.append({
                        "time": timestamp,
                        "participant": participant,
                        "message": message
                    })
                except ValueError:
                    continue

        self.participants = list(sorted(participants))

