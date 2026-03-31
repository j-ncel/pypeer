from textual.app import ComposeResult
from textual.widgets import Header, Footer, Input, Button, Label, LoadingIndicator
from textual.containers import Vertical, Container
from textual.screen import Screen


class JoinScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Header(show_clock=True, icon="P")
        with Container(id="center-container"):
            yield Label("PYPEER", id="app-title")
            yield Label("Python Terminal P2P Messaging", id="app-description")
            with Vertical(id="join-view"):
                yield Input(placeholder="Enter Room ID", id="join-code-input", max_length=6)
                yield Button("Connect", id="btn-connect")
                yield Label("Connecting to signaling server...", id="join-status", classes="hidden")
                yield LoadingIndicator(id="join-loading", classes="hidden")
                yield Button("Back", id="btn-back")
        yield Footer()
