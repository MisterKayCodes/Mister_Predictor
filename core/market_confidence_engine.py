class MarketConfidenceEngine:
    def get_score(self, prediction: str, odds_history: list[dict]) -> float:
        if not odds_history or len(odds_history) < 2:
            return 0.5

        first = odds_history[0]
        latest = odds_history[-1]

        home_change = (latest.get("home_odds", 0) - first.get("home_odds", 0))
        away_change = (latest.get("away_odds", 0) - first.get("away_odds", 0))

        score = 0.5

        if prediction == "HOME_WIN":
            if home_change < 0:
                score += min(0.3, abs(home_change) * 0.1)
            elif home_change > 0:
                score -= min(0.2, abs(home_change) * 0.08)
        elif prediction == "AWAY_WIN":
            if away_change < 0:
                score += min(0.3, abs(away_change) * 0.1)
            elif away_change > 0:
                score -= min(0.2, abs(away_change) * 0.08)

        num_snapshots = len(odds_history)
        stability_bonus = min(0.1, num_snapshots * 0.02)
        score += stability_bonus

        return max(0.1, min(1.0, round(score, 3)))

    def get_score_simple(self, our_pred: str, movement: str) -> float:
        score = 0.5
        if our_pred == movement:
            score += 0.3
        return min(1.0, score)
