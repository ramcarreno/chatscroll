import re

import pandas as pd
import streamlit as st

from chatscroll.plots import get_word_frequencies, plot_wordcloud, plot_msg_over_time, get_emoji_frequencies, \
    plot_msg_over_days, plot_msg_over_hours


def get_df(chat):
    df = pd.DataFrame(chat)
    df["date"] = df["time"].dt.date
    df["year_month"] = df["time"].dt.to_period("M")
    df["year"] = df["time"].dt.year
    df["weekday"] = df["time"].dt.day_name()
    df["hour"] = df["time"].dt.hour
    df["word_count"] = df["message"].apply(lambda x: len(str(x).split()))
    df["char_count"] = df["message"].apply(lambda x: len(str(x)))
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
    word_freqs = get_word_frequencies(user_df, stopwords)
    emoji_freqs = get_emoji_frequencies(user_df)

    # General overview
    st.subheader(f"👤 Overview of _{selected_user}_")

    # First row of metrics
    c11, c12, c13 = st.columns(3)
    c11.metric("User messages", len(user_df),
               help=f"**{user_df["word_count"].mean():.2f}** avg. words per message"
                    f"\n\n**{user_df["char_count"].mean():.2f}** avg. characters per message"
               )
    c12.metric("Participation (% of total messages)", f"{(len(user_df) / len(df)) * 100:.2f}%")
    c13.metric("Active days", len(user_df.date.unique()),
               help=f"**{len(user_df.date.unique()) / len(df.date.unique()) * 100:.2f}%** of total chat active days")

    # Second row of metrics
    c21, c22, c23 = st.columns(3)
    c21.metric("Last message date", user_df["date"].max().strftime("%Y-%m-%d"))
    c22.metric("Top word",  word_freqs[0][0])
    c23.metric("Top emoji", f"{emoji_freqs.most_common(1)[0][0]}",
               help=f"Used **{emoji_freqs.most_common(1)[0][1]}** times")  # TODO: correct bug with multilayered emojis

    # Wordcloud + messaging frequency plots
    st.subheader(f"📖️🕰️ What's _{selected_user}_ saying... and when?")
    p11, p12 = st.columns(2)

    with p11:
        st.markdown(
            "<h6 style='text-align: left; font-weight: bold;'>Wordcloud</h6>",
            unsafe_allow_html=True
        )
        n_words_slider = st.slider(
            "Number of words to display",
            min_value=5, max_value=200, value=100, step=1
        )
        st.pyplot(plot_wordcloud(dict(word_freqs[:n_words_slider])), use_container_width=True)
    with p12:
        st.markdown(
            "<h6 style='text-align: left; font-weight: bold;'>Messages by time period</h6>",
            unsafe_allow_html=True
        )
        st.plotly_chart(plot_msg_over_time(user_df), use_container_width=True)

    # Daily messages plot
    user_df_by_date = user_df.groupby('date').agg(msg=('message', 'count')).reset_index()
    st.plotly_chart(plot_msg_over_days(user_df_by_date), use_container_width=True)

    # Hourly messages plot
    user_df_by_hours = user_df.groupby('hour').agg(msg=('message', 'count')).reset_index()
    st.plotly_chart(plot_msg_over_hours(user_df_by_hours))

    # TODO:
    # Activity graph
    # Clock
    # Top emojis
    # Emoji frequency
    # Filter df by time
    # Spammy words -> ratio of word count / messages