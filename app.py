from io import StringIO

import pandas as pd
import streamlit as st

from chatscroll.parser import ChatParser
from chatscroll.stats import ChatStats
from views import *


def main():
    st.set_page_config(
        page_title="ChatScroll",
        page_icon="🗣️",
        layout="wide",
    )

    # Upload and parse only once
    if "chat" not in st.session_state:
        uploaded_file = st.file_uploader("Upload your WhatsApp chat (.txt)", type=["txt"])
        if uploaded_file is None:
            st.warning("👆 Please upload a chat file to begin.")
            st.stop()

        # Parse file and extract useful params
        f = StringIO(uploaded_file.getvalue().decode("utf-8"))
        parser = ChatParser(f)
        chat = parser.chat
        users = parser.users
        df = pd.DataFrame(parser.chat)
        stats = ChatStats(df)

        # Save useful params to session state and update
        st.session_state.chat = chat
        st.session_state.users = users
        st.session_state.df = df
        st.session_state.stats = stats
        st.rerun()

    # Sidebar common to all next pages
    with st.sidebar:
        st.title("🗣️📜 chatscroll")
        st.markdown("Upload and explore your WhatsApp chat!")

    # Pages
    pg = st.navigation(
        {
            "Dashboard": [
                st.Page(overview, title="Overview", icon=":material/dashboard:"),
                st.Page(activity, title="Activity", icon=":material/insights:"),
                st.Page(content, title="Content", icon=":material/article:"),
                st.Page(user, title="User", icon=":material/person:"),
            ]
            #"Tools": [search, llm],
        }
    )
    pg.run()


if __name__ == "__main__":
    main()