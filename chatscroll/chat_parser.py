import datetime
import json
import pathlib
import re

from collections import Counter
from typing import Any


class ChatParser:
    def __init__(self, path_to_chat: pathlib.Path, app) -> None:
        self.path_to_chat: pathlib.Path = path_to_chat
        self.app: str = app
        self.chat: list[dict[str, Any]] = []
        self.raw_chat: str | Any = None
        self.participants: list[str] = []
        self.metadata: dict[str, Any] = {}

    def parse_chat(self):
        print("Parsing chat...")
