import datetime
import json
import pathlib
import re

from collections import Counter
from typing import Any


class ChatParser:
    def __init__(self, path_to_chat: pathlib.Path, app) -> None:
        """

        :param path_to_chat:
        :param app:
        """
        self.path_to_chat: pathlib.Path = path_to_chat  # TODO: unzip if chat is uploaded zipped
        self.app: str = app
        self.chat: list[dict[str, Any]] = []
        self.raw_chat: str | Any = None
        self.participants: list[str] = []

    def parse_chat(self) -> None:
        """
        Parse chat file.
        """
        with open(self.path_to_chat, "r", encoding="utf-8") as f:
            lines = f.readlines()
            for line in lines:
                try:
                    # Separate timestamp from the rest; cast to datetime
                    timestamp_str, rest = line.split(" - ", 1)
                    timestamp = datetime.datetime.strptime(timestamp_str, '%d.%m.%Y, %H:%M')
                    # Process participant & message fields
                    participant, message = rest.split(":", 1)
                    participant = participant.strip()
                    message = message.strip()  # TODO: filter media & status change messages

                    self.chat.append({
                        "time": timestamp_str,
                        "participant": participant,
                        "message": message
                    })

                except ValueError:
                    participant, message = None, None

    # TODO: set participants
    @property
    def participants(self) -> list[str]:
        return self.participants

    # TODO: some method to print the json
    def print_chat(self) -> None:
        pass
