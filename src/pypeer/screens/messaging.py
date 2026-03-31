from textual.app import ComposeResult
from textual.widgets import Header, Footer, Input, Button, RichLog
from textual.containers import Horizontal, Vertical
from textual.screen import Screen


class MessagingScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Header(show_clock=True, icon="P")
        with Horizontal(id="center-container"):
            with Vertical(id="chat-main"):
                yield RichLog(id="messages-log", auto_scroll=True, markup=True)
                with Horizontal(id="input-container"):
                    yield Input(placeholder="Type your message...", id="message-input")
                    yield Button("Send", id="btn-send", variant="primary")
        yield Footer()

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        message = event.value.strip()
        if message and self.app.engine:
            self.app.engine.send_message(message)
            self.add_message(message, is_peer=False)
            event.input.value = ""

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-send":
            input_widget = self.query_one("#message-input", Input)
            await self.on_input_submitted(Input.Submitted(input_widget, input_widget.value))

    def add_message(self, message: str, is_peer: bool = True) -> None:
        try:
            log = self.query_one("#messages-log", RichLog)
            if is_peer:
                log.write(f"[bold magenta]Peer:[/] {message}")
            else:
                log.write(f"[bold green]You:[/] {message}")
        except Exception:
            pass
