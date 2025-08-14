from io import StringIO
from pathlib import Path

import pytest

from chatscroll.parser import ChatParser


@pytest.fixture
def resolve_path():
    """
    Returns a function to resolve file paths relative to this test file.

    Usage:
        file = resolve_path("app.py")
    """
    base_dir = Path(__file__).parent.parent  # directory containing the test file

    def _resolve(relative_path: str) -> Path:
        return base_dir / relative_path

    return _resolve


@pytest.fixture
def parse_chat(resolve_path):
    """
    Parses a Chat file into a ChatParser object and returns it. Automatically resolves relative paths.

    Usage:
        parser = parse_chat("sample_chat.txt")
    """
    def _parse(filename: str):
        fp = resolve_path(filename)
        with fp.open("r", encoding="utf-8") as f_obj:
            f = StringIO(f_obj.read())
        parser = ChatParser(f)
        return parser
    return _parse