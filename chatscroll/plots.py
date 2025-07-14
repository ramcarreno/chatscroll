import pandas as pd
import plotly.graph_objects as go


def plot_user_msg_stats(df):
    # Group by user message count and word/character averages
    user_talk_stats = df.groupby('user').agg(
        message_count=('message', 'count'),
        avg_words=('word_count', 'mean'),
        avg_chars=('char_count', 'mean')
    ).reset_index()

    # Init plot and add traces
    fig = go.Figure()
    fig.add_trace(go.Bar(x=user_talk_stats["user"], y=user_talk_stats["message_count"], name='Total Messages',
                         visible=True))
    fig.add_trace(go.Bar(x=user_talk_stats["user"], y=user_talk_stats["avg_words"], name='Avg. Words per Message',
                         visible=False))
    fig.add_trace(go.Bar(x=user_talk_stats["user"], y=user_talk_stats["avg_chars"], name='Avg. Characters per Message',
                         visible=False))

    # Setup dropdown buttons for each trace
    fig.update_layout(
        updatemenus=[dict(
            type="dropdown",
            direction="down",
            showactive=True,
            x=1.05,
            xanchor="left",
            y=1,
            yanchor="top",
            buttons=[
                dict(label="Messages",
                     method="update",
                     args=[
                         {"visible": [True, False, False]},
                         {"yaxis.title.text": "Message Count"}
                     ]),
                dict(label="Words",
                     method="update",
                     args=[
                         {"visible": [False, True, False]},
                         {"yaxis.title.text": "Average Words per Message"}
                     ]),
                dict(label="Characters",
                     method="update",
                     args=[
                         {"visible": [False, False, True]},
                         {"yaxis.title.text": "Average Characters per Message"}
                     ]),
            ]
        )],
        title="Users Messaging Statistics",
        xaxis_title="User",
        yaxis_title="Message Count",
        height=500,
        margin=dict(l=40, r=40, t=60, b=40)
    )

    return fig


def plot_msg_over_time(df):
    # Group counts by time period
    by_year = df.groupby("year").agg(msg=("message", "count")).reset_index()
    by_month = df.groupby("year_month").agg(msg=("message", "count")).reset_index()
    by_weekday = df.groupby("weekday").agg(msg=("message", "count")).reset_index()

    # Weekday ordering to prevent auto alphabetical
    weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    by_weekday["weekday"] = pd.Categorical(by_weekday["weekday"], categories=weekday_order, ordered=True)
    by_weekday = by_weekday.sort_values("weekday")

    # Init plot and traces
    fig = go.Figure()
    fig.add_trace(go.Bar(x=by_year["year"].astype(str), y=by_year["msg"], name="Year", visible=True))
    fig.add_trace(go.Bar(x=by_month["year_month"].astype(str), y=by_month["msg"], name="Month", visible=False))
    fig.add_trace(go.Bar(x=by_weekday["weekday"].astype(str), y=by_weekday["msg"], name="Weekday", visible=False))

    # Setup dropdown buttons for each trace
    fig.update_layout(
        updatemenus=[dict(
            type="dropdown",
            direction="down",
            showactive=True,
            x=1.05,
            xanchor="left",
            y=1,
            yanchor="top",
            buttons=[
                dict(label="Year",
                     method="update",
                     args=[
                         {"visible": [True, False, False]},
                         {"xaxis.title.text": "Year"}
                     ]),
                dict(label="Month",
                     method="update",
                     args=[
                         {"visible": [False, True, False]},
                         {"xaxis.title.text": "Month"}
                     ]),
                dict(label="Weekday",
                     method="update",
                     args=[
                         {"visible": [False, False, True]},
                         {"xaxis.title.text": "Weekday"}
                     ]),
            ]
        )],
        title="Messages by Time Period",
        xaxis=dict(type="category"),
        xaxis_title="Time Period",
        yaxis_title="Message Count",
        height=500,
        margin=dict(l=40, r=40, t=60, b=40)
    )

    return fig
