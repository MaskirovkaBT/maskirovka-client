import csv
from pathlib import Path

from domains.hangar_unit import HangarUnit
from domains.unit import Unit


class HangarService:
    DATA_DIR = Path('data')
    CSV_FILE = DATA_DIR / 'hangar.csv'

    def __init__(self):
        self._ensure_data_dir()
        self._units: list[HangarUnit] = []
        self._load()

    def get_all(self) -> list[HangarUnit]:
        return self._units.copy()

    def get_by_unit_id(self, unit_id: int) -> HangarUnit | None:
        for u in self._units:
            if u.unit_id == unit_id:
                return u
        return None

    def increase_quantity(self, unit_id: int) -> None:
        existing = self.get_by_unit_id(unit_id)
        if not existing:
            return

        existing.quantity += 1
        self._save()

    def decrease_quantity(self, unit_id: int) -> None:
        existing = self.get_by_unit_id(unit_id)
        if not existing:
            return

        existing.quantity -= 1
        if existing.quantity <= 0:
            self._units = [u for u in self._units if u.unit_id != unit_id]
        self._save()

    def add_unit(self, unit: Unit, quantity: int = 1, comment: str = '') -> None:
        existing = self.get_by_unit_id(unit.unit_id)
        if existing:
            existing.quantity += quantity
        else:
            self._units.append(HangarUnit(unit, quantity, comment))
        self._save()

    def remove_unit(self, unit_id: int, quantity: int = 1) -> None:
        existing = self.get_by_unit_id(unit_id)
        if not existing:
            return

        existing.quantity -= quantity
        if existing.quantity <= 0:
            self._units = [u for u in self._units if u.unit_id != unit_id]
        self._save()

    def update_comment(self, unit_id: int, comment: str) -> None:
        existing = self.get_by_unit_id(unit_id)
        if existing:
            existing.comment = comment
            self._save()

    def _ensure_data_dir(self) -> None:
        self.DATA_DIR.mkdir(parents=True, exist_ok=True)

    def _load(self) -> None:
        if not self.CSV_FILE.exists():
            self._units = []
            return

        try:
            with open(self.CSV_FILE, 'r', encoding='utf-8', newline='') as f:
                reader = csv.DictReader(f)
                self._units = [HangarUnit.from_dict(row) for row in reader]
        except (csv.Error, KeyError, ValueError):
            self._units = []

    def _save(self) -> None:
        if not self._units:
            if self.CSV_FILE.exists():
                self.CSV_FILE.unlink()
            return

        with open(self.CSV_FILE, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=self._units[0].to_dict().keys())
            writer.writeheader()
            for unit in self._units:
                writer.writerow(unit.to_dict())