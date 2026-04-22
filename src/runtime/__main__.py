"""Launch the chat ASGI server: ``python -m src.runtime`` (same app as ``src.chat_server``)."""

from .chat_server import run_chat_server

if __name__ == "__main__":
    run_chat_server()
