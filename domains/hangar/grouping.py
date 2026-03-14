from domains.hangar.models import HangarUnit


class GroupedUnits:
    def __init__(self, base_name: str, units: list[HangarUnit]):
        self.base_name = base_name
        self.units = units
        self.total_quantity = sum(u.quantity for u in units)
        self.variant_count = len(units)
        self.is_expanded = False
