class MarketConfidenceEngine:
    def get_score(self, our_pred: str, movement: str) -> float:
        # If we predict Home Win and the odds are dropping (Smart Money), confidence goes up
        score = 0.5 # Base
        if our_pred == movement:
            score += 0.3
        return score