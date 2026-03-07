from textual import work
from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Header, Footer, Label, TabbedContent, TabPane

from domains.api_client import ApiError
from domains.search_state import SearchState
from domains.unit_service import UnitService
from screens.error_screen import ErrorScreen
from screens.filter_screen import FilterScreen
from screens.sort_screen import SortScreen
from screens.splash_screen import SplashScreen
from screens.unit_details_screen import UnitDetailsScreen
from widgets.search_widget import SearchWidget


class Maskirovka(App):
    CSS_PATH = 'styles/styles_maskirovka.tcss'

    BINDINGS = [
        ('q', 'quit', 'Выход'),
        ('ctrl+s', 'search', 'Поиск'),
        ('ctrl+o', 'sort', 'Сортировка'),
        ('ctrl+f', 'filter', 'Фильтр'),
        ('ctrl+left', 'prev_page', 'Пред. страница'),
        ('ctrl+right', 'next_page', 'След. страница'),
    ]

    def __init__(self):
        super().__init__()

        self.state = SearchState()
        self.service = UnitService()
        self.splash_screen = SplashScreen()
        self.exception_on_splash: Exception | None = None

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True, icon='≡')

        with TabbedContent(id='main-tabs', initial="search-tab"):
            with TabPane('Поиск', id='search-tab'):
                yield SearchWidget(id='search-widget')
            with TabPane('Ангар', id='hangar-tab'):
                yield Container(id='hangar-content')

        yield Label('Страница: —', id='pagination-info')
        yield Footer(show_command_palette=False)

    async def on_mount(self) -> None:
        await self.push_screen(self.splash_screen)

        search_widget = self.query_one('#search-widget', SearchWidget)
        search_widget.setup_table()

        self._load_initial_data()

    def check_action(self, action: str, parameters: tuple[object, ...]) -> bool | None:
        if action == 'quit':
            return True

        tabs = self.query_one('#main-tabs', TabbedContent)
        is_search_active = tabs.active == 'search-tab'

        if action in ('search', 'sort', 'filter', 'prev_page', 'next_page'):
            if not is_search_active:
                return False
            if action == 'prev_page':
                return self.state.page > 1
            if action == 'next_page':
                return self.state.page < self.state.pages
        return True

    def on_tabbed_content_tab_activated(self, event: TabbedContent.TabActivated) -> None:
        self.refresh_bindings()

    def on_search_widget_unit_selected(self, event: SearchWidget.UnitSelected) -> None:
        unit = next((u for u in self.state.units if str(u.unit_id) == event.unit_id), None)
        if unit:
            self.push_screen(UnitDetailsScreen(unit=unit))

    async def action_search(self) -> None:
        self._search(page=1)

    async def action_sort(self) -> None:
        async def handle_sort(result: dict | None) -> None:
            if result is not None:
                self.state.sort_by = result['field']
                self.state.sort_order = result['order']
                self._search(page=1)

        await self.push_screen(
            SortScreen(
                current_field=self.state.sort_by,
                current_order=self.state.sort_order
            ),
            handle_sort
        )

    async def action_filter(self) -> None:
        async def handle_filter(result: dict | None) -> None:
            if result is not None:
                self.state.filters = result
                self._search(page=1)

        await self.push_screen(
            FilterScreen(
                current_filters=self.state.filters,
                types=self.state.types,
                roles=self.state.roles
            ),
            handle_filter
        )

    async def action_prev_page(self) -> None:
        if self.state.prev_page():
            self._search(page=self.state.page)

    async def action_next_page(self) -> None:
        if self.state.next_page():
            self._search(page=self.state.page)

    @work(exclusive=False)
    async def _load_initial_data(self) -> None:
        try:
            self.state.eras, self.state.factions, self.state.types, self.state.roles = \
                await self.service.load_reference_data()
        except Exception as e:
            self.exception_on_splash = e

        await self._hide_splash()

        if not self.exception_on_splash:
            self._populate_ui()

    def _populate_ui(self) -> None:
        search_widget = self.query_one('#search-widget', SearchWidget)

        radio_set = search_widget.query_one('#eras')
        for item in self.state.eras:
            from textual.widgets import RadioButton
            radio_set.mount(RadioButton(item.title))

        selection_list = search_widget.query_one('#factions')
        options = [(item.title, item.faction_id) for item in self.state.factions]
        selection_list.add_options(options)

    async def _hide_splash(self) -> None:
        self.splash_screen.styles.animate(
            'opacity',
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

    @work(exclusive=False)
    async def _search(self, page: int) -> None:
        try:
            if not self.state.eras or not self.state.factions:
                await self.push_screen(
                    ErrorScreen(title='Данные не загружены. Подождите завершения загрузки.')
                )
                return

            search_widget = self.query_one('#search-widget', SearchWidget)

            faction_ids = search_widget.get_selected_faction_ids()
            era_index = search_widget.get_selected_era_index()

            if not faction_ids or era_index is None or era_index < 0:
                await self.push_screen(
                    ErrorScreen(title='Следует вначале выбрать эру и фракцию')
                )
                return

            if era_index >= len(self.state.eras):
                await self.push_screen(
                    ErrorScreen(title='Некорректный выбор эры или фракции')
                )
                return

            era_id = self.state.eras[era_index].era_id

            self.state.units, self.state.page, self.state.pages = await self.service.search_units(
                era_id=era_id,
                faction_ids=faction_ids,
                page=page,
                sort_by=self.state.sort_by,
                sort_order=self.state.sort_order,
                filters=self.state.filters if self.state.filters else None
            )

            search_widget.populate_table(self.state.units)

            pagination_label = self.query_one('#pagination-info', Label)
            pagination_label.update(f'Страница: {self.state.page} из {self.state.pages}')

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
