def odds_to_prob(decimal_odds: float) -> float:
    return 1.0 / decimal_odds if decimal_odds > 0 else 0.0


def odds_to_implied_prob(home: float, draw: float, away: float) -> tuple:
    h = 1.0 / home if home > 0 else 0
    d = 1.0 / draw if draw > 0 else 0
    a = 1.0 / away if away > 0 else 0
    return h, d, a


def calculate_edge(pred_prob: float, market_odds: float) -> float:
    market_prob = odds_to_prob(market_odds)
    return pred_prob - market_prob


def remove_margin(home: float, draw: float, away: float) -> tuple:
    raw_probs = [1 / home, 1 / draw, 1 / away]
    total = sum(raw_probs)
    return tuple(p / total for p in raw_probs)


def get_margin(h_odds: float, d_odds: float, a_odds: float) -> float:
    total_prob = (1 / h_odds) + (1 / d_odds) + (1 / a_odds)
    return total_prob - 1.0
