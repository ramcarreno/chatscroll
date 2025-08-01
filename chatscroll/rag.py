import streamlit as st
from langchain.schema import Document
from langchain_ollama import ChatOllama


@st.cache_resource
def get_llm(model_name):
    return ChatOllama(
        model=model_name,
        num_predict=50,
        reasoning=False
    )


class ChatSplitter:
    def __init__(self, chunk_size=10, overlap=3, max_message_length=500):
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.max_message_length = max_message_length

    def split_messages(self, messages):
        chunks = []
        i = 0

        # Iterate over a chat message list and format
        while i < len(messages):
            # Format a window of chunk_size messages into plain text, truncate long messages
            window = messages[i:i + self.chunk_size]
            formatted = [
                f"[{msg['time'].strftime('%Y-%m-%d %H:%M')}] {msg['user']}: {self.truncate_message(msg['message'])}"
                for msg in window
            ]
            chunk_text = "\n".join(formatted)

            # Save chunk as LC document and move window to next chunk - overlap position
            chunks.append(Document(page_content=chunk_text))
            i += self.chunk_size - self.overlap

        return chunks

    def truncate_message(self, message):
        if len(message) > self.max_message_length:
            return message[:self.max_message_length] + "..."
        return message