from domains.units.models import Unit


def extract_base_name(title: str) -> str:
    title = title.strip()
    if ' ' in title:
        title = title.split(' ')[0]
    if '-' in title:
        title = title.split('-')[0]
    if '(' in title:
        title = title.split('(')[0].strip()
    return title


class HangarUnit:
    def __init__(
        self,
        unit: Unit,
        quantity: int = 1,
        comment: str = '',
        unit_id: int | None = None,
        base_name: str | None = None
    ):
        self.unit = unit
        self.quantity = quantity
        self.comment = comment
        self.unit_id = unit_id or unit.unit_id
        self.base_name = base_name or extract_base_name(unit.title)

    def to_dict(self) -> dict:
        return {
            'unit_id': self.unit_id,
            'quantity': self.quantity,
            'comment': self.comment,
            'base_name': self.base_name,
            'unit_type': self.unit.unit_type,
            'title': self.unit.title,
            'pv': self.unit.pv,
            'role': self.unit.role,
            'sz': self.unit.sz,
            'mv': self.unit.mv,
            'short': self.unit.short,
            'medium': self.unit.medium,
            'long': self.unit.long,
            'extreme': self.unit.extreme,
            'ov': self.unit.ov,
            'armor': self.unit.armor,
            'struc': self.unit.struc,
            'threshold': self.unit.threshold,
            'specials': self.unit.specials,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'HangarUnit':
        unit = Unit(
            unit_id=int(data['unit_id']),
            unit_type=data['unit_type'],
            title=data['title'],
            pv=int(data['pv']),
            role=data['role'],
            sz=int(data['sz']),
            mv=data['mv'],
            short=int(data['short']),
            medium=int(data['medium']),
            long=int(data['long']),
            extreme=int(data['extreme']),
            ov=int(data['ov']),
            armor=int(data['armor']),
            struc=int(data['struc']),
            threshold=int(data['threshold']),
            specials=data['specials'],
        )
        return cls(
            unit=unit,
            quantity=int(data.get('quantity', 1)),
            comment=data.get('comment', ''),
            unit_id=int(data['unit_id']),
            base_name=data.get('base_name')
        )
