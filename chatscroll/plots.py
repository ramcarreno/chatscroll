from collections import Counter

import emoji
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from matplotlib import pyplot as plt

from sklearn.feature_extraction.text import CountVectorizer
from wordcloud import WordCloud


def plot_user_msg_stats(df):
    """
    Plots user message counts, user average words per message and user average characters per message.
    The three different traces of the plot are toggleable with a dropdown menu.

    Args:
        df (DataFrame): A chat DataFrame with precomputed `word_count` and `char_count` columns.

    Returns:
        go.Figure: A Plotly figure.
    """
    # Group by user message count and word/character averages
    user_talk_stats = df.groupby('user').agg(
        message_count=('message', 'count'),
        avg_words=('word_count', 'mean'),
        avg_chars=('char_count', 'mean')
    ).reset_index()

    # Init plot and add traces
    fig = go.Figure()
    fig.add_trace(go.Bar(x=user_talk_stats["user"], y=user_talk_stats["message_count"], name='Messages',
                         visible=True))
    fig.add_trace(go.Bar(x=user_talk_stats["user"], y=user_talk_stats["avg_words"], name='Average words per message',
                         visible=False))
    fig.add_trace(go.Bar(x=user_talk_stats["user"], y=user_talk_stats["avg_chars"], name='Average characters per message',
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
                         {"yaxis.title.text": "Messages"}
                     ]),
                dict(label="Words",
                     method="update",
                     args=[
                         {"visible": [False, True, False]},
                         {"yaxis.title.text": "Average words per message"}
                     ]),
                dict(label="Characters",
                     method="update",
                     args=[
                         {"visible": [False, False, True]},
                         {"yaxis.title.text": "Average characters per message"}
                     ]),
            ]
        )],
        #title="User messaging statistics",
        xaxis_title="User",
        yaxis_title="Messages",
        height=450,
        margin=dict(l=40, r=40, t=60, b=40)
    )

    return fig


def plot_msg_over_time(df):
    """
    Plots message counts over yearly, monthly periods and day of the week.
    The three different traces of the plot are toggleable with a dropdown menu.

    Args:
        df (DataFrame): A chat DataFrame with precomputed `year`, `year_month` and `weekday` period columns.

    Returns:
        go.Figure: A Plotly figure.
    """
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
        #title="Messages by time period",
        xaxis=dict(type="category"),
        xaxis_title="Time period",
        yaxis_title="Messages",
        height=450,
        margin=dict(l=40, r=40, t=60, b=40)
    )

    return fig


def plot_msg_over_days(df):
    """
    Simple Plotly Express plot that tracks message frequency at the day level.
    Includes a range slider for more trackable and accurate zooming.

    Args:
        df (DataFrame): A chat DataFrame grouped by precomputed `date` column.

    Returns:
        go.Figure: A Plotly figure.
    """
    fig = px.line(
        df, x='date', y='msg',
        title='Messages per day',
        labels={'date': 'Date', 'msg': 'Messages'}
    )
    fig.update_layout(xaxis_rangeslider_visible=True)

    return fig


def plot_msg_over_hours(df):
    """
    Polar plot showing a clock-like representation of messaging frequency.

    Args:
        df (DataFrame): A chat DataFrame grouped by precomputed `hour` column.

    Returns:
        go.Figure: A Plotly figure.
    """
    # Predefine hour labels
    hour_labels = [
        "12 AM", "1 AM", "2 AM", "3 AM", "4 AM", "5 AM", "6 AM", "7 AM",
        "8 AM", "9 AM", "10 AM", "11 AM", "12 PM", "1 PM", "2 PM", "3 PM",
        "4 PM", "5 PM", "6 PM", "7 PM", "8 PM", "9 PM", "10 PM", "11 PM"
    ]

    # Add degrees for each hour for polar plot, 15º per hour
    # And custom hover labels
    df["theta"] = df["hour"] * 15
    df["hover_text"] = [f"Hour: {label}<br>Messages: {msg}" for label, msg in zip(hour_labels, df["msg"])]

    # Init plot and trace
    fig = go.Figure()
    fig.add_trace(go.Barpolar(
        r=df['msg'],
        theta=df['theta'],
        width=[15] * 24,
        marker_color=df['msg'],
        marker_colorscale='Plasma',
        opacity=0.85,
        text=df["hover_text"],
        hoverinfo="text"
    ))

    # Layout setup
    fig.update_layout(
        title="Message volume by hour",
        polar=dict(
            angularaxis=dict(
                direction="clockwise",
                rotation=90,
                tickmode='array',
                tickvals=df["theta"],
                ticktext=hour_labels,
                tickfont=dict(size=10)
            ),
            radialaxis=dict(
                visible=True,
                showticklabels=False
            )
        ),
        showlegend=False,
        height=500,
        margin=dict(t=50, b=30, l=30, r=30)
    )

    return fig


def get_word_frequencies(df, stopwords):
    """
    Calculate word frequencies from a message column in a DataFrame.

    Applies a `CountVectorizer` to the `message` column of the input DataFrame,
    filters out the provided stopwords, and returns a list of words with their
    corresponding frequencies in descending order.

    Args:
        df (DataFrame): A chat Dataframe.
        stopwords (Any): A collection of words to exclude from counting.
            Passed as the `stop_words` argument to `CountVectorizer`, which
            can be either `None`, `"english"` or a `List`.

    Returns:
        List[Tuple[str, int]]: A list of (word, frequency) tuples sorted by frequency.
                               Returns an empty list if vectorization fails.
    """
    # Initialize the vectorizer and feed message corpus
    try:
        vectorizer = CountVectorizer(lowercase=True, stop_words=stopwords)
        corpus = vectorizer.fit_transform(df["message"])

        # Obtain word counts array and then word frequencies in descending order
        word_counts = corpus.sum(axis=0).A1
        word_freq_sorted = sorted(
            list(zip(vectorizer.get_feature_names_out(), word_counts)),
            key=lambda x: x[1],
            reverse=True
        )

        # Return entire list (can be filtered later)
        return word_freq_sorted
    except ValueError:
        return []


def plot_wordcloud(frequencies: dict[str, int]):
    """
    Uses the WordCloud library to create a visualization from a dictionary of word-frequency pairs.
    The result is rendered using matplotlib.

    Args:
        frequencies (dict[str, int]): A dictionary where keys are words and values are their frequencies.

    Returns:
        plt.Figure: The matplotlib.pyplot figure containing the word cloud.
    """
    # Generate WordCloud
    wc = WordCloud(width=800, height=400, background_color='white', colormap='tab10').generate_from_frequencies(
        frequencies
    )

    # Display with matplotlib
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wc, interpolation='bilinear')
    ax.axis('off')

    return fig


def get_emoji_frequencies(df):
    """
    Count emoji frequencies in a chat DataFrame's messages.

    Iterates over each message, extracts characters that are valid emojis using
    the emoji.EMOJI_DATA dictionary, and returns a frequency count.

    Args:
        df (DataFrame): A chat DataFrame.

    Returns:
        Counter: A collections Counter mapping each emoji character to its frequency.
    """
    return Counter(sum(df["message"].apply(lambda text: [c for c in text if c in emoji.EMOJI_DATA]), []))


def plot_top_n_emojis(frequencies: Counter, n: int):
    """
    Plot a bar chart of the top N emojis by frequency.

    Args:
        frequencies (Counter): A collections Counter mapping emojis to their frequencies.
        n (int): Number of top emojis to plot.

    Returns:
        Figure: A Plotly figure.
    """
    # Create plotable df from frequencies
    top_n = frequencies.most_common(n)
    df = pd.DataFrame(top_n, columns=['Emoji', 'Frequency'])

    # Barplot
    fig = px.bar(df, x='Emoji', y='Frequency', text='Frequency',
                 height=450)

    # Layout setup
    fig.update_traces(marker_color='mediumseagreen', textposition='outside')
    fig.update_layout(
        xaxis_title='Emoji',
        yaxis_title='Frequency',
        plot_bgcolor='white'
    )

    return fig