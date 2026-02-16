from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum
from data.database import Base

class MatchStatus(enum.Enum):
    SCHEDULED = "SCHEDULED"
    TIMED = "TIMED"
    FINISHED = "FINISHED"

class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True)
    external_id = Column(Integer, unique=True)
    utc_date = Column(DateTime, nullable=False)
    status = Column(Enum(MatchStatus), default=MatchStatus.SCHEDULED)
    
    home_team_id = Column(Integer, ForeignKey("teams.id"))
    away_team_id = Column(Integer, ForeignKey("teams.id"))
    
    home_score = Column(Integer, nullable=True)
    away_score = Column(Integer, nullable=True)
    
    # Probabilities calculated by Core Engine (stored for later learning)
    predicted_home_win_prob = Column(Float, nullable=True)
    predicted_draw_prob = Column(Float, nullable=True)
    predicted_away_win_prob = Column(Float, nullable=True)

    home_team = relationship("Team", foreign_keys=[home_team_id], back_populates="home_matches")
    away_team = relationship("Team", foreign_keys=[away_team_id], back_populates="away_matches")
    odds = relationship("Odds", back_populates="match", cascade="all, delete-orphan")
    signal = relationship("Signal", back_populates="match", uselist=False)