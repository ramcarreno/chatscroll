import pandas as pd
import streamlit as st


def get_df(chat):
    df = pd.DataFrame(chat)
    return df


def search():
    # Init page and load df
    st.header("Search")
    df = get_df(st.session_state["chat"])

    # Prompt search query
    query = st.text_input(
        "Type a keyword or phrase to search in your chat messages",
        help="**Tip:** You can use regular expressions!"
    )

    # Execute search query if something was written
    if query:
        results = df[df["message"].str.contains(query, case=False, na=False)]
        if len(results) == 0:
            st.warning("Sorry, we did not find any messages matching your query.")
            st.stop()

        # Order by descending time and rename columns
        results = results.sort_values("time", ascending=False).reset_index(drop=True)
        results = results.rename(columns={
            "time": "Time",
            "user": "User",
            "message": "Message"
        })[["Time", "User", "Message"]]

        # Display resulting dataframe without index
        # TODO: pretty paginated view
        st.markdown(f"#### 🕵️‍♀️ Found {len(results)} messages matching your query")
        st.dataframe(results, use_container_width=True, hide_index=True)