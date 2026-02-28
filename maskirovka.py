import httpx
from pydantic import TypeAdapter
from textual import events, work
from textual.app import App, ComposeResult
from textual.containers import Vertical, Horizontal, Container
from textual.widget import Widget
from textual.widgets import Header, Footer, RadioSet, RadioButton, DataTable

from domains.blocks import Blocks
from domains.era import Era
from domains.faction import Faction
from domains.settings import settings
from domains.unit import Unit
from screens.error_screen import ErrorScreen
from screens.splash_screen import SplashScreen


class Maskirovka(App):
    CSS_PATH = 'styles/styles_maskirovka.tcss'

    BINDINGS = [
        ('q', 'quit', 'Выход'),
        ('ctrl+s', 'search', 'Поиск'),
        ('ctrl+left', 'prev_page', 'Пред. страница'),
        ('ctrl+right', 'next_page', 'След. страница'),
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
        self.page = 1
        self.pages = 0

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

        self._load_eras()
        self._load_factions()
        await self._hide_splash()

    def on_key(self, event: events.Key) -> None:
        if event.key == "tab":
            event.prevent_default()
            self._select_block()
        elif event.key == "shift+tab":
            event.prevent_default()
            self._select_block(backward=True)

    def check_action(self, action: str, parameters: tuple[object, ...]) -> bool | None:
        if action == "prev_page":
            print(f"prev_page: {self.page}")
            return self.page > 1
        if action == "next_page":
            print(f"next_page: {self.page}")
            return self.page < self.pages
        return True

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
        self._search(page=1)

    async def action_prev_page(self) -> None:
        if self.page - 1 <= 0:
            return
        self._search(page=self.page - 1)

    async def action_next_page(self) -> None:
        if self.page + 1 > self.pages:
            return
        self._search(page=self.page + 1)

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

    @work(exclusive=False)
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

    @work(exclusive=False)
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

    @work(exclusive=False)
    async def _search(self, page: int) -> None:
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

                response = await client.get(
                    f"{settings.api_base_url}"
                    f"/units?era_id={era_id}"
                    f"&faction_id={faction_id}"
                    f"&page={page}"
                )
                data = response.json()

                items = data.get('items', [])
                self.units = TypeAdapter(list[Unit]).validate_python(items)
                self.page = data['page']
                self.pages = data['pages']

                table = self.query_one(f"#{self.blocks[Blocks.MAIN_CONTENT]}", DataTable)
                table.loading = True
                table.clear()

                for item in self.units:
                    table.add_row(
                        item.title,
                        item.unit_type,
                        item.role,
                        str(item.pv),
                        item.mv,
                        str(item.short),
                        str(item.medium),
                        str(item.long),
                        str(item.armor),
                        str(item.struc),
                        key=str(item.unit_id)
                    )

                table.loading = False
                table.focus()

                self.refresh_bindings()

        except Exception as e:
            await self.push_screen(
                ErrorScreen(title=f"{type(e).__name__}: {e}")
            )


if __name__ == '__main__':
    app = Maskirovka()
    app.run()
