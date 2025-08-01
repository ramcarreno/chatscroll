import time

import ollama
import streamlit as st

from chatscroll.rag import get_llm, ChatSplitter


def chat2chat():
    # Init page and get original chat
    st.header("Chat with your chat")
    chat = st.session_state['chat']

    # Split
    chunks = ChatSplitter().split_messages(chat)
    # TODO: vector store

    # Search for locally pulled ollama models and default to first model as choice
    available_llms = [model["model"] for model in ollama.list()["models"]]
    if not available_llms:
        st.error("No LLMs found. Please pull a model of your choice from Ollama.")
        st.stop()
    if st.session_state["model_name"] is None:
        st.session_state["model_name"] = available_llms[0] # default to first model

    # Create selectbox that memorizes current selection as default
    selected_model = st.selectbox(
        "Choose an LLM",
        available_llms,
        index=available_llms.index(st.session_state["model_name"])
    )
    if selected_model != st.session_state["model_name"]:
        st.session_state["model_name"] = selected_model

    # Rewrite chat history everytime the page is selected (plus first "message")
    with st.chat_message("assistant"):
        st.write(f'Hi! So... is there anything you want to know about "{st.session_state["chatname"]}"?')
    for message in st.session_state["messages"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    ### CHAT LOGIC
    if prompt := st.chat_input(placeholder="Ask anything about your conversations!"):
        # User input: Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)
        # Add message to chat history (in session state)
        st.session_state["messages"].append({"role": "user", "content": prompt})

        # Assistant (LLM) output: take entire history for next response
        llm = get_llm(st.session_state["model_name"])
        try:
            with st.chat_message("assistant"):
                stream = (x.content for x in llm.stream(st.session_state["messages"]))
                full_response = st.write_stream(stream)
        except ollama._types.ResponseError as e:
            st.error(f"⚠️ Oops, the model ran into an error... {e}")
            st.stop()

        # Add response to chat history
        st.session_state["messages"].append({"role": "assistant", "content": full_response})
