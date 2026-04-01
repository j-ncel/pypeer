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
                yield Input(
                    placeholder="Password (Optional)",
                    id="join-password-input",
                    password=True
                )
                yield Button("Connect", id="btn-connect")
                yield Label("Connecting to signaling server...", id="join-status", classes="hidden")
                yield LoadingIndicator(id="join-loading", classes="hidden")
                yield Button("Back", id="btn-back")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-connect":
            room_id = self.query_one("#join-code-input", Input).value.strip().upper()
            password = self.query_one("#join-password-input", Input).value.strip()

            if len(room_id) == 6:
                self.app.manager.run_join_sequence(room_id, password, self)
            else:
                self.notify("Room ID must be 6 characters.", severity="error")
