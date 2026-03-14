import csv
import weakref
from pathlib import Path
from typing import Protocol, runtime_checkable, Optional

from domains.hangar.grouping import GroupedUnits
from domains.hangar.models import HangarUnit, extract_base_name
from domains.units.models import Unit


@runtime_checkable
class HangarServiceDelegate(Protocol):
    def service_did_change_unit_quantity(self, service: 'HangarService', unit_id: int) -> None:
        pass


class HangarService:
    DATA_DIR = Path('data')
    CSV_FILE = DATA_DIR / 'hangar.csv'

    def __init__(self):
        self._ensure_data_dir()
        self._units: list[HangarUnit] = []
        self._delegate: Optional[weakref.ref] = None
        self._load()

    @property
    def delegate(self) -> Optional[HangarServiceDelegate]:
        if self._delegate:
            return self._delegate()
        return None

    @delegate.setter
    def delegate(self, value: Optional[HangarServiceDelegate]):
        self._delegate = weakref.ref(value) if value else None

    def get_all(self) -> list[HangarUnit]:
        return self._units.copy()

    def get_by_unit_id(self, unit_id: int) -> HangarUnit | None:
        for u in self._units:
            if u.unit_id == unit_id:
                return u
        return None

    def is_empty(self) -> bool:
        return self._units == []

    def is_variants_exists(self, for_model: str) -> bool:
        grouped_units = self.get_grouped_units()
        model_base_name = extract_base_name(for_model)
        return any(u.base_name == model_base_name for u in grouped_units)

    def get_grouped_units(self) -> list[GroupedUnits]:
        groups: dict[str, list[HangarUnit]] = {}
        for u in self._units:
            base = u.base_name
            if base not in groups:
                groups[base] = []
            groups[base].append(u)
        return [GroupedUnits(name, units) for name, units in sorted(groups.items())]

    def increase_quantity(self, unit_id: int) -> None:
        existing = self.get_by_unit_id(unit_id)
        if not existing:
            return

        existing.quantity += 1
        self._save()

        if d := self.delegate:
            d.service_did_change_unit_quantity(service=self, unit_id=unit_id)

    def decrease_quantity(self, unit_id: int) -> None:
        existing = self.get_by_unit_id(unit_id)
        if not existing:
            return

        existing.quantity -= 1
        if existing.quantity <= 0:
            self._units = [u for u in self._units if u.unit_id != unit_id]
        self._save()

        if d := self.delegate:
            d.service_did_change_unit_quantity(service=self, unit_id=unit_id)

    def add_unit(self, unit: Unit, quantity: int = 1, comment: str = '') -> None:
        existing = self.get_by_unit_id(unit.unit_id)
        if existing:
            existing.quantity += quantity
        else:
            self._units.append(HangarUnit(unit, quantity, comment))
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
