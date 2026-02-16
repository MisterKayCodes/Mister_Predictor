from sqlalchemy import Column, Integer, Float, String, DateTime
from datetime import datetime
from data.database import Base


class PatternStat(Base):
    __tablename__ = "pattern_stats"

    id = Column(Integer, primary_key=True, autoincrement=True)
    pattern_name = Column(String, unique=True)
    occurrences = Column(Integer, default=0)
    wins = Column(Integer, default=0)
    losses = Column(Integer, default=0)
    reliability_score = Column(Float, default=0.0)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
