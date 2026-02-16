from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class MatchBase(BaseModel):
    external_id: int
    utc_date: datetime
    status: str = "SCHEDULED"
    home_team_id: int
    away_team_id: int
    home_score: Optional[int] = None
    away_score: Optional[int] = None
    matchday: Optional[int] = None
    season: Optional[str] = None


class MatchDisplay(BaseModel):
    id: int
    home_team: str
    away_team: str
    utc_date: datetime
    status: str
    home_score: Optional[int] = None
    away_score: Optional[int] = None

    class Config:
        from_attributes = True
