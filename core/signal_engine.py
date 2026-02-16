class SignalEngine:
    def generate_final_decision(self, prob_report, value_report, confidence_score, stake_amount):
        # The threshold for a "Green Light"
        is_viable = value_report > 0.05 and confidence_score > 0.6 and stake_amount > 0
        
        return {
            "decision": "BET" if is_viable else "PASS",
            "edge": value_report,
            "confidence": confidence_score,
            "stake": stake_amount,
            "expected_outcome": max(prob_report, key=prob_report.get)
        }