from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from datetime import datetime
from data.database import Base


class BankrollHistory(Base):
    __tablename__ = "bankroll_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    balance = Column(Float, nullable=False)
    stake = Column(Float, nullable=True)
    pnl = Column(Float, nullable=True)
    match_id = Column(Integer, ForeignKey("matches.id"), nullable=True)
