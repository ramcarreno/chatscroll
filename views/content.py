import re

import emoji
import pandas as pd
import streamlit as st

from chatscroll.plots import get_word_frequencies, get_emoji_frequencies, plot_wordcloud, plot_top_n_emojis


def get_df(chat):
    df = pd.DataFrame(chat)
    df["word_count"] = df["message"].apply(lambda x: len(str(x).split()))
    df["char_count"] = df["message"].apply(lambda x: len(str(x)))
    return df


def content():
    # Init page and load df
    st.header("Content")
    df = get_df(st.session_state.chat)

    # Selectbox for stopword settings
    sw_choice = st.selectbox(
        "Stopword filtering (affects word counts)",
        options=["Use default stopwords (English)", "Add custom list", "None"]
    )

    if sw_choice == "Use default stopwords (English)":
        stopwords = "english"
    elif sw_choice == "Add custom list":
        custom_input = st.text_area(
            "Please enter custom stopwords (comma, space or newline separated):",
            height=80
        )
        stopwords = [w.strip().lower() for w in re.split(r'[,\n\s]+', custom_input) if w.strip()]
    else:  # Last (no stopwords) option
        stopwords = None

    # Extract word frequencies according to stopword selection and emoji frequencies
    word_freqs = get_word_frequencies(df, stopwords)
    emoji_freqs = get_emoji_frequencies(df)

    p11, p12 = st.columns(2)

    with p11:
        st.markdown(
            "<h6 style='text-align: left; font-weight: bold;'>Top emojis</h6>",
            unsafe_allow_html=True
        )
        st.plotly_chart(plot_top_n_emojis(emoji_freqs, 10), use_container_width=True)
    with p12:
        st.markdown(
            "<h6 style='text-align: left; font-weight: bold;'>Wordcloud</h6>",
            unsafe_allow_html=True
        )
        n_words_slider = st.slider(
            "Number of words to display",
            min_value=5, max_value=200, value=100, step=1
        )
        st.pyplot(plot_wordcloud(dict(word_freqs[:n_words_slider])), use_container_width=True)