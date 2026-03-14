from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical, Horizontal
from textual.screen import ModalScreen
from textual.widgets import Label, Button, Link, Input, Static

from domains import Unit, HangarService
from domains.messages import AddToHangar


class UnitDetailsScreen(ModalScreen):
    BINDINGS = [
        Binding('escape', 'close', 'Закрыть'),
    ]
    CSS_PATH = '../styles/styles_unit_details.tcss'

    def __init__(
        self,
        unit: Unit,
        hangar_service: HangarService,
        initial_comment: str = '',
        is_in_hangar: bool = True,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.unit = unit
        self.hangar_service = hangar_service
        self.initial_comment = initial_comment
        self.is_in_hangar = is_in_hangar
        self._hangar_unit = self.hangar_service.get_by_unit_id(unit.unit_id)

    def compose(self) -> ComposeResult:
        url = f'http://masterunitlist.info/Unit/Details/{self.unit.unit_id}'

        with Vertical(id='unit-card'):
            yield Link(f'Детальная информация: {self.unit.title}', id='title', url=url)

            if self._hangar_unit:
                yield Static(
                    f'В ангаре: {self._hangar_unit.quantity} шт. | '
                    f'Комментарий: {self._hangar_unit.comment or 'нет'}',
                    id='hangar-info'
                )

            yield Label(f'Тип: {self.unit.unit_type}')
            yield Label(f'Роль: {self.unit.role}')
            yield Label(f'Стоимость: {self.unit.pv}')
            yield Label(f'Размер: {self.unit.sz}')
            yield Label(f'Движение: {self.unit.mv}')
            yield Label(f'Тяга: {self.unit.threshold}')
            yield Label(f'Нагрев: {self.unit.ov}')
            yield Label(f'Броня: {self.unit.armor}')
            yield Label(f'Структура: {self.unit.struc}')
            yield Label(f'Ближняя: {self.unit.short}')
            yield Label(f'Средняя: {self.unit.medium}')
            yield Label(f'Дальняя: {self.unit.long}')
            yield Label(f'Экстремальная: {self.unit.extreme}')
            yield Label(f'Спец. правила: {self.unit.specials}')

            if self.is_in_hangar:
                yield Label('Комментарий:', id='comment-label')
                yield Input(
                    value=self.initial_comment or (self._hangar_unit.comment if self._hangar_unit else ''),
                    placeholder='Добавьте заметку об этом юните...',
                    id='comment-input'
                )

            with Horizontal(id='button-container'):
                if not self.is_in_hangar:
                    yield Button('В ангар', variant='success', id='add-to-hangar')
                yield Button('Закрыть', variant='primary', id='close')

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == 'close':
            self._save_comment()
            self.app.pop_screen()
        elif event.button.id == 'add-to-hangar':
            self._add_to_hangar()

    def _add_to_hangar(self) -> None:
        self._hangar_unit = self.hangar_service.get_by_unit_id(self.unit.unit_id)

        info = self.query_one_optional('#hangar-info', Static)
        if info:
            info.update(
                f'В ангаре: {self._hangar_unit.quantity} шт. | '
                f'Комментарий: {self._hangar_unit.comment or 'нет'}'
            )

        self.post_message(AddToHangar(str(self.unit.unit_id)))
        self.dismiss()

    def _save_comment(self) -> None:
        if not self.is_in_hangar:
            return

        comment_input = self.query_one_optional('#comment-input', Input)
        if comment_input:
            comment = comment_input.value.strip()
            if self._hangar_unit and comment != self._hangar_unit.comment:
                self.hangar_service.update_comment(self.unit.unit_id, comment)

    def action_close(self) -> None:
        self._save_comment()
        self.app.pop_screen()
