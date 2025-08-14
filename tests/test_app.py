from streamlit.testing.v1 import AppTest


# Note: file uploader can't be tested with Streamlit testing module
def test_loadpage(resolve_path):
    at = AppTest.from_file(resolve_path("app.py"), default_timeout=60).run()

    assert at.markdown[0].value == "<h2 style='text-align: center;'>ChatScroll 🗣️📜</h2>"
