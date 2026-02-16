from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from data.database import Base

class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True)
    external_id = Column(Integer, unique=True, nullable=False) # ID from API
    name = Column(String, nullable=False)
    short_name = Column(String)
    tla = Column(String) # e.g., 'ARS' for Arsenal

    # Relationships
    home_matches = relationship("Match", foreign_keys="Match.home_team_id", back_populates="home_team")
    away_matches = relationship("Match", foreign_keys="Match.away_team_id", back_populates="away_team")

    def __repr__(self):
        return f"<Team(name={self.name})>"