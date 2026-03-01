from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal
from textual.screen import ModalScreen
from textual.widgets import Label, Button, RadioSet, RadioButton


class SortScreen(ModalScreen):
    CSS_PATH = '../styles/styles_sort.tcss'

    SORT_FIELDS = [
        ('title', 'Название'),
        ('role', 'Роль'),
        ('pv', 'Стоимость'),
        ('mv', 'Движение'),
        ('short', 'Ближняя'),
        ('medium', 'Средняя'),
        ('long', 'Дальняя'),
        ('armor', 'Броня'),
        ('struc', 'Структура'),
    ]

    SORT_ORDERS = [
        ('asc', 'По возрастанию'),
        ('desc', 'По убыванию'),
    ]

    def __init__(
        self,
        current_field: str = 'title',
        current_order: str = 'asc',
        **kwargs
    ):
        super().__init__(**kwargs)
        self.current_field = current_field
        self.current_order = current_order

    def compose(self) -> ComposeResult:
        with Vertical(id='sort-container'):
            yield Label('Сортировка', id='sort-title')

            yield Label('Поле:')
            with RadioSet(id='field-select'):
                for field_value, field_label in self.SORT_FIELDS:
                    yield RadioButton(
                        field_label,
                        value=field_value == self.current_field
                    )

            yield Label('Порядок:')
            with RadioSet(id='order-select'):
                for order_value, order_label in self.SORT_ORDERS:
                    yield RadioButton(
                        order_label,
                        value=order_value == self.current_order
                    )

            with Horizontal(id='button-container'):
                yield Button('Сортировать', variant='primary', id='sort')
                yield Button('Отмена', id='cancel')

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == 'sort':
            field_select = self.query_one('#field-select', RadioSet)
            order_select = self.query_one('#order-select', RadioSet)

            field_index = field_select.pressed_index
            order_index = order_select.pressed_index

            if field_index is not None and field_index >= 0:
                selected_field = self.SORT_FIELDS[field_index][0]
            else:
                selected_field = self.current_field

            if order_index is not None and order_index >= 0:
                selected_order = self.SORT_ORDERS[order_index][0]
            else:
                selected_order = self.current_order

            self.dismiss({
                'field': selected_field,
                'order': selected_order,
            })
        elif event.button.id == 'cancel':
            self.dismiss(None)
