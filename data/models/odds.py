from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from data.database import Base


class Odds(Base):
    __tablename__ = "odds_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    match_id = Column(Integer, ForeignKey("matches.id"), nullable=False)
    bookmaker = Column(String, default="average")
    market_type = Column(String, default="1x2")

    home_odds = Column(Float)
    draw_odds = Column(Float)
    away_odds = Column(Float)

    over_25_odds = Column(Float, nullable=True)
    under_25_odds = Column(Float, nullable=True)
    over_15_odds = Column(Float, nullable=True)
    under_15_odds = Column(Float, nullable=True)
    over_35_odds = Column(Float, nullable=True)
    under_35_odds = Column(Float, nullable=True)

    implied_home_prob = Column(Float, nullable=True)
    implied_draw_prob = Column(Float, nullable=True)
    implied_away_prob = Column(Float, nullable=True)

    recorded_at = Column(DateTime, default=datetime.utcnow)

    match = relationship("Match", back_populates="odds")
