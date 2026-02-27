from textual.app import ComposeResult
from textual.containers import Grid
from textual.screen import Screen
from textual.widgets import Button, Label


class ErrorScreen(Screen):
    CSS_PATH = 'styles/styles_error.tcss'

    def __init__(self, title: str):
        super().__init__()

        self.title = title

    def compose(self) -> ComposeResult:
        yield Grid(
            Label(self.title, id='error_title'),
            Button("OK", variant="primary", id="error_ok"),
            id='error_container'
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.app.pop_screen()