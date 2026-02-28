from pydantic import BaseModel

class Faction(BaseModel):
    faction_id: int
    title: str