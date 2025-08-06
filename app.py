from io import StringIO
from typing import Any

import streamlit as st

from chatscroll.parser import ChatParser
from views import activity, content, user, chat2chat, search


def main():
    """
    Streamlit app entry point.

    Initializes necessary `st.session_state` values, sets up the main application loop,
    and defines the overall page layout and UI structure.
    """
    st.set_page_config(
        page_title="ChatScroll",
        page_icon="🗣️",
        layout="wide",
    )

    # Upload and parse only once
    if "chat" not in st.session_state:
        st.markdown("<h2 style='text-align: center;'>ChatScroll 🗣️📜</h2>", unsafe_allow_html=True)

        uploaded_file = st.file_uploader("Upload your WhatsApp chat (.txt)", type=["txt"])
        if uploaded_file is None:
            st.warning("👆 Please upload a chat file to continue.")
            st.stop()

        # Parse file and extract useful params
        f = StringIO(uploaded_file.getvalue().decode("utf-8"))
        parser = ChatParser(f)
        chat: list[dict[str, Any]] = parser.chat
        users: list[str] = parser.users

        if not chat or not users:
            st.error("📄❌ The file could not be parsed. Please upload a WhatsApp chat exported as a .txt file.")
            st.stop()

        # Init session state parameters used elsewhere
        st.session_state["messages"] = []
        st.session_state["model_name"] = None

        # Save useful params to session state and update
        st.session_state["chatname"] = uploaded_file.name.split(".")[0]
        st.session_state["chat"] = chat
        st.session_state["users"] = users
        st.rerun()

    # Sidebar common to all next pages
    with st.sidebar:
        st.title("🗣️📜 ChatScroll")
        st.markdown("A simple tool to uncover insights from your chat history.")
        if st.button("🔄 Upload new file"):
            st.session_state.clear()
            st.rerun()

    # Pages
    pg = st.navigation(
        {
            "Dashboard": [
                st.Page(activity, title="Activity", icon=":material/insights:", url_path="/activity", default=True),
                st.Page(content, title="Content", icon=":material/article:", url_path="/content"),
                st.Page(user, title="User", icon=":material/person:", url_path="/user"),
            ],
            "Tools": [
                st.Page(chat2chat, title="Chat with your chat", icon=":material/forum:", url_path="/chat2chat"),
                st.Page(search, title="Search", icon=":material/search:", url_path="/search"),
            ],
        }
    )
    pg.run()


if __name__ == "__main__":
    main()