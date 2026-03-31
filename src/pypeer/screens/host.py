from textual.app import ComposeResult
from textual.widgets import Header, Footer, Button, Label, LoadingIndicator
from textual.containers import Vertical, Container
from textual.screen import Screen


class HostScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Header(show_clock=True, icon="P")
        with Container(id="center-container"):
            yield Label("PYPEER", id="app-title")
            yield Label("Python Terminal P2P Messaging", id="app-description")
            with Vertical(id="host-view"):
                yield LoadingIndicator(id="host-loading")
                yield Label("Creating Room...", id="status-label")
                yield Label("", id="host-code-display", classes="hidden")
                yield Button("Cancel", id="btn-back")
        yield Footer()
