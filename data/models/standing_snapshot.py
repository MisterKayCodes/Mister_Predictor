from sqlalchemy import Column, Integer, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship
from datetime import datetime
from data.database import Base


class StandingSnapshot(Base):
    __tablename__ = "standings_snapshots"

    id = Column(Integer, primary_key=True, autoincrement=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)

    position = Column(Integer)
    played = Column(Integer)
    wins = Column(Integer, default=0)
    draws = Column(Integer, default=0)
    losses = Column(Integer, default=0)
    points = Column(Integer)
    goals_for = Column(Integer)
    goals_against = Column(Integer)
    goal_diff = Column(Integer)

    snapshot_date = Column(DateTime, default=datetime.utcnow)

    team = relationship("Team")
