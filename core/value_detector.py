class ValueDetector:
    def __init__(self, min_edge: float = 0.05):
        self.min_edge = min_edge

    def find_edge(self, pred_prob: float, market_prob: float) -> float:
        return pred_prob - market_prob

    def evaluate_all_markets(self, probs: dict, odds: dict, features: dict = None) -> list[dict]:
        markets = []

        market_map = {
            "HOME_WIN": ("home", "home_odds", "1x2"),
            "DRAW": ("draw", "draw_odds", "1x2"),
            "AWAY_WIN": ("away", "away_odds", "1x2"),
            "OVER_2.5": ("over_25", "over_25_odds", "totals"),
            "UNDER_2.5": (None, "under_25_odds", "totals"),
            "OVER_1.5": ("over_15", "over_15_odds", "totals"),
            "UNDER_1.5": (None, "under_15_odds", "totals"),
            "OVER_3.5": ("over_35", "over_35_odds", "totals"),
            "UNDER_3.5": (None, "under_35_odds", "totals"),
        }

        for bet_type, (prob_key, odds_key, market_key) in market_map.items():
            if prob_key is None:
                base = bet_type.replace("UNDER_", "OVER_")
                over_prob_key = market_map.get(base, (None,))[0]
                if over_prob_key and over_prob_key in probs:
                    pred_prob = 1.0 - probs[over_prob_key]
                else:
                    continue
            else:
                pred_prob = probs.get(prob_key, 0)

            decimal_odds = odds.get(odds_key, 0)
            if not decimal_odds or decimal_odds <= 1:
                continue

            implied_prob = 1.0 / decimal_odds
            edge = self.find_edge(pred_prob, implied_prob)
            if edge >= self.min_edge:
                consistency = self._get_consistency(bet_type, features) if features else 0.5
                markets.append({
                    "bet_type": bet_type,
                    "market_key": market_key,
                    "predicted_prob": round(pred_prob, 4),
                    "implied_prob": round(implied_prob, 4),
                    "odds": decimal_odds,
                    "edge": round(edge, 4),
                    "is_value": True,
                    "has_bookmaker_odds": True,
                    "consistency": round(consistency, 4),
                })

        TYPICAL_ODDS = {
            "BTTS_YES": 1.80,
            "BTTS_NO": 1.95,
            "CLEAN_SHEET_HOME": 2.50,
            "CLEAN_SHEET_AWAY": 3.00,
            "ODD_GOALS": 1.90,
            "EVEN_GOALS": 1.90,
            "HT_HOME": 2.80,
            "HT_DRAW": 2.00,
            "HT_AWAY": 4.50,
            "HT_OVER_0.5": 1.40,
            "LATE_GOAL": 2.20,
        }

        model_only_markets = {
            "BTTS_YES": ("btts_yes", "btts"),
            "BTTS_NO": ("btts_no", "btts"),
            "CLEAN_SHEET_HOME": ("clean_sheet_home", "clean_sheet"),
            "CLEAN_SHEET_AWAY": ("clean_sheet_away", "clean_sheet"),
            "ODD_GOALS": ("odd_goals", "odd_even"),
            "EVEN_GOALS": ("even_goals", "odd_even"),
            "HT_HOME": ("ht_home", "half_time"),
            "HT_DRAW": ("ht_draw", "half_time"),
            "HT_AWAY": ("ht_away", "half_time"),
            "HT_OVER_0.5": ("ht_over_05", "half_time"),
            "LATE_GOAL": ("late_goal", "late_goal"),
        }

        for bet_type, (prob_key, market_key) in model_only_markets.items():
            pred_prob = probs.get(prob_key, 0)
            if pred_prob < 0.05:
                continue

            reference_odds = TYPICAL_ODDS.get(bet_type, 2.0)
            implied_prob = 1.0 / reference_odds

            edge = pred_prob - implied_prob
            if edge < self.min_edge:
                continue

            fair_odds = round(1.0 / pred_prob, 2) if pred_prob > 0 else 0
            consistency = self._get_consistency(bet_type, features) if features else 0.5

            markets.append({
                "bet_type": bet_type,
                "market_key": market_key,
                "predicted_prob": round(pred_prob, 4),
                "implied_prob": round(implied_prob, 4),
                "odds": fair_odds,
                "edge": round(edge, 4),
                "is_value": True,
                "has_bookmaker_odds": False,
                "consistency": round(consistency, 4),
            })

        markets.sort(key=lambda x: x["edge"], reverse=True)
        return markets

    def _get_consistency(self, bet_type: str, features: dict) -> float:
        if not features:
            return 0.5

        mapping = {
            "HOME_WIN": "home_form_avg",
            "AWAY_WIN": "away_form_avg",
            "DRAW": None,
            "OVER_2.5": "over_25_home_rate",
            "OVER_1.5": "over_15_home_rate",
            "OVER_3.5": "over_35_home_rate",
            "BTTS_YES": "btts_home_rate",
            "BTTS_NO": None,
            "CLEAN_SHEET_HOME": "clean_sheet_home_rate",
            "CLEAN_SHEET_AWAY": "clean_sheet_away_rate",
            "ODD_GOALS": "odd_goals_rate",
            "EVEN_GOALS": None,
            "HT_HOME": None,
            "HT_DRAW": None,
            "HT_AWAY": None,
            "HT_OVER_0.5": None,
            "LATE_GOAL": "late_goal_home_rate",
        }

        feat_key = mapping.get(bet_type)
        if feat_key and feat_key in features:
            return features[feat_key]

        if bet_type == "BTTS_NO":
            r = features.get("btts_home_rate", 0.5)
            return 1.0 - r
        if bet_type == "EVEN_GOALS":
            r = features.get("odd_goals_rate", 0.5)
            return 1.0 - r
        if bet_type.startswith("UNDER_"):
            over_bt = bet_type.replace("UNDER_", "OVER_")
            over_key = mapping.get(over_bt)
            if over_key and over_key in features:
                return 1.0 - features[over_key]

        return 0.5
