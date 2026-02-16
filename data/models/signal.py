from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from data.database import Base

class Signal(Base):
    __tablename__ = "signals"

    id = Column(Integer, primary_key=True)
    match_id = Column(Integer, ForeignKey("matches.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    suggested_bet = Column(String) # e.g., "HOME_WIN"
    value_edge = Column(Float)     # e.g., 0.13 (13%)
    bookmaker_odds = Column(Float)
    
    confidence_score = Column(Float) # 0.0 to 1.0
    recommended_stake = Column(Float)
    
    is_published = Column(Boolean, default=False)
    result_won = Column(Boolean, nullable=True) # Updated by Learning Loop later

    match = relationship("Match", back_populates="signal")