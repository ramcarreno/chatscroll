import streamlit as st
import pandas as pd

from dateutil.relativedelta import relativedelta

from chatscroll.plots import plot_msg_over_time, plot_user_msg_stats


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


def activity():
    # Init page and load df
    st.header("Activity")
    df = get_df(st.session_state.chat)

    # General overview
    st.subheader("📊 Overview")

    # Calculations for first row
    start_date = df["time"].min().date()
    end_date = df["time"].max().date()
    range_bd = relativedelta(end_date, start_date)

    # Add first row of metrics
    c11, c12, c13 = st.columns(3)
    c11.metric("Messages", len(df))
    c12.metric("Active Users", len(st.session_state.users))
    c13.metric(
        "Date Range", f"{start_date} to {end_date}",
        help=f"Chat active for {range_bd.years} years, {range_bd.months} months and {range_bd.days} days"
    )

    # Calculations for second row
    range_days = (end_date - start_date).days + 1
    most_active_day = df.groupby('date').agg(ct=('message', 'count')).ct.idxmax()
    most_active_count = df.groupby('date').agg(ct=('message', 'count')).ct.max()

    # Second row of metrics
    c21, c22, c23 = st.columns(3)
    c21.metric("Messages per Day",  f"{len(df) / range_days:.2f}")
    c22.metric("% Active Days", f"{(len(df.date.unique()) / range_days)*100:.2f}%")
    c23.metric("Most Active Day", f"{most_active_day}", help=f"{most_active_count} messages were sent on that day")

    # User message rankings
    st.subheader("🗣️📆 Who's talking — and when?")
    col1, col2 = st.columns(2)

    with col1:
        st.plotly_chart(plot_user_msg_stats(df), use_container_width=True)
    with col2:
        st.plotly_chart(plot_msg_over_time(df), use_container_width=True)
