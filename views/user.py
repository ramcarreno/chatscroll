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
    df = get_df(st.session_state["chat"])

    # Start user selectbox (default selected by alphabetical order) and filter df
    users = sorted(df["user"].unique())
    selected_user = st.selectbox("Select a user", users)
    user_df = df[df["user"] == selected_user]

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

    # Filter dfs according to selected values
    date_df = df[(df["date"] >= start_date) & (df["date"] <= end_date)]
    date_user_df = user_df[(user_df["date"] >= start_date) & (user_df["date"] <= end_date)]
    if len(date_user_df) == 0:
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

    # Extract word frequencies according to stopword selection and emoji frequencies
    word_freqs = get_word_frequencies(date_user_df, stopwords)
    emoji_freqs = get_emoji_frequencies(date_user_df)

    # General overview
    st.subheader(f"👤 Overview of _{selected_user}_")

    # First row of metrics
    c11, c12, c13 = st.columns(3)
    c11.metric("User messages", len(date_user_df),
               help=f"**{date_user_df['word_count'].mean():.2f}** avg. words per message"
                    f"\n\n**{date_user_df['char_count'].mean():.2f}** avg. characters per message"
               )
    c12.metric("Participation (% of total messages)", f"{(len(date_user_df) / len(date_df)) * 100:.2f}%")
    c13.metric("Active days", len(date_user_df.date.unique()),
               help=f"**{len(date_user_df.date.unique()) / len(date_df.date.unique()) * 100:.2f}%** of days when "
                    f"someone participated in the chat")

    # Second row of metrics
    c21, c22, c23 = st.columns(3)
    c21.metric("Last message date", date_user_df["date"].max().strftime("%Y-%m-%d"))
    if word_freqs:
        top_word, top_word_count = word_freqs[0]
        c22.metric("Top word", f"{top_word}", help=f"Sent **{top_word_count}** times")
    else:
        c22.metric("Top word", "None", help="**Warning**: No words outside stopword list!")
    if emoji_freqs:  # TODO: correct bug with multilayered emojis
        top_emoji, top_emoji_count = emoji_freqs.most_common(1)[0]
        c23.metric("Top emoji", f"{top_emoji}", help=f"Sent **{top_emoji_count}** times")
    else:
        c23.metric("Top emoji", "None", help="No emojis sent during the selected time period")

    # Wordcloud + messaging frequency plots
    st.subheader(f"📖️🕰️ What's _{selected_user}_ saying... and when?")
    p11, p12 = st.columns(2)

    with p11:
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
    with p12:
        st.markdown(
            "<h6 style='text-align: left; font-weight: bold;'>Messages by time period</h6>",
            unsafe_allow_html=True
        )
        st.plotly_chart(plot_msg_over_time(date_user_df), use_container_width=True)

    # Daily messages plot
    filtered_df_by_date = date_user_df.groupby('date').agg(msg=('message', 'count')).reset_index()
    st.plotly_chart(plot_msg_over_days(filtered_df_by_date), use_container_width=True)

    # Hourly messages plot
    filtered_df_by_hours = date_user_df.groupby('hour').agg(msg=('message', 'count')).reset_index()
    st.plotly_chart(plot_msg_over_hours(filtered_df_by_hours))

    # TODO:
    # User top emojis
    # User emoji frequency
    # Spammy words -> ratio of word count / messages
    # Substitute graph titles by markdown
    # What to do with graphs when message count=1