import asyncio
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Input, Static, Button, Label
from textual.containers import Horizontal, Container

from engine.firebase_sync import FirebaseSignaler
from engine.rtc_engine import RTCEngine
from constants import FIREBASE_DB_URL


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

    def __init__(self):
        super().__init__()
        self.engine = None

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True, icon="✉︎")
        yield StartScreen()
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        room_id = self.query_one("#room-id-input").value.strip()

        if not room_id:
            self.notify("Room ID Required", severity="error", title="Room ID Error")
            return

        signaler = FirebaseSignaler(FIREBASE_DB_URL, room_id)
        self.engine = RTCEngine(signaler)

        self.engine.on_status_callback = self.handle_status_change

        if event.button.id == "btn-host":
            self.notify(f"Initializing Host: {room_id}")
            asyncio.create_task(self.engine.setup_as_host())
        else:
            self.notify(f"Joining Room: {room_id}")
            asyncio.create_task(self.engine.setup_as_peer())

    def handle_status_change(self, status: str) -> None:
        self.notify(f"Connection Status: {status}", title="PYPEER Sync")


if __name__ == "__main__":
    PyPeer().run()
