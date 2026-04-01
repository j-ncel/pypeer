import asyncio
from textual.screen import Screen
from textual.widgets import Label, LoadingIndicator
from pypeer.engine.signaler import FirebaseSignaler
from pypeer.engine.rtc_engine import RTCEngine
from pypeer.constants import FIREBASE_DB_URL


class ConnectionManager:
    def __init__(self, app):
        self.app = app

    def start_engine(self, room_id, is_host, password=""):
        signaler = FirebaseSignaler(FIREBASE_DB_URL, room_id, password)
        self.app.engine = RTCEngine(signaler)
        self.app.engine.on_status_callback = self.app.handle_status_change
        self.app.engine.on_message_callback = self.app.handle_incoming_message

        if is_host:
            asyncio.create_task(self.app.engine.setup_as_host())
        else:
            asyncio.create_task(self.app.engine.setup_as_peer())

    def run_host_sequence(self, room_id, password, screen: Screen):
        status = screen.query_one("#status-label", Label)
        loader = screen.query_one("#host-loading", LoadingIndicator)
        room_code = screen.query_one("#host-code-display", Label)

        status.update("Gathering ICE Candidates...")
        self.start_engine(room_id, is_host=True, password=password)

        attempts = 0

        def check_ice_status():
            nonlocal attempts
            attempts += 1

            if not self.app.engine or not self.app.engine.pc:
                return

            if self.app.engine.pc.iceGatheringState == "complete":
                loader.add_class("hidden")
                status.update("[cyan]Room Ready![/] Share this code:")
                room_code.update(room_id)
                room_code.remove_class("hidden")
            elif attempts > 150:
                loader.add_class("hidden")
                status.update("[red]Failed to create room. Check connection.[/]")
            else:
                screen.set_timer(0.2, check_ice_status)

        screen.set_timer(0.2, check_ice_status)

    def run_join_sequence(self, room_id, password, screen: Screen):
        screen.query_one("#join-code-input").add_class("hidden")
        screen.query_one("#btn-connect").add_class("hidden")
        screen.query_one("#join-status").remove_class("hidden")
        screen.query_one("#join-loading").remove_class("hidden")

        self.start_engine(room_id, is_host=False, password=password)
