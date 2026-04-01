from textual.app import ComposeResult
from textual.widgets import Header, Footer, Button, RichLog, TextArea
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.events import Key


class ChatInput(TextArea):
    def on_key(self, event: Key) -> None:
        if event.key == "ctrl+j":
            self.insert("\n")
            event.stop()
            event.prevent_default()
            return
        elif event.key == "enter":
            event.stop()
            event.prevent_default()
            self.screen.action_send()


class MessagingScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Header(show_clock=True, icon="P")
        with Horizontal(id="center-container"):
            with Vertical(id="chat-main"):
                yield RichLog(id="messages-log", auto_scroll=True, markup=True)
                with Horizontal(id="input-container"):
                    yield ChatInput(placeholder="Type your message...", id="message-input")
                    yield Button("Send", id="btn-send", variant="primary")
        yield Footer()

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-send":
            self.action_send()

    def action_send(self) -> None:
        input_widget = self.query_one("#message-input", ChatInput)
        message = input_widget.text.strip()

        if message and self.app.engine:
            self.app.engine.send_message(message)
            self.add_message(message, is_peer=False)
            input_widget.load_text("")
            input_widget.focus()

    def add_message(self, message: str, is_peer: bool = True) -> None:
        try:
            log = self.query_one("#messages-log", RichLog)
            if is_peer:
                log.write(f"[bold magenta]Peer:[/] {message}")
            else:
                log.write(f"[bold green]You:[/] {message}")
        except Exception:
            pass
