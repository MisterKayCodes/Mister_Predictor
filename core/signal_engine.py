class SignalEngine:
    def __init__(self, min_edge: float = 0.05, min_confidence: float = 0.5):
        self.min_edge = min_edge
        self.min_confidence = min_confidence

    def generate_final_decision(
        self,
        prob_report: dict,
        value_edge: float,
        confidence_score: float,
        stake_amount: float,
        bet_type: str = "HOME_WIN",
        patterns: list = None,
        market_confidence: float = 0.5,
    ) -> dict:
        is_viable = (
            value_edge >= self.min_edge
            and confidence_score >= self.min_confidence
            and stake_amount > 0
        )

        explanation_parts = []
        if value_edge >= 0.10:
            explanation_parts.append("Strong value edge detected")
        elif value_edge >= 0.05:
            explanation_parts.append("Moderate value edge")

        if confidence_score >= 0.75:
            explanation_parts.append("High confidence signal")
        elif confidence_score >= 0.60:
            explanation_parts.append("Decent confidence")

        if market_confidence >= 0.7:
            explanation_parts.append("Market agrees with prediction")

        if patterns:
            pattern_names = [p["name"] if isinstance(p, dict) else str(p) for p in patterns]
            explanation_parts.append(f"Patterns: {', '.join(pattern_names)}")

        explanation = ". ".join(explanation_parts) if explanation_parts else "Standard analysis"

        return {
            "decision": "BET" if is_viable else "PASS",
            "bet_type": bet_type,
            "edge": round(value_edge, 4),
            "confidence": round(confidence_score, 4),
            "market_confidence": round(market_confidence, 4),
            "stake": stake_amount,
            "expected_outcome": max(prob_report, key=prob_report.get),
            "explanation": explanation,
        }
