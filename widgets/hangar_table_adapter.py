from typing import ClassVar

from textual.coordinate import Coordinate
from textual.widgets import DataTable

from domains import extract_base_name, HangarService
from widgets.hangar_widget import HangarWidget


class HangarTableAdapter:
    def __init__(self, table: DataTable, hangar_service: HangarService):
        self.table = table
        self.service = hangar_service

    def is_group_row(self, row_key: str) -> bool:
        return row_key.startswith(HangarWidget.GROUP_UNITS_PREFIX)

    def cleanup_group(self, full_title: str) -> None:
        base_name = self._extract_base_name(full_title)
        group_row_key = f'{HangarWidget.GROUP_UNITS_PREFIX}{base_name}'

        try:
            if self.table.get_row(row_key=group_row_key) and not self.service.is_variants_exists(base_name):
                self.refresh()
        except Exception as e:
            pass

    def is_empty_row(self, row_key: str) -> bool:
        return row_key == 'empty'

    def get_unit_info_at_cursor(self) -> tuple[int, int, str] | None:
        row_index = self.table.cursor_row
        if row_index is None or row_index < 0:
            return None

        if not self.table.rows:
            return None

        row_key = self.table.ordered_rows[row_index].key
        key_value = str(row_key.value)

        if self.is_group_row(key_value) or self.is_empty_row(key_value):
            return None

        cell_qty_value = self.table.get_cell(
            row_key=row_key,
            column_key=HangarWidget.COLUMN_QTY_KEY
        )
        current_qty = int(cell_qty_value)

        title = self.table.get_cell(
            row_key=row_key,
            column_key=HangarWidget.COLUMN_TITLE_KEY
        )

        return int(key_value), current_qty, title

    def increase_quantity(self, row_index: int, current_qty: int) -> None:
        coordinate = Coordinate(row_index, 0)
        cell_value = self.table.get_cell_at(coordinate)

        prefix = self._get_prefix(cell_value)
        new_value = f'{prefix}{current_qty + 1}'
        self.table.update_cell_at(coordinate, new_value)

        if prefix:
            self._update_group_quantity(row_index, 1)

    def decrease_quantity(self, row_index: int, current_qty: int) -> bool:
        coordinate = Coordinate(row_index, 0)
        cell_value = self.table.get_cell_at(coordinate)
        prefix = self._get_prefix(cell_value)

        if current_qty - 1 <= 0:
            row_key = self.table.ordered_rows[row_index].key

            cell_title_value = self.table.get_cell_at(Coordinate(row_index, 1))
            base_name = self._extract_base_name(cell_title_value)

            if self.service.is_variants_exists(for_model=base_name):
                self._update_group_quantity_for_base_name(base_name, -1)

            self.table.remove_row(row_key)
            return True

        new_value = f'{prefix}{current_qty - 1}'
        self.table.update_cell_at(coordinate, new_value)

        if prefix:
            self._update_group_quantity(row_index, -1)

        return False

    def refresh(self) -> None:
        hangar_widget = self.table.parent
        if isinstance(hangar_widget, HangarWidget):
            hangar_widget.refresh_data()

    def _get_prefix(self, cell_value: str) -> str:
        if cell_value.startswith(HangarWidget.GROUPED_UNIT_PREFIX):
            return HangarWidget.GROUPED_UNIT_PREFIX
        return ''

    def _update_group_quantity_for_base_name(self, base_name: str, delta: int) -> None:
        group_row_key = f'{HangarWidget.GROUP_UNITS_PREFIX}{base_name}'
        group_values = self.table.get_row(row_key=group_row_key)

        if not group_values:
            return

        group_qty = int(group_values[0])
        new_qty = group_qty + delta

        if new_qty > 0:
            self.table.update_cell(
                row_key=group_row_key,
                column_key=HangarWidget.COLUMN_QTY_KEY,
                value=str(new_qty),
                update_width=True
            )
        else:
            self.table.remove_row(group_row_key)

    def _update_group_quantity(self, row_index: int, delta: int) -> None:
        cell_title_value = self.table.get_cell_at(Coordinate(row_index, 1))
        base_name = self._extract_base_name(cell_title_value)

        if not base_name:
            return

        self._update_group_quantity_for_base_name(base_name, delta)

    def _extract_base_name(self, title_value: str) -> str | None:
        import re
        match = re.search(r'.+?([()\s\w-]+)$', title_value, flags=re.IGNORECASE)
        if match:
            return extract_base_name(match.group(1).strip())
        return None
