import datetime
import re

import emoji
import pandas as pd
import streamlit as st

from chatscroll.plots import get_word_frequencies, get_emoji_frequencies, plot_wordcloud, plot_top_n_emojis


def get_df(chat):
    df = pd.DataFrame(chat)
    df["date"] = df["time"].dt.date
    df["word_count"] = df["message"].apply(lambda x: len(str(x).split()))
    df["char_count"] = df["message"].apply(lambda x: len(str(x)))
    return df


def content():
    # Init page and load df
    st.header("Content")
    df = get_df(st.session_state.chat)

    # Calendar selector to filter date range
    start_date, end_date = df["date"].min(), df["date"].max()
    date_range = st.date_input(
        label="Select a date range to filter messages",
        value=(start_date, end_date),
        min_value=start_date,
        max_value=end_date,
        format="MM.DD.YYYY",
    )
    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_date, end_date = date_range
    elif isinstance(date_range, tuple) and len(date_range) == 1:
        start_date = date_range[0]  # Only 1 element selected, fallback to start of range to maximum

    # Filter df according to selected values
    date_df = df[(df["date"] >= start_date) & (df["date"] <= end_date)]
    if len(date_df) == 0:
        st.error("Looks like there were no messages sent during that time range. Try selecting different dates before "
                 "continuing.")
        st.stop()

    # Selectbox for stopword settings
    sw_choice = st.selectbox(
        label="Stopword filtering (affects word counts)",
        options=["Use default stopwords (English)", "Add custom list", "None"]
    )

    if sw_choice == "Use default stopwords (English)":
        stopwords = "english"
    elif sw_choice == "Add custom list":
        custom_input = st.text_area(
            label="Please enter custom stopwords (comma, space or newline separated):",
            height=80
        )
        stopwords = [w.strip().lower() for w in re.split(r'[,\n\s]+', custom_input) if w.strip()]
    else:  # Last (no stopwords) option
        stopwords = None

    # Extract word frequencies according to stopword selection and emoji frequencies and plot
    word_freqs = get_word_frequencies(date_df, stopwords)
    emoji_freqs = get_emoji_frequencies(date_df)
    p11, p12 = st.columns(2)

    with p11:
        st.markdown(
            "<h6 style='text-align: left; font-weight: bold;'>Top emojis</h6>",
            unsafe_allow_html=True
        )
        if emoji_freqs:
            st.plotly_chart(plot_top_n_emojis(emoji_freqs, 10), use_container_width=True)
        else:
            st.warning("😶‍🌫️ No emojis found! 🕵️‍♀️ Perhaps try a different date range? 📅")
    with p12:
        st.markdown(
            "<h6 style='text-align: left; font-weight: bold;'>Wordcloud</h6>",
            unsafe_allow_html=True
        )
        if word_freqs:
            n_words_slider = st.slider(
                "Number of words to display",
                min_value=5, max_value=200, value=100, step=1
            )
            st.pyplot(plot_wordcloud(dict(word_freqs[:n_words_slider])), use_container_width=True)
        else:
            st.warning("No words to show right now. Try a different date range or change your stopword list.")
