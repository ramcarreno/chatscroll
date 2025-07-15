import re

import pandas as pd
import streamlit as st


def get_df(chat):
    df = pd.DataFrame(chat)
    df["date"] = df["time"].dt.date
    df["year_month"] = df["time"].dt.to_period("M")
    df["year"] = df["time"].dt.year
    df["weekday"] = df["time"].dt.day_name()
    df["hour"] = df["time"].dt.hour
    return df


def user():
    # Init page and load df
    st.header("User")
    df = get_df(st.session_state.chat)

    # Start selectbox (default user selected by alphabetical order) and filter df by user
    users = sorted(df["user"].unique())
    selected_user = st.selectbox("Select a user", users)
    user_df = df[df["user"] == selected_user]

    # Selectbox for stopword settings
    selected_stopwords = st.selectbox(
        "Stopword filtering (affects word stats)",
        options=["Use default stopwords (English)", "Add custom"]
    )
    custom_stopwords = []
    if selected_stopwords == "Add custom":
        custom_stopwords_input = st.text_area(
            "Please enter custom stopwords (comma, space or newline separated):",
            height=80
        )
        custom_stopwords = [w.strip().lower() for w in re.split(r'[,\n\s]+', custom_stopwords_input) if
                            w.strip()]

    # General overview
    st.subheader("👤 Overview")

    # First row of metrics
    c11, c12, c13 = st.columns(3)
    c11.metric("User messages", len(user_df))  # TODO: tooltip word/char avgs
    c12.metric("Participation (% of total messages)", f"{(len(user_df) / len(df)) * 100:.2f}%")  # TODO: tt relative
    c13.metric("Active days", user_df["date"].nunique())

    # Second row of metrics
    c21, c22, c23 = st.columns(3)
    c21.metric("Last message date", user_df["date"].max().strftime("%Y-%m-%d"))
    c22.metric("Top word",  f"Placeholder")
    c23.metric("Top emoji", f"📌")
