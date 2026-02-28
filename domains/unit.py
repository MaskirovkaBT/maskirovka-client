from pydantic import BaseModel

class Unit(BaseModel):
    unit_id: int
    unit_type: str
    title: str
    pv: int
    role: str
    sz: int
    mv: str
    short: int
    medium: int
    long: int
    extreme: int
    ov: int
    armor: int
    struc: int
    threshold: int
    specials: str