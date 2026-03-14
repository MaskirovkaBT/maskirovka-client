from typing import ClassVar

from textual.app import ComposeResult
from textual.containers import Container
from textual.reactive import reactive
from textual.widgets import DataTable

from domains.hangar import GroupedUnits, HangarService, HangarUnit
from domains.messages import HangarUnitSelected


class HangarWidget(Container):
    GROUPED_UNIT_PREFIX: ClassVar[str] = '  '
    GROUP_UNITS_PREFIX: ClassVar[str] = 'group:'
    COLUMN_QTY_KEY: ClassVar[str] = 'column_qty_key'
    COLUMN_TITLE_KEY: ClassVar[str] = 'column_title_key'

    _hangar_units: reactive[list[HangarUnit]] = reactive([])

    def __init__(self, service: HangarService, **kwargs):
        super().__init__(**kwargs)
        self.service = service
        self._unit_ids: list[int] = []
        self._grouped: list[GroupedUnits] = []
        self._expanded_groups: set[str] = set()

    def compose(self) -> ComposeResult:
        yield DataTable(
            id='hangar-table',
            cursor_type='row',
            classes='border'
        )

    def on_mount(self) -> None:
        self.service.delegate = self
        self.setup_table()
        self.refresh_data()

    def setup_table(self) -> None:
        table = self.query_one('#hangar-table', DataTable)
        table.add_columns(
            ('Кол-во', HangarWidget.COLUMN_QTY_KEY),
            ('Название', HangarWidget.COLUMN_TITLE_KEY),
            'Роль',
            'PV',
            'MV',
            'Ближ',
            'Сред',
            'Дал',
            'Брон',
            'Стр',
        )

    def refresh_data(self) -> None:
        self._hangar_units = self.service.get_all()
        self._grouped = self.service.get_grouped_units()
        self._populate_table()

    def service_did_change_unit_quantity(self, service: HangarService, unit_id: int) -> None:
        self._hangar_units = self.service.get_all()
        self._grouped = self.service.get_grouped_units()

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted):
        self.refresh_bindings()

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        row_key = str(event.row_key.value)
        if row_key.startswith(HangarWidget.GROUP_UNITS_PREFIX):
            group_name = row_key[6:]
            self._toggle_group(group_name)
        else:
            self._open_unit_details(row_key)

    def _toggle_group(self, group_name: str) -> None:
        if group_name in self._expanded_groups:
            self._expanded_groups.discard(group_name)
        else:
            self._expanded_groups.add(group_name)
        self._populate_table(should_preserve_cursor=True)

    def _populate_table(self, should_preserve_cursor: bool = False) -> None:
        table = self.query_one('#hangar-table', DataTable)

        row_index = table.cursor_row if should_preserve_cursor else None
        scroll_offset = table.scroll_offset

        table.clear()
        self._unit_ids = []

        if not self._hangar_units:
            table.add_row('—', '—', '-', '—', '—', '—', '—', '—', '—', '—', key='empty')
            return

        for group in self._grouped:
            is_expanded = group.base_name in self._expanded_groups
            icon = '▼' if is_expanded else '▶'
            first_unit = group.units[0].unit if group.units else None

            if group.variant_count == 1 and first_unit:
                table.add_row(
                    str(group.total_quantity),
                    first_unit.title,
                    first_unit.role,
                    str(first_unit.pv),
                    first_unit.mv,
                    str(first_unit.short),
                    str(first_unit.medium),
                    str(first_unit.long),
                    str(first_unit.armor),
                    str(first_unit.struc),
                    key=str(first_unit.unit_id)
                )
                self._unit_ids.append(first_unit.unit_id)
            else:
                table.add_row(
                    str(group.total_quantity),
                    f'{icon} {group.base_name}',
                    f'({group.variant_count} вар.)',
                    '',
                    '',
                    '',
                    '',
                    '',
                    '',
                    '',
                    key=f'{HangarWidget.GROUP_UNITS_PREFIX}{group.base_name}'
                )

                if is_expanded:
                    for hangar_unit in group.units:
                        u = hangar_unit.unit
                        self._unit_ids.append(u.unit_id)
                        table.add_row(
                            f'{HangarWidget.GROUPED_UNIT_PREFIX}{hangar_unit.quantity}',
                            f'{HangarWidget.GROUPED_UNIT_PREFIX}{HangarWidget.GROUPED_UNIT_PREFIX}└── {u.title}',
                            u.role,
                            str(u.pv),
                            u.mv,
                            str(u.short),
                            str(u.medium),
                            str(u.long),
                            str(u.armor),
                            str(u.struc),
                            key=str(u.unit_id)
                        )

        if row_index:
            table.move_cursor(row=row_index)
            table.scroll_to(y=scroll_offset.y, animate=False, immediate=True)

    def _open_unit_details(self, unit_id: str) -> None:
        hangar_unit = self.service.get_by_unit_id(int(unit_id))
        if hangar_unit:
            self.post_message(HangarUnitSelected(unit_id, hangar_unit.comment))
