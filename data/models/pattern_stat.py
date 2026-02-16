# data/models/pattern_stat.py
class PatternStat(Base):
    __tablename__ = "pattern_stats"
    id = Column(Integer, primary_key=True)
    pattern_name = Column(String, unique=True) # e.g., "Home_Underdog_Streak"
    occurrences = Column(Integer, default=0)
    wins = Column(Integer, default=0)
    reliability_score = Column(Float, default=0.0)