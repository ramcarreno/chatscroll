import streamlit as st
import pandas as pd

from dateutil.relativedelta import relativedelta

from chatscroll.plots import plot_msg_over_time, plot_user_msg_stats, plot_msg_over_days, plot_msg_over_hours


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
    c12.metric("Active users", len(st.session_state.users))
    c13.metric(
        "Date range", f"{start_date} to {end_date}",
        help=f"Chat active for {range_bd.years} years, {range_bd.months} months and {range_bd.days} days"
    )

    # Calculations for second row
    range_days = (end_date - start_date).days + 1
    df_by_date = df.groupby('date').agg(msg=('message', 'count'))
    most_active_day = df_by_date.msg.idxmax()
    most_active_count = df_by_date.msg.max()

    # Second row of metrics
    c21, c22, c23 = st.columns(3)
    c21.metric("Messages per day",  f"{len(df) / range_days:.2f}")
    c22.metric("% Active days", f"{(len(df.date.unique()) / range_days)*100:.2f}%")
    c23.metric("Most active day", f"{most_active_day}", help=f"{most_active_count} messages were sent on that day")

    # User/time period messaging stats
    st.subheader("🗣️📆 Who's talking — and when?")
    p11, p12 = st.columns(2)

    with p11:
        st.plotly_chart(plot_user_msg_stats(df), use_container_width=True)
    with p12:
        st.plotly_chart(plot_msg_over_time(df), use_container_width=True)

    # Daily messages plot
    st.plotly_chart(plot_msg_over_days(df_by_date.reset_index()), use_container_width=True)

    # Hourly messages plot
    df_by_hours = df.groupby('hour').agg(msg=('message', 'count')).reset_index()
    st.plotly_chart(plot_msg_over_hours(df_by_hours))