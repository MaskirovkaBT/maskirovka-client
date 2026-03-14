from textual.message import Message


class HangarUpdated(Message):
    def __init__(self, unit_id: int | None = None) -> None:
        self.unit_id = unit_id
        super().__init__()


class QuantityChanged(Message):
    def __init__(self, unit_id: int, new_quantity: int) -> None:
        self.unit_id = unit_id
        self.new_quantity = new_quantity
        super().__init__()
