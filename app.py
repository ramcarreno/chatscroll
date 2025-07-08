import pathlib

from chatscroll.chat_parser import ChatParser


def main():
    with open("sample_chat.txt", "r", encoding="utf-8") as f:
        chat_text = f.read()

    chat_data = ChatParser(pathlib.Path("sample_chat.txt"), "asdf").parse_chat()

if __name__ == "__main__":
    main()