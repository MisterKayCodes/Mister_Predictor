from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from data.database import Base


class Signal(Base):
    __tablename__ = "signals"

    id = Column(Integer, primary_key=True, autoincrement=True)
    match_id = Column(Integer, ForeignKey("matches.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    market_key = Column(String, default="1x2")
    suggested_bet = Column(String)
    predicted_prob = Column(Float, nullable=True)
    implied_prob = Column(Float, nullable=True)
    value_edge = Column(Float)
    bookmaker_odds = Column(Float)

    confidence_score = Column(Float)
    market_confidence = Column(Float, nullable=True)
    reliability_score = Column(Float, nullable=True)
    recommended_stake = Column(Float)
    consistency_pct = Column(Float, nullable=True)
    rank_in_match = Column(Integer, nullable=True)

    patterns_detected = Column(String, nullable=True)
    explanation = Column(String, nullable=True)

    is_published = Column(Boolean, default=False)
    result_won = Column(Boolean, nullable=True)

    match = relationship("Match", back_populates="signals")
