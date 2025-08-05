import os
from typing import Literal

import streamlit as st
import yaml
from pydantic import BaseModel, Field, ValidationError, model_validator


class ModelConfig(BaseModel):
    temperature: float = Field(default=0.5, gt=0)


class SplitterConfig(BaseModel):
    chunk_size: int = Field(default=10, ge=1)
    chunk_overlap: int = Field(default=5, ge=0)
    max_message_length: int = Field(default=300, ge=10, le=5000)

    @model_validator(mode="after")
    def check_overlap_less_than_chunk(self) -> "SplitterConfig":
        if self.chunk_overlap >= self.chunk_size:
            raise ValueError(
                f"`chunk_overlap` ({self.chunk_overlap}) must be less than `chunk_size` ({self.chunk_size})"
            )
        return self


class RetrieverConfig(BaseModel):
    retrieval_method: Literal["bm25", "FAISS"] = "bm25"
    k: int = Field(default=3, ge=1, le=50)
    embeddings_model: str = Field(default="sentence-transformers/all-MiniLM-L6-v2")


class AppConfig(BaseModel):
    model: ModelConfig
    splitter: SplitterConfig
    retriever: RetrieverConfig


@st.cache_resource
def load_config(path="llm_config.yaml") -> AppConfig:
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Hmmm, the LLM config file was not found at: {path}. Please restore it.")

    with open(path, "r") as f:
        raw_config = yaml.safe_load(f)
    try:
        config = AppConfig(**raw_config)
    except ValidationError as e:
        # Validation errors are then caught in the Streamlit page
        raise e
    return config