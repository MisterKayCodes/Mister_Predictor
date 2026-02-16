class StakeEngine:
    def __init__(self, kelly_fraction: float = 0.1, max_stake_pct: float = 0.05):
        self.kelly_fraction = kelly_fraction
        self.max_stake_pct = max_stake_pct

    def calculate_kelly_stake(self, bankroll: float, odds: float, prob: float) -> float:
        if prob <= 0 or odds <= 1:
            return 0.0

        if prob <= (1 / odds):
            return 0.0

        b = odds - 1
        q = 1 - prob
        kelly = (b * prob - q) / b

        safe_stake = bankroll * kelly * self.kelly_fraction

        max_allowed = bankroll * self.max_stake_pct
        safe_stake = min(safe_stake, max_allowed)

        return max(0, round(safe_stake, 2))

    def adjust_for_streak(self, stake: float, recent_results: list[bool]) -> float:
        if len(recent_results) < 3:
            return stake

        last_3 = recent_results[-3:]
        if all(not r for r in last_3):
            return round(stake * 0.5, 2)

        if all(r for r in last_3):
            return round(stake * 1.2, 2)

        return stake
