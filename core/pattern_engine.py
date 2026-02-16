class PatternEngine:
    def detect_patterns(self, home_history: list, away_history: list) -> list:
        patterns = []
        
        # Example: Loss Streak Detection
        home_losses = [m for m in home_history[-3:] if m.home_score < m.away_score]
        if len(home_losses) >= 3:
            patterns.append("HOME_COLD_STREAK")
            
        # Example: "Giant Killer" pattern
        # (Logic to see if a small team consistently beats top 5 teams)
        
        return patterns