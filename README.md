# ChatScroll 🗣️📜

**ChatScroll** is a dashboard app for analyzing WhatsApp chats. It parses a previously exported `.txt` chat file 
and shows stats for the whole chat and individual users. It also includes a search functionality and local LLM support 
via Ollama, so you can ask any questions about your chat—and all completely offline, meaning **your data stays in your 
device**!

## Installation

### Prerequisites
- Python 3.10 or higher
- Poetry ([installation guide](https://python-poetry.org/docs/#installation))
- Ollama (optional) ([installation guide](https://ollama.com/download))

### Steps
1. Clone this repo and access its root directory
```bash
git clone git@github.com:ramcarreno/chatscroll.git
cd chatscroll
```
2. Install dependencies using Poetry 
```bash
poetry install
```
3. If you plan on using the LLM chatting module, pull one or more Ollama models from the 
[Ollama library](https://ollama.com/library). I recommend `llama3.1:8b` (requires around 6GB RAM) or `gemma3:4b` (≈4GB)
if your machine is on the low end, although note it will perform worse. Take a look at the
[About the local LLM feature](#about-the-local-llm-feature) section for more details on setup and performance 
considerations.

```bash
ollama pull [model name]
```
4. Finally, run the app:
```bash
poetry run streamlit run app.py
```

### Additional configuration
By default, the app will run in `localhost:8501`. If you want to change the port, you can either set the env variable
```bash
export STREAMLIT_SERVER_PORT=[your port of choice]
```
or run the app with:
```bash
poetry run streamlit run app.py --server.port [your port of choice]
```

## Pages

Once a chat is uploaded, the sidebar shows three dashboard-related views or pages (*Activity*, *Content* and *User*) 
plus two additional tools (*Chat with your chat* and *Search*).

- **Activity** shows message volume over time (daily, monthly, hourly, etc.) and most active users.
- **Content** breaks down word usage, emoji stats, and more. Words can be filtered by specifying a *stopword* list and
narrow results to a specific date range in the chat.
- **User** combines some of the insights displayed in both previous pages but focused on a single chat participant 
(or *user*). Choose a user and optionally filter by date range and *stopwords*.
- **Chat with your chat** contains a LLM chat module powered by Ollama and augmented through the uploaded chat file.
- **Search** supports keyword and regex-based message search. Results return timestamp, user, and message content in a 
compact table.

## About the local LLM feature

This feature is implemented exclusively in the **Chat with your chat** page, so users can access the dashboard and 
search pages separately. While the Ollama models can run on CPU, having at least a small GPU provides a much smoother
user experience. Models below 2 billion parameters and reasoning models are discouraged for typical use, as they tend 
to produce too long or lower quality outputs.

If your uploaded chat is in a language other than English, it's recommended to ask questions in that same language for 
better relevance. However, please note that LLM performance may be lower in non-English languages, depending on the model's multilingual capabilities.

### Limitations and other features

This feature was designed for fun and experimentation. Do not expect any models to understand ambiguous messages or 
perfectly remember every detail. User queries by retrieving relevant chat context and prompting the model to generate 
responses accordingly. Specifically, it:

- Retrieves 3 context chunks, each containing 10 messages relevant to the user's query.
- Generates answers based on this context, but does **not** maintain conversation memory (yet), meaning each query is 
independent of previous ones.

More advanced users can customize retrieval and model settings, although there is no dedicated config file yet. Relevant
source code sections include:

- `chatscroll.rag`: Controls LLM parameters like temperature, chunk size and length (ChatSplitter), and number of 
retrieved chunks per query (Retriever).
- `views.chat2chat`: By default, a simple BM25 ranker is used for retrieval. In this module, the retriever can be 
changed to FAISS with Hugging Face embeddings for higher-quality context. This implies longer preprocessing times for 
large chats, however, embeddings are persisted and cached so queries remain fast.

## Notes

- Since only .txt files can be uploaded and therefore media is not supported, any text between `< >` is removed. This is 
done to skip messages that only contain placeholders (such as `<Media omitted>`).
- Chats over 200MB are not supported (soft limit set for performance reasons).
- Supported timestamp formats are:
```
%d.%m.%Y, %H:%M
%d/%m/%Y, %H:%M
%d/%m/%y, %H:%M
```
Other formats might exist depending on your device's locale. If your chat can't be parsed, open an issue or let me know,
I'll add support.
