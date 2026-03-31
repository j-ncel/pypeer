from textual.app import ComposeResult
from textual.widgets import Header, Footer, Input, Button, RichLog
from textual.containers import Horizontal, Vertical
from textual.screen import Screen


class MessagingScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Header(show_clock=True, icon="P")
        with Horizontal(id="center-container"):
            with Vertical(id="chat-main"):
                yield RichLog(id="messages-log", auto_scroll=True, markup=True)
                with Horizontal(id="input-container"):
                    yield Input(placeholder="Type your message...", id="message-input")
                    yield Button("Send", id="btn-send", variant="primary")
        yield Footer()
