from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Input, Static, Button, Label
from textual.containers import Horizontal, Container


class StartScreen(Static):
    def compose(self) -> ComposeResult:
        with Container(id="center-container"):
            yield Label("PYPEER", id="app-title")
            yield Label("Python Terminal P2P Messaging via WebRTC", id="app-description")

            yield Input(placeholder="Enter Room ID", id="room-id-input")

            with Horizontal(id="action-bar"):
                yield Button("Initialize Host", id="btn-host")
                yield Button("Join Remote", id="btn-join")


class PyPeer(App):
    TITLE = "pypeer"
    CSS_PATH = "styles.tcss"

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True, icon="✉︎")
        yield StartScreen()
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        key = self.query_one("#room-id-input").value.strip()
        if not key:
            self.notify("Room ID Required", severity="error", title="Room ID Error")
            return

        action = "Hosting" if event.button.id == "btn-host" else "Joining"
        self.notify(f"{action} Room: {key}", title="Connection Success")


if __name__ == "__main__":
    PyPeer().run()
