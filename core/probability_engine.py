class ProbabilityEngine:
    def calculate_probs(self, features: dict) -> dict:
        # Simple Weighted Logic for now
        # Form is 60% weight, Position Gap is 40%
        base_home = 0.38 + (features['home_form_avg'] * 0.2) + (features['position_gap'] * 0.01)
        
        # Keep it between 0 and 1
        home_win = max(0.05, min(0.95, base_home))
        draw = 0.25
        away_win = 1.0 - home_win - draw
        
        return {"home": home_win, "draw": draw, "away": away_win}