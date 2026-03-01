from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal, Grid, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Label, Button, Input, Select


class FilterScreen(ModalScreen):
    CSS_PATH = '../styles/styles_filter.tcss'

    NUMERIC_FIELDS = [
        ('pv', 'Стоимость (PV)'),
        ('sz', 'Размер (SZ)'),
        ('short', 'Ближняя'),
        ('medium', 'Средняя'),
        ('long', 'Дальняя'),
        ('extreme', 'Экстремальная'),
        ('ov', 'Нагрев (OV)'),
        ('armor', 'Броня'),
        ('struc', 'Структура'),
        ('threshold', 'Тяга'),
        ('mv', 'Движение'),
    ]

    COMPARE_MODES = [
        ('eq', '=', 'Равно'),
        ('gt', '>', 'Больше'),
        ('gte', '>=', 'Больше или равно'),
        ('lt', '<', 'Меньше'),
        ('lte', '<=', 'Меньше или равно'),
    ]

    def __init__(self, current_filters: dict | None = None, **kwargs):
        super().__init__(**kwargs)
        self.current_filters = current_filters or {}

    def compose(self) -> ComposeResult:
        with Vertical(id='filter-container'):
            yield Label('Фильтрация юнитов', id='filter-title')

            with VerticalScroll(id='filter-scroll'):
                with Grid(id='filter-grid'):
                    yield Label('Название:')
                    yield Input(
                        value=self.current_filters.get('title', ''),
                        placeholder='Введите название...',
                        id='filter-title-input'
                    )

                    yield Label('Тип:')
                    yield Input(
                        value=self.current_filters.get('unit_type', ''),
                        placeholder='Введите тип...',
                        id='filter-unit-type-input'
                    )

                    yield Label('Роль:')
                    yield Input(
                        value=self.current_filters.get('role', ''),
                        placeholder='Введите роль...',
                        id='filter-role-input'
                    )

                    yield Label('Спец. правила:')
                    with Horizontal(classes='specials-row'):
                        yield Input(
                            value=self.current_filters.get('specials', ''),
                            placeholder='Введите спец. правила...',
                            id='filter-specials-input'
                        )
                        yield Select(
                            [('ИЛИ (любое)', 'or'), ('И (все)', 'and')],
                            value=self.current_filters.get('specials_mode', 'or'),
                            id='filter-specials-mode',
                            classes='specials-mode-select'
                        )

                yield Label('Числовые фильтры:', id='numeric-label')

                with Grid(id='numeric-filters-grid'):
                    for field_key, field_label in self.NUMERIC_FIELDS:
                        with Vertical(classes='numeric-filter-group'):
                            yield Label(field_label)
                            yield Input(
                                value=str(self.current_filters.get(field_key, '')),
                                placeholder='Значение',
                                id=f'filter-{field_key}-input',
                                classes='numeric-input'
                            )
                            yield Select(
                                [(mode[2], mode[0]) for mode in self.COMPARE_MODES],
                                value=self.current_filters.get(f'{field_key}_mode', 'eq'),
                                id=f'filter-{field_key}-mode',
                                classes='mode-select'
                            )

            with Horizontal(id='button-container'):
                yield Button('Применить', variant='primary', id='apply')
                yield Button('Сбросить', id='reset')
                yield Button('Отмена', id='cancel')

    def _get_input_value(self, input_id: str) -> str | None:
        input_widget = self.query_one(f'#{input_id}', Input)
        value = input_widget.value.strip()
        return value if value else None

    def _get_select_value(self, select_id: str) -> str | None:
        select_widget = self.query_one(f'#{select_id}', Select)
        value = select_widget.value
        return value if value != Select.BLANK else None

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == 'apply':
            filters = {}

            title = self._get_input_value('filter-title-input')
            if title:
                filters['title'] = title

            unit_type = self._get_input_value('filter-unit-type-input')
            if unit_type:
                filters['unit_type'] = unit_type

            role = self._get_input_value('filter-role-input')
            if role:
                filters['role'] = role

            specials = self._get_input_value('filter-specials-input')
            if specials:
                filters['specials'] = specials
                specials_mode = self._get_select_value('filter-specials-mode')
                filters['specials_mode'] = specials_mode if specials_mode else 'or'

            for field_key, _ in self.NUMERIC_FIELDS:
                value = self._get_input_value(f'filter-{field_key}-input')
                if value:
                    try:
                        filters[field_key] = int(value)
                        mode = self._get_select_value(f'filter-{field_key}-mode')
                        if mode:
                            filters[f'{field_key}_mode'] = mode
                    except ValueError:
                        pass

            self.dismiss(filters)

        elif event.button.id == 'reset':
            self.dismiss({})

        elif event.button.id == 'cancel':
            self.dismiss(None)
