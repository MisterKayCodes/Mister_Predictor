from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from data.database import Base


class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, autoincrement=True)
    external_id = Column(Integer, unique=True)
    utc_date = Column(DateTime, nullable=False)
    status = Column(String, default="SCHEDULED")
    matchday = Column(Integer, nullable=True)
    season = Column(String, nullable=True)

    home_team_id = Column(Integer, ForeignKey("teams.id"))
    away_team_id = Column(Integer, ForeignKey("teams.id"))

    home_score = Column(Integer, nullable=True)
    away_score = Column(Integer, nullable=True)
    home_ht_score = Column(Integer, nullable=True)
    away_ht_score = Column(Integer, nullable=True)

    predicted_home_win_prob = Column(Float, nullable=True)
    predicted_draw_prob = Column(Float, nullable=True)
    predicted_away_win_prob = Column(Float, nullable=True)

    home_team = relationship("Team", foreign_keys=[home_team_id], back_populates="home_matches")
    away_team = relationship("Team", foreign_keys=[away_team_id], back_populates="away_matches")
    odds = relationship("Odds", back_populates="match", cascade="all, delete-orphan")
    signals = relationship("Signal", back_populates="match")
