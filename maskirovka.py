import asyncio

from textual import events, work
from textual.app import App, ComposeResult
from textual.containers import Vertical, Horizontal, Container
from textual.widget import Widget
from textual.widgets import Header, Footer, RadioSet, RadioButton, DataTable, Label

from domains.api_client import ApiClient, ApiError
from domains.blocks import Blocks
from domains.era import Era
from domains.faction import Faction
from domains.unit import Unit
from screens.error_screen import ErrorScreen
from screens.splash_screen import SplashScreen
from screens.unit_details_screen import UnitDetailsScreen


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
        self.api_client = ApiClient()

    async def on_mount(self) -> None:
        await self.push_screen(self.splash_screen)

        table = self.query_one(f"#{self.blocks[Blocks.MAIN_CONTENT]}", DataTable)
        table.add_columns(
            'Название',
            'Роль',
            'Стоимость',
            'Движение',
            'Ближняя',
            'Средняя',
            'Дальняя',
            'Броня',
            'Структура',
        )

        try:
            await asyncio.gather(
                self._load_eras(),
                self._load_factions()
            )
        except Exception as e:
            self.exception_on_splash = e

        await self._hide_splash()

    def on_key(self, event: events.Key) -> None:
        if event.key == "tab":
            event.prevent_default()
            self._select_block()
        elif event.key == "shift+tab":
            event.prevent_default()
            self._select_block(backward=True)

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        unit_id = event.row_key.value

        unit = next((u for u in self.units if str(u.unit_id) == unit_id), None)

        if unit:
            self.push_screen(UnitDetailsScreen(unit=unit))

    def check_action(self, action: str, parameters: tuple[object, ...]) -> bool | None:
        if action == "prev_page":
            return self.page > 1
        if action == "next_page":
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

        yield Label('Страница: —', id='pagination-info')
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
                ErrorScreen(title=f'{type(self.exception_on_splash).__name__}: {self.exception_on_splash}')
            )

    async def _load_eras(self) -> None:
        self.eras = await self.api_client.get_eras()

        radio_set = self.query_one(f"#{self.blocks[Blocks.ERAS]}", RadioSet)
        for item in self.eras:
            await radio_set.mount(RadioButton(item.title))

    async def _load_factions(self) -> None:
        self.factions = await self.api_client.get_factions()

        radio_set = self.query_one(f"#{self.blocks[Blocks.FACTIONS]}", RadioSet)
        for item in self.factions:
            await radio_set.mount(RadioButton(item.title))

    @work(exclusive=False)
    async def _search(self, page: int) -> None:
        try:
            if not self.eras or not self.factions:
                await self.push_screen(
                    ErrorScreen(title='Данные не загружены. Подождите завершения загрузки.')
                )
                return

            radio_set_factions = self.query_one(f"#{self.blocks[Blocks.FACTIONS]}", RadioSet)
            faction_index = radio_set_factions.pressed_index

            radio_set_eras = self.query_one(f"#{self.blocks[Blocks.ERAS]}", RadioSet)
            era_index = radio_set_eras.pressed_index

            if faction_index is None or era_index is None or faction_index < 0 or era_index < 0:
                await self.push_screen(
                    ErrorScreen(title='Следует вначале выбрать эру и фракцию')
                )
                return

            if era_index >= len(self.eras) or faction_index >= len(self.factions):
                await self.push_screen(
                    ErrorScreen(title='Некорректный выбор эры или фракции')
                )
                return

            era_id = self.eras[era_index].era_id
            faction_id = self.factions[faction_index].faction_id

            self.units, self.page, self.pages = await self.api_client.get_units(
                era_id=era_id,
                faction_id=faction_id,
                page=page
            )

            table = self.query_one(f"#{self.blocks[Blocks.MAIN_CONTENT]}", DataTable)
            table.loading = True
            table.clear()

            if not self.units:
                table.add_row('—', 'Нет данных', '—', '—', '—', '—', '—', '—', '—')
                table.loading = False
                pagination_label = self.query_one("#pagination-info", Label)
                pagination_label.update(f'Страница: {self.page} из {self.pages} (нет результатов)')
                self.refresh_bindings()
                return

            for item in self.units:
                table.add_row(
                    item.title,
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

            pagination_label = self.query_one("#pagination-info", Label)
            pagination_label.update(f'Страница: {self.page} из {self.pages}')

            self.refresh_bindings()

        except ApiError as e:
            await self.push_screen(
                ErrorScreen(title=f'Ошибка API: {e}')
            )
        except Exception as e:
            await self.push_screen(
                ErrorScreen(title=f'{type(e).__name__}: {e}')
            )


if __name__ == '__main__':
    app = Maskirovka()
    app.run()
