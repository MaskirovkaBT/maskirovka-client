from textual.message import Message


class SearchUnitSelected(Message):
    def __init__(self, unit_id: str) -> None:
        self.unit_id = unit_id
        super().__init__()


class HangarUnitSelected(Message):
    def __init__(self, unit_id: str, comment: str = '') -> None:
        self.unit_id = unit_id
        self.comment = comment
        super().__init__()


class AddToHangar(Message):
    def __init__(self, unit_id: str) -> None:
        self.unit_id = unit_id
        super().__init__()
