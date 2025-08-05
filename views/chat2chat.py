import ollama
import streamlit as st
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from pydantic import ValidationError

from chatscroll.rag import get_llm, SimpleRetriever, FAISSRetriever
from chatscroll.prompts import system_rag_refined
from config.loader import load_config, AppConfig


@st.cache_resource
def get_retriever_cached(chat, config_json: str):
    config = AppConfig.model_validate_json(config_json)

    if config.retriever.retrieval_method == "simple":
        return SimpleRetriever(passages=chat, k=config.retriever.k, splitter_config=config.splitter)
    elif config.retriever.retrieval_method == "FAISS":
        return FAISSRetriever(passages=chat, k=config.retriever.k, splitter_config=config.splitter)
    return SimpleRetriever(passages=chat, k=config.retriever.k, splitter_config=config.splitter)


def get_retriever(config_json: str):
    # If retriever already in session state, return it
    if "retriever" in st.session_state:
        return st.session_state["retriever"]

    # Otherwise, build retriever once and store it
    chat = st.session_state["chat"]
    retriever = get_retriever_cached(chat, config_json)
    st.session_state["retriever"] = retriever
    return retriever


def chat2chat():
    # Init page and get original chat
    st.header("Chat with your chat")

    # Load LLM config
    try:
        config = load_config()
    except FileNotFoundError as e:
        st.error(str(e))
        st.stop()
    except ValidationError as e:
        st.error("Config file validation failed. Refer to the JSON below:")
        st.json(e.errors())
        st.stop()

    import ipdb; ipdb.set_trace()
    # Search for locally pulled ollama models and default to first model as choice
    try:
        available_llms = [model["model"] for model in ollama.list()["models"]]
    except ConnectionError:
        st.error(
            "Oops! Ollama isn't installed or can't be accessed right now. "
            "Please install it or check your setup. Download it here: https://ollama.com/download"
        )
        st.stop()
    if not available_llms:
        st.error("No LLMs found. Please pull a model of your choice from Ollama.")
        st.stop()
    if st.session_state["model_name"] is None:
        st.session_state["model_name"] = available_llms[0] # default to first model

    # Init retriever
    with st.spinner("Loading retriever... (May take a while)", show_time=True):
        retriever = get_retriever(config.model_dump_json())

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
        llm = get_llm(st.session_state["model_name"], config.model.temperature)
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
            {
                "context": RunnableLambda(lambda d: retriever.retrieve(query=d["input"])),
                "input": RunnablePassthrough()
            }
            | prompt
            | llm
            | StrOutputParser()
    )
    return rag_chain