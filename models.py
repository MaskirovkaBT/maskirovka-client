from enum import Enum, auto

from pydantic import BaseModel


class Blocks(Enum):
    ERAS = auto()
    FACTIONS = auto()
    MAIN_CONTENT = auto()

class Era(BaseModel):
    era_id: int
    title: str

class Faction(BaseModel):
    faction_id: int
    title: str

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