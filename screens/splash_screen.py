import random
import string
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static


class MatrixRain(Static):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.columns = []
        self.chars = "ｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉﾊﾋﾌﾍﾎﾏﾐﾑﾒﾓﾔﾕﾖﾗﾘﾙﾚﾛﾜﾝ" + string.ascii_uppercase + string.digits

    def on_mount(self) -> None:
        self.set_interval(0.05, self.update_matrix)

    def update_matrix(self) -> None:
        width = self.size.width
        height = self.size.height

        if width == 0 or height == 0:
            return

        if len(self.columns) != width:
            self.columns = [
                {
                    'drop_pos': random.randint(-20, height),
                    'speed': random.randint(1, 3),
                    'length': random.randint(5, 15),
                }
                for _ in range(width)
            ]

        screen = [[' ' for _ in range(width)] for _ in range(height)]

        for x, col in enumerate(self.columns):
            col['drop_pos'] += col['speed']

            if col['drop_pos'] - col['length'] > height:
                col['drop_pos'] = random.randint(-10, 0)
                col['speed'] = random.randint(1, 3)
                col['length'] = random.randint(5, 15)

            for i in range(col['length']):
                y = int(col['drop_pos']) - i
                if 0 <= y < height:
                    screen[y][x] = random.choice(self.chars)

        output = "\n".join("".join(row) for row in screen)
        self.update(output)


class SplashScreen(Screen):
    CSS_PATH = '../styles/styles_splash.tcss'

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
