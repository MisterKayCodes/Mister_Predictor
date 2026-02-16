class StakeEngine:
    def calculate_kelly_stake(self, bankroll: float, odds: float, prob: float) -> float:
        if prob <= (1 / odds): return 0.0 # No value, no bet
        
        # Kelly Formula: (bp - q) / b 
        # b = odds - 1, p = prob, q = 1 - prob
        b = odds - 1
        kelly_fraction = (b * prob - (1 - prob)) / b
        
        # Apply 10% "Safety" fraction so we don't go broke
        safe_stake = bankroll * kelly_fraction * 0.1
        return max(0, safe_stake)