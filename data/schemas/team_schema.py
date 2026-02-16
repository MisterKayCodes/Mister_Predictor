from pydantic import BaseModel
from typing import Optional


class TeamBase(BaseModel):
    external_id: int
    name: str
    short_name: Optional[str] = None
    tla: Optional[str] = None
