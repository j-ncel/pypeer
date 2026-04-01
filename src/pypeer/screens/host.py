import re
from textual.app import ComposeResult
from textual.widgets import Header, Footer, Button, Label, LoadingIndicator, Input
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

                yield Input(placeholder="Optional Password", id="host-password-input", password=True)
                yield Button("Create Room", variant="primary", id="btn-start-hosting")

                yield LoadingIndicator(id="host-loading", classes="hidden")
                yield Label("Creating Room...", id="status-label", classes="hidden")

                code_label = Label("", id="host-code-display", classes="hidden")
                code_label.can_focus = True
                yield code_label

                yield Button("Cancel", id="btn-back")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-start-hosting":
            self.query_one("#host-password-input").add_class("hidden")
            self.query_one("#btn-start-hosting").add_class("hidden")

            self.query_one("#host-loading").remove_class("hidden")
            self.query_one("#status-label").remove_class("hidden")

            password = self.query_one("#host-password-input", Input).value.strip()
            self.app.start_hosting_sequence(password)

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
