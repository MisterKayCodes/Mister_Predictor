class ReliabilityTracker:
    def adjust_confidence(self, base_confidence: float, pattern_stats: list[dict]) -> float:
        if not pattern_stats:
            return base_confidence

        total_weight = 0
        weighted_score = 0

        for stat in pattern_stats:
            win_rate = stat.get("win_rate", 0.5)
            sample_size = stat.get("sample_size", 1)
            weight = min(sample_size / 20, 1.0)

            weighted_score += win_rate * weight
            total_weight += weight

        if total_weight == 0:
            return base_confidence

        avg_reliability = weighted_score / total_weight
        reliability_multiplier = avg_reliability / 0.5

        adjusted = base_confidence * reliability_multiplier
        return max(0.1, min(1.0, adjusted))

    def calculate_pattern_reliability(self, wins: int, total: int) -> float:
        if total == 0:
            return 0.5
        return wins / total
