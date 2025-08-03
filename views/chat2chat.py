import ollama
import streamlit as st
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnablePassthrough

from chatscroll.rag import get_llm, SimpleRetriever, FAISSRetriever
from chatscroll.prompts import system_rag, system_rag_refined


@st.cache_resource
def get_retriever_cached(chat, retriever_type):
    if retriever_type == "simple":
        return SimpleRetriever(chat)
    elif retriever_type == "FAISS":
        return FAISSRetriever(chat)


def get_retriever(retriever_type):
    # If retriever already in session state, return it
    if "retriever" in st.session_state:
        return st.session_state["retriever"]

    # Otherwise, build retriever once and store it
    chat = st.session_state["chat"]
    retriever = get_retriever_cached(chat, retriever_type)
    st.session_state["retriever"] = retriever
    return retriever


def chat2chat():
    # Init page and get original chat
    st.header("Chat with your chat")

    # Init retriever
    with st.spinner("Loading retriever... (May take a while)", show_time=True):
        retriever = get_retriever(retriever_type="simple")

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
    if user_input := st.chat_input(placeholder="Ask anything about your conversations!"):
        # User input: Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(user_input)

        # Add message to chat history (in session state)
        st.session_state["messages"].append({"role": "user", "content": user_input})

        # Load LLM for response and get RAG chain
        llm = get_llm(st.session_state["model_name"])
        rag_chain = get_rag_chain(llm, retriever)

        # Execute LLM
        try:
            with st.chat_message("assistant"):
                stream = (t for t in rag_chain.stream({"input": user_input}))
                with st.spinner("Thinking..."):
                    full_response = st.write_stream(stream)

        except ollama._types.ResponseError as e:
            st.error(f"⚠️ Oops, the model ran into an error... {e}")
            st.stop()

        # Add response to chat history
        st.session_state["messages"].append({"role": "assistant", "content": full_response})


def get_rag_chain(llm, retriever):
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_rag_refined),
        ("system", "Here are the chat messages: {context}"),
        ("human", "{input}")
    ])
    rag_chain = (
            {"context": RunnableLambda(lambda d: retriever.retrieve(d["input"])), "input": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
    )
    return rag_chain