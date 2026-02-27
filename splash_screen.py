import random
import string
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static


class MatrixRain(Static):
    def on_mount(self) -> None:
        self.set_interval(0.1, self.update_matrix)

    def update_matrix(self) -> None:
        chars = string.ascii_uppercase + string.digits + "ｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿ"
        width = self.size.width
        height = self.size.height

        lines = []
        for _ in range(height):
            line = "".join(random.choice(chars) if random.random() > 0.7 else " " for _ in range(width))
            lines.append(line)

        self.update("\n".join(lines))

class SplashScreen(Screen):
    CSS_PATH = 'styles/styles_splash.tcss'

    def compose(self) -> ComposeResult:
        yield Static(
            """
███╗   ███╗ █████╗ ███████╗██╗  ██╗██╗██████╗  ██████╗ ██╗   ██╗██╗  ██╗ █████╗ 
████╗ ████║██╔══██╗██╔════╝██║ ██╔╝██║██╔══██╗██╔═══██╗██║   ██║██║ ██╔╝██╔══██╗
██╔████╔██║███████║███████╗█████╔╝ ██║██████╔╝██║   ██║██║   ██║█████╔╝ ███████║
██║╚██╔╝██║██╔══██║╚════██║██╔═██╗ ██║██╔══██╗██║   ██║╚██╗ ██╔╝██╔═██╗ ██╔══██║
██║ ╚═╝ ██║██║  ██║███████║██║  ██╗██║██║  ██║╚██████╔╝ ╚████╔╝ ██║  ██╗██║  ██║
╚═╝     ╚═╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝╚═╝  ╚═╝ ╚═════╝   ╚═══╝  ╚═╝  ╚═╝╚═╝  ╚═╝
                                                                                                                                                                                                                                                             
            """,
            id="splash",
        )

        yield MatrixRain()

        yield Static(
            '[blink]Загружаем данные[/]',
            id='loader',
        )