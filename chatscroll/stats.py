import emoji
import pandas as pd

from typing import Any
from collections import Counter


class ChatStats:
    def __init__(self, df: pd.DataFrame):
        self.df: pd.DataFrame = df.copy()
        self.df["date"]: pd.Series = self.df["time"].dt.date
        self.df["hour"]: pd.Series = self.df["time"].dt.hour
        self.df["word_count"]: pd.Series = self.df["message"].apply(lambda x: len(str(x).split()))
        self.df["char_count"]: pd.Series = self.df["message"].apply(lambda x: len(str(x)))

    def participant_message_counts(self) -> pd.DataFrame:
        message_counts = self.df["participant"].value_counts().reset_index()
        message_counts.columns = ["participant", "messages"]
        return message_counts

    def top_n_words(self, n: int, participant: str | None):
        return
