import asyncio
from textual.app import App
from textual.widgets import Input, Button, RichLog

from logic.connection_manager import ConnectionManager
from screens import StartScreen, HostScreen, JoinScreen, MessagingScreen

from utils.id_generator import generate_room_id


class PyPeer(App):
    TITLE = "pypeer"
    CSS_PATH = "styles.tcss"

    BINDINGS = [
        ("ctrl+q", "exit", "Quit"),
        ("escape", "back", "Back"),
    ]

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
            await self.action_back()

    async def action_back(self) -> None:
        if self.engine:
            self.notify("Cleaning up session...", title="PYPEER")
            asyncio.create_task(self.cleanup_engine())
        if len(self.screen_stack) > 2:
            self.pop_screen()
        else:
            self.exit()

    async def action_exit(self) -> None:
        self.notify("Shutting down...", title="PYPEER")
        await self.cleanup_engine()
        self.exit()

    def handle_status_change(self, status: str) -> None:
        success_states = ["Live", "Connected"]
        failure_states = ["Closed", "Failed", "Disconnected"]
        pending_states = ["Gathering", "Connecting", "Signaling"]

        if not self._is_mounted or not self.screen_stack:
            return

        if status in success_states:
            if not isinstance(self.screen, MessagingScreen):
                self.push_screen(MessagingScreen())
            self.notify("Secure P2P tunnel established.", title="PYPEER: ACTIVE", severity="information")

        elif status in failure_states:
            if isinstance(self.screen, MessagingScreen):
                self.notify("Peer connection lost. Returning to Menu.", title="PYPEER: OFFLINE", severity="error")
                while len(self.screen_stack) > 2:
                    self.pop_screen()
                asyncio.create_task(self.cleanup_engine())
            else:
                self.notify(f"Connection {status.lower()}.", severity="error")

        elif status in pending_states:
            self.notify(f"{status}...", title="PYPEER: SYNC", severity="information")

    def handle_incoming_message(self, message: str) -> None:
        if isinstance(self.screen, MessagingScreen):
            self.screen.add_message(message, is_peer=True)

    async def cleanup_engine(self) -> None:
        """Helper to safely cancel and close the engine."""
        if self.engine:
            engine_to_clean = self.engine
            self.engine = None
            try:
                async with asyncio.timeout(2.0):
                    await engine_to_clean.signaler.clear_room()
                    await engine_to_clean.close()
            except Exception as e:
                self.log(f"Cleanup error: {e}")

    async def on_unmount(self) -> None:
        await self.cleanup_engine()


if __name__ == "__main__":
    PyPeer().run()
