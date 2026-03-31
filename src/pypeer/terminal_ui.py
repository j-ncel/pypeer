import asyncio
from textual.app import App
from textual.widgets import Input, Button, RichLog

from logic.connection_manager import ConnectionManager
from screens import StartScreen, HostScreen, JoinScreen, MessagingScreen

from utils.id_generator import generate_room_id


class PyPeer(App):
    TITLE = "pypeer"
    CSS_PATH = "styles.tcss"

    def __init__(self):
        super().__init__()
        self.engine = None
        self.manager = ConnectionManager(self)

    def on_mount(self) -> None:
        self.push_screen(StartScreen())

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-host":
            host_screen = HostScreen()
            await self.push_screen(host_screen)
            room_id = generate_room_id()
            self.call_after_refresh(self.manager.run_host_sequence, room_id, host_screen)

        elif event.button.id == "btn-join":
            await self.push_screen(JoinScreen())

        elif event.button.id == "btn-back":

            if self.engine:
                self.notify("Cancelling and cleaning up room...", title="PYPEER")
                asyncio.create_task(self.cleanup_engine())

            self.pop_screen()

        elif event.button.id == "btn-connect":
            room_input = self.screen.query_one("#join-code-input", Input)
            room_id = room_input.value.strip().upper()
            if len(room_id) == 6:
                self.manager.run_join_sequence(room_id, self.screen)

        elif event.button.id == "btn-send":
            input_widget = self.screen.query_one("#message-input", Input)
            await self.on_input_submitted(Input.Submitted(input_widget, input_widget.value))

    def handle_status_change(self, status: str) -> None:
        success_states = ["Live", "Connected"]
        failure_states = ["Closed", "Failed", "Disconnected"]
        pending_states = ["Gathering", "Connecting", "Signaling"]

        if status in success_states:
            if not isinstance(self.screen, MessagingScreen):
                self.push_screen(MessagingScreen())
            self.notify("Secure P2P tunnel established.", title="PYPEER: ACTIVE", severity="information")

        elif status in failure_states:
            if isinstance(self.screen, MessagingScreen):
                self.notify("Peer connection lost. Cleaning up...", title="PYPEER: OFFLINE", severity="error")
                self.pop_screen()
            else:
                self.notify(f"Connection {status.lower()}.", title="PYPEER: ERROR", severity="error")

        elif status in pending_states:
            self.notify(f"{status}...", title="PYPEER: SYNC", severity="information")

    def handle_incoming_message(self, message: str) -> None:
        if isinstance(self.screen, MessagingScreen):
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

    async def cleanup_engine(self) -> None:
        """Helper to safely cancel and close the engine."""
        if self.engine:
            engine_to_clean = self.engine
            self.engine = None
            try:
                await asyncio.shield(engine_to_clean.signaler.clear_room())
                await engine_to_clean.close()
            except Exception as e:
                self.log(f"Cleanup error: {e}")

    async def on_unmount(self) -> None:
        await self.cleanup_engine()


if __name__ == "__main__":
    PyPeer().run()
