from datetime import datetime

from langchain.schema import Document
from chatscroll.rag import ChatSplitter


def test_chunking(parse_chat):
    chat = parse_chat("sample_chat.txt").chat
    splitter = ChatSplitter(chunk_size=3, chunk_overlap=1, max_message_length=0)  # Instantiate a splitter
    chunks = splitter.split_messages(chat[:100])  # Take first 100 messages, without omissions
    assert len(chunks) == 50  # 100 / (3 - 1)
    assert all(isinstance(c, Document) for c in chunks)
    assert (chunks[0].page_content ==  # max_message_length=0, only date + sender + ... visible
            "2025-07-01 10:12 - Alex: ...\n2025-07-01 10:13 - Jamie: ...\n2025-07-01 10:14 - Sam: ...")


def test_truncate_message():
    long_msg = "X" * 100
    splitter = ChatSplitter(chunk_size=1, chunk_overlap=0, max_message_length=50)
    chunks = splitter.split_messages([
        {
            "time": datetime(2020, 1, 1, 0, 0),
            "user": "Alice",
            "message": long_msg
        }
    ])
    assert chunks[0].page_content == f"2020-01-01 00:00 - Alice: {'X'*50}..."  # long_msg cut to max_message_length
