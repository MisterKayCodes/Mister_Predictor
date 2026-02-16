def odds_to_implied_prob(decimal_odds: float) -> float:
    if decimal_odds <= 1:
        return 0.0
    return 1.0 / decimal_odds


def calculate_poisson_win_prob(lambda_home: float, lambda_away: float):
    pass


def get_margin(h_odds: float, d_odds: float, a_odds: float) -> float:
    total_prob = (1 / h_odds) + (1 / d_odds) + (1 / a_odds)
    return total_prob - 1.0
