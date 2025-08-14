def test_parsing(parse_chat):
    parser = parse_chat("sample_chat.txt")
    assert len(parser.chat) == 495  # 500 messages - 5 media / status changes omitted
    assert len(parser.users) == 6   # 6 unique users

