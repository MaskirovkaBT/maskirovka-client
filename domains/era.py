from pydantic import BaseModel

class Era(BaseModel):
    era_id: int
    title: str