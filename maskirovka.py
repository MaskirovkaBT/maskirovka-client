import httpx
from pydantic import TypeAdapter
from textual import case, events
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Vertical, Horizontal, Container
from textual.widget import Widget
from textual.widgets import Header, Footer, Placeholder, RadioSet, RadioButton, DataTable

from error_screen import ErrorScreen
from models import *
from settings import settings
from splash_screen import SplashScreen


class Maskirovka(App):
    CSS_PATH = 'styles/styles_maskirovka.tcss'

    BINDINGS = [
        ('q', 'quit', 'Выход'),
        ('ctrl+s', 'search', 'Поиск'),
    ]

    def __init__(self):
        super().__init__()

        self.blocks = {
            Blocks.ERAS: 'eras',
            Blocks.FACTIONS: 'factions',
            Blocks.MAIN_CONTENT: 'main-content',
        }
        self.current_block = Blocks.ERAS
        self.splash_screen = SplashScreen()
        self.eras: list[Era] | None = None
        self.factions: list[Faction] | None = None
        self.exception_on_splash: Exception | None = None
        self.units: list[Unit] | None = None

    async def on_mount(self) -> None:
        await self.push_screen(self.splash_screen)

        table = self.query_one(f"#{self.blocks[Blocks.MAIN_CONTENT]}", DataTable)
        table.add_columns(
            'Название',
            'Тип',
            'Роль',
            'Стоимость',
            'Движение',
            'Ближняя',
            'Средняя',
            'Дальняя',
            'Броня',
            'Структура',
        )

        await self._load_eras()
        await self._load_factions()
        await self._hide_splash()

    def on_key(self, event: events.Key) -> None:
        if event.key == "tab":
            event.prevent_default()
            self._select_block()
        elif event.key == "shift+tab":
            event.prevent_default()
            self._select_block(backward=True)

    def compose(self) -> ComposeResult:
        yield Header(
            show_clock=True,
            icon='≡'
        )

        yield Container(
            Horizontal(
                Container(
                    Vertical(
                        RadioSet(
                            id=self.blocks[Blocks.ERAS],
                            classes='border selected-border',
                        ),
                        DataTable(
                            cursor_type='row',
                            id=self.blocks[Blocks.MAIN_CONTENT],
                            classes='border',
                        )
                    ),
                    id='left'
                ),
                Container(
                    RadioSet(
                        id=self.blocks[Blocks.FACTIONS],
                        classes='border',
                    ),
                    id='right'
                )
            ),
            id='main'
        )

        yield Footer(
            show_command_palette=False,
        )

    async def action_search(self) -> None:
        await self._search()

    def _select_block(self, backward: bool = False) -> None:
        block = self.query_one(f"#{self.blocks[self.current_block]}")
        block.remove_class('selected-border')

        view: Widget | None = None

        match self.current_block:
            case Blocks.ERAS:
                if backward:
                    self.current_block = Blocks.MAIN_CONTENT
                    view = self.query_one(f"#{self.blocks[Blocks.MAIN_CONTENT]}", DataTable)
                else:
                    self.current_block = Blocks.FACTIONS
                    view = self.query_one(f"#{self.blocks[Blocks.FACTIONS]}", RadioSet)
            case Blocks.FACTIONS:
                if backward:
                    self.current_block = Blocks.ERAS
                    view = self.query_one(f"#{self.blocks[Blocks.ERAS]}", RadioSet)
                else:
                    self.current_block = Blocks.MAIN_CONTENT
                    view = self.query_one(f"#{self.blocks[Blocks.MAIN_CONTENT]}", DataTable)
            case Blocks.MAIN_CONTENT:
                if backward:
                    self.current_block = Blocks.FACTIONS
                    view = self.query_one(f"#{self.blocks[Blocks.FACTIONS]}", RadioSet)
                else:
                    self.current_block = Blocks.ERAS
                    view = self.query_one(f"#{self.blocks[Blocks.ERAS]}", RadioSet)

        block = self.query_one(f"#{self.blocks[self.current_block]}")
        block.add_class('selected-border')

        if view:
            view.focus()

    async def _hide_splash(self) -> None:
        self.splash_screen.styles.animate(
            "opacity",
            value=0.0,
            duration=3.0,
            on_complete=self._on_splash_hidden
        )

    async def _on_splash_hidden(self) -> None:
        await self.pop_screen()

        if self.exception_on_splash:
            await self.push_screen(
                ErrorScreen(title=f"{type(self.exception_on_splash).__name__}: {self.exception_on_splash}")
            )

    async def _load_eras(self) -> None:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{settings.api_base_url}/eras")
                data = response.json()
                self.eras = TypeAdapter(list[Era]).validate_python(data)

                radio_set = self.query_one(f"#{self.blocks[Blocks.ERAS]}", RadioSet)
                for item in self.eras:
                    await radio_set.mount(RadioButton(item.title))

        except Exception as e:
            self.exception_on_splash = e

    async def _load_factions(self) -> None:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{settings.api_base_url}/factions")
                data = response.json()
                self.factions = TypeAdapter(list[Faction]).validate_python(data)

                radio_set = self.query_one(f"#{self.blocks[Blocks.FACTIONS]}", RadioSet)
                for item in self.factions:
                    await radio_set.mount(RadioButton(item.title))

        except Exception as e:
            self.exception_on_splash = e

    async def _search(self) -> None:
        try:
            async with httpx.AsyncClient() as client:
                radio_set_factions = self.query_one(f"#{self.blocks[Blocks.FACTIONS]}", RadioSet)
                faction_index = radio_set_factions.pressed_index

                radio_set_eras = self.query_one(f"#{self.blocks[Blocks.ERAS]}", RadioSet)
                era_index = radio_set_eras.pressed_index

                if faction_index < 0 or era_index < 0:
                    await self.push_screen(
                        ErrorScreen(title='Следует вначале выбрать эру и фракцию')
                    )
                    return

                era_id = self.eras[era_index].era_id
                faction_id = self.factions[faction_index].faction_id

                response = await client.get(f"{settings.api_base_url}/units?era_id={era_id}&faction_id={faction_id}")
                data = response.json()
                self.units = TypeAdapter(list[Unit]).validate_python(data)

        except Exception as e:
            await self.push_screen(
                ErrorScreen(title=f"{type(e).__name__}: {e}")
            )


if __name__ == '__main__':
    app = Maskirovka()
    app.run()
