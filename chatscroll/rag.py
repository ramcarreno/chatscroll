import hashlib
import os
from abc import ABC, abstractmethod

import streamlit as st
from langchain.schema import Document
from langchain_community.retrievers import BM25Retriever
from langchain_ollama import ChatOllama
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings


@st.cache_resource
def get_llm(model_name):
    return ChatOllama(
        model=model_name,
        temperature=0.5,
        reasoning=False
    )


class ChatSplitter:
    def __init__(self, chunk_size=10, overlap=5, max_message_length=300):
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
                f"{msg['time'].strftime('%Y-%m-%d %H:%M')} - {msg['user']}: {self.truncate_message(msg['message'])}"
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


class Retriever(ABC):
    def __init__(self, passages):
        self.passages = passages
        self.chunks = None
        self._split_passages()

    def _split_passages(self):
        # Call external splitter class with default parameters
        self.chunks = ChatSplitter().split_messages(self.passages)

    @abstractmethod
    def retrieve(self, query, k):
        """

        """


class SimpleRetriever(Retriever):
    def __init__(self, passages):
        super().__init__(passages)
        self.retriever = BM25Retriever.from_documents(documents=self.chunks)

    def retrieve(self, query, k=3):
        docs = self.retriever.invoke(query)[:k]
        return "\n\n".join(doc.page_content for doc in docs)


class FAISSRetriever(Retriever):
    def __init__(
            self, passages,
            embeddings_model="sentence-transformers/all-MiniLM-L6-v2",
            base_index_dir="./.index_cache"
        ):
        super().__init__(passages)
        self.embeddings = HuggingFaceEmbeddings(
            model_name=embeddings_model,
            cache_folder="./hf_cache",
            show_progress=True,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={"batch_size": 32}
        )
        if not os.path.exists(base_index_dir):
            os.makedirs(base_index_dir)

        # Getting the vector store
        index_path = self._get_index_path(base_index_dir)
        if os.path.exists(index_path):
            # Load existing index from disk
            self.vector_store = FAISS.load_local(index_path, self.embeddings, allow_dangerous_deserialization=True)
        else:
            # Build index from scratch
            self.vector_store = FAISS.from_documents(self.chunks, self.embeddings)
            self.vector_store.save_local(index_path)

    def _get_index_path(self, base_dir):
        text = str(self.passages)
        content_hash = hashlib.md5(text.encode('utf-8')).hexdigest()
        return os.path.join(base_dir, f"faiss_index_{content_hash}")

    def retrieve(self, query, k=3):
        docs = self.vector_store.similarity_search(query, k=k)
        return "\n\n".join(doc.page_content for doc in docs)
