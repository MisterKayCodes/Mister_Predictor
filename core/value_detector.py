class ValueDetector:
    def find_edge(self, pred_prob: float, market_prob: float) -> float:
        # Edge = Our % - Their %
        return pred_prob - market_prob