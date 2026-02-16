a/models/pattern_stat.py
Python

# data/models/bankroll.py
class BankrollHistory(Base):
    __tablename__ = "bankroll_history"
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    balance = Column(Float, nullable=False)
    pnl = Column(Float) # Profit/Loss from last update