import asyncio
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Input, Button, Label, LoadingIndicator
from textual.containers import Horizontal, Vertical, Container
from textual.screen import Screen

from engine.firebase_sync import FirebaseSignaler
from engine.rtc_engine import RTCEngine
from constants import FIREBASE_DB_URL
from utils.id_generator import generate_room_id


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


class PyPeer(App):
    TITLE = "pypeer"
    CSS_PATH = "styles.tcss"

    def __init__(self):
        super().__init__()
        self.engine = None

    def on_mount(self) -> None:
        self.push_screen(StartScreen())

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-host":
            host_screen = HostScreen()
            await self.push_screen(host_screen)
            room_id = generate_room_id()
            self.call_after_refresh(self.run_host_sequence, room_id, host_screen)

        elif event.button.id == "btn-join":
            await self.push_screen(JoinScreen())

        elif event.button.id == "btn-back":
            self.pop_screen()

        elif event.button.id == "btn-connect":
            room_input = self.screen.query_one("#join-code-input", Input)
            room_id = room_input.value.strip().upper()
            if len(room_id) == 6:
                await self.run_join_sequence(room_id, self.screen)

    async def run_host_sequence(self, room_id: str, screen: Screen):
        status = screen.query_one("#status-label", Label)
        loader = screen.query_one("#host-loading", LoadingIndicator)
        room_code = screen.query_one("#host-code-display", Label)

        status.update("Gathering ICE Candidates...")

        self.start_engine(room_id, is_host=True)

        async def check_ice_status():
            if self.engine and self.engine.pc.iceGatheringState == "complete":
                loader.add_class("hidden")
                status.update("[cyan]Room Ready![/] Share this code:")
                room_code.update(room_id)
                room_code.remove_class("hidden")
            else:
                self.set_timer(0.2, check_ice_status)

        await check_ice_status()

    async def run_join_sequence(self, room_id: str, screen: Screen):
        screen.query_one("#join-code-input").add_class("hidden")
        screen.query_one("#btn-connect").add_class("hidden")
        screen.query_one("#join-status").remove_class("hidden")
        screen.query_one("#join-loading").remove_class("hidden")

        self.start_engine(room_id, is_host=False)

    def start_engine(self, room_id, is_host):
        signaler = FirebaseSignaler(FIREBASE_DB_URL, room_id)
        self.engine = RTCEngine(signaler)
        self.engine.on_status_callback = self.handle_status_change

        if is_host:
            asyncio.create_task(self.engine.setup_as_host())
        else:
            asyncio.create_task(self.engine.setup_as_peer())

    def handle_status_change(self, status: str) -> None:
        if status == "Connected":
            try:
                self.screen.query_one("#join-loading").add_class("hidden")
                self.screen.query_one("#join-status").update("[cyan]Connected![/]")
            except Exception:
                pass

        self.notify(f"PYPEER: {status}", title="Network Sync")


if __name__ == "__main__":
    PyPeer().run()
