import asyncio
from textual.app import App
from textual.widgets import Input, Button, Label, LoadingIndicator, RichLog
from textual.screen import Screen

from screens import StartScreen, HostScreen, JoinScreen, MessagingScreen

from engine.firebase_sync import FirebaseSignaler
from engine.rtc_engine import RTCEngine
from constants import FIREBASE_DB_URL
from utils.id_generator import generate_room_id


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

        elif event.button.id == "btn-send":
            input_widget = self.screen.query_one("#message-input", Input)
            await self.on_input_submitted(Input.Submitted(input_widget, input_widget.value))

    async def run_host_sequence(self, room_id: str, screen: Screen):
        status = screen.query_one("#status-label", Label)
        loader = screen.query_one("#host-loading", LoadingIndicator)
        room_code = screen.query_one("#host-code-display", Label)

        status.update("Gathering ICE Candidates...")

        self.start_engine(room_id, is_host=True)

        self.attempts = 0

        async def check_ice_status():
            self.attempts += 1
            if self.engine and self.engine.pc.iceGatheringState == "complete":
                loader.add_class("hidden")
                status.update("[cyan]Room Ready![/] Share this code:")
                room_code.update(room_id)
                room_code.remove_class("hidden")
            elif self.attempts > 150:
                loader.add_class("hidden")
                status.update("[red]Failed to create room. Check connection.[/]")
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
        self.engine.on_message_callback = self.handle_incoming_message

        if is_host:
            asyncio.create_task(self.engine.setup_as_host())
        else:
            asyncio.create_task(self.engine.setup_as_peer())

    def handle_status_change(self, status: str) -> None:
        if status in ["Live", "Connected"]:
            if not isinstance(self.screen, MessagingScreen):
                chat_screen = MessagingScreen()
                self.push_screen(chat_screen)

        self.notify(f"PYPEER: {status}", title="Network Sync")

    def handle_incoming_message(self, message: str) -> None:
        try:
            msg = self.screen.query_one("#messages-log", RichLog)
            msg.write(f"[bold magenta]Peer:[/] {message}")
        except Exception:
            pass

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "message-input":
            message = event.value.strip()
            if message and self.engine:
                self.engine.send_message(message)

                msg = self.screen.query_one("#messages-log", RichLog)
                msg.write(f"[bold green]You:[/] {message}")

                event.input.value = ""


if __name__ == "__main__":
    PyPeer().run()
