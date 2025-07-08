import datetime
import json
import re

from collections import Counter
from typing import Any
from pathlib import Path


class ChatExportReader:
    def __init__(self, chat_export_file, app) -> None:
        self.chat_export_file: str = chat_export_file
        self.app: str = app
        self.file_extension: str = chat_export_file.split(".")[-1]
        self.conversation: list[dict[str, Any]] = []
        self.raw_conversation: str | Any = None
        self.senders: list[str] = []
        self.metadata: dict[str, Any] = {}
