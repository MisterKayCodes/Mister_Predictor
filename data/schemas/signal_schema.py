from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class SignalDisplay(BaseModel):
    id: int
    match_id: int
    home_team: str
    away_team: str
    match_date: datetime
    suggested_bet: str
    predicted_prob: Optional[float] = None
    value_edge: float
    bookmaker_odds: float
    confidence_score: float
    recommended_stake: float
    explanation: Optional[str] = None
    is_published: bool = False
    result_won: Optional[bool] = None
