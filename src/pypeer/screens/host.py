import re
from textual.app import ComposeResult
from textual.widgets import Header, Footer, Button, Label, LoadingIndicator
from textual.containers import Vertical, Container
from textual.screen import Screen


class HostScreen(Screen):
    BINDINGS = [("c", "copy_code", "Copy Code")]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True, icon="P")
        with Container(id="center-container"):
            yield Label("PYPEER", id="app-title")
            yield Label("Python Terminal P2P Messaging", id="app-description")
            with Vertical(id="host-view"):
                yield LoadingIndicator(id="host-loading")
                yield Label("Creating Room...", id="status-label")

                code_label = Label("", id="host-code-display", classes="hidden")
                code_label.can_focus = True
                yield code_label

                yield Button("Cancel", id="btn-back")
        yield Footer()

    def on_click(self, event) -> None:
        label = self.query_one("#host-code-display", Label)
        if getattr(event, "widget", None) == label and not label.has_class("hidden"):
            self.action_copy_code()

    def action_copy_code(self) -> None:
        label = self.query_one("#host-code-display", Label)
        try:
            raw_text = label.render().plain
        except AttributeError:
            raw_text = str(label.renderable)

        match = re.search(r'[A-Z0-9]{6}', raw_text.upper())

        if match:
            clean_code = match.group(0)
            try:
                self.app.copy_to_clipboard(clean_code)
                self.app.notify(
                    f"Room Code: [cyan]{clean_code}[/] copied to clipboard!\nShare it with Peer.",
                    title="PYPEER",
                    severity="information"
                )
            except Exception:
                self.app.notify("Clipboard access denied.", severity="error")
