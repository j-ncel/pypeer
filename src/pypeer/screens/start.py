from textual.app import ComposeResult
from textual.widgets import Header, Footer, Button, Label
from textual.containers import Horizontal, Container
from textual.screen import Screen


class StartScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Header(show_clock=True, icon="P")
        with Container(id="center-container"):
            yield Label("PYPEER", id="app-title")
            yield Label("Python Terminal P2P Messaging", id="app-description")
            with Horizontal(id="action-bar"):
                yield Button("Host a Room", id="btn-host")
                yield Button("Join a Room", id="btn-join")
        yield Footer()