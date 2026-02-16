from pydantic import BaseModel
from typing import Optional


class OddsSnapshot(BaseModel):
    match_id: int
    bookmaker: str = "average"
    market_type: str = "1x2"
    home_odds: float
    draw_odds: float
    away_odds: float
    implied_home_prob: Optional[float] = None
    implied_draw_prob: Optional[float] = None
    implied_away_prob: Optional[float] = None
