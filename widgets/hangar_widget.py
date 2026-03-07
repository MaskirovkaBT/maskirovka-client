from textual.app import ComposeResult
from textual.containers import Container
from textual.message import Message
from textual.reactive import reactive
from textual.widgets import DataTable

from domains.hangar_service import HangarService
from domains.hangar_unit import HangarUnit


class HangarWidget(Container):
    hangar_units: reactive[list[HangarUnit]] = reactive([])

    class UnitSelected(Message):
        def __init__(self, unit_id: str, comment: str = '') -> None:
            self.unit_id = unit_id
            self.comment = comment
            super().__init__()

    class DataChanged(Message): pass

    def __init__(self, service: HangarService | None = None, **kwargs):
        super().__init__(**kwargs)
        self.service = service or HangarService()
        self._unit_ids: list[int] = []

    def compose(self) -> ComposeResult:
        yield DataTable(
            id='hangar-table',
            cursor_type='row',
            classes='border'
        )

    def on_mount(self) -> None:
        self.setup_table()
        self.refresh_data()

    def setup_table(self) -> None:
        table = self.query_one('#hangar-table', DataTable)
        table.add_columns(
            'Кол-во',
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

    def refresh_data(self) -> None:
        self.hangar_units = self.service.get_all()
        self._populate_table()
        self.post_message(self.DataChanged())

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        self._open_unit_details(str(event.row_key.value))

    def _populate_table(self) -> None:
        table = self.query_one('#hangar-table', DataTable)
        table.clear()
        self._unit_ids = []

        if not self.hangar_units:
            table.add_row('—', '—', '-', '—', '—', '—', '—', '—', '—', '—')
            return

        for hangar_unit in self.hangar_units:
            u = hangar_unit.unit
            self._unit_ids.append(u.unit_id)
            table.add_row(
                str(hangar_unit.quantity),
                u.title,
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

        if self.hangar_units:
            table.focus()

    def _open_unit_details(self, unit_id: str) -> None:
        hangar_unit = self.service.get_by_unit_id(int(unit_id))
        if hangar_unit:
            self.post_message(self.UnitSelected(unit_id, hangar_unit.comment))
