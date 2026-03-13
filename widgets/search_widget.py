from typing import ClassVar

from rich.text import Text
from textual.app import ComposeResult
from textual.containers import Container, Vertical, Horizontal
from textual.message import Message
from textual.reactive import reactive
from textual.widgets import RadioSet, DataTable, SelectionList, Static, Label


class SearchWidget(Container):
    COLUMN_TITLE_KEY: ClassVar[str] = 'column_title_key'

    BINDINGS = [
        ('tab', 'next_block', None),
        ('shift+tab', 'prev_block', None),
    ]

    current_block: reactive[str] = reactive('eras')
    _row_unit_ids: list[int] = []

    class UnitSelected(Message):
        def __init__(self, unit_id: str) -> None:
            self.unit_id = unit_id
            super().__init__()

    class AddToHangar(Message):
        def __init__(self, unit_id: str) -> None:
            self.unit_id = unit_id
            super().__init__()

    def compose(self) -> ComposeResult:
        yield Horizontal(
            Container(
                Vertical(
                    RadioSet(id='eras', classes='border selected-border'),
                    DataTable(id='main-content', cursor_type='row', classes='border'),
                    Label('Страница: —', id='pagination-info'),
                ),
                id='left'
            ),
            Vertical(
                SelectionList(id='factions', classes='border'),
                Static('Выберите фракцию', id='faction-hint'),
                id='right'
            )
        )

    def action_next_block(self) -> None:
        self._select_block()

    def action_prev_block(self) -> None:
        self._select_block(backward=True)

    def watch_current_block(self, old: str, new: str) -> None:
        if old:
            old_widget = self.query_one(f'#{old}')
            old_widget.remove_class('selected-border')
        new_widget = self.query_one(f'#{new}')
        new_widget.add_class('selected-border')

    def _select_block(self, backward: bool = False) -> None:
        blocks = ['eras', 'factions', 'main-content']
        current = str(self.current_block)
        current_idx = blocks.index(current)

        if backward:
            new_idx = (current_idx - 1) % len(blocks)
        else:
            new_idx = (current_idx + 1) % len(blocks)

        self.current_block = blocks[new_idx]

        widget_map = {
            'eras': RadioSet,
            'factions': SelectionList,
            'main-content': DataTable
        }
        new_block = str(self.current_block)
        widget = self.query_one(f'#{new_block}', widget_map[new_block])
        widget.focus()

    def on_radio_set_changed(self, event: RadioSet.Changed) -> None:
        self.current_block = 'eras'

    def on_selection_list_selection_highlighted(self, event: SelectionList.SelectionHighlighted) -> None:
        self.current_block = 'factions'
        selection_list = self.query_one('#factions', SelectionList)
        if selection_list.highlighted is not None:
            option = selection_list.get_option_at_index(selection_list.highlighted)
            self.update_faction_hint(str(option.prompt))

    def on_selection_list_selection_changed(self, event: SelectionList.SelectedChanged) -> None:
        selection_list = self.query_one('#factions', SelectionList)
        if selection_list.highlighted is not None:
            option = selection_list.get_option_at_index(selection_list.highlighted)
            self.update_faction_hint(str(option.prompt))

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        self.current_block = 'main-content'

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        self.post_message(self.UnitSelected(event.row_key.value))

    def setup_table(self) -> None:
        table = self.query_one('#main-content', DataTable)
        table.add_columns(
            ('Название', SearchWidget.COLUMN_TITLE_KEY),
            'Роль',
            'Стоимость',
            'Движение',
            'Ближняя',
            'Средняя',
            'Дальняя',
            'Броня',
            'Структура',
        )

    def populate_table(self, units: list, hangar_unit_ids: set[int] | None = None) -> None:
        table = self.query_one('#main-content', DataTable)
        table.clear()
        self._row_unit_ids = []
        hangar_ids = hangar_unit_ids or set()

        if not units:
            table.add_row('—', '-', '—', '—', '—', '—', '—', '—', '—')
        else:
            for item in units:
                self._row_unit_ids.append(item.unit_id)
                in_hangar = item.unit_id in hangar_ids
                title_text = Text(item.title)
                if in_hangar:
                    title_text.stylize('bold blink2 green')
                table.add_row(
                    title_text,
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

        if units:
            table.focus()

    def get_selected_era_index(self) -> int | None:
        radio_set = self.query_one('#eras', RadioSet)
        return radio_set.pressed_index

    def get_selected_faction_ids(self) -> list[int]:
        selection_list = self.query_one('#factions', SelectionList)
        return list(selection_list.selected)

    def update_faction_hint(self, title: str) -> None:
        hint = self.query_one('#faction-hint', Static)
        hint.update(title)

    def focus_table(self) -> None:
        table = self.query_one('#main-content', DataTable)
        table.focus()

    def add_to_hangar(self) -> None:
        table = self.query_one('#main-content', DataTable)
        if table.cursor_row is not None and table.cursor_row < len(self._row_unit_ids):
            unit_id = self._row_unit_ids[table.cursor_row]
            self.post_message(self.AddToHangar(str(unit_id)))
