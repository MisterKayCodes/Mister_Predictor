from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from data.database import Base

class StandingSnapshot(Base):
    __tablename__ = "standings_snapshots"

    id = Column(Integer, primary_key=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    
    position = Column(Integer)
    played = Column(Integer)
    points = Column(Integer)
    goals_for = Column(Integer)
    goals_against = Column(Integer)
    goal_diff = Column(Integer)
    
    snapshot_date = Column(DateTime, default=datetime.utcnow)

    team = relationship("Team")