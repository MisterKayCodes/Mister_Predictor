def odds_to_implied_prob(home_odds: float, draw_odds: float, away_odds: float) -> tuple:
    """
    Converts decimal odds to implied probability, removing the 'bookmaker margin'.
    """
    raw_h = 1 / home_odds
    raw_d = 1 / draw_odds
    raw_a = 1 / away_odds
    
    total = raw_h + raw_d + raw_a
    # Normalized probabilities (sums to 1.0)
    return (raw_h / total), (raw_d / total), (raw_a / total)