class ReliabilityTracker:
    def adjust_confidence(self, base_confidence: float, pattern_stats: dict) -> float:
        """
        pattern_stats example: {'pattern_name': 'HOME_COLD_STREAK', 'win_rate': 0.75}
        """
        if not pattern_stats:
            return base_confidence
            
        # If the pattern usually wins, boost confidence. If it's failing, tank it.
        win_rate = pattern_stats.get('win_rate', 0.5)
        reliability_multiplier = win_rate / 0.5 # 0.5 is neutral
        
        return min(1.0, base_confidence * reliability_multiplier)