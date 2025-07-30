# ChatScroll 🗣️📜

**ChatScroll** is a lightweight dashboard for analyzing WhatsApp chats. It parses a previously exported `.txt` chat file 
and shows stats for the whole chat and individual users. It also includes a search functionality and local LLM support 
via Ollama, so you can ask any questions about your chat—and all completely offline, meaning **your data stays in your 
device**!

## Installation

### Prerequisites
- Python 3.10 or higher
- Poetry ([installation guide](https://python-poetry.org/docs/#installation))
- Ollama ([installation guide](https://ollama.com/download))

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
3. Finally, run the app:
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
