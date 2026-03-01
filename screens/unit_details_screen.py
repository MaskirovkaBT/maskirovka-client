from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal
from textual.screen import ModalScreen
from textual.widgets import Label, Button, Link

from domains.unit import Unit


class UnitDetailsScreen(ModalScreen):
    CSS_PATH = '../styles/styles_unit_details.tcss'

    def __init__(self, unit: Unit, **kwargs):
        super().__init__(**kwargs)
        self.unit = unit

    def compose(self) -> ComposeResult:
        url = f"http://masterunitlist.info/Unit/Details/{self.unit.unit_id}"
        with Vertical(id="unit-card"):
            yield Link(f"Детальная информация: {self.unit.title}", id="title", url=url)
            yield Label(f"Тип: {self.unit.unit_type}")
            yield Label(f"Роль: {self.unit.role}")
            yield Label(f"Стоимость: {self.unit.pv}")
            yield Label(f"Размер: {self.unit.sz}")
            yield Label(f"Движение: {self.unit.mv}")
            yield Label(f"Тяга: {self.unit.threshold}")
            yield Label(f"Нагрев: {self.unit.ov}")
            yield Label(f"Броня: {self.unit.armor}")
            yield Label(f"Структура: {self.unit.struc}")
            yield Label(f"Ближняя: {self.unit.short}")
            yield Label(f"Средняя: {self.unit.medium}")
            yield Label(f"Дальняя: {self.unit.long}")
            yield Label(f"Экстремальная: {self.unit.extreme}")
            yield Label(f"Спец. правила: {self.unit.specials}")
            with Horizontal(id="button-container"):
                yield Button("Закрыть", variant="primary", id="close")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "close":
            self.app.pop_screen()
